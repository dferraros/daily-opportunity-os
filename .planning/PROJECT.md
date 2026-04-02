---
gsd_project_version: 1.0
created: "2026-04-01"
owner: Daniel Ferraro
---

# Daily Opportunity OS -- Project

## What This Is

A daily-run intelligence system that discovers, evaluates, and ranks real business opportunities -- with mandatory LATAM and Venezuela focus. Not an idea generator. A structured OS that finds businesses worth building.

## Core Value

Daniel runs the machine each morning. It ingests raw signals, kills weak ideas at the gate, scores survivors across 16 dimensions, assigns portfolio lanes, and produces three reports (global / LATAM / Venezuela) plus Notion exports. Over time it compounds into a proprietary deal-flow system.

## Stack

- **Runtime**: Python 3.11+ via uv | **CLI**: Click (`opp-os` entry point)
- **Schema**: 73-field Pydantic Opportunity model
- **Storage**: JSONL flat files (no DB dependency)
- **Reporting**: Jinja2 -> Markdown reports
- **Exports**: CSV -> Notion import
- **Hooks**: 9 Claude Code hook scripts
- **Agents**: 5 specialist agents (geo-scout-ve / geo-scout-latam / tam-analyst / competitive-intel / synthesis-lead)
- **Skills**: 12 SKILL.md files (signal-harvester to validation-runner)
- **Superpowers**: All Claude Code skills installed -- invoke via Skill tool before any analysis, research, or specialized work

## Requirements

### Validated (Build Complete)
- REQ-01: 73-field Pydantic schema with kill gate, portfolio lanes, founder fit, distribution profile
- REQ-02: Kill gate -- 7 criteria, 2+ failures = killed, never scored
- REQ-03: Scoring engine -- 16 dimensions, weighted, geo-adjusted (VE: 0.25x, LATAM: 0.40x)
- REQ-04: Venezuela always-present -- pipeline + Stop hook enforcement
- REQ-05: 3 reports per daily run (global / LATAM / venezuela)
- REQ-06: Notion CSV exports (daily_feed + opportunity_database)
- REQ-07: 5 agents with model-optimized frontmatter (haiku/sonnet/opus)
- REQ-08: 12 skills covering full scout to validate pipeline
- REQ-09: 9 hooks covering all lifecycle events

### Active (Operationalization)
- REQ-10: Real opportunity signals fed daily into data/raw/
- REQ-11: Daily automation running (scheduled task or cron)
- REQ-12: First real validation run on top 2-3 opportunities

### Out of Scope (V1)
- ML-based scoring (planned V3)
- Real-time API integrations (CoinGecko optional, free tier only)
- Multi-user / team access

## Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Storage | JSONL flat files | Zero infrastructure, portable, Claude-readable |
| Python runtime | uv | Already installed, fastest dep resolution on Windows |
| Worktree isolation | feat/daily-opportunity-os branch, NOT merged to master | .claude/ hooks would pollute all Projects if merged |
| Venezuela enforcement | Two layers: pipeline + Stop hook | Single layer too easy to bypass |
| Agent models | haiku (scouts) / sonnet (analysts) / opus (synthesis) | Cost-optimized per task complexity |
| Scoring | 16 weighted dimensions + 3 hard caps | Captures nuance while preventing bad ideas scoring through |
| Portfolio lanes | now/soon/strategic/no | Forces decision, prevents flat ranked fantasy list |

## Constraints

- Windows paths with spaces: always use PYTHONPATH=src uv run python
- Write tool fails on Desktop paths: use Temp/ Python workaround
- .planning/ must not contain Playbook Maestro content (cleaned 2026-04-01)
- Worktree must not be merged into master (hook isolation)

## Superpowers

All 90+ skills available. Key ones for this project:
- `signal-harvester` -- daily opportunity discovery
- `latam-venezuela-lens` -- re-score through local reality
- `tam-estimator` -- dual-method TAM
- `deep-dive-builder` -- full thesis for shortlisted opps
- `validation-runner` -- Stage 2 customer validation
- `decision-memo-builder` -- 1-page memo for promoted opps
- `weekly-review` -- forced weekly outputs (top 3 validate / top 3 kill / top 3 rising / 1 conviction)
