# Roadmap: Daily Opportunity OS

## Overview

Two-milestone structure. Milestone 1 (Build) is complete across 15 commits.
Milestone 2 (Launch) operationalizes the system: real signals, real reports, automation.

## Milestone 1: Build (COMPLETE)

**Status:** 100% complete | 15 commits | Verified 2026-04-01

- [x] **Phase 1: Foundation** -- scaffold, CLAUDE.md, 73-field Pydantic schema, config YAMLs
- [x] **Phase 2: Engines** -- kill_gate, scoring_engine, geo_lens, storage, normalization, tam_engine, benchmark_engine, exporters, filters
- [x] **Phase 3: Skills + Agents** -- 12 SKILL.md files, 5 specialist agents (haiku/sonnet/opus)
- [x] **Phase 4: Hooks** -- 9 hook scripts (PreToolUse, PostToolUse, Stop, SubagentStop, InstructionsLoaded, PreCompact, FileChanged)
- [x] **Phase 5: Templates + CLI** -- 4 Jinja2 templates, Click CLI (daily/weekly/deep-dive/search/stats), 3 pipelines
- [x] **Phase 6: Scripts + Sample Data** -- bootstrap.sh, run_daily.sh, run_weekly.sh, 3 sample records, README

## Milestone 2: Launch (ACTIVE)

**Status:** In progress | Started 2026-04-01

- [x] **Phase 01: Bootstrap** -- deps installed, dirs created, sample data verified (3 opps loading)
- [x] **Phase 02: First Real Scout** -- 13 signals, 12 scored, 1 killed, 3 reports generated (2026-04-01)
- [ ] **Phase 03: Automation** -- daily scheduled task running at 09:00
- [x] **Phase 04: First Validation** -- all 3 top VE opportunities through Stage 2 validation-runner (2026-04-01)

## Phase Details: Milestone 2

### Phase 01: Bootstrap
**Goal:** System installed and sample data verified
**Status:** COMPLETE (2026-04-01)
**Verified:** `opp-os stats` shows 3 opportunities, 2 lanes (now/soon), 1 Venezuela

Plans:
- [x] 01-01: Run bootstrap.sh -- deps installed, dirs created
- [x] 01-02: Verify sample data -- stats command works, all 3 records loading

### Phase 02: First Real Scout
**Goal:** First daily run with real opportunity signals producing 3 reports
**Status:** COMPLETE (2026-04-01)
**Success criteria:**
  1. data/raw/2026-04-01-signals.jsonl exists with 5+ real signals
  2. `opp-os daily` completes without errors
  3. reports/daily/2026-04-01-global.md exists
  4. reports/daily/2026-04-01-venezuela.md exists (even if empty signals)
  5. exports/notion/daily_feed.csv updated

Plans:
- [x] 02-01: Run signal-harvester skill -- 13 real signals (5 global, 4 LATAM, 4 VE)
- [x] 02-02: Run `opp-os daily` -- 12 scored, 1 killed, 3 reports generated
- [x] 02-03: Check Notion CSV -- daily_feed.csv + opportunity_database.csv generated

### Phase 03: Automation
**Goal:** Daily 09:00 run without manual intervention
**Status:** PENDING
**Options (in priority order):**
  1. /schedule in Claude Code Desktop (retry when cloud connected)
  2. Windows Task Scheduler -> bash scripts/run_daily.sh
  3. WSL cron: `0 9 * * 1-5 cd ... && uv run python -m opportunity_os.main daily`

Plans:
- [ ] 03-01: Set up automation via one of the 3 options above
- [ ] 03-02: Verify automation ran by checking reports/daily/ next morning

### Phase 04: First Validation
**Goal:** Top opportunities through Stage 2 validation (validation-runner skill)
**Status:** COMPLETE (2026-04-01)
**Success criteria:**
  1. 2-3 opportunities promoted to stage=validation
  2. validation_report.md generated for each
  3. At least 1 opportunity with validation_status=passed or failed

Plans:
- [x] 04-01: Ran validation-runner on top 3 VE opportunities -- all PROCEED verdicts
- [x] 04-02: First conviction area: Venezuelan USDT commerce infrastructure (see STATE.md)

## Progress

