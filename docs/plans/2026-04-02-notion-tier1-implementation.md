# Notion Tier-1 Org Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a live-synced tier-1 Notion workspace for Daily Opportunity OS — 64 opps synced, 6 views, daily scout feed auto-populated, main page updated each morning.

**Architecture:** Python pipeline builds structured JSON sync payloads; Claude Code executes Notion MCP calls in-session after each daily run. Step 13 of daily_run.py writes `reports/daily/YYYY-MM-DD-notion-sync.json`; Claude Code reads it and fires MCP upserts.

**Tech Stack:** Notion MCP (`mcp__4da6be16__notion-*`), Python 3.13, daily_run.py Step 13 hook.

**Notion IDs (hardcoded — do not change):**
- Main page: `335adfa8-5ce2-810c-a3d7-d89674b77e9f`
- Opportunity DB page: `69aed397-3a99-4fd8-99cb-61d32435e4f5`
- Opportunity DB collection: `ad158a23-902c-4fed-9503-a8cffab29754`
- Daily Scout Feed page: `a27f4787-07d0-4a07-a6c4-e39dc3f0e75a`
- Daily Scout Feed collection: `243c2636-188c-4e7b-a9b2-520ca82b3834`

---

## Task 1: Add 5 fields to Opportunity Database schema

**Files:** No file changes — Notion MCP only.

Call `notion-update-data-source` on `collection://ad158a23-902c-4fed-9503-a8cffab29754`.

Add these properties:
- `Pain Severity` — type: number
- `Competition` — type: number
- `Executability` — type: number
- `Why Now` — type: text
- `First Seen` — type: date

**Verify:** Fetch `collection://ad158a23-902c-4fed-9503-a8cffab29754` and confirm 5 new columns appear.

---

## Task 2: Add 6 views to Opportunity Database

**Files:** No file changes — Notion MCP only.

Call `notion-create-view` on DB `https://www.notion.so/69aed3973a994fd899cb61d32435e4f5`.
Data source: `collection://ad158a23-902c-4fed-9503-a8cffab29754`
All views: type=table, sort Score descending.

1. Name: `Top 20 by Score` — filter Score >= 5.5
2. Name: `Venezuela` — filter Geography = venezuela
3. Name: `LATAM` — filter Geography = latam
4. Name: `Global` — filter Geography = global
5. Name: `Soon / Now Lane` — filter Lane = soon OR Lane = now
6. Name: `In Validation` — filter Stage = validation OR Stage = validated

**Verify:** Fetch the DB and confirm 7 views total (6 new + Default view).

---

## Task 3: Bulk sync 64 opportunities to Notion

**Files:** Read `data/opportunities/opportunities.jsonl`

Property mapping function (use this for each opp):
```python
def opp_to_props(o):
    props = {
        "Name": {"title": [{"text": {"content": (o.get("name") or "")[:100]}}]},
        "Score": {"number": round(float(o.get("final_score") or 0), 4)},
        "Stage": {"select": {"name": o.get("stage", "scout")}},
        "Geography": {"select": {"name": o.get("geography", "global")}},
        "Bucket": {"select": {"name": o.get("bucket", "venture_scale")}},
        "Lane": {"select": {"name": o.get("portfolio_lane", "strategic")}},
        "Opportunity ID": {"rich_text": [{"text": {"content": o.get("id", "")}}]},
        "Problem Statement": {"rich_text": [{"text": {"content": (o.get("problem_statement") or "")[:2000]}}]},
        "First Revenue Path": {"rich_text": [{"text": {"content": (o.get("first_revenue_path") or o.get("path_to_first_revenue") or "")[:2000]}}]},
        "Vertical": {"rich_text": [{"text": {"content": (o.get("vertical") or "")}}]},
        "Wedge Category": {"rich_text": [{"text": {"content": (o.get("venezuela_wedge_category") or "")}}]},
        "Kill Decision": {"checkbox": bool(o.get("kill_decision", False))},
        "Pain Severity": {"number": int(o.get("pain_severity") or 0)},
        "Competition": {"number": int(o.get("competition_intensity") or 0)},
        "Executability": {"number": round(float(o.get("executability_score") or 0), 2)},
        "Why Now": {"rich_text": [{"text": {"content": (o.get("why_now") or o.get("why_now_venezuela") or "")[:2000]}}]},
    }
    if o.get("tam"):
        props["TAM USD"] = {"number": float(o["tam"])}
    if o.get("validation_status"):
        props["Validation Status"] = {"select": {"name": o["validation_status"]}}
    if o.get("first_seen"):
        props["First Seen"] = {"date": {"start": str(o["first_seen"])[:10]}}
    return props
```

