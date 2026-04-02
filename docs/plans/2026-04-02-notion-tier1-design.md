# Notion Tier-1 Org Design — Daily Opportunity OS
**Date:** 2026-04-02
**Status:** Approved
**Author:** Daniel Ferraro

---

## Problem

64 scored opportunities live in `data/opportunities/opportunities.jsonl` but **zero are in Notion**.
The Daily Scout Feed is empty. The main dashboard has manually-curated sections that go stale.
Result: the intelligence machine produces data that nobody sees.

## Goal

A Notion workspace that:
1. Reflects the current opportunity DB at all times (auto-synced each morning)
2. Requires zero manual updates after setup
3. Provides 6 filtered views for fast daily scanning
4. Logs every daily run in the Daily Scout Feed automatically

---

## Existing Structure (do not rebuild)

| Asset | Notion ID | Collection ID |
|---|---|---|
| Main page | 335adfa8-5ce2-810c-a3d7-d89674b77e9f | — |
| Opportunity Database | 69aed397-3a99-4fd8-99cb-61d32435e4f5 | ad158a23-902c-4fed-9503-a8cffab29754 |
| Daily Scout Feed | a27f4787-07d0-4a07-a6c4-e39dc3f0e75a | 243c2636-188c-4e7b-a9b2-520ca82b3834 |
| Deep Dives | 0bcd4caa-79aa-43a9-b39f-2d2dc059d8ff | e8079401-811e-4e9b-a43a-234bc03cce7b |

---

## Plan B — Full Live Sync

### Phase 1: Schema Enhancement

Add 5 fields to Opportunity Database (verified 64/64 coverage):

| Field | Type | Source field | Notes |
|---|---|---|---|
| Pain Severity | number | `pain_severity` | 1–10 |
| Competition | number | `competition_intensity` | 1–10, lower = better |
| Executability | number | `executability_score` | 0–10 composite |
| Why Now | text | `why_now` | Timing rationale |
| First Seen | date | `first_seen` | ISO date |

### Phase 2: 6 New Views on Opportunity Database

| View name | Filter | Sort |
|---|---|---|
| 🏆 Top 20 by Score | score >= 5.5 | score desc |
| 🇻🇪 Venezuela | geography = venezuela | score desc |
| 🌎 LATAM | geography = latam | score desc |
| 🌐 Global | geography = global | score desc |
| ⏱️ Soon / Now | lane = soon OR now | score desc |
| 🧪 In Validation | stage = validation | score desc |

### Phase 3: Bulk Sync (64 opportunities)

- Create all 64 records in Opportunity Database via MCP `notion-create-pages`
- Deduplication key: `Opportunity ID` text field
- If record exists: skip (first sync is additive)
- Properties to sync: Name, Score, Stage, Geography, Bucket, Lane, Problem Statement,
  First Revenue Path, TAM USD, Vertical, Wedge Category, Validation Status,
  Opportunity ID, Kill Decision, Last Updated, + 5 new fields

### Phase 4: Daily Scout Feed Schema

Add fields to Daily Scout Feed database:

| Field | Type | Populated from |
|---|---|---|
| Title | title | `Scout — YYYY-MM-DD` |
| Date | date | run date |
| Signals Harvested | number | raw signal count |
| New Opps | number | newly scored count |
| Killed | number | kill count |
| Top Score | number | max final_score |
| Score Range | text | `min – max` |
| VE Signals | number | venezuela geo count |
| LATAM Signals | number | latam geo count |
| Global Signals | number | global geo count |
| Top Opportunity | text | name of #1 scored |
| Notes | text | warnings, flags |

### Phase 5: notion_sync.py Rewrite

Replace `get_sync_instructions()` (text output) with `run_live_sync()` (live MCP calls).

```python
def run_live_sync(opportunities: list[dict], run_stats: dict, date: str) -> dict:
    """
    Three-action live sync called from daily_run.py Step 13.
    Returns: {"opps_synced": int, "scout_row_created": bool, "main_page_updated": bool}
    """
    # Action 1: Upsert new opportunities to Opportunity DB
    # Action 2: Append daily scout row to Daily Scout Feed
    # Action 3: Patch main page Conviction Area + Weekly Quotas
```

**Upsert logic:**
1. Query Opportunity DB for existing `Opportunity ID` values
2. For each new opp: if ID missing → `notion-create-pages`; if present → `notion-update-page`
3. Max 16 new records per run (typical daily batch)

**Scout row creation:**
- Always `notion-create-pages` on Daily Scout Feed (one row per run, no dedup needed)

**Main page patch (Action 3):**
- Read current top-3 validation opps from JSONL
- Update the Conviction Area table with current scores and deadlines
- Update Weekly Quotas numbers (signals count, opps count, validations count)
- Uses `notion-update-page` with block content replacement

### Phase 6: Pipeline Wiring

In `daily_run.py` Step 13, replace current `get_sync_instructions()` call with:

```python
from opportunity_os.notion_sync import run_live_sync
sync_result = run_live_sync(top_5, run_stats, date)
```

`run_stats` dict assembled at end of pipeline:
```python
run_stats = {
    "signals_total": len(raw_signals),
    "new_opps": scored_count,
    "killed": killed_count,
    "top_score": max_score,
    "score_range": f"{min_score:.2f} – {max_score:.2f}",
    "by_geo": {"venezuela": ve_count, "latam": la_count, "global": gl_count},
    "top_opportunity": top_opp_name,
}
```

---

## Acceptance Criteria

- [ ] Opportunity Database has 5 new properties in schema
- [ ] 6 views exist on Opportunity Database
- [ ] All 64 opportunities synced to Notion (verify count in Notion = 64)
- [ ] Daily Scout Feed has today's entry (2026-04-02)
- [ ] Daily Scout Feed has correct schema (10 fields)
- [ ] `run_live_sync()` runs without error from daily_run.py
- [ ] Running `opp-os daily` creates a new scout row and upserts any new opps
- [ ] Main page Conviction Area reflects current top-3 validation opps
- [ ] Main page Weekly Quotas numbers match JSONL actuals

---

## Implementation Waves

| Wave | Tasks | Parallel? |
|---|---|---|
| Wave 1 | Add 5 DB fields + 6 views | Sequential (schema first, then views) |
| Wave 2 | Bulk sync 64 opps | After Wave 1 |
| Wave 3 | Daily Scout Feed schema + today's row | Parallel with Wave 2 |
| Wave 4 | Rewrite notion_sync.py | After Wave 2+3 complete |
| Wave 5 | Wire pipeline + update main page | After Wave 4 |

Estimated: 2–3 hours of agent execution.
