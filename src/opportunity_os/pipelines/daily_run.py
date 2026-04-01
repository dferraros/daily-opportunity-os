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


def run_daily(date: str = None, geo: str = "global", dry_run: bool = False) -> dict:
    """
    Run the full daily opportunity pipeline.
    Returns summary dict: {processed, scored, killed, reports_written, errors}
    """
    from opportunity_os.storage import (
        read_all_opportunities,
        append_opportunity,
        dedupe_check,
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

    # Steps 3-8: Process each opportunity
    lane_assigner = PortfolioLaneAssigner()
    scored_opps = []
    killed_opps = []

    for opp in valid_opps:
        opp_dict = opp.model_dump()

        # Step 3: Dedupe
        dup_id = dedupe_check(opp_dict.get("name", ""), opp_dict.get("geography", ""))
        if dup_id:
            print(f"Duplicate skipped: {opp_dict.get('name')} (existing: {dup_id})")
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

    # Step 9: Render reports
    all_opps_sorted = sorted(
        scored_opps, key=lambda x: x.get("final_score", 0), reverse=True
    )

    # Global daily report
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
    tam = opp_dict.get("tam_usd_estimate")
    answers["KG-06"] = bool(tam and float(tam) >= 10_000_000)
    answers["KG-07"] = opp_dict.get("defensibility", 5) >= 5 or bool(
        opp_dict.get("venezuela_wedge_category")
    )
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
