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

## Wave 2.1 kill-thesis shipped (2026-06-12) — local commits 57c5091, ece86b4
Adversarial pass: `opp-os kill-thesis [--top-n 5] [--force] [--dry-run]`. Inverted
searches (tavily) per top opp -> skeptic prompt (Haiku) -> single kill_thesis +
strength 1-10; strength >= 7 caps final_score at 5.0 via apply_caps (new
KILL_THESIS_CAP_THRESHOLD const + kill_thesis_strong cap in scoring_weights.yaml,
combines with decision-filter cap by min). Never fabricates: missing key/empty
search/parse-fail -> opp unchanged + loud log. 30d TTL skip guard. kill_thesis.py +
test_kill_thesis.py (26 tests, 516 total).
ALSO fixed latent bug (57c5091): evidence_coverage + low_evidence_flag were written
by the scoring engine since the calibration work but never declared on the
Opportunity model — Pydantic extra='ignore' was silently dropping them on every
round-trip. Now declared + drift guard extended.
REMAINING (manual, costs API credits — Daniel's call): a live `opp-os kill-thesis`
run to satisfy the plan's Wave 2 success criterion ("at least one live opp carries a
kill_thesis with strength >= 7 and a capped score"). Dry-run verified target selection.
4 commits ahead of origin (1eb9806, d1d4737, c86da71, 57c5091, ece86b4) — not pushed.

## Milestone 2 hygiene shipped (2026-06-12) — local commits 5d27131, 749e9cd, 11e5862
- CLI smoke tests (test_cli_smoke.py): introspects cli.commands, frozen EXPECTED_COMMANDS
  guard + `<cmd> --help` for all 23 commands (catches import/option-wiring breakage).
- Shared retry helper (retry.py): call_with_retry, bounded exponential backoff, injectable
  sleep. Wired into tavily.search (hot path for free-research AND kill-thesis) — transient
  httpx timeout/transport errors now retry instead of silently dropping a result.
- env.get_key consolidation: tavily/apify/firecrawl/ai_scorer dropped their duplicate .env
  walkers (which IGNORED OPP_OS_SKIP_DOTENV — a test could read the real .env). Now all
  route through env.get_key which respects the skip flag. Removed dead os/Path imports +
  ai_scorer._find_project_root orphan. Ruff clean, 532 tests.
## G2 retool + Wave 2.2 shipped (2026-06-12, live-verified) — commits f-block below
- competitor_intelligence.py: Tavily review search + Haiku weakness extraction replaces the
  broken Apify G2 category mode. Wired into enrichment as primary, Apify G2 as fallback.
  Verified live (search->Haiku->clamped rate). FINDING: 0/80 opps have direct_competitors
  populated, so it runs on a name-keyword category fallback (weak signal) — tagged
  competitor_signal_basis. REAL UNLOCK: populate direct_competitors upstream (scout/enrich gap).
- deep_dive_synthesis.py: Sonnet bull-case/risks/go-validate-pass section, opt-in via
  `opp-os deep-dive <id> --synthesize` (~$0.10). Verified live on #1 opp — sharp, named real
  incumbents + per-country cert risk + $0 govt price anchor -> VALIDATE with gates.
- All new pipeline fields declared on the model + drift guard (no silent-drop). 562 tests,
  ruff clean, idempotency 0/80.

## direct_competitors gap CLOSED in code (2026-06-12) — commit below
research_executor now extracts direct_competitors in BOTH paths (combined web_search +
Tavily-context), free (rides existing per-opp Claude call); added to deep_dive merge-back
allowlist. Verified live: top opp -> Alegra, Siigo, Pagero, Fonoa; competitor_intelligence
upgrades category_fallback -> grounded per-competitor search. 566 tests.
CAVEAT (action needed): the 80 EXISTING opps have research_executed_at set, so the executor
SKIPS them -- they stay competitor-less until re-researched. New opps get competitors
automatically. To backfill existing: clear research_executed_at on target opps and re-run
research (costs ~$0.01-0.015/opp, ~$1-2 for all 80). NOT done autonomously -- bulk data
rewrite is Daniel's call. Could add a surgical `opp-os backfill-competitors` if wanted.

## Deep-dive depth overhaul (2026-06-12) — commits below
Root cause of "vague deep research": the report rendered 3 aggregate layer scores and
DISCARDED the 16 per-dimension reasons the scorer computes. Fixed in three layers:
1. _section_scoring_breakdown: every ~23 dims with value/weight/contribution/reason, by
   layer, weight-0 (consolidated) dims marked, kill thesis as adversarial counterweight.
   Zero API cost (surfaces existing data).
2. Rich reasons at source: score_dimensions_with_ai now asks 2-3 evidence sentences/dim
   (was 15-word stub; trunc 200->450, max_tokens 3500). Wired into deep-dive on-demand,
   REASONS ONLY (numbers stay batch-normalized — avoids report/score desync), 30d TTL.
3. Sonnet synthesis deepened: + swing_factors (what decides go/no-go) + key_unknown
   (decisive missing evidence). Cross-cutting, not dimension restatement. Opt-in --synthesize.
All live-verified on #1 opp (e-invoicing): named Alegra/Siigo/Contacloud, $5-15/mo, cert
6-18mo bottleneck, "6-week MVP vs 18-month regulatory odyssey". 579 tests, ruff clean, 0/80.

## Backlog now (all need Daniel / API spend)
- Backfill direct_competitors on existing 80 opps (optional, ~$1-2) to activate grounded
  competitor signal portfolio-wide now rather than as opps refresh.
- Record outcomes (`opp-os outcome <id> <status>`) — calibration still at 0 resolved.
- Live `opp-os kill-thesis` run (Wave 2 success criterion).
DEPLOYED 2026-06-12: all 19 commits pushed to origin/main (6534417..b019000). Tree clean,
ruff + 579 tests green pre-push. origin/main now current. (gh not auth'd locally — verify
CI green on GitHub if needed.)

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
