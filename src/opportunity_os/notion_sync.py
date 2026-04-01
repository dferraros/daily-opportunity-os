"""
Notion Sync — live MCP sync for opportunity data.
Replaces CSV export. Called after enrichment in daily_run.py.

Notion Collection IDs:
  Opportunity Database: ad158a23-902c-4fed-9503-a8cffab29754
  Daily Scout Feed: 243c2636-188c-4e7b-a9b2-520ca82b3834
  Deep Dives: e8079401-811e-4e9b-a43a-234bc03cce7b

NOTE: Full live sync requires Claude Code MCP context. For automated sync
outside Claude Code, use exporters.py CSV pipeline. This module handles
in-session sync only.
"""
import os
from typing import Optional

NOTION_COLLECTION_IDS = {
    "opportunity_database": os.getenv("NOTION_OPPORTUNITY_DB_ID", "ad158a23-902c-4fed-9503-a8cffab29754"),
    "daily_feed": os.getenv("NOTION_DAILY_FEED_ID", "243c2636-188c-4e7b-a9b2-520ca82b3834"),
    "deep_dives": os.getenv("NOTION_DEEP_DIVES_ID", "e8079401-811e-4e9b-a43a-234bc03cce7b"),
}


def opportunity_to_notion_properties(opp: dict) -> dict:
    """Convert opportunity dict to Notion page properties format."""
    props = {
        "Name": {"title": [{"text": {"content": opp.get("name", "Unnamed")}}]},
        "Score": {"number": opp.get("final_score", 0)},
        "Stage": {"select": {"name": opp.get("stage", "scout")}},
        "Geography": {"select": {"name": opp.get("geography", "global")}},
        "Bucket": {"select": {"name": opp.get("bucket", "latam_asymmetry")}},
        "Lane": {"select": {"name": opp.get("portfolio_lane", "soon")}},
    }
    # Add pain validation if present
    if opp.get("pain_validation_score"):
        props["Pain Score"] = {"number": opp["pain_validation_score"]}
    return props


def format_notion_sync_command(opp: dict, collection_id: str) -> dict:
    """
    Format the MCP call payload for notion-create-pages or notion-update-page.

    Usage: pass this to the Notion MCP tool in Claude Code.
    The actual MCP call must be made by Claude Code (not this Python module).
    This function prepares the payload.
    """
    return {
        "parent": {"database_id": collection_id},
        "properties": opportunity_to_notion_properties(opp),
    }


def get_sync_instructions(opportunities: list[dict]) -> str:
    """
    Generate human-readable sync instructions for Claude Code to execute.
    Since MCP calls must be made by Claude Code, this produces a structured
    instruction set that the agent reads and executes.
    """
    lines = ["# Notion Sync Instructions", f"Sync {len(opportunities)} opportunities to Notion.", ""]
    for opp in opportunities:
        lines.append(f"## {opp.get('name', 'Unknown')} ({opp.get('id', 'no-id')})")
        lines.append(f"Action: upsert to Opportunity Database ({NOTION_COLLECTION_IDS['opportunity_database']})")
        lines.append(f"Score: {opp.get('final_score', 0)} | Stage: {opp.get('stage', 'scout')} | Geo: {opp.get('geography', '?')}")
        lines.append("")
    return "\n".join(lines)
