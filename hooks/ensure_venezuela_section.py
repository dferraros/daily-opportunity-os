"""
ensure_venezuela_section.py — Stop hook
Blocks session end if today's reports are missing a Venezuela section.
This ensures the mandatory Venezuela analysis is never skipped.
"""
import sys
import json
import os
import glob
import re
from datetime import date

# Windows fix: reconfigure stdout to UTF-8 to support emoji/unicode output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def find_project_root(start: str) -> str:
    """Walk up from start until pyproject.toml is found."""
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def main():
    try:
        today = date.today().isoformat()  # YYYY-MM-DD

        hook_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = find_project_root(hook_dir)

        reports_dir = os.path.join(project_root, "reports", "daily")

        if not os.path.isdir(reports_dir):
            sys.exit(0)

        # Find any report file matching today's date
        pattern = os.path.join(reports_dir, f"{today}*.md")
        today_reports = glob.glob(pattern)

        # No reports today — don't block short sessions
        if not today_reports:
            sys.exit(0)

        # Venezuela heading pattern: ## Venezuela or # Venezuela (case-insensitive)
        venezuela_pattern = re.compile(r"^#{1,2}\s+Venezuela", re.IGNORECASE | re.MULTILINE)

        for report_path in today_reports:
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if venezuela_pattern.search(content):
                    sys.exit(0)  # Found — allow
            except Exception:
                continue  # Can't read file — don't block

        # Reports exist but no Venezuela section found
        date_display = today
        print(
            f"\u274c Session blocked: today's report missing Venezuela section.\n"
            f"   Run the latam-venezuela-lens skill or add a ## Venezuela section "
            f"to reports/daily/{date_display}-*.md"
        )
        sys.exit(1)

    except Exception as e:
        print(f"[ensure_venezuela_section] unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
