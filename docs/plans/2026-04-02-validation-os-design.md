# Validation OS — Design Doc

**Date:** 2026-04-02
**Status:** Approved
**Context:** Sits on top of the Opportunity OS scouting engine. Converts top-ranked opps into actionable validation packages.

---

## Problem

The Opportunity OS produces 64 scored opportunities but provides no bridge to market testing. High-scoring opps (7.0+) sit in a ranked list with no interview script, no pricing test, no landing page hypothesis, no outreach message. The system finds signals but stops before the most valuable step: contact with reality.

---

## Solution

A `validation_engine.py` module that takes a scored opportunity dict and produces an 8-section validation package. Pure template-driven (no LLM required). Triggered automatically in the daily pipeline for opps scoring ≥ 7.0 and manually via `opp-os validate <opp-id>` for full-depth packages.

---

## Architecture

### Module pattern
Follows `pain_intelligence.py` and `distribution_intelligence.py` exactly:
- Pure computation, zero I/O, zero side effects
- Input: `opp: dict` (not a Pydantic model)
- Output: dict with schema fields + `_`-prefixed helper keys
- `daily_run.py` Step 14 owns all file writes (same as Steps 12 and 13)
- `_validation_markdown: str` key carries the rendered output as a string

### Trigger conditions
Auto (Step 14, daily pipeline):
```python
validation_candidates = [
    o for o in all_opps_sorted
    if float(o.get("final_score", 0)) >= AUTO_VALIDATION_THRESHOLD  # default 7.0
    and not o.get("kill_decision")
    and o.get("stage") == "scout"
]
```
This guard prevents re-running on already-validated opps, on killed records, and on opps already in validation stage.

Manual (CLI):
```
opp-os validate <opp-id> [--dry-run]
```
Loads opp via `storage.get_opportunity_by_id(opp_id)`, runs full 8-section package, writes output, pushes to Notion.

---

## 8 Sections

| # | Section | Auto (≥7.0) | Manual full | Key schema fields used |
|---|---------|:-----------:|:-----------:|------------------------|
| 1 | Thesis brief + kill criteria | ✅ | ✅ | `name`, `problem_statement`, `why_now`, `portfolio_lane`, `decision_filter_results`, `final_score`, `*_reason` fields |
| 2 | Customer + pain snapshot | ✅ | ✅ | `target_customer`, `customer_pain_level`, `urgency_of_need`, `frequency_of_need`, `exact_customer_phrases`, `workarounds_found`, `pain_severity_reason` |
| 3 | 5 interview questions (open-ended, past-focused) | ✅ | ✅ | `target_customer`, `problem_statement`, `vertical`, `geography`, `demand_signals` |
| 4 | 3 falsifiable assumptions + kill criteria | ✅ | ✅ | `decision_filter_results` (can_sell_fast, can_build_lean, can_compound), `assumptions`, `risks` |
| 5 | Pricing test — 3 EUR options | ✅ | ✅ | `first_revenue_path.first_price_point`, `willingness_to_pay`, `geography`, `pricing_benchmark` |
| 6 | Landing page hypothesis (headline + CTA + conversion target) | ✅ | ✅ | `problem_statement`, `target_customer`, `exact_customer_phrases`, `why_now` |
| 7 | Outreach script (imports `TRUST_MECHANISMS_BY_GEO`) | ✅ | ✅ | `distribution_profile`, `first_revenue_path.first_sales_channel`, `trust_profile`, `geography` |
| 8 | MVP scope + 7-day sprint | — | ✅ | `time_to_mvp`, `speed_to_mvp`, `capital_intensity`, `first_revenue_path.first_proof_point_needed`, `ai_leverage` |

**Spec alignment note:** Sections 3/5 match `validation-runner/SKILL.md` exactly (5 questions, 3 price points). Section 6 absorbs the skill's "Landing Page Test Hypothesis" step. Section 8 is a new extension beyond the skill scope.

---

## Output

### File
`reports/validation/YYYY-MM-DD-{opp-id}-validation.md`

`reports/validation/` must be added to `ensure_report_dirs()` in `reports.py`.

### Notion
One page created in the Deep Dives database (`e8079401-811e-4e9b-a43a-234bc03cce7b`). Requires:
- New constant `DEEP_DIVES_PAGE_ID` in `notion_sync.py`
- New function `build_validation_properties(opp, package) -> dict`
- Validation packages appended to `{date}-notion-sync.json` under a new `validation_packages` key (no second file format)

### Stage transition (atomic)
When a validation package is generated, the opp record is updated atomically:
```python
opp["stage"] = "validation"
opp["validation_status"] = "in_progress"
opp["validation_start_date"] = date
opp["validation_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
```
This re-persist happens inside the existing Step 12 JSONL save block, not as a separate write.

---

## Files Touched

| File | Change |
|------|--------|
| `src/opportunity_os/validation_engine.py` | **CREATE** — core module |
| `src/opportunity_os/pipelines/validation_run.py` | **CREATE** — manual pipeline |
| `src/opportunity_os/pipelines/daily_run.py` | **MODIFY** — add Step 14 after line 224 |
| `src/opportunity_os/main.py` | **MODIFY** — add `validate` command |
| `src/opportunity_os/notion_sync.py` | **MODIFY** — add Deep Dives constants + `build_validation_properties()` |
| `src/opportunity_os/reports.py` | **MODIFY** — add `reports/validation/` to `ensure_report_dirs()` |
| `config/scoring_weights.yaml` | **MODIFY** — add `thresholds.auto_validation: 7.0` |
| `.claude/skills/validation-runner/SKILL.md` | **MODIFY** — reference `validation_engine.py`, add section 8 |
| `tests/test_validation_engine.py` | **CREATE** — unit tests |

---

## Config

```yaml
# config/scoring_weights.yaml — new section
thresholds:
  auto_validation: 7.0   # opps scoring >= this are auto-promoted to validation in daily Step 14
```

---

## Key Design Decisions

1. **Template-driven, not LLM** — all 64 opps have enough populated fields (problem_statement, target_customer, *_reason fields, decision_filter_results) to produce high-quality structured output without API calls. LLM enrichment added later as optional upgrade.

2. **No I/O inside validation_engine.py** — the module returns a dict. Step 14 (daily_run.py) and validation_run.py own file writes. This is the established contract in pain_intelligence.py and distribution_intelligence.py.

3. **Single JSON sync file** — validation packages append to the existing `{date}-notion-sync.json` under `validation_packages` key. No second file format. Claude Code reads one file and executes all Notion MCP calls in one pass.

4. **Auto trigger guard = stage == "scout"** — prevents re-running on in-progress or completed validations. Stage promotion to "validation" is atomic with the Step 12 JSONL re-persist.

5. **5 questions, not 10** — matches validation-runner SKILL.md quality gate. 10 questions creates review fatigue. 5 past-focused, open-ended questions is the industry benchmark for early customer discovery interviews.
