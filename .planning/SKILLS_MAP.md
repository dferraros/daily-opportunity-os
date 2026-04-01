# Skills Map — Daily Opportunity OS
## All 233+ skills mapped to system components
## Date: 2026-04-01

This file maps every available skill to the pipeline layer it powers.
Reference this during any build phase — don't guess, use the skill.

---

## LEGEND
- **P1** = Used in current build (Phases A-C)
- **P2** = Used in Phase D expansion
- **P3** = Available for future use
- **Source**: `skills/` = C:\Users\ferra\.claude\skills\ | `awesome/` = awesome-skills plugin

---

## Layer 1: Signal Harvesting (raw opportunity detection)

| Skill | Source | Job |
|-------|--------|-----|
| `scrapingbee-automation` | awesome/ | Scrape app reviews, Trustpilot, G2/Capterra, Google reviews | P1 |
| `firecrawl-automation` | awesome/ | Crawl Reddit threads, YouTube comments, niche forums | P1 |
| `serpapi-automation` | awesome/ | Google search intent signals ("cómo cobrar", "sin banco") | P1 |
| `twitter-algorithm-optimizer` | awesome/ | Optimize X/Twitter pain signal mining queries | P2 |
| `content-research-writer` | awesome/ | Research + citations for pain library sourcing | P1 |
| `lead-research-assistant` | awesome/ | Identify first 10 customers per opportunity profile | P1 |
| `deep-research` | skills/ | Multi-source synthesis with citations | P1 |
| `research-lookup` | skills/ | Perplexity + academic source lookup | P2 |
| `gpt-researcher` | skills/ | Autonomous deep research agent for TAM/pain | P2 |
| `fact-checker` | skills/ | Verify pain claims and market size assumptions | P2 |
| `bit2me-data-analyst` | skills/ | Bit2Me internal data queries via BigQuery | P3 |
| `data-analyst` | skills/ | EDA on opportunity JSONL data | P2 |

---

## Layer 2: Pain Intelligence (Customer Pain OS)

| Skill | Source | Job |
|-------|--------|-----|
| `customer-pain-miner` | **NEW** | Core Pain OS skill — mine complaints, cluster pain | P1 |
| `customer-research` | skills/ | JTBD interviews, survey design, Mode 2 digital watering holes | P1 |
| `meeting-insights-analyzer` | awesome/ | Analyze customer interview transcripts for pain patterns | P1 |
| `marketing-psychology` | skills/ | Jobs-to-be-done, pain trigger identification, buying psychology | P1 |
| `cohort-analysis` | skills/ | Cohort-level pain pattern analysis | P2 |
| `churn-prevention` | skills/ | Identify pain points causing product abandonment | P2 |

---

## Layer 3: Distribution Intelligence (Distribution OS)

| Skill | Source | Job |
|-------|--------|-----|
| `distribution-mapper` | **NEW** | Core Distribution OS skill — channel map, CAC logic, first 10 path | P1 |
| `competitive-ads-extractor` | awesome/ | Extract competitor ad copy and channel strategy | P1 |
| `googleads-automation` | awesome/ | Google Ads CAC benchmarks by vertical | P2 |
| `google-search-console-automation` | awesome/ | Organic demand signal mining | P2 |
| `revops` | skills/ | Pipeline stages, lead lifecycle, channel attribution | P1 |
| `launch-strategy` | skills/ | ORB framework — owned/rented/borrowed channel mapping | P1 |
| `paid-ads` | skills/ | Google + Meta targeting, bidding, CAC estimates | P2 |
| `cold-email` | skills/ | Outbound sequences, deliverability for first 10 customers | P2 |
| `referral-program` | skills/ | WhatsApp referral mechanics for LATAM | P2 |
| `social-content` | skills/ | Platform-specific content for distribution | P2 |
| `content-strategy` | skills/ | Editorial calendar for distribution content | P3 |
| `ad-creative` | skills/ | Ad copy, hooks, platform formats | P2 |

