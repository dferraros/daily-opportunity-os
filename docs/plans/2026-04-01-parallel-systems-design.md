# Parallel Intelligence Systems — Design Doc v1.0
## Date: 2026-04-01 | Author: Daniel Ferraro | Status: APPROVED

---

## Decision Summary

**Architecture chosen:** Approach A — Enrichment Pipeline
**Trigger:** After daily scoring, top 5 opportunities automatically enriched
**Repo:** Inside `daily-opportunity-os` (same repo, new skills + agents)
**Notion sync:** Live MCP push via `mcp__4da6be16` (replaces CSV export)

---

## What We're Building

Two parallel intelligence systems that run automatically every morning after the scoring pipeline completes. They do not generate new opportunities — they validate and enrich the top-scored ones with real market signal.

```
Daily Pipeline (existing):
  Raw signals → Kill Gate → Scoring → Ranking → Report

New enrichment step (appended to daily_run.py):
  Top 5 scored opportunities
    → Customer Pain OS     (validates: is the pain real and urgent?)
    → Distribution OS      (validates: can we actually reach the buyer?)
    → Enriched opportunity records saved back to JSONL
    → Notion sync via MCP
```

---

## System A: Customer Pain OS

### Job
Mine real complaints. Confirm the pain is specific, recurring, and monetizable.
Run on top 5 scored opportunities each morning.

### Sources (powered by new integrations)
| Source | Tool | Geo priority |
|--------|------|-------------|
| Reddit threads | `scrapingbee-automation` | VE communities, LATAM forums |
| App store reviews | `firecrawl-automation` | Google Play LATAM reviews |
| X/Twitter complaints | `serpapi-automation` + `twitter-algorithm-optimizer` | Spanish-language signals |
| Trustpilot / G2 / Capterra | `scrapingbee-automation` | Competitor reviews |
| YouTube comments | `firecrawl-automation` | LATAM creator/finance channels |
| Google search intent | `serpapi-automation` | "cómo cobrar", "cómo vender sin banco" |
| WhatsApp/Telegram (public) | `content-research-writer` | VE informal commerce groups |

### New Agent: `pain-intelligence-agent.md`
```yaml
name: pain-intelligence-agent
description: Mine customer complaints and recurring pain from digital sources. Extract exact language, workarounds, and monetization signals. Run on top 5 scored opportunities daily.
model: sonnet
tools: [WebSearch, WebFetch, Read, Write]
```

### New Skill: `.claude/skills/customer-pain-miner/SKILL.md`
**Workflow:**
1. Receive opportunity name + vertical + geography
2. Search 5 sources (Reddit, app reviews, X, Trustpilot, YouTube comments)
3. Extract: exact complaint phrases, workarounds used today, what they hate paying for
4. Cluster by: pain severity (1-10), frequency (daily/weekly/occasional), monetization potential
5. Map back to `data/pain_library.jsonl` — update or create pain cluster
6. Output: pain validation score (0-10) + top 3 exact customer phrases (copy-ready)

### Output fields added to Opportunity schema
```python
pain_validation_score: Optional[float]       # 0-10, from Pain OS
pain_evidence_sources: Optional[List[str]]   # URLs of raw evidence
exact_customer_phrases: Optional[List[str]]  # max 3, copy-ready
workarounds_found: Optional[List[str]]       # what they use today
pain_validated_date: Optional[str]           # ISO date
```

---

## System B: Distribution OS

### Job
Map how each buyer can realistically be reached. Benchmark CAC logic.
Identify channels competitors underuse. Produce first 10 customer path.

### Sources (powered by new integrations)
| Source | Tool | Purpose |
|--------|------|---------|
| Competitor ad libraries | `competitive-ads-extractor` | Channel gaps, messaging angles |
| Google Ads benchmarks | `googleads-automation` | CAC estimates by vertical |
| Search Console signals | `google-search-console-automation` | Organic demand signals |
| Lead profiles | `lead-research-assistant` | First 10 customer identification |
| Content research | `content-research-writer` | Distribution content angles |

### New Agent: `distribution-intelligence-agent.md`
```yaml
name: distribution-intelligence-agent
description: Map distribution reality for each opportunity. Answer: where does the buyer spend attention? What does CAC look like? What is the first 10 customer path?
model: sonnet
tools: [WebSearch, WebFetch, Read, Write]
```

### New Skill: `.claude/skills/distribution-mapper/SKILL.md`
**Workflow:**
1. Receive opportunity + geography + target buyer
2. Apply geography rules: VE = WhatsApp-first; LATAM = WhatsApp + TikTok; Spain = LinkedIn + SEO
3. Extract competitor distribution from `competitive-ads-extractor` — where are they spending?
4. Identify channel gaps (what competitors underuse)
5. Build first 10 customer path: specific channel + message + trust mechanism
6. Estimate CAC logic: channel CPL × funnel conversion = approx CAC
7. Output: distribution profile (top 3 channels, CAC logic, first 10 path, trust mechanism)

