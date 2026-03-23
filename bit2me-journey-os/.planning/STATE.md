# J02 Journey System — STATE

## Current Position
Phase 01 executing. Wave 1 in progress.
- 01-01: DONE (j02-research.md)
- 01-02: DONE (j02-hub-spain.md) — commit 32500e5
- 01-03: DONE (j02-spokes-01-05.md) — commit b2956c0
- 01-04: pending
- 01-05: DONE (j02-recovery-loyalty.md) — commit b05c28f
- 01-06 through 01-08: pending

## Project: bit2me-journey-os
- Folder: C:/Users/ferra/OneDrive/Desktop/bit2me-journey-os/
- Output folder: docs/plans/
- Git: initialized, commits active

## Architecture Decisions
1. Hub + Spokes (NOT linear journey with branches)
2. B2C Spain/EU separate from B2C LatAm — different copy, channel, timing
3. B2B is a separate architecture (J05), not a spoke
4. Frequency cap: max 2 emails/week, max 2 push/week per user
5. Hub pauses when Spoke is active (no double messaging)
6. Holdout: 10% global control group (Welch t-test)
7. Diego approval by LAYER (not by individual message — batch efficiency)
8. WhatsApp is PRIMARY channel in LatAm (replaces push in S1/S4)
9. B2B tone: ROI/treasury, never emotional, longer sales cycle
10. A/B test priority: SP-01 Earn first (biggest segment, loss framing vs gain)

## Segmentation from Excel Data
- 5,182 FM users analyzed (Jan-Mar 2026)
- Non-converters: 1,333 (25.7%)
- Tipo A (warm, <30d): 491 users
- Tipo B (cold, 31-60d): 547 users — HIGHEST PRIORITY, lanzable esta semana
- Tipo C (frozen, 60+d): 295 users — goes to FOMO Agent pool
- D+0 conversions: 39.6% same-day (invalidates 24h-wait architecture)

## Key Blockers
- price_change_pct_24h event: Alvaro P0 — S1 and S4 use neutral copy without it
- Diego copy approval: batch by layer to speed up
- Katy onboarding to Journey OS: blocking CleverTap setup

## Output Files Being Built
- docs/plans/2026-03-23-j02-research.md (01-01) [DONE]
- docs/plans/2026-03-23-j02-hub-spain.md (01-02) [DONE — commit 32500e5]
- docs/plans/2026-03-23-j02-spokes-01-05.md (01-03) [DONE — commit b2956c0]
- docs/plans/2026-03-23-j02-latam.md (01-04) [pending]
- docs/plans/2026-03-23-j02-recovery-loyalty.md (01-05) [DONE — commit b05c28f]
- docs/plans/2026-03-23-j05-b2b.md (01-06) [pending]
- docs/plans/2026-03-23-j02-diagram-jira.md (01-07) [pending]
- docs/plans/2026-03-23-J02_MASTER.docx (01-08) [pending]

## Decisions from 01-02 (Hub J02-CORE)
- Hub ends at D+7 (6 touchpoints). Recovery handles D+30+.
- price_change_pct_24h required for dynamic push copy. Fallback: NEUTRAL confirmed.
- Only S3 email needs MiCA footer (not In-App/Push).
- Diego batch approval table: 17 variants, ready for one-session review.
- A/B sizes: S0=500, S0.5=400, S1=600, S2=400, S3=300x3.

## Decisions from 01-03 (Spokes SP-01 to SP-05)
- SP-01 Earn A/B (loss vs gain) is THE most important test in the system
- SP-05 Referidos MUST NEVER trigger before 2nd purchase confirmed — behavioral economics rule
- Spoke priority: SP-01 > SP-02 > SP-03 > SP-04 > SP-05 (by monetary impact)
- Implementation order: SP-01 first (EUR 19.5M AUC), SP-05 second (no new BigQuery events needed)
- BigQuery P0 fields for Alvaro: balance_idle_days, earn_product_active, second_purchase_confirmed

## Decisions from 01-01 (Research Benchmarks)
- S0.5 price alert validated by Binance 4.1x conversion data — implement with fallback until Alvaro delivers price_change_pct_24h
- Push scheduling: 20:30 CET Spain (not fixed T+24h) — OneSignal/Braze peak data validated
- WhatsApp PRIMARY LatAm: 4.3x open rate vs push (Bnext), Venezuela 92% penetration
- Earn copy: endowment framing ("Tu BTC trabajando para ti") not yield — Coinbase/Binance validated
- SP-02 Pro trigger: cumulative fee spend threshold — Kraken fee-savings framing +31% conversion
- Tipo A/B/C validated by Klaviyo/Braze win-back data (22%/13%/7.5%)

## Decisions from 01-05 (Recovery + Loyalty)
- Tipo C (295 users) routes to FOMO Agent pool — no automated journey (unsubscribe risk + low conversion ROI)
- Tipo B manual launch this week: Marta BigQuery export + Katy CleverTap one-off (no journey setup)
- J02.5 Loyalty entry at D+45 post second_purchase_confirmed, 3 touchpoints D+45/D+60/D+90
- Diego batch approval: 12 messages all Tier 1, single-batch recommended (48h SLA)
- first_purchase_price_eur + current_price_eur are P0 blockers for Tipo B launch (coordinate Marta/Alvaro)

## Last session
2026-03-23 — completed 01-01 research benchmarks (ff5ddc8) + 01-02 Hub Spain (32500e5) + 01-03 Spokes SP-01-05 (b2956c0) + 01-05 Recovery+Loyalty (b05c28f)
