"""
validate_required_fields.py — PreToolUse hook
Checks that opportunity records written to JSONL have required fields.
Blocks the write and injects auto-filled defaults where possible.
Exits 0 to allow, exits 1 to block with helpful message.
"""
import sys
import json
import os
import hashlib
from datetime import date

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
        if not (file_path.endswith(".jsonl") and "opportunities" in file_path):
            sys.exit(0)

        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        if not content:
            sys.exit(0)

        today = date.today().isoformat().replace("-", "")
        errors = []
        warnings = []

        for lineno, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # not a JSON line, skip

            # Check name — hard requirement
            if not record.get("name"):
                errors.append(f"Line {lineno}: opportunity missing required field 'name'")
                continue

            # Check geography — hard requirement
            if not record.get("geography"):
                errors.append(
                    f"Line {lineno}: opportunity '{record.get('name')}' missing required field 'geography'"
                )
                continue

            # Check vertical — hard requirement
            if not record.get("vertical"):
                errors.append(
                    f"Line {lineno}: opportunity '{record.get('name')}' missing required field 'vertical'"
                )
                continue

            # Check bucket — hard requirement
            if not record.get("bucket"):
                errors.append(
                    f"Line {lineno}: opportunity '{record.get('name')}' missing required field 'bucket'"
                )
                continue

            # Auto-generate id if missing (warn only)
            if not record.get("id"):
                geo = record.get("geography", "XX")[:2].upper()
                h4 = hashlib.md5(record.get("name", "").encode()).hexdigest()[:4]
                auto_id = f"opp_{today}_{geo}_{h4}"
                warnings.append(
                    f"Line {lineno}: 'id' missing for '{record.get('name')}' — "
                    f"will be auto-generated as '{auto_id}'"
                )

        if errors:
            print("\u274c Blocked: opportunity record validation failed:")
            for err in errors:
                print(f"  - {err}")
            print("\nRequired fields: name, geography, vertical, bucket")
            sys.exit(1)

        if warnings:
            for warn in warnings:
                print(f"\u26a0\ufe0f  {warn}")

        sys.exit(0)

    except Exception as e:
        # Never crash — fail open
        print(f"[validate_required_fields] unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
