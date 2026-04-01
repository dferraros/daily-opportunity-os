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
- [ ] **Phase 04: First Validation** -- top 2-3 opportunities through Stage 2 validation-runner skill

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
**Status:** PENDING
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
**Status:** PENDING -- requires Phase 02 to produce real scored opportunities first
**Success criteria:**
  1. 2-3 opportunities promoted to stage=validation
  2. validation_report.md generated for each
  3. At least 1 opportunity with validation_status=passed or failed

Plans:
- [ ] 04-01: Run /validation-runner on top 2 opportunities from first real scout
- [ ] 04-02: Document first conviction area in STATE.md

## Progress

| Milestone | Phase | Status |
|-----------|-------|--------|
| Build | 1-6 (all) | Complete |
| Launch | 01 Bootstrap | Complete |
| Launch | 02 First Real Scout | Complete |
| Launch | 03 Automation | Pending |
| Launch | 04 First Validation | Pending |
