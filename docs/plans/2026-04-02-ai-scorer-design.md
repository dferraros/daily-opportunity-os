# Design: AI Dimension Scorer
## Date: 2026-04-02

---

## Goal

Replace the regex heuristic `estimate_dimensions()` in the daily pipeline with an AI-powered step that uses Claude to produce calibrated 1-10 scores for all 16 opportunity dimensions, with one-line reasoning per dimension stored in the record.

**Expected outcome:** Score range expands from 5.1–6.6 (heuristic) to ~3.0–9.5 (AI judgment). `now` lane (≥7.5) becomes populated with real daily signals.

---

## Architecture

### New Module: `src/opportunity_os/ai_scorer.py`

**Public API:**
```python
def score_dimensions_with_ai(opp: dict) -> dict:
    """
    Score an opportunity on 16 dimensions using Claude.
    Returns the opp dict with dimension fields + _reason fields populated.
    Falls back to heuristic estimator if API call fails.
    """
```

**Model:** `claude-haiku-4-5-20251001`
- Structured JSON tasks are its sweet spot
- ~$0.001 per opportunity (35 opps = ~$0.035/day)
- Fast enough to run inline in the daily pipeline (~1-2s per call)

**Caching:**
- Check `ai_scored_at` field before calling API
- Skip if already scored and `rescore_requested != True`
- New fields: `ai_scored_at` (ISO date string), `ai_scorer_version` (model ID)

**Fallback:**
- If API call fails, times out, or returns unparseable JSON → fall back to heuristic estimator silently
- Log `ai_scored_at: null` so the record is identifiable as heuristic-scored

---

## Prompt Design

```
SYSTEM:
You are a business opportunity scoring analyst. Score the opportunity below on 16 dimensions using the rubrics provided. Return ONLY a valid JSON object — no prose, no markdown.

USER:
Geography: {geography} | Vertical: {vertical} | Bucket: {bucket}
Name: {name}
Problem: {problem_statement}
Signal: {trigger_signal}
Notes: {raw_notes}

Score each of the 16 dimensions from 1-10 using these rubrics:

[full rubric text for all 16 dimensions from docs/scoring-criteria.md]

Return JSON with this exact structure:
{
  "pain_severity": <int 1-10>,
  "pain_severity_reason": "<one sentence>",
  "market_size": <int 1-10>,
  "market_size_reason": "<one sentence>",
  ... (all 16 dimensions + reasons)
}
```

**Key prompt rules:**
- Rubric text is injected verbatim from `docs/scoring-criteria.md` so scoring stays synchronized with the documented criteria
- Venezuela/LATAM geographic adjustments are mentioned in the system prompt (WTP 0.25x baseline, informal commerce 55%, etc.)
- Model is instructed: "Do not cluster scores around 5-6. Use the full 1-10 range. A score of 9-10 means exceptional; 1-2 means near-fatal flaw."

---

## Fields Added to Opportunity Records

```python
# New optional fields in models.py
ai_scored_at: Optional[str] = None          # ISO date, e.g. "2026-04-02"
ai_scorer_version: Optional[str] = None     # model ID used

# Per-dimension reason fields (16 total)
pain_severity_reason: Optional[str] = None
market_size_reason: Optional[str] = None
timing_tailwind_reason: Optional[str] = None
willingness_to_pay_reason: Optional[str] = None
monetization_clarity_reason: Optional[str] = None
speed_to_mvp_reason: Optional[str] = None
capital_efficiency_reason: Optional[str] = None
distribution_accessibility_reason: Optional[str] = None
competition_intensity_reason: Optional[str] = None
defensibility_reason: Optional[str] = None
regional_fit_reason: Optional[str] = None
founder_fit_reason: Optional[str] = None
ai_leverage_reason: Optional[str] = None
operational_simplicity_reason: Optional[str] = None
regulatory_simplicity_reason: Optional[str] = None
path_to_first_revenue_reason: Optional[str] = None
```

---

## Pipeline Integration

`src/opportunity_os/pipelines/daily_run.py` — insert Step 2.5:

```
Step 1:   Load raw signals from data/raw/YYYY-MM-DD-signals.jsonl
Step 2:   Normalize → Opportunity objects (normalization.py)
Step 2.5: AI dimension scoring (ai_scorer.py) ← NEW
Step 3:   Dedupe against existing opportunities
Step 4:   Kill gate (engines/kill_gate.py)
Step 5:   Score surviving opportunities (engines/scoring_engine.py)
Step 6:   Geo adjustments (geo_lens.py)
Step 7:   Portfolio lane assignment (filters.py)
Step 8:   Persist to opportunities.jsonl
Step 9:   Render and write reports (global, LATAM, Venezuela)
Step 10:  Export Notion CSVs
```

The scoring engine (Step 5) reads the numeric dimension fields that Step 2.5 populates. No changes to `scoring_engine.py` itself.

---

## Backfill Plan

After wiring, run a one-shot backfill on the 35 real signals already in `opportunities.jsonl`:
1. Read all records where `geography != "sample"` and `ai_scored_at` is null
2. Run `score_dimensions_with_ai()` on each
3. Overwrite the JSONL with updated records
4. Re-run the scoring engine on all updated records
5. Rebuild reports from the new scores

**Expected result:** The 3 top VE opportunities move from ~7.82 (heuristic-inflated) to their true score. Some global signals likely drop to 3-4 range. The `now` lane gets 2-5 real candidates.

---

## Files Changed

| File | Change |
|------|--------|
| `src/opportunity_os/ai_scorer.py` | NEW — AI scoring module |
| `src/opportunity_os/models.py` | ADD 18 optional fields (ai_scored_at, ai_scorer_version, 16 _reason fields) |
| `src/opportunity_os/pipelines/daily_run.py` | ADD Step 2.5 |
| `.env.example` | ADD `ANTHROPIC_API_KEY=` |
| `data/opportunities/opportunities.jsonl` | BACKFILL 35 records with AI scores |

---

## Success Criteria

1. `ai_scored_at` populated on all 35 real-signal records after backfill
2. Score range is 3.0–9.5 (not clustered at 5-6)
3. At least 1 opportunity in `now` lane (final_score ≥ 7.5)
4. Each opportunity record has all 16 `*_reason` fields populated
5. Pipeline runs `daily --date 2026-04-02` without errors from ai_scorer step
6. Fallback works: if `ANTHROPIC_API_KEY` missing, heuristic runs silently

---

*Design v1.0 — 2026-04-02 — daily-opportunity-os*