Process in batches of 10. Parent for each: `{"database_id": "69aed397-3a99-4fd8-99cb-61d32435e4f5"}`

**Verify:** Query Opportunity DB and confirm 64 rows.

---

## Task 4: Enhance Daily Scout Feed schema

**Files:** No file changes — Notion MCP only.

Call `notion-update-data-source` on `collection://243c2636-188c-4e7b-a9b2-520ca82b3834`.

Add these fields:
- `Date` — type: date
- `Signals` — type: number
- `New Opps` — type: number
- `Killed` — type: number
- `Top Score` — type: number
- `Score Range` — type: text
- `VE Signals` — type: number
- `LATAM Signals` — type: number
- `Global Signals` — type: number
- `Top Opportunity` — type: text
- `Notes` — type: text

**Verify:** Fetch `collection://243c2636-188c-4e7b-a9b2-520ca82b3834` and confirm 11 fields.

---

## Task 5: Create today's Daily Scout Feed row (2026-04-02)

**Files:** Read `data/opportunities/opportunities.jsonl` and `data/raw/2026-04-02-signals.jsonl`

Stats to compute:
- signals: count lines in signals JSONL (51)
- new_opps: count opps with first_seen starting "2026-04-02" (25)
- killed: 0
- top_score: 7.82
- score_range: "5.12 - 7.82"
- ve: 15, latam: 16, global: 20
- top_opp: "USDT Accounting Tool for Venezuelan Informal SMBs"
- notes: "Heuristic scoring (no ANTHROPIC_API_KEY). 0 now-lane candidates. 25 opps added."

Call `notion-create-pages`:
- Parent: `{"database_id": "a27f4787-07d0-4a07-a6c4-e39dc3f0e75a"}`
- Properties: map all stats to fields from Task 4

**Verify:** Query Daily Scout Feed and confirm 1 row with Date = 2026-04-02.

---

## Task 6: Rewrite notion_sync.py

**Files:**
- Modify: `src/opportunity_os/notion_sync.py`

New module replaces `get_sync_instructions()` with `build_sync_payload()` that returns structured JSON.
Key functions:
1. `opportunity_to_notion_properties(opp)` — same as Task 3 mapping above
2. `build_scout_row_properties(run_stats, date)` — maps run stats to scout feed fields
3. `build_sync_payload(opportunities, run_stats, date) -> dict` — returns `{date, generated_at, upsert_opps, scout_row, run_stats, main_page_id}`
4. `get_sync_instructions()` — kept as no-op stub for backward compat

The `build_sync_payload` output structure:
```json
{
  "date": "2026-04-02",
  "generated_at": "ISO timestamp",
  "upsert_opps": [
    {"parent": {"database_id": "..."}, "properties": {...}, "_opp_id": "...", "_opp_name": "..."}
  ],
  "scout_row": {
    "parent": {"database_id": "..."},
    "properties": {...}
  },
  "run_stats": {...},
  "main_page_id": "335adfa8-5ce2-810c-a3d7-d89674b77e9f"
}
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -c "
from opportunity_os.notion_sync import build_sync_payload
p = build_sync_payload([{'name':'Test','id':'t01','final_score':7.5,'geography':'venezuela','stage':'scout','bucket':'latam_asymmetry','portfolio_lane':'soon'}], {'signals_total':51,'new_opps':1,'killed':0,'top_score':7.5,'score_range':'5.1-7.5','by_geo':{'venezuela':15,'latam':16,'global':20},'top_opportunity':'Test','notes':''}, '2026-04-02')
print('OK — keys:', list(p.keys()))
print('Opp count:', len(p['upsert_opps']))
"
```
Expected: `OK — keys: ['date', 'generated_at', 'upsert_opps', 'scout_row', 'run_stats', 'main_page_id']`

**Commit:**
```bash
git add src/opportunity_os/notion_sync.py
git commit -m "feat(notion): rewrite notion_sync — structured MCP payload builder replaces markdown"
```

---

## Task 7: Wire Step 13 in daily_run.py to write sync JSON

