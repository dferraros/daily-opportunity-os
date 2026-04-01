"""
append_score_history.py — PostToolUse hook
Tracks score changes in opportunity records and appends to history log.
Always exits 0.
"""
import sys
import json
import os


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
        except ImportError:
            sys.exit(0)

        # Read previous state from storage
        try:
            previous = {o["id"]: o for o in storage.read_all_opportunities() if "id" in o}
        except Exception:
            sys.exit(0)

        # Parse newly written records from tool_input
        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        if not content:
            sys.exit(0)

        new_records = {}
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if "id" in record:
                    new_records[record["id"]] = record
            except json.JSONDecodeError:
                continue

        # Compare scores
        for opp_id, new_opp in new_records.items():
            new_score = new_opp.get("final_score")
            if new_score is None:
                continue

            old_opp = previous.get(opp_id)
            if old_opp is None:
                continue

            old_score = old_opp.get("final_score")
            if old_score is None:
                continue

            try:
                old_score = float(old_score)
                new_score = float(new_score)
            except (TypeError, ValueError):
                continue

            if abs(new_score - old_score) < 0.001:
                continue  # No meaningful change

            delta = new_score - old_score
            name = new_opp.get("name") or old_opp.get("name") or opp_id

            try:
                storage.append_score_history(
                    opp_id, old_score, new_score, "auto-tracked by hook"
                )
            except Exception:
                pass  # Don't crash if storage fails

            sign = "+" if delta >= 0 else ""
            print(
                f"\U0001f4ca Score updated: {name} \u2192 "
                f"{old_score:.1f} \u2192 {new_score:.1f} ({sign}{delta:.1f})"
            )

        sys.exit(0)

    except Exception as e:
        print(f"[append_score_history] unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
