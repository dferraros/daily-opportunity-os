"""
auto_rescore.py — FileChanged hook
Automatically scores opportunities with final_score=None when JSONL is modified.
Runs silently. Always exits 0.
"""
import sys
import os
import json
from pathlib import Path


def get_file_path() -> str:
    # Try env first, then stdin
    fp = os.environ.get("CLAUDE_FILE_PATH", "")
    if not fp:
        try:
            fp = sys.stdin.read().strip()
        except Exception:
            fp = ""
    return fp


def find_project_root(file_path: str) -> Path:
    if file_path:
        p = Path(file_path)
        for parent in p.parents:
            if (parent / "data").exists():
                return parent
    candidates = [
        Path("C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"),
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path(__file__).resolve().parent.parent


def main():
    file_path = get_file_path()

    # Only act on opportunities.jsonl
    if file_path and "opportunities.jsonl" not in file_path:
        sys.exit(0)

    root = find_project_root(file_path)
    jsonl = root / "data" / "opportunities" / "opportunities.jsonl"

    if not jsonl.exists():
        sys.exit(0)

    # Try to import scoring engine; skip silently if unavailable
    try:
        sys.path.insert(0, str(root / "src"))
        from opportunity_os.engines.scoring_engine import score_opportunity  # type: ignore
        from opportunity_os import storage  # type: ignore
        update_opportunity = storage.update_opportunity
    except ImportError:
        sys.exit(0)

    records = []
    with open(jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    unscored = [
        r for r in records
        if r.get("final_score") is None and not r.get("kill_decision", False)
    ]

    count = 0
    for opp in unscored:
        try:
            scored = score_opportunity(opp)
            update_opportunity(scored)
            count += 1
        except Exception:
            pass

    if count > 0:
        print(f"Auto-scored {count} new opportunities")

    sys.exit(0)


if __name__ == "__main__":
    main()
