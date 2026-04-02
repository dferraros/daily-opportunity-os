"""Weekly run pipeline -- computes score deltas and renders weekly report."""

from datetime import datetime, timedelta
import os


def run_weekly(dry_run: bool = False) -> dict:
    """
    Run the weekly review pipeline.
    Returns summary dict: {week, promote_count, kill_count}
    """
    from opportunity_os.storage import read_all_opportunities
    from opportunity_os.reports import (
        render_template,
        report_path,
        write_report,
        ensure_report_dirs,
    )

    ensure_report_dirs()
    week = datetime.now().strftime("%Y-W%W")
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    all_opps = read_all_opportunities()

    # This week's opportunities
    week_opps = [
        o for o in all_opps if o.get("first_seen", "") >= str(week_start)
    ]

    scored = [
        o for o in week_opps if o.get("final_score") and not o.get("kill_decision")
    ]
    killed = [o for o in week_opps if o.get("kill_decision")]

    promote = sorted(
        scored, key=lambda x: x.get("final_score", 0), reverse=True
    )[:3]
    to_kill = sorted(
        [o for o in scored if o.get("final_score", 10) < 4.0],
        key=lambda x: x.get("final_score", 0),
    )[:3]

    # Quota check
    quota_status = {
        "signals": len(all_opps),
        "signals_ok": len(all_opps) >= 30,
        "structured": len(scored),
        "structured_ok": len(scored) >= 10,
        "deep_dives": _count_deep_dives_this_week(week_start),
        "deep_dives_ok": _count_deep_dives_this_week(week_start) >= 3,
        "validations": 0,
        "validations_ok": False,
    }

    context = {
        "week": week,
        "date_range": f"{week_start} – {today}",
        "promote": promote,
        "kill": to_kill,
        "rising": [],  # TODO: compute from score history
        "conviction_area": "Venezuela payments infrastructure",
        "quota_status": quota_status,
        "score_deltas": [],
    }

    content = render_template("weekly_report.md.j2", context)
    path = report_path("weekly")

    if not dry_run:
        write_report(content, path)
    print(f"Weekly report: {os.path.basename(path)}")
    return {
        "week": week,
        "promote_count": len(promote),
        "kill_count": len(to_kill),
    }


def _count_deep_dives_this_week(week_start) -> int:
    from opportunity_os.reports import get_project_root

    deep_dive_dir = os.path.join(get_project_root(), "reports", "deep-dives")
    if not os.path.exists(deep_dive_dir):
        return 0
    count = 0
    for f in os.listdir(deep_dive_dir):
        if f >= str(week_start):
            count += 1
    return count
