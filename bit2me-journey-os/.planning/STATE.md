# J02 Journey System — STATE

## Current Position
Phase 01 executing. Wave 1 in progress.
- 01-01: DONE (j02-research.md)
- 01-02: DONE (j02-hub-spain.md) — commit 32500e5
- 01-03: DONE (j02-spokes-01-05.md) — commit b2956c0
- 01-04: DONE (j02-latam.md) — commit ff1d7b8
- 01-05: DONE (j02-recovery-loyalty.md) — commit b05c28f
- 01-06: DONE (j05-b2b.md) — commit a04c828
- 01-07: DONE (j02-diagram.mmd + j02-jira-tickets.md) — commit 8ee3cbc
- 01-08: pending

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
- docs/plans/2026-03-23-j02-latam.md (01-04) [DONE — commit ff1d7b8]
- docs/plans/2026-03-23-j02-recovery-loyalty.md (01-05) [DONE — commit b05c28f]
- docs/plans/2026-03-23-j05-b2b.md (01-06) [DONE — commit a04c828]
- docs/plans/2026-03-23-j02-diagram.mmd (01-07) [DONE — commit 8ee3cbc]
- docs/plans/2026-03-23-j02-jira-tickets.md (01-07) [DONE — commit 8ee3cbc]
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

## Decisions from 01-06 (B2B J05)
- J05 is architecturally separate from J02 — kyc_type = empresa trigger, no push/WhatsApp
- Three personas: CFO (risk/MiCA), Legal (FATF/AEAT), Ops (API/panel)
- 3 emails in 20 days, max 1/week, signed by named Sales lead (+12% open rate benchmark)
- E1 fee savings anchor validated (+31% demo booking, Bitstamp benchmark)
- Escalation to Daniel for first operation > EUR 50,000
- Demo booked rate target: >5%; account upgrade: >2% in 60 days; sales cycle: <45 days
- Diego review: 3-5 days batch for B2B (higher legal complexity than B2C)
- Prerequisite: Alvaro surfaces kyc_type as CleverTap user property before launch

## Decisions from 01-04 (J02-LATAM)
- WhatsApp replaces push for S1/S4 in all LatAm markets (VE/MX/CO/AR)
- USD framing everywhere -- never local currency for portfolio value
- SP-01 Earn: loss framing expected to win more strongly in LatAm due to inflation context
- SP-03 DCA reframed as "cuenta de ahorro en USD" not "inversion periodica"
- Venezuela: kyc_enhanced_confirmed gate required before any financial touchpoint (OFAC/FATF)
- Argentina: "activos digitales" safer than "criptomonedas" due to BCRA restrictions
- Frequency cap: max 1 WhatsApp/week per user (Meta sender reputation protection)
- Fallback: WhatsApp delivery failure in 2h triggers push notification
- 22 WhatsApp templates for Meta pre-approval -- Katy to initiate immediately (48-72h process)
- New blocker added: whatsapp_marketing_opt_in field needed in CleverTap (Alvaro P1)

## Decisions from 01-07 (Diagram + Jira Tickets)
- Mermaid diagram uses 6 subgraphs with 8 classDef color themes — Hub(blue), Spokes(green), Recovery(amber), Decision(dark), Entry/Exit(violet), LatAm(pink), B2B(gray), Loyalty(navy)
- Diego approval batched as 2 cycles: Hub batch Sprint 1 + Spokes batch Sprint 2 (not 25 individual approvals)
- Recovery B1 (J02-12) flagged as P0 Sprint 1 manual campaign — no journey automation required, executable this week
- A/B test SP-01 fully specified: 600 users/variant, loss vs gain framing, Welch t-test alpha=0.05, Marta analysis owner
- Critical path: J02-01 (Alvaro BigQuery) is single blocker for all Hub tickets — must be Day 1

## Last session
2026-03-23 — completed 01-01 (ff5ddc8) + 01-02 (32500e5) + 01-03 (b2956c0) + 01-04 (ff1d7b8) + 01-05 (b05c28f) + 01-06 (a04c828) + 01-07 (8ee3cbc)
