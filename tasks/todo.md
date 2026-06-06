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

## Up next

- [ ] Hook up Apify API token in .env and run first real LinkedIn/G2 pass
- [ ] Add score_history chart to All Opportunities tab
- [ ] Weekly run automation via scheduled task
