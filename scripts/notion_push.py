"""
Notion Push -- reads the daily sync payload and prints MCP call instructions.

Architecture: Python builds the payload (notion_sync.py); Claude Code fires MCP calls.
This script bridges the gap: reads the JSON, formats it for Claude Code execution.

Usage:
    PYTHONPATH=src uv run python scripts/notion_push.py
    PYTHONPATH=src uv run python scripts/notion_push.py --date 2026-04-02
    PYTHONPATH=src uv run python scripts/notion_push.py --execute  # prints MCP call payloads

The --execute flag prints JSON blocks that can be copy-pasted into a Claude Code session
for direct MCP tool invocation.
"""

import argparse
import json
import sys
from pathlib import Path


def _project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[4]


def find_latest_payload(date: str = None) -> Path | None:
    """Find the most recent notion-sync JSON payload."""
    root = _project_root()
    reports_dir = root / "reports" / "daily"
    if not reports_dir.exists():
        return None

    if date:
        target = reports_dir / f"{date}-notion-sync.json"
        return target if target.exists() else None

    # Find most recent
    payloads = sorted(reports_dir.glob("*-notion-sync.json"))
    return payloads[-1] if payloads else None


def main():
    parser = argparse.ArgumentParser(description="Notion sync push helper")
    parser.add_argument("--date", help="Date to push (YYYY-MM-DD). Defaults to most recent.")
    parser.add_argument("--execute", action="store_true", help="Print full MCP call payloads")
    parser.add_argument("--summary-only", action="store_true", help="Print only summary stats")
    args = parser.parse_args()

    payload_path = find_latest_payload(args.date)
    if not payload_path:
        print("ERROR: No notion-sync.json payload found.")
        print("Run 'opp-os daily' first to generate one.")
        sys.exit(1)

    with open(payload_path, encoding="utf-8") as f:
        payload = json.load(f)

    upsert_opps = payload.get("upsert_opps", [])
    run_stats = payload.get("run_stats", {})
    date = payload.get("date", "unknown")

    print(f"\n{'='*60}")
    print(f"Notion Sync Payload: {payload_path.name}")
    print(f"Date: {date}")
    print(f"Opportunities to upsert: {len(upsert_opps)}")
    print(f"{'='*60}\n")

    if args.summary_only:
        print(f"Run stats: {json.dumps(run_stats, indent=2)}")
        return

    # Show what will be synced
    print("Opportunities queued for Notion sync:")
    print(f"{'#':3} {'Score':6} {'Geo':12} {'Lane':10} {'Name'}")
    print("-" * 70)
    for i, opp in enumerate(upsert_opps[:20], 1):
        score = opp.get("Score", {}).get("number", 0)
        geo = opp.get("Geography", {}).get("select", {}).get("name", "--")
        lane = opp.get("Lane", {}).get("select", {}).get("name", "--")
        name_entry = opp.get("Name", {}).get("title", [{}])
        name = name_entry[0].get("text", {}).get("content", "--")[:40] if name_entry else "--"
        print(f"{i:3} {score:6.2f} {geo:12} {lane:10} {name}")

    print("\nCollection IDs:")
    print("  Opportunity DB: ad158a23-902c-4fed-9503-a8cffab29754")
    print("  Daily Feed:     243c2636-188c-4e7b-a9b2-520ca82b3834")

    if args.execute:
        print(f"\n{'='*60}")
        print("MCP CALL INSTRUCTIONS FOR CLAUDE CODE")
        print(f"{'='*60}")
        print("\nPaste this into a Claude Code session to fire Notion MCP calls:\n")

        print("```")
        print("# Step 1: Search for existing opportunity pages in Notion DB")
        print("# Use: notion-search tool with each opportunity ID to check for existing pages")
        print("# Step 2: For each opportunity:")
        print("#   - If page exists: notion-update-page with the properties")
        print("#   - If page doesn't exist: notion-create-pages in collection ad158a23-902c-4fed-9503-a8cffab29754")
        print("")
        print("# Payload to execute:")
        for i, opp in enumerate(upsert_opps[:5], 1):
            name_entry = opp.get("Name", {}).get("title", [{}])
            name_content = name_entry[0].get("text", {}).get("content", "--") if name_entry else "--"
            id_entry = opp.get("Opportunity ID", {}).get("rich_text", [{}])
            opp_id = id_entry[0].get("text", {}).get("content", "--") if id_entry else "--"
            score = opp.get("Score", {}).get("number", 0)
            print(f"# [{i}] {name_content[:50]} (ID: {opp_id[:20]}, Score: {score:.2f})")
        if len(upsert_opps) > 5:
            print(f"# ... and {len(upsert_opps) - 5} more")
        print("```")

        print(f"\nFull payload saved at: {payload_path}")
        print("Claude Code can read this file and fire notion-create-pages / notion-update-page MCP tools.")

    print(f"\nTo fire Notion sync in Claude Code session:")
    print(f"  1. Run: `uv run python scripts/notion_push.py --execute`")
    print(f"  2. Ask Claude: 'Read {payload_path} and sync all upsert_opps to Notion'")
    print(f"  3. Claude will use notion-search + notion-create-pages + notion-update-page MCP tools")


if __name__ == "__main__":
    main()
