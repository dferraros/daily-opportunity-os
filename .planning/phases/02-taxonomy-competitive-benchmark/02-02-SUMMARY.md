---
phase: 02-taxonomy-competitive-benchmark
plan: 02
subsystem: documentation
tags: [asset-classification, product-eligibility, trigger-scope, bigquery, crypto-assets]

# Dependency graph
requires:
  - phase: 01-foundation-safety-architecture
    provides: Consent categories (CAT-SEC through CAT-PRO) and priority tiers (P0-P5)
provides:
  - 4-tier asset classification system (T1 Major, T2 Stablecoin, T3 Mid-cap, T4 Micro-cap)
  - Product-asset eligibility matrix for all 11 Bit2Me products
  - Trigger-family asset scope rules (Families A-F) with BigQuery pseudocode
  - Asset scope governance framework (dynamic views, volume thresholds, de-peg monitoring)
affects: [02-01-trigger-taxonomy, 03-scoring-system, 03-master-trigger-table]

# Tech tracking
tech-stack:
  added: []
  patterns: [dynamic-bigquery-views-not-hardcoded-lists, 3-layer-asset-scope-model, quarterly-tier-review]

key-files:
  created:
    - .planning/phases/02-taxonomy-competitive-benchmark/playbook-section-asset-universe.md
  modified: []

key-decisions:
  - "Asset tier classification uses trailing 30-day median daily volume on Bit2Me, not external market cap alone"
  - "Stablecoins always T2 regardless of volume (classification by function, not volume)"
  - "All asset scope references must be dynamic (BigQuery views) -- never hard-coded asset lists"
  - "Stablecoin de-peg monitoring classified as CAT-SEC P0 (no consent required, contractual necessity)"
  - "New listings default to T4 with 30-day promotion evaluation"

patterns-established:
  - "Layer 1/2/3 asset scope model: Layer 1 = all listed, Layer 2 = product-specific, Layer 3 = per-user"
  - "Dynamic BigQuery views (asset_classification + asset_product_eligibility) as canonical asset scope source"

requirements-completed: [TAX-08]

# Metrics
duration: 5min
completed: 2026-03-22
---

# Phase 2 Plan 02: Asset Universe Mapping Summary

**4-tier asset classification (T1-T4) with product eligibility matrix for 11 Bit2Me products and trigger-family scope rules referencing BigQuery views**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-22T18:14:11Z
- **Completed:** 2026-03-22T18:19:34Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Defined 4 asset classification tiers (T1 Major, T2 Stablecoin, T3 Mid-cap/Long-tail, T4 Micro-cap/Memecoin) with notification behavior per tier
- Mapped all 11 Bit2Me products (Wallet, Brokerage, Pro, Earn, Card, Loan, Launchpad, Space Center, Pay, Wealth, API) to eligible asset subsets
- Specified trigger-family asset scope rules for all 6 families (A-F) with BigQuery WHERE clause pseudocode
- Documented asset scope governance: dynamic views, volume threshold maintenance, stablecoin de-peg monitoring, new listing/delisting processes
- Added cross-references to Section 6 (Trigger Taxonomy), Phase 3 (Master Trigger Table), and Phase 1 constructs
- Included Appendix 7B with 5 high-value cross-sell asset patterns for Family E triggers

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the asset universe mapping playbook section** - `1bd32ad` (feat)

## Files Created/Modified
- `.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-asset-universe.md` - Complete asset universe mapping (Section 7) with classification tiers, product eligibility matrix, trigger scope rules, and governance

## Decisions Made
- Asset tiers use trailing 30-day median daily volume on Bit2Me rather than external market cap -- ensures classification reflects actual platform activity
- Stablecoins always classified as T2 regardless of volume -- classification by function, not trading volume
- All asset scope references must be dynamic BigQuery views -- hard-coded lists are unmaintainable with 420+ assets
- Stablecoin de-peg alerts classified as CAT-SEC P0 (no consent required) -- protecting user assets is contractual necessity
- New listings default to T4 with automatic tier promotion evaluation after 30 days of trading data

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Asset universe mapping is ready for Phase 3 Master Trigger Table (each trigger row can now reference asset_scope)
- Section 7 cross-references Section 6 (Trigger Taxonomy) -- both can proceed in parallel within Phase 2
- BigQuery view schemas (asset_classification, asset_product_eligibility) are documented and ready for Alvaro to implement

---
*Phase: 02-taxonomy-competitive-benchmark*
*Completed: 2026-03-22*
