#!/usr/bin/env python3
"""
Hook: check_interview_quota.py
Event: Stop
Purpose: Warn if customer interview quota is behind.
15 interviews required by 2026-04-08.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from opportunity_os.interview_tracker import get_interview_quota_status
    status = get_interview_quota_status()
    if not status["on_track"] and status["days_remaining"] <= 7:
        print(
            f"WARNING  INTERVIEW QUOTA: {status['completed']}/{status['total_required']} interviews done. "
            f"{status['days_remaining']} days to deadline {status['deadline']}. "
            f"Run interview-tracker skill."
        )
        # Don't block (exit 0) — warn only
except Exception:
    pass  # never block on hook failure

sys.exit(0)
