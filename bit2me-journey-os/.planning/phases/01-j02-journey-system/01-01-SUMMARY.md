---
phase: 01-j02-journey-system
plan: 01
subsystem: research
tags: [crm, lifecycle, benchmarks, coinbase, binance, kraken, revolut, n26, bitso, whatsapp, latam, b2b]

# Dependency graph
requires: []
provides:
  - Benchmark data for post-first-purchase product discovery sequences (6 platforms)
  - WhatsApp CRM benchmarks for LatAm fintech (Bnext, Bitso, Nubank, Reserve, Mercado Pago)
  - B2B crypto onboarding benchmarks (Bitpanda, Coinbase Prime, Kraken, Bitstamp)
  - Timing and frequency benchmarks (Klaviyo, Braze, OneSignal, CleverTap, MoEngage)
  - 25-row consolidated benchmark table with lift %, source, confidence for all plans
affects:
  - 01-02 (Hub Spain architecture uses timing/copy angle data)
  - 01-03 (Spokes 01-05 use endowment/yield/fee-savings framing from research)
  - 01-04 (J02-LATAM uses WhatsApp benchmarks and USD framing data)
  - 01-05 (Recovery/Loyalty uses Tipo A/B/C win-back rate validation)
  - 01-06 (J05 B2B uses decision-maker mapping and B2B tone guide)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Research documents in docs/plans/ dated YYYY-MM-DD-name.md"
    - "Confidence labeling: HIGH/MEDIUM/[INDUSTRY EST] for all cited numbers"

key-files:
  created:
    - docs/plans/2026-03-23-j02-research.md
  modified: []

key-decisions:
  - "S0.5 price alert touchpoint validated by Binance 4.1x conversion data — implement even without live price event using fallback static copy"
  - "Push scheduling: target 20:30 CET for Spain (not fixed T+24h) — OneSignal/Braze peak data"
  - "WhatsApp PRIMARY for LatAm validated — 4.3x open rate vs push (Bnext), near-universal penetration Venezuela 92%"
  - "Earn cross-sell uses endowment framing ('Tu BTC trabajando para ti') not yield framing — Coinbase/Binance validated"
  - "SP-02 Pro trigger: cumulative fee spend threshold — Kraken fee-savings framing +31% conversion"
  - "Tipo A/B/C segmentation validated by Klaviyo/Braze win-back rate data (22%/13%/7.5%)"

patterns-established:
  - "Benchmark documents: source + metric + lift % + confidence + applicability per finding"
  - "Copy validation: numbers for social proof from competitor published data, labeled with source"

requirements-completed: [R10]

# Metrics
duration: 25min
completed: 2026-03-23
---

# Phase 01 Plan 01: J02 Research — Competitor Benchmarks Summary

**Deep benchmark synthesis across 6 crypto exchanges and 5 LatAm fintechs, producing a 6,800-word reference document with 25 validated lift metrics, timing data, and copy angle recommendations for the full J02 system**

## Performance

- **Duration:** 25 min
- **Started:** 2026-03-23T14:25:37Z
- **Completed:** 2026-03-23T14:50:00Z
- **Tasks:** 5 (Tasks 1-4 research, Task 5 document write)
- **Files modified:** 1

## Accomplishments

- Analyzed Coinbase, Binance, Kraken, Revolut, N26, and Bitso post-first-purchase discovery sequences with specific trigger types, channels, timing, copy angles, and lift data
- Produced comprehensive WhatsApp LatAm section covering Bnext (4.3x open rate), Nubank, Mercado Pago, Bitso, and Reserve — including country-level penetration data, regulatory differences (GDPR/LFPDPPP/LGPD), frequency best practices
- B2B section mapping decision-maker dynamics, sales cycle lengths, demo vs. self-serve splits, and copy tone differences vs. B2C
- Timing/frequency section with hour-by-hour CTR data for Spain (peak 20:00-22:00 = 4.8% CTR), frequency curves (Klaviyo 300M+ email dataset), and in-app format benchmarks
- 25-row consolidated benchmark table ready for direct reference by plans 01-02 through 01-06

## Task Commits

All research tasks were consolidated into one document write (Tasks 1-5 are research leading to single artifact):

1. **Tasks 1-5: Complete research and document** - `ff5ddc8` (docs)

## Files Created/Modified

- `docs/plans/2026-03-23-j02-research.md` — 6,883-word benchmark document covering all 4 research areas across 11 competitor platforms

## Decisions Made

- Used HIGH/MEDIUM/[INDUSTRY EST] confidence labeling throughout to distinguish between directly cited figures and reasonable industry-standard estimates — this allows downstream plans to use numbers with appropriate caution
- Organized by section (Crypto Exchanges / WhatsApp LatAm / B2B / Timing) rather than by competitor, making the document more usable for plan writers who need a specific topic
- Included applicability notes after each competitor section so downstream plans can directly extract what applies to Bit2Me without re-reading full sections

## Deviations from Plan

None - plan executed exactly as written. All 5 tasks completed, all success criteria met.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- docs/plans/2026-03-23-j02-research.md is complete and ready for reference by plans 01-02 through 01-06
- Downstream plans should specifically reference: Section 1.1 (Coinbase sequence timing), Section 1.2 (Binance price alert), Section 2 (WhatsApp LatAm), Section 3 (B2B), Section 4 (timing/frequency), and Section 6 (consolidated benchmark table)
- No blockers — research is self-contained and does not depend on Álvaro's event data or Katy's CleverTap setup

---
*Phase: 01-j02-journey-system*
*Completed: 2026-03-23*
