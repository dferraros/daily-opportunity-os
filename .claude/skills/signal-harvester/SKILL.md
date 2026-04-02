---
name: signal-harvester
description: Use to scout and harvest raw business opportunity signals from web sources. Invoke when starting a daily opportunity run or searching for new market signals.
tools: [WebSearch, WebFetch, Read, Write]
---

# Signal Harvester

## Purpose
Systematically scans multiple web verticals to collect raw business opportunity signals. Covers global markets, LATAM, and Venezuela with mandatory minimum coverage per geography. Outputs normalized JSONL records ready for downstream scoring and enrichment.

## When to Use
- Starting a daily opportunity run from scratch
- Need to refresh or expand the signal pool for a specific vertical
- Venezuela coverage has dropped below the 2-signal minimum
- Requested to search for new market gaps in a specific industry

## Workflow

### Step 1: Define Scan Scope
Read today's date. Check `config/source_registry.yaml` for active sources and any vertical overrides. Note any paused sources or geo blacklists.

### Step 2: Global Scan
Search 5+ verticals: fintech, logistics, SMB software, creator economy, B2B SaaS.
Query pattern per vertical:
```
[vertical] startup funding 2024 2025 OR "market gap" OR "no good solution"
```
Collect 2-5 raw signals per vertical. Record source URL, title, and a 1-2 sentence raw note for each.

### Step 3: LATAM Scan
Same 5 verticals, geo-filtered. Query pattern:
```
site:linkedin.com OR site:crunchbase.com [vertical] latam colombia mexico argentina
```
Also search: `[vertical] latam "series a" 2024 OR "underserved market"`. Target 3-5 LATAM signals total.

### Step 4: Venezuela Mandatory Scan
Run minimum 2 Venezuela-specific searches:
```
venezuela fintech 2024 OR venezuela logistics problem OR "mercado venezolano" oportunidad
venezuela startup 2024 OR "emprendimiento venezuela" OR venezuela "dolor de mercado"
```
This step is BLOCKING — do not proceed to Step 5 if zero results are found.

### Step 5: Normalize Signals
For each raw signal, create a minimal dict:
```json
{
  "name": "short opportunity name",
  "description": "1-2 sentence description of the gap or pain",
  "geography": "global|latam|venezuela|[country code]",
  "vertical": "fintech|logistics|smb_software|creator_economy|b2b_saas|other",
  "source_url": "https://...",
  "raw_notes": "free text notes from search",
  "harvested_at": "YYYY-MM-DD"
}
```

### Step 6: Write to Staging
Append all normalized signals to `data/raw/YYYY-MM-DD-signals.jsonl` (one JSON object per line). Create the file if it does not exist.

### Step 7: Return Count
Report summary:
- N global signals found across M verticals
- K LATAM signals found
- J Venezuela signals found (must be >= 2)
- Path written: `data/raw/YYYY-MM-DD-signals.jsonl`

## Output Spec
`data/raw/YYYY-MM-DD-signals.jsonl` with 10-30 raw signal records. Each record is a single-line JSON object with the 7 fields defined in Step 5.

## Quality Gate
- At least 2 Venezuela signals required — block and re-search if 0
- At least 1 signal per vertical scanned (5 verticals = 5 minimum signals)
- No duplicate URLs within the same run (deduplicate by source_url before writing)
- Total signals: 10 minimum, 30 maximum per run
