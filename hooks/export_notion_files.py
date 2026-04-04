# SYNC STRATEGY:
# - In-session (Claude Code active): notion_sync.py uses MCP tools directly
# - Out-of-session (scheduled cron): this hook writes CSVs for manual Notion import
# - Future: implement Notion API direct calls for fully automated sync
# Both approaches are valid — CSVs are the reliable fallback.

"""
export_notion_files.py — SubagentStop hook
Rebuilds Notion-ready CSV exports after each subagent completes.
Runs silently on success. Always exits 0.
"""
import sys
import json
import os

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
        # Find project root and add src to path
        hook_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = find_project_root(hook_dir)
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from opportunity_os import storage, exporters
        except ImportError as e:
            print(f"[export_notion_files] import error: {e}", file=sys.stderr)
            sys.exit(0)

        # Read all opportunities
        try:
            all_opps = storage.read_all_opportunities()
        except Exception as e:
            print(f"[export_notion_files] storage read error: {e}", file=sys.stderr)
            sys.exit(0)

        # Filter: non-killed, scored
        eligible = [
            o for o in all_opps
            if not o.get("kill_decision", False)
            and o.get("final_score") is not None
        ]

        if not eligible:
            sys.exit(0)

        # Ensure export directory exists
        exports_dir = os.path.join(project_root, "exports", "notion")
        os.makedirs(exports_dir, exist_ok=True)

        # Run opportunity_database export
        try:
            csv_path = os.path.join(exports_dir, "opportunity_database.csv")
            exporters.opportunities_to_csv(eligible, output_path=csv_path)
        except Exception as e:
            print(f"[export_notion_files] opportunity_database export error: {e}", file=sys.stderr)

        # Run daily_feed export
        try:
            feed_path = os.path.join(exports_dir, "daily_feed.csv")
            exporters.daily_feed_to_csv(eligible, output_path=feed_path)
        except Exception as e:
            print(f"[export_notion_files] daily_feed export error: {e}", file=sys.stderr)

        print(
            f"\U0001f4e4 Notion exports updated: {len(eligible)} opportunities "
            f"\u2192 exports/notion/"
        )
        sys.exit(0)

    except Exception as e:
        print(f"[export_notion_files] unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
