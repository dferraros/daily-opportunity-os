---
phase: 02-taxonomy-competitive-benchmark
plan: 03
subsystem: research
tags: [competitive-benchmark, notifications, crypto, preference-center, trigger-families]

# Dependency graph
requires:
  - phase: 01-foundation-safety-architecture
    provides: 6 consent categories (CAT-SEC through CAT-PRO), frequency caps, suppression layers
provides:
  - 6-competitor benchmark matrix (Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo)
  - COPY/AVOID/INNOVATE recommendations mapped to trigger families A-F
  - Blue ocean gaps with MVP/V2/V3 timing
  - 14 documented anti-patterns with alternatives
affects: [03-trigger-table-mvp, playbook-section-trigger-taxonomy]

# Tech tracking
tech-stack:
  added: []
  patterns: [structured-benchmark-matrix, copy-avoid-innovate-framework, trigger-family-mapping]

key-files:
  created:
    - .planning/phases/02-taxonomy-competitive-benchmark/playbook-section-competitor-benchmark.md
  modified: []

key-decisions:
  - "Alert-to-action deep links should be MVP architectural decision, not V2"
  - "No artificial alert limits (avoiding Binance 50/10/90d anti-pattern)"
  - "Family B market triggers scoped to top 50-100 assets by volume to avoid noise"
  - "Bit2Me 6-category consent model is more granular than any competitor"

patterns-established:
  - "Per-competitor deep dive template: confidence, strengths, weaknesses, eligibility, limits, insight, sources"
  - "Recommendation tables with Trigger Family column for Phase 3 cross-referencing"

requirements-completed: [BENCH-01, BENCH-02, BENCH-03]

# Metrics
duration: 9min
completed: 2026-03-22
---

# Phase 02 Plan 03: Competitor Benchmark Summary

**6-competitor benchmark matrix with 16-row notification feature comparison, per-competitor deep dives, 6 blue ocean gaps, 14 anti-patterns, and COPY/AVOID/INNOVATE recommendations mapped to trigger families A-F**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-22T18:13:54Z
- **Completed:** 2026-03-22T18:22:41Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Comprehensive 6-competitor benchmark covering notification types, channels, preference centers, asset scope, eligibility rules, and alert limits
- 16-row notification feature matrix with Bit2Me current state and MVP/V2/V3 target columns
- Per-competitor deep dives with confidence levels, strengths (4-6 bullets), weaknesses (3-5 bullets), eligibility models, and key insights
- COPY (5 items), AVOID (4 items), INNOVATE (5 items) recommendation tables with Trigger Family mapping column
- 6 blue ocean gaps identified with complexity assessment and trigger family mapping
- 14 anti-patterns documented with source competitor, failure reason, and recommended alternative
- Competitive position summary showing Bit2Me behind on 14/16 features today but at parity or ahead on 10/16 at MVP

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the competitor benchmark playbook section** - `2dfaf36` (feat)

## Files Created/Modified
- `.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-competitor-benchmark.md` - Complete Section 8 of playbook: 6-competitor benchmark with structured matrices, deep dives, and actionable recommendations

## Decisions Made
- Alert-to-action deep links elevated from V2 to MVP architectural decision -- no competitor does this, and it is low complexity with high conversion impact
- No artificial alert limits -- explicitly avoiding Binance's 50 alert cap and 90-day expiry
- Family B market triggers scoped to top 50-100 assets by volume -- avoids Revolut's noise problem with microcap tokens
- Bit2Me's 6-category consent model confirmed as more granular than any competitor (Binance: 3 categories, others: fewer)

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None -- no external service configuration required.

## Next Phase Readiness
- Competitor benchmark ready for Phase 3 trigger prioritization
- COPY/AVOID/INNOVATE recommendations mapped to trigger families for direct Phase 3 cross-referencing
- Blue ocean gaps provide innovation backlog for V2/V3 planning
- Anti-patterns provide guardrails for trigger implementation decisions

---
*Phase: 02-taxonomy-competitive-benchmark*
*Completed: 2026-03-22*
