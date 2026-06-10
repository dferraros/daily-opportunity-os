# tasks/todo.md — Opportunity OS

Active task list. Updated by /plan and /build commands.

## Status

- [x] P0: Upgrade tavily_client.py — search_news + search_with_content
- [x] P1: Add scrape_structured to firecrawl_client.py
- [x] P2: Create apify_client.py
- [x] P3a: Add new fields to models.py
- [x] P3b: Upgrade scoring_engine.py — normalization + new weights
- [x] P4a: Add Tavily news signal to free_research.py
- [x] P4b: Add Apify enrichment step 11.7 to enrichment.py
- [x] P5: Add competitor pricing snapshot to validation_run.py
- [x] Bug: research_executor results discarded in enrichment.py
- [x] Bug: Step 12 saves only top_20 instead of all_opps_sorted
- [x] Bug: opp.pop() mutation in main.py research command
- [x] Bug: "now" lane never fires (time_to_mvp fallback to speed_to_mvp)
- [x] Bug: hash() non-deterministic IDs in storage._make_id
- [x] Bug: first_seen.startswith() crash in stats command
- [x] Bug: ai_scorer model name wrong (claude-haiku-4-5-20251001 -> claude-haiku-4-5)
- [x] Bug: AI partial results dropped on count mismatch
- [x] Bug: survivors rebuild fragile after AI batch scoring
- [x] Chore: Expand .gitignore, clean tracked files, write README + CHANGELOG
- [x] Install agent-skills framework
- [x] Audit C1: enrichment steps 9.7/10/11 results lost before persistence — merge-back + 30-day research TTL (b762650)
- [x] Audit: test_enrichment_apify wrote to live pain_library.jsonl — patched (0fb764d)

## Up next (from 2026-06-10 audit — see audit doc for full task plan)

- [x] QW1+QW2: CI fixed (triggers on main, unified suite + ruff syntax gate) + tests/ folded into colocated layout (379 tests)
- [x] GitHub: default branch flipped to main; deleted origin/master + origin/feat/daily-opportunity-os (both fully merged) + 12 stale local branches
- [x] QW3: research_executor mutation fixed + bonus: dated model IDs (claude-haiku-4-5-20251001) replaced in 3 modules — paid research extraction was silently failing (86a481e, 2e9928a)
- [x] QW4: expired INTERVIEW_DEADLINE quota check removed from daily_run step 17 (6cfe547)
- [x] QW5: path traversal guard in backup restore (c6d2841)
- [x] Test isolation: conftest redirects pipeline_failures.jsonl to tmp suite-wide (252d222)
- [ ] QW6: Add TAVILY_API_KEY + APIFY_API_TOKEN to .env, run free-research --force + rescore-all
- [x] T1.2: 14 silent excepts now log warnings; free-research CLI lists unconfigured sources upfront (c51bfb1)
- [x] T1.3: scoring_weights.yaml is single source of truth (all 23 weights); DEFAULT_WEIGHTS now equal-weight loud fallback; zero score drift verified (cc0d2a3)
## Upgrade plan (approved 2026-06-10 — docs/plans/2026-06-10-research-scoring-validation-upgrade.md)

- [x] Wave 1.1: opp-os like / liked / --undo + dashboard Like button (3dfcf71)
- [x] Wave 1.2: opp-os export — self-contained report.md + dashboard download button (3dfcf71)
- [x] Wave 1.3: opp-os kickoff — PROJECT.md seed + Claude Code kickoff prompt (3dfcf71)
- [ ] Wave 2.1: kill-thesis pass (needs .env keys)
- [ ] Wave 2.2: Sonnet deep-dive synthesis on #1 opp (needs .env keys)
- [ ] Wave 2.3: evidence provenance tags
- [ ] Wave 3.1: confidence-weighted scoring (provenance multipliers)
- [ ] Wave 3.2: idempotent normalization (fixes ~75/80 phantom drift)
- [ ] Wave 3.3: calibration loop — outcomes recorded by like/kickoff/validate
- [ ] Wave 4.1: evidence-gated validation sections (pass/unverified/fail)
- [ ] Wave 4.2: validation experiment kit (outreach scripts, landing copy, 7-day checklist)

## Backlog

- [ ] Milestone 2 (audit): shared env loader, retry helper, CLI smoke tests
- [ ] Add score_history chart to All Opportunities tab
- [ ] Weekly run automation via scheduled task