---

## Layer 4: Market Sizing & Validation

| Skill | Source | Job |
|-------|--------|-----|
| `market-sizing-analysis` | skills/ | TAM/SAM/SOM bottom-up analysis | P1 |
| `competitive-landscape` | skills/ | Porter's Five Forces, positioning maps | P1 |
| `competitor-alternatives` | skills/ | Positioning vs. competitors, comparison pages | P2 |
| `startup-metrics-framework` | skills/ | CAC, LTV, burn, unit economics | P1 |
| `startup-financial-modeling` | skills/ | Financial projections, runway, cash flow | P2 |
| `ab-test-setup` | skills/ | Validation test design, hypothesis → sample size | P1 |
| `strategy-advisor` | skills/ | Strategic options evaluation, recommendation | P1 |
| `north-star-framework` | skills/ | North star metric identification per opportunity | P2 |
| `growth-loops` | skills/ | Identify compounding growth loops per opportunity | P2 |

---

## Layer 5: Scoring & Ranking

| Skill | Source | Job |
|-------|--------|-----|
| `statistical-analysis` | skills/ | Hypothesis tests, regression, power analysis on scores | P2 |
| `senior-data-scientist` | skills/ | Modeling, causal inference on opportunity data | P3 |
| `data-storytelling` | skills/ | Narrative around top opportunities for weekly review | P2 |
| `visualization-expert` | skills/ | Chart type selection for opportunity dashboard | P2 |
| `kpi-dashboard-design` | skills/ | KPI hierarchy, dashboard layout for machine metrics | P1 |
| `d3-viz` | skills/ | Custom interactive opportunity ranking visualization | P3 |

---

## Layer 6: Reporting & Export

| Skill | Source | Job |
|-------|--------|-----|
| `artifacts-builder` | awesome/ | Rich HTML report artifacts for daily output | P2 |
| `data-storytelling` | skills/ | Narrative synthesis for weekly conviction memo | P2 |
| `marp-slide` | skills/ | Slide decks for opportunity deep dives | P3 |
| `frontend-slides` | skills/ | Animation-rich HTML presentations | P3 |
| `docx` | skills/ | Export reports to Word/DOCX format | P3 |
| `pdf` | skills/ | Export reports to PDF | P3 |
| `pptx` | skills/ | Export to PowerPoint | P3 |
| `internal-comms` | awesome/ | Weekly conviction memo in Slack/email format | P2 |
| `technical-writer` | skills/ | API docs, skill documentation | P3 |

---

## Layer 7: Notion Sync & Data Pipeline

| Skill / MCP Tool | Source | Job |
|-----------------|--------|-----|
| `notion-create-pages` | MCP `4da6be16` | Create new opportunity records in Notion | P1 |
| `notion-update-page` | MCP `4da6be16` | Update enriched fields after Pain/Distribution OS | P1 |
| `notion-search` | MCP `4da6be16` | Find existing records before creating duplicates | P1 |
| `notion-create-database` | MCP `4da6be16` | Add new database views as system grows | P2 |
| `googlebigquery-automation` | awesome/ | Push machine metrics to BigQuery | P2 |
| `googledrive-automation` | awesome/ | Archive reports to Google Drive | P3 |
| `googledocs-automation` | awesome/ | Export deep dives to Google Docs | P3 |

---

## Layer 8: Automation & Hooks

| Skill | Source | Job |
|-------|--------|-----|
| `n8n-automation` | skills/ | Alternative webhook-based automation | P3 |
| `lark-automation` | skills/ | Lark/Feishu notifications for daily report | P3 |
| `active-campaign-automation` | awesome/ | CRM automation for opportunity follow-up | P3 |
| `customerio-automation` | awesome/ | Customer engagement workflows | P3 |
| `slackbot-automation` | awesome/ | Slack notifications for new top opportunities | P2 |
| `googletasks-automation` | awesome/ | Auto-create Google Tasks from kill gate failures | P3 |
| `googlecalendar-automation` | awesome/ | Schedule customer interviews from opportunity pipeline | P2 |
| `firecrawl-automation` | awesome/ | Scheduled crawl of competitor sites | P2 |

