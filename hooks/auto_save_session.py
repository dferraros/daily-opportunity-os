"""
SessionEnd / Stop hook: summarises opportunities before the session closes.

Actions:
1. Read data/opportunities/opportunities.jsonl
2. Count records by stage
3. Warn about any unscored non-archived records (final_score=None or 0)
4. Print session summary line
5. Append a session-end entry to data/machine_metrics.jsonl (if it exists)
Exits 0 always (never blocks).
"""
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import Counter


def find_project_root() -> Path:
    candidates = [
        Path("C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"),
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if (c / "data").exists():
            return c
    return Path(__file__).resolve().parent.parent


def read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def main():
    root = find_project_root()
    opps_path = root / "data" / "opportunities" / "opportunities.jsonl"
    metrics_path = root / "data" / "machine_metrics.jsonl"

    records = read_jsonl(opps_path)

    # Count by stage
    stage_counts = Counter(r.get("stage", "unknown") for r in records)

    active_count = stage_counts.get("scout", 0) + stage_counts.get("active", 0)
    validation_count = stage_counts.get("validation", 0)
    killed_count = stage_counts.get("killed", 0) + stage_counts.get("no", 0)
    archived_count = stage_counts.get("archived", 0)
    deep_dive_count = stage_counts.get("deep_dive", 0)

    # Find unscored, non-archived records
    needs_rescore = [
        r for r in records
        if (r.get("final_score") is None or r.get("final_score") == 0)
        and (r.get("stage") or "").lower() not in ("archived", "killed", "no")
    ]

    if needs_rescore:
        ids = [r.get("id", "unknown") for r in needs_rescore[:10]]
        print(
            f"WARNING: {len(needs_rescore)} unscored opportunities need rescore: "
            + ", ".join(ids)
        )

    print(
        f"Session ended. "
        f"Active: {active_count} | "
        f"Validation: {validation_count} | "
        f"Deep Dive: {deep_dive_count} | "
        f"Killed: {killed_count} | "
        f"Archived: {archived_count}"
    )

    # Append session-end metric if metrics file exists (don't create it from scratch here)
    if metrics_path.exists():
        session_record = {
            "event": "session_end",
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(records),
            "stage_counts": dict(stage_counts),
            "unscored_count": len(needs_rescore),
        }
        with open(metrics_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(session_record, default=str) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
