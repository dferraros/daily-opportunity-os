# STATE.md — Daily Opportunity OS
Last updated: 2026-06-12 (calibration loop shipped: goal rubric + calibrate CLI + evidence coverage)

## Calibration loop (2026-06-12) — Wave 3.3 shipped, NOT pushed yet
Goal rubric: docs/plans/2026-06-12-scoring-calibration-goal.md ("the score must predict
reality"). Commits on main (local, push pending): 9813ca9 evidence_coverage +
low_evidence_flag (collected/collectable evidence, flag at final>=7.5 & coverage<0.5),
e42a94f calibration engine + `opp-os calibrate` (bucket discrimination, Brier skill,
dimension effects, damped never-auto-applied proposals, HOLD_WEIGHTS_VALIDATE_ONLY under
30 resolved outcomes), ccccb9b goal doc, 5c0a2e7 leaked-data cleanup. Tests 491 green;
rescore-all --dry-run 0/80.
First live findings: (1) ZERO resolved outcomes — bottleneck is recording; bridge
`outcome` cmd now auto-snapshots into outcome_tracking.jsonl BEFORE kill cap zeroes the
score. (2) speed_to_mvp redundancy cluster (spearman 0.71-0.82 with capital_efficiency,
competition_intensity, operational_simplicity, distribution_accessibility, n=76) — one
"execution ease" factor counted 5x; candidate consolidation at next weight edit.
Leak fixed: conftest now redirects outcome_tracking._outcome_file to tmp (bridge CLI
tests were writing live data).
Follow-up shipped (1eb9806, d1d4737 — local): execution-ease consolidation
(capital_efficiency + operational_simplicity -> 0, speed_to_mvp 0.04 -> 0.07 carrier;
portfolio rescored 74/80 small corrections, idempotency 0/80) and research-queue
priority (low_evidence_flag jumps free-research + apify-research queues). 494 tests.
NOTE: repo history was rewritten + force-pushed 2026-06-12 (employer/external-project
purge) — re-clone anywhere a stale clone exists.

## Second audit pass (2026-06-10, evening) — verified-then-fixed
6-agent workflow audit produced 45 raw findings -> 7 after dedup; manual verification
against code AND live data killed 2 as false positives before any fix:
- FALSE: "weights fallback inflates scores 2-3x" — score_layer divides by total_weight,
  scale is irrelevant; equal-weight fallback is the documented design
- FALSE: "duplicate records corrupting data" — 0 dup IDs / 0 dup name+geo in 80 records;
  daily_run dedupes BEFORE append. Latent gap only: 7-day window
Fixed and pushed (525bc70, 3bef517, 04b7d4c):
- scoring: job_posting_count=0 now no-signal (fetch_linkedin_jobs returns 0 on failure)
- scoring: scoring_incomplete flag disambiguates unscored (0.0) from killed (0.0)
- models: 19 pipeline-written fields declared (extra='ignore' silently DROPS undeclared
  fields on round-trip — latent data-loss trap, drift-guard test added)
- pipeline: daily dedupe window 7 -> 365 days (dated IDs would split history on re-surface)
Tests 419 -> 426, all green. rescore-all --dry-run: 0/80 changed (idempotency intact).
Dashboard root cause found: STALE streamlit (PID from Projects/.worktrees copy) was
squatting port 8501 — kill stray streamlit processes before relaunching.

## Current Position
Repo: C:/Users/ferra/OneDrive/Desktop (root) — branch `main` only (master + feat deleted).
CI live on every push to main (lint + 419 tests). All API keys configured and verified live.
Data-backed scoring IS live: job_posting_count (9 opps), news_signal_count (relevance-filtered),
pain_signal_count 5-7 across top-20, pain_validation_score 76/76.

## Source stack (FINAL — decided 2026-06-10, do not re-litigate)
- Tavily (news + pain search + SERP fallback) — free 1k/mo, ~12% used
- Apify (LinkedIn jobs live; G2 retool pending) — $5 console cap, ~$1-3/mo actual
- Firecrawl (Reddit scraping + competitor pricing) — free 1k pages/mo
- HN (keyless), Anthropic ($10 console cap)
- REJECTED: Serper (not needed), SearchAPI ($40/mo min breaks $20 ceiling),
  Reddit OAuth (marginal), Jina (keyless access dead — 401)
- Budget ceiling: $20/mo hard; expected $5-11; caps make worst case $15

## Done this session (2026-06-10) — see git log for detail
- Full principal-level audit; Milestone 1 complete (all Critical/High fixed)
- C1: enrichment merge-back + 30d research TTLs (was discarding paid research daily)
- Model IDs fixed in 4 modules (claude-haiku-4-5 — dated IDs don't exist, calls failed silently)
- 14 silent excepts now log; free-research CLI lists unconfigured sources
- Test suites unified: 419 colocated tests, `uv run pytest` runs everything; 3 live-data
  leaks fixed (pain_library, pipeline_failures, .env via OPP_OS_SKIP_DOTENV in conftest)
- scoring_weights.yaml = single source of truth; DEFAULT_WEIGHTS = loud equal-weight fallback
- Wave 1 bridge: opp-os like / liked / export / kickoff + dashboard Like/Download buttons
- Wave 3.2: idempotent normalization (raw_final_score only input; 0/80 drift verified)
- env.py: unified .env bootstrap at CLI/dashboard startup
- Apify fixed live: v3 client API, real actor input schemas, $0.25/run caps,
  apify-research CLI for the standing portfolio
- news_signal_count: relevance-filtered (raw counts saturate at max_results)
- Tavily replaced dead Jina as pain-search fallback

## Next Actions (plan: docs/plans/2026-06-10-research-scoring-validation-upgrade.md)
1. Wave 2.1: kill-thesis pass — inverted searches top-5, strength>=7 caps score.
   SEMANTICS-HEAVY: review cap interaction with apply_caps() carefully.
2. Wave 2.2: Sonnet deep-dive synthesis on #1 opp (~$0.10/dive, budget approved)
3. Wave 2: G2 retool — productUrls from direct_competitors (category mode returns
   product summaries, not reviews) or Tavily site:g2.com + Haiku extraction
4. Wave 3.3: calibration loop (like/kickoff/validate record outcomes; opp-os calibration)
5. Wave 4.1/4.2: evidence-gated validation sections + experiment kit
6. Milestone 2 backlog: shared retry helper, CLI smoke tests, consolidate 6 .env
   parsers onto env.py

## Hard-won context (do not rediscover)
- NEVER read Projects/.worktrees/daily-opportunity-os/ — stale copy, reports phantom bugs
- rescore-all --dry-run on unchanged data MUST report 0 changed (idempotency invariant)
- Tests must never write live data files — conftest fixtures guard this; extend them
  for any new file-writing module
- Apify G2 category mode returns garbage (404 products, rating: null) — parser skips
  rating-less items; competitor_weakness_score stays null until retool
- Tavily basic search = 1 credit regardless of max_results

## Pipeline Commands
- Daily: uv run opp-os daily | Standing enrichment: opp-os free-research / apify-research
- Bridge: opp-os like <id> -> export <id> -> kickoff <id>
- Dashboard: uv run streamlit run src/opportunity_os/dashboard.py
- Tests: uv run pytest -q (419) | Rescore: opp-os rescore-all --dry-run