| Milestone | Phase | Status |
|-----------|-------|--------|
| Build | 1-6 (all) | Complete |
| Launch | 01 Bootstrap | Complete |
| Launch | 02 First Real Scout | Complete |
| Launch | 03 Automation | Complete (Task Scheduler setup) |
| Launch | 04 First Validation | Complete |
| Launch | 07 Free Intelligence Stack | Complete |

### Phase 5: Intelligence Amplification — wire all 9 orphaned skills into automated pipeline, build research execution engine that runs WebSearch for all 64 opportunities, build Streamlit dashboard, auto-fire Notion MCP sync, automate weekly ritual

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 4
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 5 to break down)

### Phase 6: Machine Hardening + Intelligence Depth

**Goal:** Harden the machine: remove schema rot, expand research from top-5 to top-20, add pipeline failure monitoring, auto-trigger deep dives, fix broken rising signals, auto-apply Venezuela lens on VE opps, read quota config from file. Zero silent failures. Full intelligence coverage.
**Requirements**: Derived from parallel audit (skills-gap, data-model, pipeline-health, ecosystem)
**Depends on:** Phase 5
**Plans:** 8 plans

Plans: **COMPLETE (2026-04-03) — 10 commits**
- [x] 06-01A-PLAN.md -- Schema Cleanup (15 deprecated fields removed, score_history + venezuela_lens_applied added)
- [x] 06-01B-PLAN.md -- Research Scope Expansion (top-5→top-20, benchmark top-10→top-30)
- [x] 06-01C-PLAN.md -- Deep Dive Auto-Trigger (top-1 >=8.0 daily, top-3 >=7.0 weekly)
- [x] 06-01D-PLAN.md -- Pipeline Health Monitor (12 silent failures → logged, audit CLI)
- [x] 06-02E-PLAN.md -- Firecrawl Integration (optional Reddit crawl, falls back to web_search)
- [x] 06-02F-PLAN.md -- Venezuela Lens Auto-Run (Step 5.5 in daily pipeline)
- [x] 06-02G-PLAN.md -- Score History + Rising Signals (fixed from always-empty to real delta tracking)
- [x] 06-02H-PLAN.md -- Quota Tracking from Config (weekly_quotas.yaml wired to stats + pipeline)

### Phase 7: Free Intelligence Stack — MCP Servers + Zero-Cost Research Layer

**Goal:** Replace all paid API research calls with free alternatives. Install 7 MCP servers. Wire Jina Reader, HN Algolia, Reddit JSON, and pytrends as a free research layer covering top-20 opps daily.
**Status:** COMPLETE (2026-04-03)
**Depends on:** Phase 6

Plans:
- [x] 07-A: Install 7 MCP servers (Brave Search, Tavily, Firecrawl, Apify, Omnisearch, Research PowerPack, Perplexity) into .claude/settings.json
- [x] 07-B: Add free research layer — src/opportunity_os/free_research.py (Jina + HN Algolia + Reddit JSON + pytrends, zero API cost)
- [x] 07-C: Wire Step 11.6 in daily_run.py — free research covers top-20 opps (API research only for top-3)
- [x] 07-D: Update .env.example with all new API key placeholders + scripts/setup_free_apis.md
- [x] 07-E: Add pytrends + yars to pyproject.toml dependencies

**Free sources now available:**
| Source | Auth | Cost | Use case |
|--------|------|------|----------|
| Jina Reader (r.jina.ai) | Optional | Free (10M tokens/key) | URL → markdown |
| Jina Search (s.jina.ai) | Optional | Free (20 req/min) | Web search |
| HN Algolia | None | Free, unlimited | Startup signals |
| Reddit JSON | None | Free, 100 QPM | Pain complaints |
| Google Trends (pytrends) | None | Free | Demand signals |
| Brave Search MCP | API key (free tier) | 2000/month free | Web search |
| Tavily MCP | API key (free tier) | Free tier | Research search |
| Firecrawl MCP | API key (500 credits) | Free tier | Full-site crawl |
| Apify MCP | API key (free tier) | $5 free credit | 1000s of scrapers |
| Perplexity MCP | API key (free tier) | Free tier | Cited research |
| Omnisearch MCP | Various | Mixed | Unified search |
| Research PowerPack MCP | None | Free | Reddit + crawl |
