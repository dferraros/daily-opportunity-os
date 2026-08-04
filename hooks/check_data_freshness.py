"""Stop hook: warn when pipeline data is stale — silence must never look like success.

Born from the 2026-08-04 audit: the scheduled daily ran a dead worktree for
months while every surface looked green. This hook makes staleness visible in
every Claude session. Warn-only (exit 0): staleness is a signal, not a blocker.
"""

import os
import sys
import time

STALE_AFTER_DAYS = 3.0
WATCHED = [
    ("data/opportunities/opportunities.jsonl", "opportunity store"),
    ("data/machine_metrics.jsonl", "daily-run metrics"),
]


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    now = time.time()
    warnings = []
    for rel, label in WATCHED:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            warnings.append(f"{label} MISSING ({rel})")
            continue
        age_days = (now - os.path.getmtime(path)) / 86400
        if age_days > STALE_AFTER_DAYS:
            warnings.append(f"{label} stale: {age_days:.1f} days since last write ({rel})")
    if warnings:
        print("[freshness] PIPELINE DATA STALE — the daily automation may be dead:")
        for w in warnings:
            print(f"[freshness]   - {w}")
        print("[freshness] Check: Get-ScheduledTask DailyOpportunityOS + tail data/automation_runs.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
