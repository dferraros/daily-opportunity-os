# Changelog

All notable changes to Daily Opportunity OS are documented here.

Format: `[version] date — description`

---

## [2.0] 2026-06-06 — Data-backed scoring, dashboard, production hardening

### Critical bug fixes
- **ai_scorer**: model name `claude-haiku-4-5-20251001` does not exist in Anthropic API — every AI scoring call was silently falling back to heuristic. Fixed to `claude-haiku-4-5`.
- **ai_scorer**: count mismatch on partial API response raised ValueError and dropped ALL results to heuristic. Now pads partial results and preserves what the API returned.
- **enrichment**: `run_research_executor()` return value was silently discarded — API spend wasted every daily run. Fixed to merge enriched results back into `all_opps_sorted`.
- **daily_run**: Step 12 saved only `top_20` enriched records back to disk. Opps 21–N were losing TAM, scoring, and benchmark enrichment every run. Fixed to use `all_opps_sorted`.
- **daily_run**: `survivors` rebuild after AI batch scoring used fragile set-subtraction pattern that could drop opps when IDs drifted on partial fallback. Replaced with dict-merge.
- **daily_run**: `first_seen` comparison in Venezuela standing report used raw `.get()` that throws TypeError when `first_seen` is a datetime object. Fixed with `str()` cast.
- **main**: `opp.pop("research_executed_at", None)` mutated the dict returned from storage. Replaced with immutable dict comprehension copy.
- **storage**: `_make_id` used Python's `hash()` which is randomised per process (PYTHONHASHSEED). Same opportunity name could produce different IDs across runs, creating duplicates in JSONL. Fixed to use `hashlib.md5`.
- **main/stats**: `first_seen.startswith(today)` throws AttributeError when `first_seen` is a datetime object. Fixed with `str()` cast.
- **free_research**: `__import__("datetime").datetime.now()` anti-pattern. Fixed to proper module import.
- **scoring_engine**: `score_opportunity` used direct dict mutation (`opp["key"] = val`). Fixed to use spread return `{**opp, ...}`.

### Scoring improvements
- **filters**: "now" lane was permanently empty because it required `time_to_mvp` (a free-text field never auto-populated by the pipeline). Fixed to fall back to `speed_to_mvp >= 7` as proxy.
- **scoring_engine**: Added data-backed sub-scores — `market_momentum_score` (from LinkedIn job count) and `competitor_weakness_score` (from G2 negative review rate) as Strategic Value layer dimensions.
- **scoring_engine**: Added pain signal fallback — `pain_validation_score` derived from `pain_signal_count` when paid research absent (capped at 6.0 so paid results always dominate).
- **scoring_engine**: Portfolio normalisation capped at max_inflation=1.5 (was 2.5). Prevents mediocre batches from scoring 8+ just because they won locally.

### New features (P0–P5 data-backed upgrade)
- **tavily_client**: Added `search_news(query, time_range)` and `search_with_content(query)`.
- **firecrawl_client**: Added `scrape_structured(url, schema)` with `CompetitorPage` schema for pricing extraction.
- **apify_client**: New client (`apify_client.py`) — `run_actor`, `fetch_linkedin_jobs`, `fetch_g2_reviews`. Mirrors tavily_client graceful-fail structure.
- **models**: New fields — `job_posting_count`, `competitor_negative_review_rate`, `news_signal_count`, `competitor_pricing_data`.
- **enrichment**: Step 11.7 — Apify enrichment (LinkedIn + G2) on top-10 opps, skip guard 14 days.
- **free_research**: Added Tavily news signal count to `research_opportunity_free()`.
- **validation_run**: Added competitor pricing snapshot section to validation markdown.
- **main**: New commands — `rescore-all`, `free-research`.

### Dashboard (v2)
- **All Opportunities tab**: Dark card header per expanded opp (hero_card aesthetic), `subsection()` label for Intelligence column, styled score token row (ATTRACT/EXEC/STRATEGIC in JetBrains Mono), styled `<hr>` divider.
- **All Opportunities tab**: Inline action buttons — "📊 Deep Dive", "▶ Research" per opp, "↺ Rescore Portfolio" global.
- **All Opportunities tab**: Cross-tab navigation banner — "X is pre-loaded in Deep Dive tab".
- **All Opportunities tab**: SAM/SOM estimated indicator with `(est.)` disclaimer + caption.
- **All Opportunities tab**: Data-backed signal badges — NEWS, PAIN, JOBS, NEG%.
- **Venezuela Focus / Weekly Ritual / Pipeline Health / Sidebar**: Fixed `width="stretch"` → `use_container_width=True` deprecation warnings throughout.
- **Pipeline Health**: Removed redundant `from .components import subsection` inside function.
- **Weekly Ritual**: Split 6-metric row into two rows of 3 to avoid cramping.
- **Sidebar**: Added `UV_LINK_MODE=copy` env var to subprocess; show stdout on success.

### Code quality
- `pyproject.toml`: Added `[tool.pytest.ini_options] testpaths = ["src/opportunity_os"]` — isolates pytest from 19 unrelated projects in Desktop root that caused collection errors.
- `.gitignore`: Added runtime data, cache, OS artifacts, and unrelated local folder exclusions.
- Removed stale tracked files: unrelated project files, old reports, machine_metrics.jsonl, exports CSV.

### Test coverage (53 → 105 tests)
- `test_kill_gate.py` (10 tests) — all evaluate_kill_gate paths, format_kill_report
- `test_normalization.py` (18 tests) — geography variants, noise filter, bucket inference, end-to-end
- `test_filters_lane.py` (8 tests) — now/soon/strategic/no lane assignment including speed_to_mvp fallback
- `test_storage_deterministic.py` (9 tests) — ID determinism cross-process, dedup check behavior
- `test_main_immutability.py` (1 test) — research command must not mutate storage dict
- `test_e2e_data_backed_scoring.py` (12 tests) — full scoring path for all P0–P5 fields
- `test_scoring_engine_data_backed.py` (9 tests) — normalization of job count and neg review rate
- `test_models_new_fields.py` (2 tests) — new field schema
- `test_free_research_news_signal.py` (2 tests) — news_signal_count population
- `test_firecrawl_client.py` (3 tests) — scrape_structured + schema
- `test_apify_client.py` (7 tests) — run_actor, fetch_linkedin_jobs, fetch_g2_reviews
- `test_tavily_client.py` (3 tests) — search_news, search_with_content
- `test_enrichment_apify.py` (6 tests) — step 11.7 integration + research merge fix

---

## [1.0] 2026-05-20 — Initial production release

- 16-dimension AI scoring pipeline (kill gate → score → geo lens → portfolio lane)
- Venezuela + LATAM geo lens with WTP multipliers and wedge categorisation
- JSONL persistence with dedup, score history, atomic writes, backup/restore
- Daily/LATAM/Venezuela Jinja2 report templates
- Deep dive and validation pipeline
- Notion CSV export
- Streamlit dashboard (initial version)
- Weekly review pipeline
- `opp-os` CLI (daily, weekly, deep-dive, validate, research, search, stats, backup)