### Output fields added to Opportunity schema
```python
distribution_validated: Optional[bool]
top_distribution_channels: Optional[List[str]]   # max 3
estimated_cac_logic: Optional[str]               # e.g. "WhatsApp cold ~$2 CPL, 15% conv = ~$13 CAC"
first_10_customer_path: Optional[str]            # step-by-step
trust_mechanism_latam: Optional[str]             # how to earn trust
distribution_validated_date: Optional[str]
```

---

## New Skills Added (from Awesome Skills Plugin)

| Skill | Use in system | Priority |
|-------|--------------|---------|
| `scrapingbee-automation` | Pain OS — scrape reviews, Trustpilot, G2 | P1 |
| `firecrawl-automation` | Pain OS — crawl Reddit, YouTube comments, forums | P1 |
| `serpapi-automation` | Pain OS — Google search intent signals | P1 |
| `competitive-ads-extractor` | Distribution OS — competitor channel mapping | P1 |
| `lead-research-assistant` | Distribution OS — first 10 customer identification | P1 |
| `content-research-writer` | Pain Library + Distribution — cited research | P2 |
| `googleads-automation` | Distribution OS — paid CAC benchmarks | P2 |
| `google-search-console-automation` | Distribution OS — organic demand signals | P2 |
| `twitter-algorithm-optimizer` | Signal harvester — X pain mining optimization | P2 |
| `developer-growth-analysis` | Machine metrics — pattern analysis | P3 |
| `webapp-testing` | System QA — pipeline automated testing | P3 |
| `artifacts-builder` | Reporting — rich HTML report artifacts | P3 |
| `meeting-insights-analyzer` | Customer interviews — transcript analysis | P3 |
| `googlebigquery-automation` | Machine metrics — push to BigQuery | P3 |

---

## Integration into Existing Pipeline

### `pipelines/daily_run.py` — new steps 10-13

```python
# Existing steps 1-9: normalize → kill gate → score → report

# NEW: Enrichment layer (Approach A)
# Step 10: Get top 5 scored opportunities
top_5 = sorted(active_opps, key=lambda x: x.get('final_score', 0), reverse=True)[:5]

# Step 11: Run Pain OS on each (parallel agent calls)
for opp in top_5:
    pain_result = run_pain_intelligence(opp)
    opp.update(pain_result)

# Step 12: Run Distribution OS on each (parallel agent calls)
for opp in top_5:
    dist_result = run_distribution_mapper(opp)
    opp.update(dist_result)

# Step 13: Save enriched records + sync to Notion via MCP
save_enriched_opportunities(top_5)
sync_to_notion(top_5)   # replaces CSV export
```

### Notion Sync (replaces CSV export)
- Replace `hooks/export_notion_files.py` CSV logic with direct MCP calls
- Use `mcp__4da6be16-fb95-4726-be0d-9cd5e06ce7d1__notion-update-page` for existing records
- Use `mcp__4da6be16-fb95-4726-be0d-9cd5e06ce7d1__notion-create-pages` for new records
- Collection IDs (confirmed):
  - Opportunity Database: `ad158a23-902c-4fed-9503-a8cffab29754`
  - Daily Scout Feed: `243c2636-188c-4e7b-a9b2-520ca82b3834`
  - Deep Dives: `e8079401-811e-4e9b-a43a-234bc03cce7b`

---

## New Files to Create

```
.claude/
  agents/
    pain-intelligence-agent.md          ← NEW
    distribution-intelligence-agent.md  ← NEW
  skills/
    customer-pain-miner/
      SKILL.md                          ← NEW
    distribution-mapper/
      SKILL.md                          ← NEW

src/opportunity_os/
  pain_intelligence.py                  ← NEW (Pain OS logic)
  distribution_intelligence.py          ← NEW (Distribution OS logic)
  notion_sync.py                        ← NEW (MCP sync, replaces CSV)
  pipelines/
    daily_run.py                        ← MODIFY (add steps 10-13)

hooks/
  export_notion_files.py                ← MODIFY (add MCP sync)

data/
  pain_library.jsonl                    ← EXTEND (auto-updated by Pain OS)
```

---

## Build Order

| Phase | Files | Priority |
|-------|-------|---------|
| Phase A | `customer-pain-miner/SKILL.md` + `pain-intelligence-agent.md` + `pain_intelligence.py` | Week 1 |
| Phase B | `distribution-mapper/SKILL.md` + `distribution-intelligence-agent.md` + `distribution_intelligence.py` | Week 2 |
| Phase C | Wire both into `daily_run.py` steps 10-13 + `notion_sync.py` | Week 3 |
| Phase D | Add Awesome Skills P2/P3 integrations | Week 3-4 |

---

## Success Criteria

- Top 5 opportunities get pain + distribution scores appended automatically each morning
- `pain_validation_score` populated for all validation-stage opportunities before customer interviews
- `first_10_customer_path` populated before promoting any opportunity to build recommendation
- Notion databases updated live (no manual CSV import)
- Pain library grows by ≥3 new clusters per week from automated mining

---

*Design Doc v1.0 — 2026-04-01 — daily-opportunity-os parallel systems*
