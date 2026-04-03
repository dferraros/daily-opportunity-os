# Phase 6: Machine Hardening + Intelligence Depth — Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Source:** Parallel audit (4 agents: skills-gap, data-model, pipeline-health, ecosystem)

<domain>
## Phase Boundary

Phase 6 hardens what Phase 5 built. The system has 64 scored opportunities, a research executor firing real web searches, a Streamlit dashboard, and a full daily pipeline — but it has critical gaps that silently degrade output quality:

1. **Schema rot** — 15 deprecated fields in `models.py` that are never populated (0% usage), plus 5 missing fields that logic already assumes
2. **Research scope too narrow** — Only top-5 opps get pain/distribution research; 59/64 have null research fields
3. **No pipeline monitoring** — 12 silent `try/except` blocks; failures swallowed with no logging
4. **Deep dives never auto-trigger** — `deep_dive.py` exists but nothing calls it on top opportunities
5. **Rising signals broken** — `rising_signals` always returns `[]` because score history is never written
6. **Venezuela lens not auto-applied** — VE opps go through generic scoring without auto-applying geo adjustments
7. **Quota tracking broken** — `config/weekly_quotas.yaml` exists but code never reads it; quotas are hardcoded

</domain>

<decisions>
## Implementation Decisions

### Wave 1 (parallel — independent modules)

**06A: Schema Cleanup**
- DELETE these 15 deprecated fields from `models.py` (0% usage, never populated):
  `pain_cluster_id`, `trust_profile`, `why_now_venezuela`, `first_revenue_path`,
  `daniels_wedge_score` (old version), `non_obviousness_score` (old version),
  `business_model_type` (old version), `thesis_fit_score` (old version),
  `decision_filter_results` (old version), `distribution_profile` (old version),
  `benchmark_archetype` (old version), `founder_fit_score` (old version),
  `pain_validation_score` (duplicated), `pain_evidence_sources` (duplicated),
  `workarounds_found` (duplicated)
  → Keep the "live" versions that `research_executor.py` actually writes to
- ADD `recommendation: Optional[str]` — populated from portfolio_lane + score logic
- ADD `score_history: Optional[List[Dict]]` — append-only, [{date, score, delta}]
- ADD `tam_formula: Optional[str]` — which of 4 TAM methods was used
- ADD `tam_confidence: Optional[str]` — "low"/"medium"/"high"
- Bump schema version comment to "v2 — Phase 6 cleanup"
- Run migration: for all existing opps in opportunities.jsonl, strip deleted fields

**06B: Research Scope Expansion**
- In `daily_run.py`, change Step 11.5 (Research Executor) from `opps[:5]` to `opps[:20]`
- In `daily_run.py`, change Step 9.7 (Benchmark mapping) from `opps[:10]` to `opps[:30]`
- In `scripts/run_research_backfill.py`, update default batch size from 5 to 20
- Adjust rate limiting: keep 1.5s between calls (Anthropic rate limit)
- Add progress output: "Researching opp {n}/{total}: {name}"

**06C: Deep Dive Auto-Trigger**
- In `pipelines/weekly_run.py`, after scoring, auto-call `run_deep_dive()` on top 3 opps with score >= 7.0
- In `pipelines/daily_run.py`, add Step 14: auto-call `run_deep_dive()` on top 1 opp with score >= 8.0
- Deep dive outputs go to `reports/deep-dives/YYYY-MM-DD-{opp_id}.md`
- Skip if deep dive already exists for this opp_id this week

**06D: Pipeline Health Monitor**
- Create `data/pipeline_failures.jsonl` — append on every caught exception in daily_run.py
- Each failure record: `{date, step, error_type, error_msg, opp_id, recovered}`
- Replace all 12 silent `pass`/`continue` except blocks with `_log_failure(step, e, opp_id)`
- Add `opp-os audit` CLI command: reads pipeline_failures.jsonl, shows failure rate by step
- The audit command prints: step name, failure count, last error, recommendation

### Wave 2 (parallel — run after Wave 1)

**06E: Firecrawl Integration (Pain Validation)**
- Create `src/opportunity_os/firecrawl_client.py` — thin wrapper reading `FIRECRAWL_API_KEY` from `.env`
- Integrate into `research_executor.py`: if `FIRECRAWL_API_KEY` set, crawl Reddit/YouTube for pain evidence
- Target URLs: `reddit.com/r/vzla`, `reddit.com/r/Colombia`, `reddit.com/r/fintech` + search pages
- Store crawled pain phrases in `exact_customer_phrases` field (max 5)
- If key not set: fall back to existing Anthropic web_search (current behavior)
- Guard with `try/except`: Firecrawl failures must not break the pipeline

