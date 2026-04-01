"""
Exporters — converts JSONL opportunity data to Notion-ready CSV and markdown formats.

Three export targets:
1. Notion Opportunity Database CSV
2. Notion Daily Feed CSV
3. Daily report markdown summary

CSV format follows Notion import spec: one row per record, headers match property names.
Uses standard library csv module only (no pandas dependency).
"""

from __future__ import annotations

import csv
import os
from datetime import date
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_OPPORTUNITY_COLUMNS = [
    "id",
    "name",
    "geography",
    "vertical",
    "bucket",
    "portfolio_lane",
    "final_score",
    "attractiveness_score",
    "tam_usd_estimate",
    "kill_decision",
    "stage",
    "first_seen",
    "last_updated",
]

_DEFAULT_EXPORT_DIR = "exports/notion"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_tam_usd(tam: Optional[float]) -> str:
    """
    Returns human-readable USD: $10M, $1.2B, $450K.
    Returns 'Unknown' if None.
    """
    if tam is None:
        return "Unknown"
    if tam >= 1_000_000_000:
        return f"${tam / 1_000_000_000:.1f}B"
    if tam >= 1_000_000:
        return f"${tam / 1_000_000:.1f}M"
    if tam >= 1_000:
        return f"${tam / 1_000:.0f}K"
    return f"${tam:.0f}"


def _ensure_dir(path: str) -> None:
    """Create directory tree if it does not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Single-row conversion
# ---------------------------------------------------------------------------

def opportunity_to_notion_row(opp: dict) -> dict:
    """
    Converts a single opportunity dict to a Notion-compatible property dict.

    - Scores formatted as percentages (score × 10)
    - TAM formatted with M/B/K suffix
    - Missing fields become empty strings
    """
    final_score = opp.get("final_score")
    attr_score = opp.get("attractiveness_score")

    return {
        "id": opp.get("id", ""),
        "name": opp.get("name", ""),
        "geography": opp.get("geography", ""),
        "vertical": opp.get("vertical", ""),
        "bucket": opp.get("bucket", ""),
        "portfolio_lane": opp.get("portfolio_lane", ""),
        "final_score": f"{final_score * 10:.0f}%" if final_score is not None else "",
        "attractiveness_score": f"{attr_score * 10:.0f}%" if attr_score is not None else "",
        "tam_usd_estimate": format_tam_usd(opp.get("tam_usd_estimate")),
        "kill_decision": opp.get("kill_decision", ""),
        "stage": opp.get("stage", ""),
        "first_seen": opp.get("first_seen", ""),
        "last_updated": opp.get("last_updated", ""),
    }


# ---------------------------------------------------------------------------
# Opportunity database CSV
# ---------------------------------------------------------------------------

def opportunities_to_csv(
    opps: list[dict],
    output_path: Optional[str] = None,
) -> str:
    """
    Converts a list of opportunity dicts to CSV for Notion import.

    Writes to exports/notion/opportunity_database.csv by default.
    Returns the path written.
    """
    if output_path is None:
        output_path = os.path.join(_DEFAULT_EXPORT_DIR, "opportunity_database.csv")

    _ensure_dir(output_path)

    rows = [opportunity_to_notion_row(opp) for opp in opps]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_OPPORTUNITY_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


# ---------------------------------------------------------------------------
# Daily feed CSV
# ---------------------------------------------------------------------------

def daily_feed_to_csv(
    opps: list[dict],
    date: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Filters opportunities to those first_seen today (or the provided date).
    Top 20 by final_score. Writes to exports/notion/daily_feed.csv.

    Returns path written.
    """
    target_date = date or _today()

    if output_path is None:
        output_path = os.path.join(_DEFAULT_EXPORT_DIR, "daily_feed.csv")

    _ensure_dir(output_path)

    filtered = [
        opp for opp in opps
        if (opp.get("first_seen") or "").startswith(target_date)
    ]

    sorted_opps = sorted(
        filtered,
        key=lambda o: (o.get("final_score") or 0),
        reverse=True,
    )[:20]

    rows = [opportunity_to_notion_row(opp) for opp in sorted_opps]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_OPPORTUNITY_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


# ---------------------------------------------------------------------------
# Markdown table
# ---------------------------------------------------------------------------

