"""
Notion Sync — structured JSON payload builder for in-session MCP execution.

Architecture: Python builds the payload; Claude Code reads it and fires MCP calls.
Each daily run writes: reports/daily/YYYY-MM-DD-notion-sync.json

Notion IDs (hardcoded — do not change):
  Main page:                335adfa8-5ce2-810c-a3d7-d89674b77e9f
  Opportunity DB page:      69aed397-3a99-4fd8-99cb-61d32435e4f5
  Opportunity DB collection: ad158a23-902c-4fed-9503-a8cffab29754
  Daily Scout Feed page:    a27f4787-07d0-4a07-a6c4-e39dc3f0e75a
  Daily Scout Feed collection: 243c2636-188c-4e7b-a9b2-520ca82b3834
"""

from datetime import datetime, timezone
from typing import Optional

# ─── Notion IDs (never read from env — these are workspace constants) ─────────

MAIN_PAGE_ID = "335adfa8-5ce2-810c-a3d7-d89674b77e9f"
OPPORTUNITY_DB_PAGE_ID = "69aed397-3a99-4fd8-99cb-61d32435e4f5"
OPPORTUNITY_DB_COLLECTION_ID = "ad158a23-902c-4fed-9503-a8cffab29754"
DAILY_FEED_PAGE_ID = "a27f4787-07d0-4a07-a6c4-e39dc3f0e75a"
DAILY_FEED_COLLECTION_ID = "243c2636-188c-4e7b-a9b2-520ca82b3834"
DEEP_DIVES_PAGE_ID = "0bcd4caa79aa43a9b39f2d2dc059d8ff"
DEEP_DIVES_COLLECTION_ID = "e8079401-811e-4e9b-a43a-234bc03cce7b"

# Legacy alias kept for backward compat
NOTION_COLLECTION_IDS = {
    "opportunity_database": OPPORTUNITY_DB_COLLECTION_ID,
    "daily_feed": DAILY_FEED_COLLECTION_ID,
    "deep_dives": "e8079401-811e-4e9b-a43a-234bc03cce7b",
}


# ─── Property mapping ─────────────────────────────────────────────────────────

def _safe_str(val, max_len: int = 2000) -> str:
    """Convert any value to a string slice safely."""
    if val is None:
        return ""
    return str(val)[:max_len]


def opportunity_to_notion_properties(opp: dict) -> dict:
    """
    Convert an opportunity dict to Notion page properties (Notion API format).

    Uses rich_text / number / select / checkbox / date / title types.
    Matches the Opportunity Database schema exactly.
    """
    props = {
        "Name": {"title": [{"text": {"content": _safe_str(opp.get("name") or "", 100)}}]},
        "Score": {"number": round(float(opp.get("final_score") or 0), 4)},
        "Stage": {"select": {"name": opp.get("stage") or "scout"}},
        "Geography": {"select": {"name": opp.get("geography") or "global"}},
        "Bucket": {"select": {"name": opp.get("bucket") or "venture_scale"}},
        "Lane": {"select": {"name": opp.get("portfolio_lane") or "strategic"}},
        "Opportunity ID": {"rich_text": [{"text": {"content": _safe_str(opp.get("id") or "")}}]},
        "Problem Statement": {"rich_text": [{"text": {"content": _safe_str(opp.get("problem_statement") or "")}}]},
        "First Revenue Path": {"rich_text": [{"text": {"content": _safe_str(
            opp.get("first_revenue_path") or opp.get("path_to_first_revenue") or ""
        )}}]},
        "Vertical": {"rich_text": [{"text": {"content": _safe_str(opp.get("vertical") or "")}}]},
        "Wedge Category": {"rich_text": [{"text": {"content": _safe_str(opp.get("venezuela_wedge_category") or "")}}]},
        "Kill Decision": {"checkbox": bool(opp.get("kill_decision", False))},
        # Fields added in Task 1
        "Pain Severity": {"number": int(opp.get("pain_severity") or 0)},
        "Competition": {"number": int(opp.get("competition_intensity") or 0)},
        "Executability": {"number": round(float(opp.get("executability_score") or 0), 2)},
        "Why Now": {"rich_text": [{"text": {"content": _safe_str(
            opp.get("why_now") or opp.get("why_now_venezuela") or ""
        )}}]},
    }

    # Optional fields — only include when data is present
    if opp.get("tam"):
        try:
            props["TAM USD"] = {"number": float(opp["tam"])}
        except (TypeError, ValueError):
            pass

    if opp.get("validation_status"):
        props["Validation Status"] = {"select": {"name": str(opp["validation_status"])}}

    if opp.get("first_seen"):
        date_str = str(opp["first_seen"])[:10]
        if len(date_str) == 10:
            props["First Seen"] = {"date": {"start": date_str}}

    return props


