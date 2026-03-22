---
phase: 03-scoring-system-master-trigger-table
plan: 02
subsystem: strategy
tags: [triggers, notification-table, mvp-selection, deep-links, compliance]

# Dependency graph
requires:
  - phase: 02-taxonomy-competitive-benchmark
    provides: "24 trigger definitions across 6 families, asset universe mapping, compliance framework"
provides:
  - "Master trigger table with 33 triggers x 14 columns"
  - "Top 10 MVP triggers scored with Impact x Risk x Complexity framework"
  - "Compact reference table + detailed vertical specifications"
  - "9 new triggers beyond Phase 2 taxonomy (A-05, B-05, C-05, D-05, D-06, E-05, E-06, F-05, F-06)"
affects: [03-03-PLAN, phase-4-measurement, mvp-implementation]

# Tech tracking
tech-stack:
  added: []
  patterns: ["14-column trigger specification pattern", "compact reference + detailed vertical spec layout", "MVP scoring formula: Impact*2 + (5-Risk)*1.5 + (5-Complexity)*1"]

key-files:
  created:
    - ".planning/phases/03-scoring-system-master-trigger-table/playbook-section-master-trigger-table.md"
  modified: []

key-decisions:
  - "33 triggers total (9 new beyond Phase 2's 24): A-05 Portfolio Milestone, B-05 New Listing, C-05 KYC Started, D-05 Pre-Dormancy, D-06 Reactivation Success, E-05 Card Activation, E-06 Pay Discovery, F-05 Login New Device, F-06 Withdrawal Confirmation"
  - "MVP top 10 sorted by score: A-01(20), A-02(20), A-03(19), F-01(19), D-02(17), F-04(17), B-01(16.5), D-01(16), C-01(14), B-04(13.5)"
  - "Split table into compact reference (8 cols) + detailed vertical specs (14 cols) for readability at 33 rows"
  - "F-04 from taxonomy (Unusual Login) renamed to F-05 in master table to avoid collision with F-04 Stablecoin De-Peg"

patterns-established:
  - "Trigger specification: vertical key-value format with all 14 columns for detailed specs"
  - "MVP scoring: 3-dimension framework (Impact, Risk, Implementation Complexity) with weighted formula"
  - "MVP implementation waves: Family A first (zero compliance), then Family F (protective), then D/B (Diego approval), then C (SDK changes)"

requirements-completed: [TRIG-01, TRIG-02, TRIG-03]

# Metrics
duration: 11min
completed: 2026-03-22
---

# Phase 3 Plan 02: Master Trigger Table Summary

**33 triggers x 14 columns with top 10 MVP scored by Impact/Risk/Complexity, 9 new triggers added, every trigger with bit2me:// deep link**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-22T19:14:49Z
- **Completed:** 2026-03-22T19:25:23Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Master trigger table with 33 fully specified triggers across all 6 families (A=5, B=5, C=5, D=6, E=6, F=6)
- 9 new triggers added to fill taxonomy gaps: KYC drop-off recovery (C-05), pre-dormancy warning (D-05), reactivation celebration (D-06), new listing announcement (B-05), portfolio milestone (A-05), Card/Pay cross-sell (E-05/E-06), new device login (F-05), withdrawal confirmation (F-06)
- Top 10 MVP triggers scored and sequenced into 4 implementation waves (30-day timeline)
- Every trigger has a deep_link value (Bit2Me MVP differentiator vs all 6 competitors)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write Master Trigger Table playbook section** - `da7a1ab` (feat)

## Files Created/Modified
- `.planning/phases/03-scoring-system-master-trigger-table/playbook-section-master-trigger-table.md` - Complete master trigger table (Section 11) with schema, compact reference, detailed specs, MVP scoring

## Decisions Made
- Added 9 new triggers to reach 33 total, filling gaps identified during taxonomy review (KYC drop-off at 32% is biggest onboarding gap, Pre-Dormancy targets L3 Near-Dormant highest revenue velocity segment)
- Renamed F-04 "Unusual Login Activity" from Section 6 taxonomy to F-05 in master table to avoid ID collision with F-04 "Stablecoin De-Peg" which was already established in Phase 2
- Split table into compact reference (8 columns for quick scan) + detailed vertical specs (14 columns for implementation) because 33 rows x 14 columns is unreadable in a single Markdown table
- MVP Wave 1 starts with Family A (zero regulatory risk, TRANSACTIONAL class) to prove pipeline before adding MARKETING-class triggers requiring Diego approval

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Master trigger table ready for Phase 3 Plan 03 (MVP Selection "NOT to launch" + Channel Policy)
- All 33 triggers can be referenced by Section 10 scoring formulas (Phase 3 Plan 01)
- Top 10 MVP triggers provide implementation priority for Phase 4 roadmap

## Self-Check: PASSED

- FOUND: playbook-section-master-trigger-table.md
- FOUND: 03-02-SUMMARY.md
- FOUND: commit da7a1ab
- TRIG-01: PASS (33 triggers, need 30+)
- TRIG-02: PASS (14/14 columns)
- TRIG-03: PASS (20 MVP markers, need 10)
- All 6 families (A-F): PASS
- Deep links: 77 occurrences
- C8_Whale_Suppression: 29 references

---
*Phase: 03-scoring-system-master-trigger-table*
*Completed: 2026-03-22*
