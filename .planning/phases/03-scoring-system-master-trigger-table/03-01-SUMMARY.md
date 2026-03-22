---
phase: 03-scoring-system-master-trigger-table
plan: 01
subsystem: scoring
tags: [bigquery, scoring-formulas, notification-engine, fatigue, churn, cross-sell]

# Dependency graph
requires:
  - phase: 01-foundation-safety-architecture
    provides: fatigue risk formula (Section 2.5), frequency caps (Section 2.2), priority tiers (P0-P5)
  - phase: 02-taxonomy-competitive-benchmark
    provides: 6 trigger families with properties, compliance classes, asset tiers
provides:
  - 8 scoring formula definitions (SCORE-01 to SCORE-08) with BigQuery pseudocode
  - Send Score Final gated architecture (3 gates + weighted composite)
  - Family-specific score overrides (Family D lifecycle_urgency, Family E cross_sell_eligibility)
  - Validation script for all 16 Phase 3 requirement IDs
affects: [03-02 master-trigger-table, 03-03 mvp-selection-channel-policy, 04 measurement]

# Tech tracking
tech-stack:
  added: []
  patterns: [gated-scoring-architecture, composable-bigquery-views, normalized-0-1-scores]

key-files:
  created:
    - .planning/phases/03-scoring-system-master-trigger-table/playbook-section-scoring-formulas.md
    - .planning/phases/03-scoring-system-master-trigger-table/validate_phase3.py
  modified: []

key-decisions:
  - "Send Score Final uses 3 binary gates (compliance, fatigue, cooldown) before weighted score -- gates are pass/fail, score only ranks"
  - "Family A and F always send (score=1.0), gated by cooldown/compliance only"
  - "Family E replaces trigger_opportunity with cross_sell_eligibility in weighted score"
  - "Family D replaces user_asset_affinity with lifecycle_urgency (CASE on lifecycle stage)"
  - "Send score weights: trigger_opportunity 0.35, user_asset_affinity 0.25, (1-pressure) 0.20, (1-fatigue) 0.10, churn_boost 0.10"
  - "Churn risk is a BOOST (high churn = more reason to send lifecycle triggers), not a penalty"

patterns-established:
  - "Gated scoring: binary gates checked BEFORE weighted score computation"
  - "Composable views: each score is an independent BigQuery view joined by Send Score Final"
  - "0-1 normalization: LEAST(1.0, GREATEST(0.0, ...)) on every formula output"

requirements-completed: [SCORE-01, SCORE-02, SCORE-03, SCORE-04, SCORE-05, SCORE-06, SCORE-07, SCORE-08]

# Metrics
duration: 9min
completed: 2026-03-22
---

# Phase 3 Plan 01: Scoring Formulas Summary

**8 scoring formulas with BigQuery pseudocode and gated Send Score Final architecture (3 binary gates + weighted composite with family-specific overrides)**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-22T19:16:42Z
- **Completed:** 2026-03-22T19:25:21Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- All 8 scoring formulas documented with concrete inputs, weights, normalizers, thresholds, and BigQuery SQL pseudocode
- Send Score Final implements gated architecture: compliance gate (binary) -> fatigue gate (threshold) -> cooldown gate (temporal) -> weighted composite score
- Validation script checks all 16 Phase 3 requirement IDs across 4 output files, reports PASS for SCORE-01 through SCORE-08
- Family-specific overrides documented (Family A/F always send, Family D uses lifecycle_urgency, Family E uses cross_sell_eligibility)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create validation script for Phase 3** - `fcc1df2` (feat)
2. **Task 2: Write Scoring Formulas playbook section** - `f7ebc15` (feat)

## Files Created/Modified

- `.planning/phases/03-scoring-system-master-trigger-table/validate_phase3.py` - Validation script checking all 16 Phase 3 requirement IDs
- `.planning/phases/03-scoring-system-master-trigger-table/playbook-section-scoring-formulas.md` - Playbook Section 10: Scoring System Architecture with 8 formulas

## Decisions Made

- Send Score Final uses gated architecture (3 binary gates before weighted score) rather than single composite score -- prevents compliance violations from being overridden by high opportunity scores
- Family A (User Configured) and F (Risk & Protective) always send with score=1.0 -- user safety and user-requested alerts bypass scoring
- Churn risk used as BOOST in Send Score Final (high churn = more reason to send lifecycle triggers) rather than penalty
- SCORE-05 Fatigue Risk formula reproduced unchanged from Phase 1 Section 2.5 -- consistency with production design

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed validation script section extraction**
- **Found during:** Task 2 verification
- **Issue:** Section content extraction started 1 character after heading instead of after the heading line, causing it to re-match the same heading and return empty section content
- **Fix:** Changed `rest = scoring_content[section_start + 1:]` to skip to end of heading line using `scoring_content.index("\n", section_start) + 1`
- **Files modified:** validate_phase3.py
- **Verification:** All 8 SCORE checks now pass
- **Committed in:** f7ebc15 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Bug fix necessary for validation to work correctly. No scope creep.

## Issues Encountered

None beyond the validation script bug fixed above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Scoring formulas ready for reference by Plan 03-02 (Master Trigger Table) and Plan 03-03 (MVP Selection + Channel Policy)
- Validation script ready to verify all remaining Phase 3 deliverables
- TRIG-01 through TRIG-04 and CHAN-01 through CHAN-04 checks report NOT_YET_CREATED (awaiting Plans 03-02, 03-03)

---
*Phase: 03-scoring-system-master-trigger-table*
*Completed: 2026-03-22*