---

## Layer 9: System Quality & Testing

| Skill | Source | Job |
|-------|--------|-----|
| `webapp-testing` | awesome/ | Automated testing of daily pipeline | P2 |
| `developer-growth-analysis` | awesome/ | Analyze chat history for system improvement patterns | P3 |
| `sql-code-review` | skills/ | Review BigQuery SQL in scoring/filtering | P3 |
| `sql-optimization` | skills/ | Optimize JSONL queries as dataset grows | P3 |
| `deployment-patterns` | skills/ | CI/CD, rollback strategies for pipeline | P3 |

---

## Layer 10: Deep Research (Venezuela + LATAM)

| Skill | Source | Job |
|-------|--------|-----|
| `deep-research` | skills/ | Multi-source VE market research with citations | P1 |
| `market-sizing-analysis` | skills/ | Bottom-up TAM for VE/LATAM geographies | P1 |
| `competitive-landscape` | skills/ | Porter's analysis on VE asymmetry opportunities | P1 |
| `content-research-writer` | awesome/ | LATAM pain signal research with source citations | P1 |
| `domain-name-brainstormer` | awesome/ | Generate product names for VE opportunity builds | P3 |

---

## New Files to Build (Phase A-D)

### Phase A — Customer Pain OS (Week 1)
```
.claude/agents/pain-intelligence-agent.md
.claude/skills/customer-pain-miner/SKILL.md
src/opportunity_os/pain_intelligence.py
```
Skills used: scrapingbee-automation, firecrawl-automation, serpapi-automation, customer-research, meeting-insights-analyzer, marketing-psychology, content-research-writer

### Phase B — Distribution OS (Week 2)
```
.claude/agents/distribution-intelligence-agent.md
.claude/skills/distribution-mapper/SKILL.md
src/opportunity_os/distribution_intelligence.py
```
Skills used: competitive-ads-extractor, lead-research-assistant, googleads-automation, revops, launch-strategy, paid-ads, cold-email, referral-program

### Phase C — Pipeline Integration (Week 3)
```
src/opportunity_os/pipelines/daily_run.py  [MODIFY — add steps 10-13]
src/opportunity_os/notion_sync.py          [NEW — live MCP sync]
hooks/export_notion_files.py               [MODIFY — add MCP sync]
```
Skills used: notion MCP tools, kpi-dashboard-design, data-storytelling

### Phase D — Awesome Skills Expansion (Week 3-4)
```
hooks/session_briefing_slack.py            [NEW — slackbot-automation]
hooks/auto_calendar_interviews.py          [NEW — googlecalendar-automation]
.claude/skills/opportunity-reporter/SKILL.md [NEW — artifacts-builder + internal-comms]
```
Skills used: slackbot-automation, googlecalendar-automation, artifacts-builder, internal-comms, googlebigquery-automation

---

## 4 Future Systems (Post Phase D)

### Asymmetry OS (Phase E)
Skills: deep-research, market-sizing-analysis, competitive-landscape, fact-checker, strategy-advisor

### Clone + Benchmark OS (Phase F)
Skills: competitive-ads-extractor, competitive-landscape, scrapingbee-automation, firecrawl-automation, content-research-writer

### Trust + Compliance OS (Phase G)
Skills: gdpr-compliance, research-lookup, strategy-advisor, startup-financial-modeling

### Workflow Replacement OS (Phase H)
Skills: meeting-insights-analyzer, data-analyst, senior-data-scientist, growth-loops, n8n-automation

---

*Skills Map v1.0 — 2026-04-01 — references 233 skills across 10 pipeline layers*
