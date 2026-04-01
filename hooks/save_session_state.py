"""
save_session_state.py — PreCompact hook
Saves session progress snapshot before context compaction.
Prevents research loss when long scouting sessions hit context limits.
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


def read_opportunities(root: Path) -> list:
    jsonl = root / "data" / "opportunities" / "opportunities.jsonl"
    if not jsonl.exists():
        return []
    records = []
    with open(jsonl, encoding="utf-8") as f:
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
    today_str = date.today().isoformat()
    now_str = datetime.now().isoformat(timespec="seconds")

    records = read_opportunities(root)
    total = len(records)

    scored_today = [
        r for r in records
        if r.get("first_seen", "").startswith(today_str)
        and r.get("final_score") is not None
    ]
    killed_today = [
        r for r in records
        if r.get("first_seen", "").startswith(today_str)
        and r.get("kill_decision") is True
    ]
    lanes = Counter(r.get("portfolio_lane") for r in records if r.get("portfolio_lane"))

    top_opp = None
    scored_all = [r for r in records if r.get("final_score") is not None]
    if scored_all:
        best = max(scored_all, key=lambda r: r.get("final_score", 0))
        top_opp = {
            "id": best.get("id", ""),
            "name": best.get("name", best.get("title", "")),
            "score": best.get("final_score"),
        }

    top_score = top_opp["score"] if top_opp else "N/A"

    state = {
        "saved_at": now_str,
        "total_opportunities": total,
        "scored_today": len(scored_today),
        "killed_today": len(killed_today),
        "top_opportunity": top_opp,
        "lane_counts": dict(lanes),
        "note": "Auto-saved before context compaction",
    }

    out_path = root / "data" / "session_state.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(f"Session state saved: {len(scored_today)} opportunities today, top score: {top_score}")
    sys.exit(0)


if __name__ == "__main__":
    main()
