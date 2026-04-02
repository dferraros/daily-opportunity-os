"""
track_machine_metrics.py — Stop hook
Appends daily run metrics to data/machine_metrics.jsonl.
Tracks: signals found, scored, killed, deep dives, validation runs.
Always exits 0.
"""
import sys
import json
from datetime import datetime, date
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


def count_deep_dives(root: Path, today_str: str) -> int:
    reports_dir = root / "reports" / "deep-dives"
    if not reports_dir.exists():
        return 0
    count = 0
    for f in reports_dir.iterdir():
        if today_str in f.name:
            count += 1
    return count


def main():
    root = find_project_root()
    today_str = date.today().isoformat()
    now_str = datetime.now().isoformat(timespec="seconds")

    records = read_jsonl(root / "data" / "opportunities" / "opportunities.jsonl")
    today_records = [r for r in records if r.get("first_seen", "").startswith(today_str)]

    opportunities_today = len(today_records)
    killed_today = sum(1 for r in today_records if r.get("kill_decision") is True)
    scored_today = sum(1 for r in today_records if r.get("final_score") is not None)
    deep_dives_today = count_deep_dives(root, today_str)

    lanes_today = dict(
        Counter(r.get("portfolio_lane") for r in today_records if r.get("portfolio_lane"))
    )

    geo_counts = Counter(
        r.get("geography", r.get("geo", ""))
        for r in today_records
        if r.get("geography") or r.get("geo")
    )
    top_geo_today = geo_counts.most_common(1)[0][0] if geo_counts else None

    bucket_counts = Counter(r.get("bucket", "") for r in today_records if r.get("bucket"))
    top_bucket_today = bucket_counts.most_common(1)[0][0] if bucket_counts else None

    metrics = {
        "date": today_str,
        "session_end": now_str,
        "opportunities_found": opportunities_today,
        "opportunities_killed": killed_today,
        "opportunities_scored": scored_today,
        "deep_dives_today": deep_dives_today,
        "lanes_today": lanes_today,
        "top_geo_today": top_geo_today,
        "top_bucket_today": top_bucket_today,
    }

    out_path = root / "data" / "machine_metrics.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics) + "\n")

    print(f"Session metrics saved: {opportunities_today} found, {scored_today} scored, {killed_today} killed")
    sys.exit(0)


if __name__ == "__main__":
    main()