**06F: Venezuela Lens Auto-Run**
- In `daily_run.py` after Step 5 (score_opportunity), add Step 5.5: for every opp where `geography == "venezuela"`, call `apply_geo_adjustments(opp, "venezuela")` from `geo_lens.py`
- Currently geo adjustments only run in Step 6 (apply_geo_adjustments); VE opps need an extra pass
- Log: "Venezuela lens applied to {n} opps"
- Write `venezuela_lens_applied: bool` field to each adjusted opp

**06G: Score History + Rising Signals**
- In `storage.py`, implement `append_score_history(opp_id, new_score)`:
  - Reads current opp from opportunities.jsonl
  - If `score_history` field exists, appends `{date: today, score: new_score, delta: new-prev}`
  - If `score_history` is None/missing, creates it with first entry (delta=0)
  - Writes back via `update_opportunity(opp_id, {"score_history": updated_history})`
- In `daily_run.py` after Step 8 (score), call `append_score_history` for each scored opp
- Fix `weekly_run.py` `get_rising_signals()`:
  - Read `score_history` field from each opp
  - Rising = score increased by >= 0.5 in last 7 days
  - Return top 3 risers sorted by delta desc

**06H: Quota Tracking from Config**
- In `pipelines/daily_run.py`, at the end of each run, read `config/weekly_quotas.yaml`
- Count: signals_ingested, opportunities_created, deep_dives, validations_run
- Append weekly quota progress to `data/machine_metrics.jsonl`
- In `main.py` `stats` command, add weekly quota progress: "This week: X/30 signals, Y/10 opps, Z/3 deep dives"
- Read quotas from config, not hardcoded values

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema and Data Model
- `src/opportunity_os/models.py` — Pydantic Opportunity model (source of truth for all fields)
- `data/opportunities/opportunities.jsonl` — Live data (check field usage before deleting)
- `src/opportunity_os/storage.py` — JSONL read/write/query/update functions

### Pipeline Orchestration
- `src/opportunity_os/pipelines/daily_run.py` — Main pipeline (all steps, step numbers, error handling)
- `src/opportunity_os/pipelines/weekly_run.py` — Weekly pipeline (rising signals, quotas)
- `src/opportunity_os/pipelines/deep_dive.py` — Deep dive runner (to be auto-triggered)

### Research and Intelligence
- `src/opportunity_os/research_executor.py` — Anthropic web_search integration
- `src/opportunity_os/pain_intelligence.py` — Pain query builder
- `src/opportunity_os/distribution_intelligence.py` — Distribution query builder
- `src/opportunity_os/geo_lens.py` — Venezuela/LATAM adjustments

### CLI and Config
- `src/opportunity_os/main.py` — Click CLI (add `audit` subcommand here)
- `config/weekly_quotas.yaml` — Quota targets (read this, don't hardcode)
- `.env` — `ANTHROPIC_API_KEY`, `FIRECRAWL_API_KEY`

### Scoring
- `src/opportunity_os/engines/benchmark_engine.py` — `run_benchmark(opp)` wrapper
- `src/opportunity_os/engines/tam_engine.py` — `estimate_tam_from_opp(opp)` wrapper

</canonical_refs>

<specifics>
## Specific Implementation Notes

### Schema Migration (06A)
Before deleting fields, run this check to confirm 0 usage:
```python
import json
opps = [json.loads(l) for l in open("data/opportunities/opportunities.jsonl") if l.strip()]
fields_to_delete = ["pain_cluster_id", "trust_profile", ...]
for f in fields_to_delete:
    count = sum(1 for o in opps if o.get(f) is not None)
    print(f"{f}: {count} non-null values")
```
Only delete if count == 0 for all.

### Research Scope (06B)
Current `daily_run.py` step 11.5 code to find and update:
```python
for opp in sorted_opps[:5]:  # ← change to [:20]
    run_research_executor(opp)
```

### Pipeline Failure Logging (06D)
Replace pattern:
```python
except Exception as e:
    pass  # ← 12 occurrences of this
```
With:
```python
except Exception as e:
    _log_failure("step_name", e, opp.get("id", "unknown"))
```

`_log_failure` function writes to `data/pipeline_failures.jsonl`.

### Firecrawl Guard (06E)
```python
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
if FIRECRAWL_API_KEY:
    # use firecrawl
else:
    # fall back to anthropic web_search
```

### Score History Format (06G)
```json
{"date": "2026-04-03", "score": 7.82, "delta": 0.15}
```
Delta is `current - previous`. First entry delta = 0.

</specifics>

<deferred>
## Deferred (Phase 7+)

- Firecrawl scheduled crawls (beyond single-opp research)
- BigQuery sync for machine metrics
- Slack daily briefing
- Google Calendar customer interview auto-schedule
- Full scraping API expansion (SerpAPI, ScrapingBee)

</deferred>

---
*Phase: 06-machine-hardening-intelligence-depth*
*Context gathered: 2026-04-03 via parallel audit (4 agents)*
