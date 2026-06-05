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
import logging
import os
import time
from opportunity_os.pipeline_monitor import log_failure

logger = logging.getLogger(__name__)


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

    # Auto-backup before any pipeline mutation (protects against step-12 full rewrite)
    if not dry_run:
        from opportunity_os.backup import create_backup
        snap = create_backup("pre-daily")
        if snap:
            logger.info("Pre-run snapshot: %d records -> %s", snap["record_count"], snap["filename"])
        else:
            logger.warning("Pre-run snapshot skipped (store empty or missing)")

    summary = {
        "date": date,
        "processed": 0,
        "scored": 0,
        "killed": 0,
        "deep_dives_produced": 0,
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
        logger.info("No raw signals file for %s -- attempting auto-harvest...", date)
        raw_signals = _auto_harvest(date, raw_file, dry_run)
        if not raw_signals:
            logger.info("Auto-harvest produced 0 signals. Writing empty report.")
            _write_empty_venezuela_report(date, dry_run, summary)
            return summary

    # Step 2: Normalize
    valid_opps, failed = normalize_signals_batch(raw_signals)
    summary["processed"] = len(valid_opps)
    for err in failed:
        summary["errors"].append(f"Normalization failed: {err.get('errors', [])}")

    # Step 2.3: Heuristic pre-score on all signals (no API call)
    from opportunity_os.ai_scorer import _heuristic_fallback, score_batch_with_ai
    valid_opps_dicts = [_heuristic_fallback(opp.model_dump()) for opp in valid_opps]

    # Step 2.4: Field enrichment — populate why_now, daniels_wedge_score, path_to_first_revenue
    valid_opps_dicts = [_enrich_fields(o) for o in valid_opps_dicts]

    # Steps 3-4: Kill gate pass — runs on heuristic scores only (no API tokens spent on throwaways)
    lane_assigner = PortfolioLaneAssigner()
    survivors = []
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
            opp_dict = {**opp_dict, "kill_decision": result.kill_decision, "kill_criteria_passed": result.passed_count}
            if result.kill_decision:
                opp_dict = {**opp_dict, "kill_reason": result.kill_reason}

        if opp_dict.get("kill_decision"):
            opp_dict = {**opp_dict, "stage": "killed", "portfolio_lane": "no"}
            killed_opps.append(opp_dict)
            if not dry_run:
                append_opportunity(opp_dict)
            summary["killed"] += 1
            continue

        survivors.append(opp_dict)

    # Step 2.5 (relocated after kill gate): Batch AI score only kill-gate survivors
    # Saves API tokens that would have been spent on throwaways.
    ai_candidates = [o for o in survivors if not o.get("ai_scored_at")][:10]
    if ai_candidates:
        logger.info("Step 2.5: Batch AI scoring %d/%d kill-gate survivors (1 API call)...", len(ai_candidates), len(survivors))
        try:
            ai_scored = score_batch_with_ai(ai_candidates)
            scored_ids = {o["id"] for o in ai_candidates if o.get("id")}
            survivors = [o for o in survivors if o.get("id") not in scored_ids] + ai_scored
            ai_count = sum(1 for o in survivors if o.get("ai_scored_at"))
            logger.info("  AI scoring complete: %d scored by AI, %d used heuristic fallback",
                        ai_count, len(survivors) - ai_count)
        except Exception as exc:
            log_failure("ai_scoring", exc)
    else:
        logger.info("Step 2.5: All %d survivors scored by heuristic (no API call needed)", len(survivors))

    # Steps 5-8: Score, adjust, assign lanes, persist for kill-gate survivors
    scored_opps = []

    for opp_dict in survivors:

        # Step 5: Score
        opp_dict = score_opportunity(opp_dict)

        # Step 6: Geo adjustments (all geographies — VE handled here, not twice)
        opp_dict = apply_geo_adjustments(opp_dict)
        if opp_dict.get("geography") == "venezuela":
            opp_dict = {**opp_dict, "venezuela_lens_applied": True}
            ve_lens_count += 1

        # Step 7: Portfolio lane
        lane = lane_assigner.assign_from_dict(opp_dict)
        opp_dict = {**opp_dict, "portfolio_lane": lane}

        scored_opps.append(opp_dict)
        summary["scored"] += 1

        # Step 8: Persist
        if not dry_run:
            opp_id = append_opportunity(opp_dict)

            # Step 8.5: Record score history
            try:
                final_score = float(opp_dict.get("final_score", 0))
                if final_score > 0:
                    append_opp_score_history(opp_id, final_score)
            except Exception as e:
                log_failure("score_history_append", e, opp_id=opp_id)

    if ve_lens_count > 0:
        logger.info("Step 5.5: Venezuela lens applied to %d opportunities", ve_lens_count)

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
            logger.info("Step 9.3: Score normalization applied. Range: %.2f - %.2f (raw preserved in raw_final_score)",
                        min(live_scores), max(live_scores))

    # ─── Step 9.5: TAM Estimation — estimate market size for all scored opps ───
    logger.info("Step 9.5: Running TAM estimation on %d scored opportunities...", len(all_opps_sorted))
    try:
        from opportunity_os.engines.tam_engine import estimate_tam_from_opp
        for i, opp in enumerate(all_opps_sorted):
            if not opp.get("tam") and not opp.get("tam_usd_estimate"):
                result = estimate_tam_from_opp(opp)
                all_opps_sorted[i] = {**opp, **{k: v for k, v in result.items() if not k.startswith("_")}}
        tam_populated = sum(1 for o in all_opps_sorted if o.get("tam") or o.get("tam_usd_estimate"))
        logger.info("  TAM populated for %d/%d opportunities", tam_populated, len(all_opps_sorted))
    except ImportError as e:
        logger.warning("TAM engine not available: %s", e)
    except Exception as e:
        log_failure("tam_estimation", e)

    # ─── Step 9.6: Wire TAM into market_size dimension and re-score ───
    tam_rescored = 0
    for i, opp in enumerate(all_opps_sorted):
        if opp.get("market_size") is not None:
            continue
        tam_val = opp.get("tam_usd_estimate") or opp.get("tam")
        if not tam_val:
            continue
        try:
            ms = _tam_to_market_size(float(tam_val))
            all_opps_sorted[i] = score_opportunity({**opp, "market_size": ms})
            tam_rescored += 1
        except (TypeError, ValueError):
            pass
    if tam_rescored:
        logger.info("Step 9.6: TAM-derived market_size wired into scoring for %d opportunities", tam_rescored)
        all_opps_sorted = sorted(all_opps_sorted, key=lambda x: x.get("final_score", 0), reverse=True)

    # Steps 9.7–11.8: benchmark, pain/distribution OS, research, pain library
    all_opps_sorted, top_20 = _step_enrich_and_rank(all_opps_sorted, dry_run)

    # Steps 12–14: save enriched, Notion sync, auto-validation
    validation_packages_for_sync = _step_validate_and_sync(
        all_opps_sorted, top_20, raw_signals, valid_opps_dicts, date, dry_run, summary
    )

    # Steps 14.5–18: deep dive, reports, CSVs, metrics
    _step_reports_deep_dive_metrics(
        all_opps_sorted, killed_opps, scored_opps, raw_signals,
        validation_packages_for_sync, date, dry_run, summary, root,
    )

    return summary


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _infer_kill_answers(opp_dict: dict) -> dict:
    """Infer kill gate answers from available opportunity fields.

    KG-03 and KG-05 use geo-aware defaults:
    - LATAM/VE opps get higher default distribution_accessibility (WhatsApp is ubiquitous)
    - Threshold lowered to >= 4 so early-stage signals get benefit of the doubt
    """
    answers: dict = {}
    geo = opp_dict.get("geography", "global")
    is_latam_ve = geo in ("venezuela", "latam", "colombia", "mexico", "argentina")

    # KG-01: require a substantive problem statement (not just a copied signal name)
    ps = (opp_dict.get("problem_statement") or "").strip()
    name = (opp_dict.get("name") or "").strip()
    answers["KG-01"] = len(ps) > 40 and ps != name

    answers["KG-02"] = bool(opp_dict.get("target_customer"))

    # KG-03: distribution accessibility — LATAM/VE defaults to 6 (WhatsApp cold outreach)
    # NOTE: use explicit None-check to avoid (3 or 5) = 3 Python gotcha
    da_raw = opp_dict.get("distribution_accessibility")
    da_default = 6 if is_latam_ve else 5
    da_score = da_raw if da_raw is not None else da_default
    answers["KG-03"] = int(da_score) >= 4

    pfr = opp_dict.get("path_to_first_revenue")
    answers["KG-04"] = bool(pfr) if isinstance(pfr, str) else ((pfr if pfr is not None else 5) >= 5)

    # KG-05: speed to MVP — lower threshold; early signals get benefit of the doubt
    speed_raw = opp_dict.get("speed_to_mvp")
    speed_default = 5 if is_latam_ve else 4
    speed_score = speed_raw if speed_raw is not None else speed_default
    answers["KG-05"] = int(speed_score) >= 4

    # KG-06: if no TAM yet, give benefit of the doubt (TAM estimation runs later at step 9.5)
    tam = opp_dict.get("tam_usd_estimate") or opp_dict.get("tam")
    answers["KG-06"] = True if not tam else float(tam) >= 10_000_000

    answers["KG-07"] = opp_dict.get("defensibility", 5) >= 5 or bool(
        opp_dict.get("venezuela_wedge_category")
    ) or bool(opp_dict.get("problem_statement"))
    return answers


def _tam_to_market_size(tam_usd: float) -> float:
    """Convert raw TAM USD estimate to market_size scoring dimension (1-10)."""
    if tam_usd >= 1_000_000_000:
        return 10.0
    if tam_usd >= 100_000_000:
        return 8.0
    if tam_usd >= 10_000_000:
        return 6.0
    if tam_usd >= 1_000_000:
        return 4.0
    return 2.0


def _enrich_fields(opp_dict: dict) -> dict:
    """
    Populate commonly-empty fields via rule-based inference after heuristic/AI scoring.

    Fields populated:
    - daniels_wedge_score: count of Daniel's 6 wedge dimensions found in text
    - why_now: infer from timing/AI/geo signals in description text
    - path_to_first_revenue: infer from vertical + geo + business model signals
    """
    import re as _re

    opp = dict(opp_dict)
    text = " ".join([
        opp.get("name", ""),
        opp.get("problem_statement", ""),
        opp.get("description", ""),
        opp.get("raw_notes", ""),
        opp.get("trigger_signal", ""),
    ]).lower()
    geo = opp.get("geography", "global")

    # Populate daniels_wedge_score (0-6 count)
    if opp.get("daniels_wedge_score") is None:
        wedges = 0
        if _re.search(r"growth|crm|lifecycle|a/b|paid ads|funnel|acquisition", text):
            wedges += 1
        if _re.search(r"narrative|positioning|story|brand|message", text):
            wedges += 1
        if _re.search(r"latam|venezuela|spain|colombia|spanish|hispano", text):
            wedges += 1
        if _re.search(r"fintech|crypto|usdt|payment|exchange|blockchain", text):
            wedges += 1
        if _re.search(r"mvp|prototype|claude|build fast|automation", text):
            wedges += 1
        if _re.search(r"whatsapp|referral|distribution|community|viral", text):
            wedges += 1
        opp["daniels_wedge_score"] = wedges

    # Populate why_now
    if not opp.get("why_now"):
        why_now_parts = []
        if _re.search(r"2025|2026|this year|recently|new|launch", text):
            why_now_parts.append("Recent market developments create urgency")
        if _re.search(r"regulation|mandator|new law|compliance", text):
            why_now_parts.append("Regulatory changes mandate new solutions")
        if _re.search(r"\bai\b|automation|llm|gpt|claude", text):
            why_now_parts.append("AI cost reduction makes this viable in 2026")
        if geo == "venezuela":
            why_now_parts.append("Venezuela's economic instability creates necessity-driven demand")
        if geo in ("latam", "venezuela") or _re.search(r"whatsapp|mobile", text):
            why_now_parts.append("WhatsApp-first commerce is accelerating across LATAM")
        if why_now_parts:
            opp["why_now"] = ". ".join(why_now_parts[:2])
        elif (opp.get("timing_tailwind") or 0) >= 7:
            opp["why_now"] = "Strong timing tailwind — market conditions favor entry now"
        else:
            opp["why_now"] = "Market opportunity identified; timing validation needed"

    # Populate path_to_first_revenue
    if not opp.get("path_to_first_revenue"):
        geo_pricing = {
            "venezuela": "$5-15/mo SaaS or 0.5-2% transaction fee",
            "latam": "$20-50/mo SaaS or performance-based fee",
            "colombia": "$20-50/mo SaaS",
            "mexico": "$20-50/mo SaaS",
            "spain": "$30-80/mo SaaS",
            "global": "$50-200/mo SaaS",
        }
        price_hint = geo_pricing.get(geo, geo_pricing["global"])
        if _re.search(r"saas|subscription|monthly", text):
            opp["path_to_first_revenue"] = (
                f"Subscription ({price_hint}) — direct WhatsApp/cold outreach to first 10 customers"
            )
        elif _re.search(r"transaction|payment|commission|take rate|fee", text):
            opp["path_to_first_revenue"] = (
                "Transaction fee — onboard 3-5 businesses, charge per transaction"
            )
        elif _re.search(r"service|consulting|done for you|agency", text):
            opp["path_to_first_revenue"] = (
                "Productized service — fixed-scope package, close first customer in 2 weeks via referral"
            )
        else:
            opp["path_to_first_revenue"] = (
                f"Direct sales via WhatsApp outreach — close first 3 customers in 30 days at {price_hint}"
            )

    return opp


def _render_and_write(content: str, path: str, dry_run: bool, summary: dict):
    """Write rendered content to path (or skip if dry_run)."""
    from opportunity_os.reports import write_report

    if dry_run:
        logger.info("[dry-run] Would write: %s", os.path.basename(path))
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


def _auto_harvest(date: str, raw_file: str, dry_run: bool) -> list[dict]:
    """
    Attempt to auto-harvest signals from free sources when no signals file exists.
    Writes harvested signals to raw_file (unless dry_run).
    Returns the list of harvested signal dicts (empty list on failure).
    """
    try:
        from opportunity_os.pipelines.signal_harvester import harvest_signals
        from opportunity_os.storage import read_all_opportunities

        existing_names = [o.get("name", "") for o in read_all_opportunities()]
        signals = harvest_signals(today=date, existing_names=existing_names)
        logger.info("Auto-harvest: %d signals found", len(signals))

        if signals and not dry_run:
            os.makedirs(os.path.dirname(raw_file), exist_ok=True)
            tmp_raw = raw_file + ".tmp"
            with open(tmp_raw, "w", encoding="utf-8") as f:
                for s in signals:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
            os.replace(tmp_raw, raw_file)
            logger.info("Auto-harvest wrote %d signals to %s", len(signals), os.path.basename(raw_file))

        return signals
    except Exception as exc:
        logger.warning("Auto-harvest failed: %s", exc)
        return []


# ─── Pipeline step helpers ────────────────────────────────────────────────────

from opportunity_os.pipelines.enrichment import run_enrichment_steps as _step_enrich_and_rank


def _step_validate_and_sync(
    all_opps_sorted: list,
    top_20: list,
    raw_signals: list,
    valid_opps_dicts: list,
    date: str,
    dry_run: bool,
    summary: dict,
) -> list:
    """Steps 12–14: save enriched records, build Notion sync payload, auto-validate scouts.

    Returns validation_packages_for_sync — list of (opp, package) tuples.
    """
    # Step 12: Save enriched records back to JSONL
    logger.info("Step 12: Saving enriched opportunity records...")
    if not dry_run:
        try:
            from opportunity_os.storage import read_all_opportunities
            all_stored_opps = read_all_opportunities()
            # BUG FIX: was {o["id"]: o for o in top_20} — only saved 20 records.
            # Must cover ALL of all_opps_sorted so opps 21-N keep their enrichment.
            enriched_ids = {o["id"]: o for o in all_opps_sorted if o.get("id")}
            updated_opps = [enriched_ids.get(o.get("id"), o) for o in all_stored_opps]
            opps_path = os.path.join(_get_project_root(), "data", "opportunities", "opportunities.jsonl")
            tmp_path = opps_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                for o in updated_opps:
                    f.write(json.dumps(o, default=str) + "\n")
            os.replace(tmp_path, opps_path)
            logger.info("  Saved %d enriched records", len(all_opps_sorted))
        except Exception as e:
            log_failure("save_enriched", e)

    # Step 14 (pre-collect): identify auto-validation candidates
    AUTO_VALIDATION_THRESHOLD = 7.0
    validation_packages_for_sync = []
    try:
        from opportunity_os.validation_engine import run_validation, AUTO_VALIDATION_THRESHOLD
        import yaml

        config_path = os.path.join(_get_project_root(), "config", "scoring_weights.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            threshold = cfg.get("thresholds", {}).get("auto_validation", AUTO_VALIDATION_THRESHOLD)
        except Exception as exc:
            logger.warning("Could not read auto_validation threshold from config: %s", exc)
            threshold = AUTO_VALIDATION_THRESHOLD

        validation_candidates = [
            o for o in all_opps_sorted
            if float(o.get("final_score", 0)) >= threshold
            and not o.get("kill_decision")
            and o.get("stage") == "scout"
        ]
        for i, opp in enumerate(validation_candidates):
            package = run_validation(opp, mode="auto")
            validation_candidates[i] = {**opp, **{k: v for k, v in package.items() if not k.startswith("_")}}
            validation_packages_for_sync.append((validation_candidates[i], package))
    except ImportError as e:
        logger.warning("Validation engine not available, skipping auto-promotion: %s", e)
    except Exception as e:
        log_failure("validation_pre_collect", e)

    # Step 13: Build Notion sync payload
    logger.info("Step 13: Building Notion sync payload...")
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
        sync_payload = build_sync_payload(
            all_opps_sorted[:20], run_stats, date,
            validation_packages=validation_packages_for_sync,
        )
        sync_path = os.path.join(_get_project_root(), "reports", "daily", f"{date}-notion-sync.json")
        with open(sync_path, "w", encoding="utf-8") as f:
            json.dump(sync_payload, f, indent=2, default=str)
        logger.info("  Notion sync payload ready: %d opps to upsert -> %s",
                    len(sync_payload["upsert_opps"]), sync_path)
        logger.info(">>> NOTION SYNC READY: run `uv run python scripts/notion_push.py` or ask Claude to sync %s", sync_path)
    except Exception as e:
        log_failure("notion_sync", e)

    # Step 14: Write validation markdown files for auto-promoted opps
    logger.info("Step 14: Auto-validating high-scoring scouts...")
    try:
        if validation_packages_for_sync:
            from opportunity_os.reports import ensure_report_dirs
            ensure_report_dirs()
            for opp, package in validation_packages_for_sync:
                if not dry_run:
                    safe_id = str(opp.get("id", "unknown"))[:40]
                    md_path = os.path.join(
                        _get_project_root(), "reports", "validation",
                        f"{date}-{safe_id}-validation.md",
                    )
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(package.get("_validation_markdown", ""))
                logger.info("  Validated: %s (score %.2f)", opp.get("name", "unknown"), opp.get("final_score", 0))
            logger.info("  %d opp(s) promoted to validation stage", len(validation_packages_for_sync))
        else:
            logger.info("  No scouts above threshold %s — no auto-validation triggered", AUTO_VALIDATION_THRESHOLD)
    except Exception as e:
        log_failure("validation_write", e)

    return validation_packages_for_sync


def _step_reports_deep_dive_metrics(
    all_opps_sorted: list,
    killed_opps: list,
    scored_opps: list,
    raw_signals: list,
    validation_packages_for_sync: list,
    date: str,
    dry_run: bool,
    summary: dict,
    root: str,
) -> None:
    """Steps 14.5–18: auto deep-dive, render reports, export CSVs, track metrics and quotas."""
    from opportunity_os.reports import render_template, report_path
    from opportunity_os.exporters import daily_feed_to_csv, opportunities_to_csv
    from opportunity_os.storage import read_all_opportunities

    # Step 14.5: Auto deep-dive on top scorer >= 8.0
    logger.info("Step 14.5: Checking for auto deep-dive candidates...")
    try:
        from opportunity_os.pipelines.deep_dive import run_deep_dive
        deep_dive_candidates = [
            o for o in all_opps_sorted
            if float(o.get("final_score", 0)) >= 8.0
            and not o.get("kill_decision")
        ][:1]
        for opp in deep_dive_candidates:
            opp_id = opp.get("id", "unknown")
            dd_path = os.path.join(
                root, "reports", "deep-dives", f"{date}-{opp_id[:40]}-deep-dive.md"
            )
            if os.path.exists(dd_path):
                logger.info("  Deep dive already exists for %s, skipping", opp_id)
                continue
            if not dry_run:
                result = run_deep_dive(opp_id=opp_id, dry_run=dry_run)
                if "error" not in result:
                    summary["deep_dives_produced"] += 1
                    logger.info("  Auto deep-dive triggered: %s (score %.1f)",
                                opp.get("name", "unknown")[:50], opp.get("final_score", 0))
                else:
                    logger.warning("  Deep dive failed for %s: %s", opp_id, result["error"])
            else:
                logger.info("  [dry-run] Would deep-dive: %s", opp.get("name", "unknown")[:50])
        if not deep_dive_candidates:
            logger.info("  No opportunities scored >= 8.0 -- no auto deep-dive")
    except Exception as e:
        logger.warning("Step 14.5 auto deep-dive error (non-blocking): %s", e)

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
    ve_opps = [o for o in all_opps_sorted if o.get("geography") == "venezuela"]
    wedge_counts: dict = {}
    for o in ve_opps:
        cat = o.get("venezuela_wedge_category", "unclassified")
        wedge_counts[cat] = wedge_counts.get(cat, 0) + 1

    all_stored = read_all_opportunities()
    standing = sorted(
        [
            o for o in all_stored
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

    # Step 16: Export CSVs
    if not dry_run:
        all_scored = read_all_opportunities()
        daily_feed_to_csv(all_scored)
        opportunities_to_csv(all_scored)

    logger.info("Daily run complete: %d scored, %d killed", summary["scored"], summary["killed"])
    logger.info("Reports: %s", ", ".join(os.path.basename(r) for r in summary["reports_written"]))

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
            "deep_dives_produced": summary["deep_dives_produced"],
            "validations_run": len(validation_packages_for_sync) if validation_packages_for_sync else 0,
            "quota_targets": {
                "signals": quotas.get("signals_ingested", {}).get("target", 40),
                "opps": quotas.get("structured_opportunities", {}).get("target", 10),
                "deep_dives": quotas.get("deep_dives_produced", {}).get("target", 3),
                "validations": quotas.get("validations_run", {}).get("target", 2),
            },
        }
        append_machine_metrics(metrics)
        logger.info("Step 15: Quota progress tracked (signals: %d, opps: %d)",
                    metrics["signals_ingested"], metrics["opportunities_scored"])
    except Exception as e:
        log_failure("quota_tracking", e)

    # Step 17: Track interview quota
    from opportunity_os.interview_tracker import get_interview_quota_status
    quota = get_interview_quota_status()
    if not quota["on_track"]:
        logger.warning("Interview quota behind: %d/%d done, %d days left",
                       quota["completed"], quota["total_required"], quota["days_remaining"])

    # Step 18: Outcome calibration check (weekly)
    from opportunity_os.outcome_tracking import get_calibration_report
    if os.path.exists(os.path.join(_get_project_root(), "data", "outcome_tracking.jsonl")):
        report = get_calibration_report()
        if report["total_tracked"] > 0:
            logger.info("Score accuracy: %.0f%% (%d tracked outcomes)",
                        report["score_accuracy"] * 100, report["total_tracked"])


def _get_project_root() -> str:
    from pathlib import Path

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])
