"""
dedupe_opportunities.py — PostToolUse hook
After writing to opportunities.jsonl, checks for duplicates.
Warn-only: always exits 0. Prints warning to stdout.
"""
import sys
import json
import os
from datetime import datetime, timedelta

# Windows fix: reconfigure stdout to UTF-8 to support emoji/unicode output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else "{}"
        tool_input = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    try:
        file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        if "opportunities.jsonl" not in file_path:
            sys.exit(0)

        # Add project root to sys.path
        hook_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = hook_dir
        for _ in range(5):
            if os.path.exists(os.path.join(project_root, "pyproject.toml")):
                break
            project_root = os.path.dirname(project_root)
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from opportunity_os import storage
            opps = storage.read_all_opportunities()
        except ImportError:
            # Storage module not available — skip silently
            sys.exit(0)
        except Exception:
            sys.exit(0)

        # Group by (name.lower(), geography.lower())
        from collections import defaultdict
        groups = defaultdict(list)
        for opp in opps:
            key = (
                (opp.get("name") or "").lower().strip(),
                (opp.get("geography") or "").lower().strip(),
            )
            groups[key].append(opp)

        window = timedelta(days=7)

        for (name, geo), entries in groups.items():
            if len(entries) < 2:
                continue

            # Parse dates and check if any pair is within 7 days
            dated = []
            for e in entries:
                raw_date = e.get("created_at") or e.get("date") or ""
                try:
                    dt = datetime.fromisoformat(raw_date[:10])
                except Exception:
                    dt = None
                dated.append((dt, e.get("id", "unknown")))

            # Check pairs within window
            flagged_ids = []
            for i in range(len(dated)):
                for j in range(i + 1, len(dated)):
                    dt_i, id_i = dated[i]
                    dt_j, id_j = dated[j]
                    if dt_i is None or dt_j is None:
                        # Can't compare dates — flag as potential duplicate
                        flagged_ids = [e.get("id", "unknown") for e in entries]
                        break
                    if abs(dt_i - dt_j) <= window:
                        if id_i not in flagged_ids:
                            flagged_ids.append(id_i)
                        if id_j not in flagged_ids:
                            flagged_ids.append(id_j)

            if flagged_ids:
                ids_str = ", ".join(flagged_ids)
                print(
                    f"\u26a0\ufe0f  Duplicate detected: \"{name}\" ({geo}) "
                    f"appears {len(flagged_ids)}x — IDs: {ids_str}"
                )

        sys.exit(0)

    except Exception as e:
        print(f"[dedupe_opportunities] unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