**Files:**
- Modify: `src/opportunity_os/pipelines/daily_run.py` lines 194-204 only

Replace existing Step 13 block with:
```python
    # Step 13: Build Notion sync payload (JSON for Claude Code to execute)
    print("Step 13: Building Notion sync payload...")
    try:
        from opportunity_os.notion_sync import build_sync_payload
        from collections import Counter
        raw_geo = Counter(s.get("geography", "global") for s in raw_signals)
        today_scores = [float(o.get("final_score", 0)) for o in valid_opps_dicts if o.get("final_score")]
        run_stats = {
            "signals_total": len(raw_signals),
            "new_opps": scored_count,
            "killed": killed_count,
            "top_score": round(max(today_scores), 2) if today_scores else 0,
            "score_range": f"{min(today_scores):.2f} - {max(today_scores):.2f}" if today_scores else "N/A",
            "by_geo": {"venezuela": raw_geo.get("venezuela", 0), "latam": raw_geo.get("latam", 0), "global": raw_geo.get("global", 0)},
            "top_opportunity": all_opps_sorted[0].get("name", "") if all_opps_sorted else "",
            "notes": f"Heuristic scoring. {sum(1 for o in all_opps_sorted if o.get('portfolio_lane') == 'now')} now-lane candidates.",
        }
        sync_payload = build_sync_payload(all_opps_sorted[:20], run_stats, date)
        sync_path = os.path.join(_get_project_root(), "reports", "daily", f"{date}-notion-sync.json")
        with open(sync_path, "w", encoding="utf-8") as f:
            json.dump(sync_payload, f, indent=2, default=str)
        print(f"  Notion sync payload ready: {len(sync_payload['upsert_opps'])} opps to upsert -> {sync_path}")
    except Exception as e:
        print(f"WARNING  Notion sync payload error (non-blocking): {e}")
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -m opportunity_os.main daily 2>&1 | grep -i notion
ls reports/daily/*notion-sync.json
```
Expected: step output `Notion sync payload ready: N opps to upsert` and JSON file exists.

**Commit:**
```bash
git add src/opportunity_os/pipelines/daily_run.py
git commit -m "feat(pipeline): step13 writes structured notion sync JSON instead of markdown"
```

---

## Task 8: Patch main page — live Conviction Area + Weekly Quotas

**Files:** No file changes — Notion MCP only.

**Step 1:** Read current stats from JSONL:
- Top-3 validation opps: name, score, deadline
- Total opps: 64, validations: 3, signals: 51

**Step 2:** Call `notion-update-page` on `335adfa8-5ce2-810c-a3d7-d89674b77e9f`.

Update page content to replace:
- Conviction Area table with current top-3 (names, scores, Stage=Validation, Deadline=2026-04-08)
- Weekly Quotas section with actual numbers:
  - Signals ingested: 51 / 30-50 (over target this week)
  - Opportunities structured: 64 cumulative / 10 weekly target
  - Deep dives: 0 / 3
  - Validations: 3 / 1-2
  - Build candidates: 0 / 0-1

**Verify:** Fetch main page and confirm Conviction Area table shows 3 validation-stage opps with current scores.

---

## Final Acceptance Checklist

Run these verifications after all tasks:

1. `notion-fetch` Opportunity DB collection — confirm 5 new fields in schema
2. `notion-fetch` Opportunity DB page — confirm 7 views total
3. Query Opportunity DB — confirm 64 rows
4. `notion-fetch` Daily Scout Feed collection — confirm 11 fields
5. Query Daily Scout Feed — confirm row with Date=2026-04-02
6. `PYTHONPATH=src uv run python -c "from opportunity_os.notion_sync import build_sync_payload; print('OK')"` — no error
7. `PYTHONPATH=src uv run python -m opportunity_os.main daily` — outputs `Notion sync payload ready`
8. `ls reports/daily/*notion-sync.json` — file exists
9. `notion-fetch` main page — Conviction Area has current top-3 opps

---

## Execution Notes

- Notion MCP tool: `mcp__4da6be16-fb95-4726-be0d-9cd5e06ce7d1__notion-*`
- If `notion-create-pages` returns error about missing select option: expected — Notion auto-creates it
- Bulk sync Task 3: process in 10-record batches to avoid timeouts
- `why_now` is null on most records — Why Now field will be empty for those (correct)
- After Task 6-7, the pipeline is self-maintaining — daily runs auto-write the JSON
