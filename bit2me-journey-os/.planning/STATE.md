# J02 Journey System — STATE

## Current Position
Phase 01 executing. Wave 1 agents spawned.

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
- docs/plans/2026-03-23-j02-research.md (01-01)
- docs/plans/2026-03-23-j02-hub-spain.md (01-02)  
- docs/plans/2026-03-23-j02-spokes-01-05.md (01-03)
- docs/plans/2026-03-23-j02-latam.md (01-04)
- docs/plans/2026-03-23-j02-recovery-loyalty.md (01-05)
- docs/plans/2026-03-23-j05-b2b.md (01-06)
- docs/plans/2026-03-23-j02-diagram-jira.md (01-07)
- docs/plans/2026-03-23-J02_MASTER.docx (01-08)
