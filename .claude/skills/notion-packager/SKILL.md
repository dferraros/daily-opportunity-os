---
name: notion-packager
description: Use to export scored opportunities to Notion-ready CSV and markdown files. Invoke at end of daily run or on demand.
tools: [Read, Write, Bash]
---

# Notion Packager

## Purpose
Transforms scored opportunity records from the internal JSONL format into Notion-ready exports: a full opportunity database CSV, a daily feed CSV for the morning digest, and a ranked markdown table for quick scanning. Optionally syncs directly to Notion via MCP if credentials are available. Logs all exports to a manifest file for auditing.

## When to Use
- At the end of each daily opportunity run after scoring is complete
- When Notion database needs a manual refresh with latest scores
- When preparing the morning digest for review
- On demand when a stakeholder requests the latest opportunity rankings

## Workflow

### Step 1: Read Scored Opportunities
Load all records from `data/opportunities/opportunities.jsonl`. Validate that records have `final_score` set (not null).

### Step 2: Filter for Export
Apply export filter:
- `kill_decision: false` (exclude killed opportunities)
- `final_score` is not null
- Do not export opportunities with `export_excluded: true`

Count filtered records. If count is 0, warn and halt — do not create empty exports.

### Step 3: Generate Opportunity Database CSV
Run `exporters.py opportunities_to_csv()` or build manually with these columns:

| Column | Source field |
|--------|-------------|
| Name | name |
| Description | description |
| Geography | geography |
| Vertical | vertical |
| Final Score | final_score |
| Portfolio Lane | portfolio_lane |
| TAM (USD) | tam_usd_estimate |
| TAM Confidence | tam_confidence |
| Archetype | benchmark_archetype |
| Kill Decision | kill_decision |
| Scored At | scored_at |
| Source URL | source_url |
| Venezuela Wedge | venezuela_wedge_category |
| Rank | rank |

Write to `exports/notion/opportunity_database.csv`. Overwrite if file exists.

### Step 4: Generate Daily Feed CSV
Run `exporters.py daily_feed_to_csv()` for today's date. Include only opportunities with `harvested_at = today` OR `rescore_requested` was processed today. Columns: Name, Final Score, Portfolio Lane, Geography, TAM (USD), Archetype.

Write to `exports/notion/daily_feed.csv`.

### Step 5: Generate Markdown Table
Run `exporters.py opportunities_to_markdown_table()` for top 10 by `final_score`. Format:

```markdown
| Rank | Name | Score | Lane | Geography | TAM |
|------|------|-------|------|-----------|-----|
| 1 | ... | 8.4 | now | venezuela | $45M |
```

Write to `reports/daily/YYYY-MM-DD-summary.md`. Include a header with today's date and run metadata (total scored, total killed, total exported).

### Step 6: Notion Sync (if MCP available)
Check if Notion MCP tools are available in the current session. If yes:
- Use `notion-create-pages` or `notion-update-page` to sync the top 10 to the Notion Opportunity Database
- Match on opportunity `name` field to determine create vs. update
- Map CSV columns to Notion database properties

If Notion MCP is not available, skip this step and note in the export manifest.

### Step 7: Write Export Manifest
Append one record to `exports/notion/export_log.jsonl`:
```json
{
  "date": "YYYY-MM-DD",
  "count_exported": N,
  "count_killed_excluded": K,
  "notion_synced": true/false,
  "paths": [
    "exports/notion/opportunity_database.csv",
    "exports/notion/daily_feed.csv",
    "reports/daily/YYYY-MM-DD-summary.md"
  ],
  "exported_at": "YYYY-MM-DDTHH:MM:SS"
}
```

## Output Spec
- `exports/notion/opportunity_database.csv`: full opportunity database, all non-killed scored opportunities
- `exports/notion/daily_feed.csv`: today's harvested and/or rescored opportunities
- `reports/daily/YYYY-MM-DD-summary.md`: top-10 markdown table with run header
- `exports/notion/export_log.jsonl`: export manifest entry appended

## Quality Gate
- All CSV files must have a headers row as the first line
- At least 1 opportunity must be exported — halt with warning if count is 0
- All export files must be valid UTF-8 (no encoding errors)
- `export_log.jsonl` entry must be written even if Notion sync is skipped
- Markdown table must have exactly 10 rows (or all available if fewer than 10 opportunities exist)
