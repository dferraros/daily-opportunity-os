"""
Daily Run Pipeline -- full daily scout + score + report workflow.

Steps:
1. Load raw signals from data/raw/YYYY-MM-DD-signals.jsonl
2. Normalize signals -> Opportunity objects
3. Dedupe against existing opportunities
4. Run kill gate on each -> mark kill_decision
5. Score surviving opportunities
6. Apply geo adjustments (VE/LATAM)
7. Assign portfolio lanes
8. Persist to opportunities.jsonl
9. Render and write reports (global, LATAM, Venezuela)
10. Export Notion CSVs
"""

from datetime import datetime
import json
import os
import time
from opportunity_os.pipeline_monitor import log_failure


def run_daily(date: str = None, geo: str = "global", dry_run: bool = False) -> dict:
    """
    Run the full daily opportunity pipeline.
    Returns summary dict: {processed, scored, killed, reports_written, errors}
    """
    from opportunity_os.storage import (
        read_all_opportunities,
        append_opportunity,
        dedupe_check,
        append_opp_score_history,
    )
    from opportunity_os.normalization import normalize_signals_batch
    from opportunity_os.engines.kill_gate import evaluate_kill_gate
    from opportunity_os.engines.scoring_engine import score_opportunity
    from opportunity_os.geo_lens import apply_geo_adjustments
    from opportunity_os.filters import PortfolioLaneAssigner
    from opportunity_os.exporters import daily_feed_to_csv, opportunities_to_csv
    from opportunity_os.reports import (
        render_template,
        report_path,
        write_report,
        ensure_report_dirs,
    )

    ensure_report_dirs()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    summary = {
        "date": date,
        "processed": 0,
        "scored": 0,
        "killed": 0,
        "reports_written": [],
        "errors": [],
    }

    # Step 1: Load raw signals
    root = _get_project_root()
    raw_file = os.path.join(root, "data", "raw", f"{date}-signals.jsonl")
    raw_signals = []
    if os.path.exists(raw_file):
        with open(raw_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        raw_signals.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        log_failure("signal_parse", exc)
                        summary["errors"].append(f"JSON parse error: {exc}")

    if not raw_signals:
        print(f"No raw signals found for {date}. Add signals to {raw_file}")
        _write_empty_venezuela_report(date, dry_run, summary)
        return summary

    # Step 2: Normalize
    valid_opps, failed = normalize_signals_batch(raw_signals)
    summary["processed"] = len(valid_opps)
    for err in failed:
        summary["errors"].append(f"Normalization failed: {err.get('errors', [])}")

    # Step 2.5: Heuristic pre-score → batch AI scoring (1 API call for survivors only)
    # Cost strategy: heuristic first on all signals, then 1 batch AI call on top candidates.
    # This replaces N individual API calls (1/opp) with at most 1 batch call for top 10.
    from opportunity_os.ai_scorer import _heuristic_fallback, score_batch_with_ai
    valid_opps_dicts = [_heuristic_fallback(opp.model_dump()) for opp in valid_opps]

    # Only batch-score opps that look promising on heuristic (avoids scoring obvious throwaways)
    candidates = [o for o in valid_opps_dicts if not o.get("ai_scored_at") and
                  sum(o.get(d, 0) or 0 for d in ["pain_severity", "regional_fit", "market_size"]) >= 12][:10]
    if candidates:
        print(f"Step 2.5: Batch AI scoring {len(candidates)}/{len(valid_opps_dicts)} candidates (1 API call)...")
        try:
            scored = score_batch_with_ai(candidates)
            scored_ids = {id(o) for o in candidates}
            valid_opps_dicts = [o for o in valid_opps_dicts if id(o) not in scored_ids] + scored
            ai_count = sum(1 for o in valid_opps_dicts if o.get("ai_scored_at"))
            print(f"  AI scoring complete: {ai_count} scored by AI, "
                  f"{len(valid_opps_dicts) - ai_count} used heuristic fallback")
        except Exception as exc:
            log_failure("ai_scoring", exc)
    else:
        print(f"Step 2.5: All {len(valid_opps_dicts)} opps scored by heuristic (no API call needed)")

    # Steps 3-8: Process each opportunity
    lane_assigner = PortfolioLaneAssigner()
    scored_opps = []
    killed_opps = []
    ve_lens_count = 0

    for opp_dict in valid_opps_dicts:

        # Step 3: Dedupe
        dup_id = dedupe_check(opp_dict.get("name", ""), opp_dict.get("geography", ""))
        if dup_id:
            continue

        # Step 4: Kill gate (if kill_decision not already set)
        if not opp_dict.get("kill_decision") and opp_dict.get("kill_criteria_passed") is None:
            answers = _infer_kill_answers(opp_dict)
            result = evaluate_kill_gate(answers)
            opp_dict["kill_decision"] = result.kill_decision
            opp_dict["kill_criteria_passed"] = result.passed_count
            if result.kill_decision:
                opp_dict["kill_reason"] = result.kill_reason

        if opp_dict.get("kill_decision"):
            opp_dict["stage"] = "killed"
            opp_dict["portfolio_lane"] = "no"
            killed_opps.append(opp_dict)
            if not dry_run:
                append_opportunity(opp_dict)
            summary["killed"] += 1
            continue

        # Step 5: Score
        opp_dict = score_opportunity(opp_dict)

        # Step 5.5: Extra Venezuela lens pass for VE opps
        if opp_dict.get("geography") == "venezuela":
            try:
                opp_dict = apply_geo_adjustments(opp_dict)
                opp_dict["venezuela_lens_applied"] = True
                ve_lens_count += 1
            except Exception as e:
                log_failure("venezuela_lens_auto", e, opp_id=opp_dict.get("id", "unknown"))

        # Step 6: Geo adjustments
        opp_dict = apply_geo_adjustments(opp_dict)

        # Step 7: Portfolio lane
        lane = lane_assigner.assign_from_dict(opp_dict)
        opp_dict["portfolio_lane"] = lane

        scored_opps.append(opp_dict)
        summary["scored"] += 1

        # Step 8: Persist
        if not dry_run:
            append_opportunity(opp_dict)

            # Step 8.5: Record score history
            try:
                final_score = float(opp_dict.get("final_score", 0))
                if final_score > 0:
                    append_opp_score_history(opp_dict["id"], final_score)
            except Exception as e:
                log_failure("score_history_append", e, opp_id=opp_dict.get("id", "unknown"))

    if ve_lens_count > 0:
        print(f"Step 5.5: Venezuela lens applied to {ve_lens_count} opportunities")

    # Step 9: Rank scored opportunities
    all_opps_sorted = sorted(
        scored_opps, key=lambda x: x.get("final_score", 0), reverse=True
    )

    # Step 9.3: Normalize scores across today's portfolio (fixes AI clustering at 7-9)
    # Only activates if >= 3 opps with spread > 0.1. Backs up raw to raw_final_score.
    if len(all_opps_sorted) >= 3:
        from opportunity_os.engines.scoring_engine import normalize_portfolio_scores
        all_opps_sorted = normalize_portfolio_scores(all_opps_sorted)
        live_scores = [o.get("final_score", 0) for o in all_opps_sorted if not o.get("kill_decision")]
        if live_scores:
            print(f"Step 9.3: Score normalization applied. Range: "
                  f"{min(live_scores):.2f} - {max(live_scores):.2f} "
                  f"(raw scores preserved in raw_final_score)")

    # ─── Step 9.5: TAM Estimation — estimate market size for all scored opps ───
    print(f"Step 9.5: Running TAM estimation on {len(all_opps_sorted)} scored opportunities...")
    try:
        from opportunity_os.engines.tam_engine import estimate_tam_from_opp
        for opp in all_opps_sorted:
            if not opp.get("tam") and not opp.get("tam_usd_estimate"):
                result = estimate_tam_from_opp(opp)
                opp.update({k: v for k, v in result.items() if not k.startswith("_")})
        tam_populated = sum(1 for o in all_opps_sorted if o.get("tam") or o.get("tam_usd_estimate"))
        print(f"  TAM populated for {tam_populated}/{len(all_opps_sorted)} opportunities")
    except ImportError as e:
        print(f"WARNING  TAM engine not available: {e}")
    except Exception as e:
        log_failure("tam_estimation", e)

    # ─── Step 9.7: Benchmark Mapping — map top 30 to archetypes ───
    print("Step 9.7: Running Benchmark Mapper on top 30 opportunities...")
    top_30 = all_opps_sorted[:30]
    try:
        from opportunity_os.engines.benchmark_engine import run_benchmark
        for opp in top_30:
            if not opp.get("benchmark_archetype"):
                result = run_benchmark(opp)
                opp.update({k: v for k, v in result.items() if not k.startswith("_")})
        bench_populated = sum(1 for o in top_30 if o.get("benchmark_archetype"))
        print(f"  Benchmark archetypes populated for {bench_populated}/{len(top_30)} opportunities")
    except ImportError as e:
        print(f"WARNING  Benchmark engine not available: {e}")
    except Exception as e:
        log_failure("benchmark_mapping", e)

    # ─── Step 10: Customer Pain OS — enrich top 20 scored opportunities ───
    print("Step 10: Running Customer Pain OS on top 20 opportunities...")
    top_20 = all_opps_sorted[:20]
    try:
        from opportunity_os.pain_intelligence import run_pain_intelligence
        for opp in top_20:
            pain_result = run_pain_intelligence(opp)
            opp.update({k: v for k, v in pain_result.items() if not k.startswith("_")})
            print(f"  Pain queries built for: {opp.get('name', 'unknown')} ({len(pain_result.get('_pain_queries', []))} queries)")
    except ImportError as e:
        print(f"WARNING  Pain intelligence module not available: {e}")
    except Exception as e:
        log_failure("pain_os", e)

    # ─── Step 11: Distribution OS — map distribution reality for top 20 ───
    print("Step 11: Running Distribution OS on top 20 opportunities...")
    try:
        from opportunity_os.distribution_intelligence import run_distribution_intelligence
        for opp in top_20:
            dist_result = run_distribution_intelligence(opp)
            opp.update({k: v for k, v in dist_result.items() if not k.startswith("_")})
            channels = dist_result.get("_recommended_channels", [])
            print(f"  Distribution mapped for: {opp.get('name', 'unknown')} -> top channel: {channels[0] if channels else 'unknown'}")
    except ImportError as e:
        print(f"WARNING  Distribution intelligence module not available: {e}")
    except Exception as e:
        log_failure("distribution_os", e)

    # ─── Step 11.5: Research Executor — fire real web searches (top 3 ONLY — API costs $) ───
    # Cost: ~$0.08-0.15 per opp with web_search. Top 3 = ~$0.50/day max.
    # Never increase this without checking Anthropic billing first.
    top_3_research = [o for o in all_opps_sorted[:3] if not o.get("research_executed_at")]
    print(f"Step 11.5: Running Research Executor on top 3 new opportunities ({len(top_3_research)} unresearched)...")
    try:
        from opportunity_os.research_executor import run_research_executor
        for i, opp in enumerate(top_3_research, 1):
            print(f"  Researching {i}/{len(top_3_research)}: {opp.get('name', 'unknown')[:50]}")
            run_research_executor(opp)
    except ImportError as e:
        print(f"WARNING  Research executor not available: {e}")
    except Exception as e:
        log_failure("research_executor", e)

    # ─── Step 11.6: Free Research — Jina + HN + Reddit for opps 4-20 ───
    # Zero cost. Covers what the paid API executor skips.
    print("Step 11.6: Running free research (Jina + HN + Reddit) on top 20...")
    try:
        from opportunity_os.free_research import research_opportunity_free
        free_researched = 0
        for opp in all_opps_sorted[:20]:
            if not opp.get("research_executed_at") and not opp.get("free_research_at"):
                updates = research_opportunity_free(opp)
                if updates:
                    opp.update(updates)
                    free_researched += 1
                time.sleep(0.5)
        print(f"  Free research complete: {free_researched} opps enriched")
    except Exception as e:
        log_failure("free_research", e)

    # ─── Step 11.8: Pain Library — persist pain clusters from researched opps ───
    print("Step 11.8: Updating pain library with researched opportunities...")
    try:
        from opportunity_os.pain_library import upsert_pain_cluster
        written = 0
        for opp in top_20:
            if opp.get("research_executed_at") and opp.get("pain_validation_score") is not None:
                if upsert_pain_cluster(opp):
                    written += 1
        print(f"  Pain library updated: {written} clusters upserted")
    except ImportError as e:
        print(f"WARNING  Pain library not available: {e}")
    except Exception as e:
        log_failure("pain_library", e)

    # ─── Step 12: Save enriched records back to JSONL ───
    print("Step 12: Saving enriched opportunity records...")
    if not dry_run:
        try:
            all_stored_opps = read_all_opportunities()
            enriched_ids = {o["id"]: o for o in top_20 if o.get("id")}
            updated_opps = [enriched_ids.get(o.get("id"), o) for o in all_stored_opps]
            opps_path = os.path.join(_get_project_root(), "data", "opportunities", "opportunities.jsonl")
            with open(opps_path, "w", encoding="utf-8") as f:
                for o in updated_opps:
                    f.write(json.dumps(o, default=str) + "\n")
            print(f"  Saved {len(top_20)} enriched records")
        except Exception as e:
            log_failure("save_enriched", e)

    # ─── Step 14 (pre-collect): Identify auto-validation candidates ─────────────
    validation_packages_for_sync = []
    try:
        from opportunity_os.validation_engine import run_validation, AUTO_VALIDATION_THRESHOLD
        import yaml

        config_path = os.path.join(_get_project_root(), "config", "scoring_weights.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            threshold = cfg.get("thresholds", {}).get("auto_validation", AUTO_VALIDATION_THRESHOLD)
        except Exception:
            threshold = AUTO_VALIDATION_THRESHOLD

        validation_candidates = [
            o for o in all_opps_sorted
            if float(o.get("final_score", 0)) >= threshold
            and not o.get("kill_decision")
            and o.get("stage") == "scout"
        ]
        for opp in validation_candidates:
            package = run_validation(opp, mode="auto")
            opp.update({k: v for k, v in package.items() if not k.startswith("_")})
            validation_packages_for_sync.append((opp, package))
    except ImportError:
        validation_candidates = []
    except Exception as e:
        log_failure("validation_pre_collect", e)
        validation_candidates = []

    # ─── Step 13: Build Notion sync payload (JSON for Claude Code to execute) ───
    print("Step 13: Building Notion sync payload...")
    try:
        from opportunity_os.notion_sync import build_sync_payload
        from collections import Counter
        raw_geo = Counter(s.get("geography", "global") for s in raw_signals)
        today_scores = [float(o.get("final_score", 0)) for o in valid_opps_dicts if o.get("final_score")]
        run_stats = {
            "signals_total": len(raw_signals),
            "new_opps": summary["scored"],
            "killed": summary["killed"],
            "top_score": round(max(today_scores), 2) if today_scores else 0,
            "score_range": f"{min(today_scores):.2f} - {max(today_scores):.2f}" if today_scores else "N/A",
            "by_geo": {
                "venezuela": raw_geo.get("venezuela", 0),
                "latam": raw_geo.get("latam", 0),
                "global": raw_geo.get("global", 0),
            },
            "top_opportunity": all_opps_sorted[0].get("name", "") if all_opps_sorted else "",
            "notes": (
                f"Heuristic scoring. "
                f"{sum(1 for o in all_opps_sorted if o.get('portfolio_lane') == 'now')} now-lane candidates."
            ),
        }
        sync_payload = build_sync_payload(all_opps_sorted[:20], run_stats, date, validation_packages=validation_packages_for_sync)
        sync_path = os.path.join(_get_project_root(), "reports", "daily", f"{date}-notion-sync.json")
        with open(sync_path, "w", encoding="utf-8") as f:
            json.dump(sync_payload, f, indent=2, default=str)
        print(f"  Notion sync payload ready: {len(sync_payload['upsert_opps'])} opps to upsert -> {sync_path}")
        print(f"\n>>> NOTION SYNC READY: run `uv run python scripts/notion_push.py` or ask Claude to sync {sync_path}")
    except Exception as e:
        log_failure("notion_sync", e)

    # ─── Step 14: Write validation markdown files for auto-promoted opps ────────
    print("Step 14: Auto-validating high-scoring scouts...")
    try:
        if validation_packages_for_sync:
            ensure_report_dirs()
            for opp, package in validation_packages_for_sync:
                if not dry_run:
                    safe_id = str(opp.get("id", "unknown"))[:40]
                    md_path = os.path.join(
                        _get_project_root(), "reports", "validation",
                        f"{date}-{safe_id}-validation.md",
                    )
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(package["_validation_markdown"])
                print(f"  Validated: {opp.get('name', 'unknown')} (score {opp.get('final_score', 0):.2f})")
            print(f"  {len(validation_packages_for_sync)} opp(s) promoted to validation stage")
        else:
            threshold_display = AUTO_VALIDATION_THRESHOLD if "AUTO_VALIDATION_THRESHOLD" in dir() else 7.0
            print(f"  No scouts above threshold {threshold_display} — no auto-validation triggered")
    except Exception as e:
        log_failure("validation_write", e)

    # --- Step 14.5: Auto deep-dive on top scorer >= 8.0 ---
    print("Step 14.5: Checking for auto deep-dive candidates...")
    try:
        from opportunity_os.pipelines.deep_dive import run_deep_dive
        deep_dive_candidates = [
            o for o in all_opps_sorted
            if float(o.get("final_score", 0)) >= 8.0
            and not o.get("kill_decision")
        ][:1]  # top 1 only
        for opp in deep_dive_candidates:
            opp_id = opp.get("id", "unknown")
            # Skip if deep dive already exists for this opp today
            dd_path = os.path.join(
                root, "reports", "deep-dives", f"{date}-{opp_id[:40]}-deep-dive.md"
            )
            if os.path.exists(dd_path):
                print(f"  Deep dive already exists for {opp_id}, skipping")
                continue
            if not dry_run:
                result = run_deep_dive(opp_id=opp_id, dry_run=dry_run)
                if "error" not in result:
                    print(f"  Auto deep-dive triggered: {opp.get('name', 'unknown')[:50]} (score {opp.get('final_score', 0):.1f})")
                else:
                    print(f"  Deep dive failed for {opp_id}: {result['error']}")
            else:
                print(f"  [dry-run] Would deep-dive: {opp.get('name', 'unknown')[:50]}")
        if not deep_dive_candidates:
            print("  No opportunities scored >= 8.0 -- no auto deep-dive")
    except Exception as e:
        print(f"WARNING  Step 14.5 auto deep-dive error (non-blocking): {e}")

    # Render reports
    context = {
        "date": date,
        "opportunities": all_opps_sorted,
        "kills": killed_opps,
        "top_n": 10,
        "rising": [],
        "run_stats": {
            "total_scored": len(scored_opps),
            "total_killed": len(killed_opps),
            "total_today": len(scored_opps) + len(killed_opps),
        },
    }
    _render_and_write(
        render_template("daily_report.md.j2", context),
        report_path("daily", date),
        dry_run,
        summary,
    )

    # LATAM report
    from opportunity_os.geo_lens import LATAM_ADJUSTMENTS

    latam_context = {
        **context,
        "payment_context": LATAM_ADJUSTMENTS.get("preferred_payment", {}),
    }
    _render_and_write(
        render_template("latam_report.md.j2", latam_context),
        report_path("latam", date),
        dry_run,
        summary,
    )

    # Venezuela report (ALWAYS written)
    ve_opps = [
        o for o in all_opps_sorted if o.get("geography") == "venezuela"
    ]
    wedge_counts: dict = {}
    for o in ve_opps:
        cat = o.get("venezuela_wedge_category", "unclassified")
        wedge_counts[cat] = wedge_counts.get(cat, 0) + 1

    all_stored = read_all_opportunities()
    standing = sorted(
        [
            o
            for o in all_stored
            if o.get("geography") == "venezuela"
            and o.get("first_seen", "") < date
        ],
        key=lambda x: x.get("final_score", 0),
        reverse=True,
    )[:3]

    ve_context = {
        "date": date,
        "ve_opps": ve_opps,
        "wedge_summary": wedge_counts,
        "standing_signals": standing,
    }
    _render_and_write(
        render_template("venezuela_report.md.j2", ve_context),
        report_path("venezuela", date),
        dry_run,
        summary,
    )

    # Step 10: Export CSVs
    if not dry_run:
        all_scored = read_all_opportunities()
        daily_feed_to_csv(all_scored)
        opportunities_to_csv(all_scored)

    print(
        f"\nDaily run complete: {summary['scored']} scored, {summary['killed']} killed"
    )
    print(
        f"   Reports: {', '.join(os.path.basename(r) for r in summary['reports_written'])}"
    )

    # Step 11: Track interview quota
    from opportunity_os.interview_tracker import get_interview_quota_status
    quota = get_interview_quota_status()
    if not quota["on_track"]:
        print(f"WARNING  Interview quota behind: {quota['completed']}/{quota['total_required']} done, {quota['days_remaining']} days left")

    # Step 12: Outcome calibration check (weekly)
    from opportunity_os.outcome_tracking import get_calibration_report
    # Only show if we have tracked outcomes
    if os.path.exists(os.path.join(_get_project_root(), "data", "outcome_tracking.jsonl")):
        report = get_calibration_report()
        if report["total_tracked"] > 0:
            print(f"Score accuracy: {report['score_accuracy']:.0%} ({report['total_tracked']} tracked outcomes)")

    # Step 15: Track quota progress from config
    try:
        import yaml
        config_path = os.path.join(root, "config", "weekly_quotas.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            quotas_config = yaml.safe_load(f)
        quotas = quotas_config.get("weekly_quotas", {})

        from opportunity_os.storage import append_machine_metrics
        metrics = {
            "date": date,
            "run_type": "daily",
            "signals_ingested": len(raw_signals),
            "opportunities_scored": summary["scored"],
            "opportunities_killed": summary["killed"],
            "deep_dives_produced": 0,  # counted separately via deep-dive command
            "validations_run": len(validation_packages_for_sync) if validation_packages_for_sync else 0,
            "quota_targets": {
                "signals": quotas.get("signals_ingested", {}).get("target", 40),
                "opps": quotas.get("structured_opportunities", {}).get("target", 10),
                "deep_dives": quotas.get("deep_dives_produced", {}).get("target", 3),
                "validations": quotas.get("validations_run", {}).get("target", 2),
            },
        }
        append_machine_metrics(metrics)
        print(f"Step 15: Quota progress tracked (signals: {metrics['signals_ingested']}, opps: {metrics['opportunities_scored']})")
    except Exception as e:
        log_failure("quota_tracking", e)

    return summary


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _infer_kill_answers(opp_dict: dict) -> dict:
    """Infer kill gate answers from available opportunity fields."""
    answers: dict = {}
    answers["KG-01"] = bool(opp_dict.get("problem_statement"))
    answers["KG-02"] = bool(opp_dict.get("target_customer"))
    answers["KG-03"] = (opp_dict.get("distribution_accessibility") or 5) >= 5
    pfr = opp_dict.get("path_to_first_revenue")
    answers["KG-04"] = bool(pfr) if isinstance(pfr, str) else (pfr or 5) >= 5
    answers["KG-05"] = (opp_dict.get("speed_to_mvp") or 5) >= 5
    # KG-06: if no TAM yet (raw scout signal), give benefit of the doubt —
    # TAM estimation runs in step 9.5 after kill gate, so we can't penalise here.
    tam = opp_dict.get("tam_usd_estimate") or opp_dict.get("tam")
    answers["KG-06"] = True if not tam else float(tam) >= 10_000_000
    answers["KG-07"] = opp_dict.get("defensibility", 5) >= 5 or bool(
        opp_dict.get("venezuela_wedge_category")
    ) or bool(opp_dict.get("problem_statement"))
    return answers


def _render_and_write(content: str, path: str, dry_run: bool, summary: dict):
    """Write rendered content to path (or skip if dry_run)."""
    from opportunity_os.reports import write_report

    if dry_run:
        print(f"[dry-run] Would write: {os.path.basename(path)}")
    else:
        write_report(content, path)
    summary["reports_written"].append(path)


def _write_empty_venezuela_report(date: str, dry_run: bool, summary: dict):
    """Write Venezuela report even when no signals found."""
    from opportunity_os.reports import render_template, report_path, write_report
    from opportunity_os.storage import read_all_opportunities

    all_stored = read_all_opportunities()
    standing = sorted(
        [o for o in all_stored if o.get("geography") == "venezuela"],
        key=lambda x: x.get("final_score", 0),
        reverse=True,
    )[:3]
    ve_context = {
        "date": date,
        "ve_opps": [],
        "wedge_summary": {},
        "standing_signals": standing,
    }
    content = render_template("venezuela_report.md.j2", ve_context)
    _render_and_write(content, report_path("venezuela", date), dry_run, summary)


def _get_project_root() -> str:
    from pathlib import Path

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])