def build_scout_row_properties(run_stats: dict, date: str) -> dict:
    """
    Build Notion properties for one Daily Scout Feed row.

    run_stats keys expected:
      signals_total, new_opps, killed, top_score, score_range,
      by_geo (dict: venezuela/latam/global), top_opportunity, notes
    """
    by_geo = run_stats.get("by_geo", {})
    props = {
        "Name": {"title": [{"text": {"content": f"Scout — {date}"}}]},
        "Date": {"date": {"start": date}},
        "Signals": {"number": int(run_stats.get("signals_total") or 0)},
        "New Opps": {"number": int(run_stats.get("new_opps") or 0)},
        "Killed": {"number": int(run_stats.get("killed") or 0)},
        "Top Score": {"number": round(float(run_stats.get("top_score") or 0), 2)},
        "Score Range": {"rich_text": [{"text": {"content": str(run_stats.get("score_range") or "N/A")}}]},
        "VE Signals": {"number": int(by_geo.get("venezuela") or 0)},
        "LATAM Signals": {"number": int(by_geo.get("latam") or 0)},
        "Global Signals": {"number": int(by_geo.get("global") or 0)},
        "Top Opportunity": {"rich_text": [{"text": {"content": _safe_str(run_stats.get("top_opportunity") or "", 500)}}]},
        "Notes": {"rich_text": [{"text": {"content": _safe_str(run_stats.get("notes") or "", 1000)}}]},
    }
    return props


def build_validation_properties(opp: dict, package: dict) -> dict:
    """
    Build Notion page properties for one Deep Dives validation entry.

    opp: the opportunity dict
    package: the dict returned by validation_engine.run_validation()
    """
    return {
        "Name": {"title": [{"text": {"content": _safe_str(opp.get("name") or "", 100)}}]},
        "Opportunity ID": {"rich_text": [{"text": {"content": _safe_str(opp.get("id") or "")}}]},
        "Score At Validation": {"number": round(float(opp.get("final_score") or 0), 4)},
        "Validation Date": {"date": {"start": package.get("validation_start_date", "")}},
        "Auto Triggered": {"checkbox": package.get("_mode", "auto") == "auto"},
        "Decision": {"select": {"name": "Validate"}},
        "Geography": {"select": {"name": opp.get("geography") or "global"}},
        "Vertical": {"rich_text": [{"text": {"content": _safe_str(opp.get("vertical") or "")}}]},
        "Deadline": {"date": {"start": package.get("validation_deadline", "")}},
    }


def build_sync_payload(
    opportunities: list,
    run_stats: dict,
    date: str,
    validation_packages: list = None,
) -> dict:
    """
    Build the full Notion sync payload for a daily run.

    Returns a dict with:
      - date: ISO date string
      - generated_at: ISO timestamp
      - upsert_opps: list of {parent, properties, _opp_id, _opp_name}
      - scout_row: {parent, properties}
      - run_stats: passed-through stats for reference
      - main_page_id: ID of the main Notion page to patch

    Claude Code reads this JSON and executes:
      notion-create-pages for upsert_opps (batch)
      notion-create-pages for scout_row
      notion-update-page for main_page_id
    """
    upsert_opps = []
    for opp in opportunities:
        upsert_opps.append({
            "parent": {"database_id": OPPORTUNITY_DB_PAGE_ID},
            "properties": opportunity_to_notion_properties(opp),
            "_opp_id": str(opp.get("id") or ""),
            "_opp_name": str(opp.get("name") or ""),
        })

    scout_row = {
        "parent": {"database_id": DAILY_FEED_PAGE_ID},
        "properties": build_scout_row_properties(run_stats, date),
    }

    validated_opps = []
    if validation_packages:
        for opp, package in validation_packages:
            validated_opps.append({
                "parent": {"database_id": DEEP_DIVES_PAGE_ID},
                "properties": build_validation_properties(opp, package),
                "_opp_id": str(opp.get("id") or ""),
                "_opp_name": str(opp.get("name") or ""),
            })

    return {
        "date": date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "upsert_opps": upsert_opps,
        "scout_row": scout_row,
        "run_stats": run_stats,
        "main_page_id": MAIN_PAGE_ID,
        "validation_packages": validated_opps,
    }


# ─── Backward-compat stub ─────────────────────────────────────────────────────

def get_sync_instructions(opportunities: list) -> str:
    """
    Stub kept for backward compatibility. Replaced by build_sync_payload().
    Returns a short message pointing to the new function.
    """
    return (
        f"# Notion Sync\n"
        f"Use build_sync_payload() to generate the structured JSON payload.\n"
        f"Opportunities available: {len(opportunities)}\n"
    )
