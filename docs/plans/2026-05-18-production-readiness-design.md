# Production Readiness Design — Daily Opportunity OS
Date: 2026-05-18

## Problem Statement

The system has three structural failures:

1. **Pain OS is theatrical.** `pain_intelligence.py` builds queries but never executes them. All 79 opportunities have `pain_validation_score = null`. Six hours of cleanup fixed symptoms, not the cause.
2. **Scoring is blind.** `scoring_engine.py` does not use `pain_validation_score` or `distribution_validated` even if they were populated. Research data has zero weight on final ranking.
3. **No regression guard.** Zero tests for `pain_intelligence.py`, `distribution_intelligence.py`, `ai_scorer.py`. No CI. A bug in research execution would be invisible until manual inspection.

## Approved Approach: Incremental Value-First (B)

Three phases, each independently shippable and testable.

---

## Phase 1 — Execute Real Research

### What changes
- `pain_intelligence.py`: add `_execute_pain_research(opp, anthropic_client)` — calls Claude API with WebSearch tool, returns populated `pain_validation_score`, `pain_evidence`, `pain_sources`
- `distribution_intelligence.py`: add `_execute_distribution_research(opp, anthropic_client)` — calls Claude API, returns `distribution_validated`, `distribution_channels_confirmed`, `distribution_risk_flags`
- `daily_run.py` steps 10-11: replace template-build calls with real execution calls (top 5 scored opps only)

### Guardrails
- Skip if `pain_researched_at` is within 7 days (avoid re-spending)
- Max 5 opps per run (~$0.75/day ceiling)
- Immutable: always `{**opp, **new_fields}` — never mutate in place
- Graceful degradation: if API fails, log error and continue with null fields (never crash the pipeline)

### Model
`claude-haiku-4-5-20251001` — already defined in `distribution_intelligence.py`, use same for pain

### Acceptance criteria
- `automation_runs.jsonl` entries show `pain_researched` and `distribution_researched` counts > 0
- Top 5 opps have non-null `pain_validation_score` after next daily run
- Cost logged per run in automation metadata

---

## Phase 2 — Wire into Scoring

### What changes
- `scoring_engine.py`: add two new optional dimensions
  - `pain_score`: maps `pain_validation_score` (0-10) directly, weight = 0.10 of final score, backward-compatible (absent = neutral 5.0)
  - `distribution_quality`: derived from `distribution_validated` bool + channel count, feeds existing `distribution_accessibility` dimension as a modifier
- Keep all existing dimension weights proportionally adjusted so sum = 1.0
- No breaking changes to existing callers

### Acceptance criteria
- An opp with `pain_validation_score=9` ranks higher than an identical opp with `pain_validation_score=3`
- An opp without `pain_validation_score` scores identically to current behavior
- `test_arch_02.py` pattern: two integration tests proving pain score moves final rank

---

## Phase 3 — Visibility + Safety Net

### What changes
- **Dashboard**: new `pain_distribution_panel()` in `dashboard.py` — per-opp expandable showing pain evidence, sources, distribution channels confirmed, risk flags
- **Tests**: `test_pain_intelligence.py` (unit + mock API), `test_distribution_intelligence.py` (unit + mock API)
- **CI**: `.github/workflows/tests.yml` — runs `pytest` on push to `feat/daily-opportunity-os`
- **File size fix**: split `daily_run.py` (currently 824 lines) — extract `_step_enrich_and_rank` into `pipelines/enrichment.py`

### Acceptance criteria
- `daily_run.py` < 800 lines
- pytest runs clean in CI (green badge)
- Dashboard shows pain/distribution data for opps that have been researched

---

## Data Flow (After All 3 Phases)

```
daily_run.py
  ├─ step 1-9: harvest + normalize + score (unchanged)
  ├─ step 10: _execute_pain_research(top_5) → pain_validation_score, pain_evidence
  ├─ step 11: _execute_distribution_research(top_5) → distribution_validated, channels
  ├─ step 12: re-score top_5 with research data → updated final_score
  └─ step 13: persist + notify
```

---

## What We Are NOT Doing

- No Vercel deployment (serverless timeout + no persistent filesystem + Streamlit incompatible)
- No background task queue (overkill for 5 opps/day)
- No LLM re-ranking (scoring formula is the source of truth)
- No schema migration (all new fields are optional extras on existing Opportunity model)

---

## File Budget

| File | Current | Target |
|------|---------|--------|
| `daily_run.py` | 824 lines | < 800 |
| `pain_intelligence.py` | 337 lines | ~420 (+execution fn) |
| `distribution_intelligence.py` | 570 lines | ~650 (+execution fn) |
| `scoring_engine.py` | 340 lines | ~380 (+2 dimensions) |
| `pipelines/enrichment.py` | does not exist | ~200 (extracted from daily_run) |

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| API cost blowup | Hard cap: 5 opps × 2 calls × ~$0.075 each = $0.75/day max |
| WebSearch latency > pipeline timeout | Async calls with 30s timeout, graceful fallback to null |
| Scoring regression | Integration tests before Phase 2 ships |
| File size creep | daily_run.py split is Phase 3 mandatory, not optional |