def opportunities_to_markdown_table(
    opps: list[dict],
    max_rows: int = 10,
) -> str:
    """
    Returns a markdown table string sorted by final_score descending.

    Columns: Rank | Name | Geo | Score | Bucket | Lane
    """
    sorted_opps = sorted(
        opps,
        key=lambda o: (o.get("final_score") or 0),
        reverse=True,
    )[:max_rows]

    header = "| Rank | Name | Geo | Score | Bucket | Lane |"
    separator = "|------|------|-----|-------|--------|------|"
    rows = []

    for i, opp in enumerate(sorted_opps, start=1):
        name = opp.get("name", "—")
        geo = opp.get("geography", "—")
        score = opp.get("final_score")
        score_str = f"{score:.1f}" if score is not None else "—"
        bucket = opp.get("bucket", "—")
        lane = opp.get("portfolio_lane", "—")
        rows.append(f"| {i} | {name} | {geo} | {score_str} | {bucket} | {lane} |")

    return "\n".join([header, separator] + rows)


# ---------------------------------------------------------------------------
# Deep dives CSV (validation + deep_dive stage)
# ---------------------------------------------------------------------------

_DEEP_DIVE_COLUMNS = [
    "id",
    "name",
    "geography",
    "vertical",
    "bucket",
    "portfolio_lane",
    "final_score",
    "stage",
    "target_customer",
    "problem_statement",
    "why_now",
    "path_to_first_revenue",
    "path_to_1m_arr",
    "path_to_10m_arr",
    "tam",
    "defensibility",
    "speed_to_mvp",
    "capital_efficiency",
    "venezuela_wedge_category",
    "kill_criteria_passed",
    "recommendation",
    "validation_status",
    "first_seen",
    "last_updated",
]


def deep_dives_to_csv(
    opps: list[dict],
    output_path: Optional[str] = None,
) -> str:
    """
    Exports opportunities in stage=validation or stage=deep_dive to CSV.

    Writes to exports/notion/deep_dives.csv by default.
    Returns the path written.
    """
    if output_path is None:
        output_path = os.path.join(_DEFAULT_EXPORT_DIR, "deep_dives.csv")

    _ensure_dir(output_path)

    target_stages = {"validation", "deep_dive"}
    filtered = [
        opp for opp in opps
        if (opp.get("stage") or "").lower().strip() in target_stages
    ]

    sorted_opps = sorted(
        filtered,
        key=lambda o: (o.get("final_score") or 0),
        reverse=True,
    )

    def _row(opp: dict) -> dict:
        final_score = opp.get("final_score")
        tam_raw = opp.get("tam_usd_estimate") or opp.get("tam")
        tam_display = format_tam_usd(float(tam_raw)) if tam_raw is not None else ""
        kill_passed = opp.get("kill_criteria_passed")
        if kill_passed is None:
            kill_passed = not opp.get("kill_decision", False)

        return {
            "id": opp.get("id", ""),
            "name": opp.get("name", ""),
            "geography": opp.get("geography", ""),
            "vertical": opp.get("vertical", ""),
            "bucket": opp.get("bucket", ""),
            "portfolio_lane": opp.get("portfolio_lane", ""),
            "final_score": f"{final_score:.2f}" if final_score is not None else "",
            "stage": opp.get("stage", ""),
            "target_customer": opp.get("target_customer", ""),
            "problem_statement": opp.get("problem_statement", ""),
            "why_now": opp.get("why_now", ""),
            "path_to_first_revenue": opp.get("path_to_first_revenue", ""),
            "path_to_1m_arr": opp.get("path_to_1m_arr", ""),
            "path_to_10m_arr": opp.get("path_to_10m_arr", ""),
            "tam": tam_display,
            "defensibility": opp.get("defensibility", ""),
            "speed_to_mvp": opp.get("speed_to_mvp", ""),
            "capital_efficiency": opp.get("capital_efficiency", ""),
            "venezuela_wedge_category": opp.get("venezuela_wedge_category", ""),
            "kill_criteria_passed": str(kill_passed),
            "recommendation": opp.get("recommendation", ""),
            "validation_status": opp.get("validation_status", ""),
            "first_seen": opp.get("first_seen", ""),
            "last_updated": opp.get("last_updated", ""),
        }

    rows = [_row(opp) for opp in sorted_opps]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_DEEP_DIVE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path
