---
phase: 01-j02-journey-system
plan: 02
subsystem: hub-j02-core
tags: [journeys, clevertap, copy, mica, ab-testing, katy, diego]
dependency_graph:
  requires: []
  provides: [j02-hub-spain-spec]
  affects: [01-03-spokes, 01-05-recovery-loyalty]
tech_stack:
  added: []
  patterns: [hub-spokes, frequency-capping, holdout-control-group]
key_files:
  created:
    - docs/plans/2026-03-23-j02-hub-spain.md
  modified: []
decisions:
  - Hub ends at D+7 (6 touchpoints), not D+30 — prevents fatigue, Recovery handles D+30 logic
  - price_change_pct_24h required for S1/S4 dynamic copy — fallback to NEUTRAL confirmed
  - 68% social proof stat in S2 derived from Jan-Mar 2026 cohort data — Marta to update monthly
  - Diego approval batch by layer (not message-by-message) for efficiency
  - Only S3 email requires MiCA footer — In-App and Push excluded per current legal criteria
metrics:
  duration_seconds: 225
  completed_date: "2026-03-23"
  tasks_completed: 4
  files_created: 1
---

# Phase 01 Plan 02: Hub J02-CORE B2C Spain Summary

**One-liner:** Complete Hub J02-CORE spec — 6 touchpoints (S0 in-app to S4 push), full Spanish copy with psychological principles, CleverTap setup instructions for Katy, Diego approval batch table (17 variants), MiCA footer, and frequency capping rules.

## What was built

`docs/plans/2026-03-23-j02-hub-spain.md` — a 620-line operational specification covering:

1. **Architecture overview:** Entry trigger, stop conditions, holdout (10%), frequency caps, post-D+30 Tipo A/B/C routing
2. **6 touchpoints fully specified:**
   - S0: In-App banner, D+0 immediate (Peak-End Rule, Binance 4.1x benchmark)
   - S0.5: In-App modal, D+0 +2min (Commitment & Consistency, Zeigarnik)
   - S1: Push 3-variant (ASSET_UP/DOWN/NEUTRAL), D+1 21:00h (Availability Heuristic, Kraken benchmark)
   - S2: In-App full-screen card, D+3 first login (Social Proof, N26 +38% CTR benchmark)
   - S3: Email with 5 subject line A/B options, D+5 10-11h (Authority Bias, Reciprocity)
   - S4: Push 3-variant, D+7 21:00h (Loss Aversion, Regret Aversion) — last Hub touchpoint
3. **KPI targets per touchpoint** (S0: >25% alert activation through S4: >18% open rate, >5% conv 24h)
4. **Diego batch approval table:** 17 message variants, MiCA footer text defined, all marked Pendiente
5. **Katy CleverTap setup checklist:** Entry events, wait conditions, personalization tokens, exit conditions, QA test procedure per touchpoint
6. **Frequency capping rules:** 2 email/week max, 2 push/week max, Hub pauses during active Spoke
7. **Dependency/blocker table:** `price_change_pct_24h` and `price_7day_trend` (Alvaro P0), fallbacks documented

## Decisions Made

1. Hub ends at D+7 (not D+30) — 6 touchpoints in 7 days. Post-D+7 without conversion goes to Recovery (separate spec)
2. `price_change_pct_24h` blocker on S1 and S4 is documented with NEUTRAL copy fallback — Katy can set up CleverTap now without waiting for Alvaro
3. Only S3 (email) requires MiCA footer per current legal criteria — confirmed in Diego batch table
4. 68% social proof stat in S2 must be updated monthly by Marta from actual cohort data
5. A/B test structure approved: S0 (500/variant), S0.5 (400/variant), S1 (600/variant), S2 (400/variant), S3 (300/variant x3)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- [x] `docs/plans/2026-03-23-j02-hub-spain.md` exists (620 lines)
- [x] All 6 touchpoints specified with copy, CleverTap spec, A/B test, KPI
- [x] Diego batch approval table complete (17 variants)
- [x] Katy setup checklist complete (6 touchpoints with QA test per each)
- [x] Frequency capping rules documented
- [x] MiCA footer defined and placed in S3 section + Diego table
- [x] Git commit `32500e5` created
