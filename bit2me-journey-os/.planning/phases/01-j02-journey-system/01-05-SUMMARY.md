---
phase: 01-j02-journey-system
plan: 05
subsystem: recovery-loyalty
tags: [recovery, loyalty, tipo-a, tipo-b, tipo-c, fomo-agent, j02.5, crm, clevertap]
dependency_graph:
  requires: [01-02]
  provides: [recovery-tracks, loyalty-sequence]
  affects: [01-07, 01-08]
tech_stack:
  added: []
  patterns: [behavioral-trigger, reactivation-framing, flywheel-loyalty, manual-campaign-launch]
key_files:
  created:
    - docs/plans/2026-03-23-j02-recovery-loyalty.md
  modified: []
decisions:
  - "Tipo C (295 users, 60+d) routes to FOMO Agent pool — no automated journey (unsubscribe risk + low conversion ROI)"
  - "Tipo B manual launch this week: Marta exports BigQuery, Katy sends one-off campaign, no CleverTap journey setup needed"
  - "J02.5 Loyalty entry at D+45 with second_purchase_confirmed — covers D+45 to D+90 with 3 touchpoints"
  - "All 12 messages are Diego Tier 1 (template standard) — send as single batch for 48h approval"
  - "price_change_pct_7d fallback: neutral copy when Alvaro field unavailable (same as Hub pattern)"
metrics:
  duration_minutes: 15
  completed_date: "2026-03-23"
  tasks_completed: 5
  tasks_total: 5
  files_created: 1
  files_modified: 0
---

# Phase 01 Plan 05: Recovery Tracks and J02.5 Loyalty Summary

**One-liner:** Recovery tracks for 1333 non-converters (Tipo A/B/C) with Tipo B manual launch this week and J02.5 Loyalty 3-touchpoint habit loop targeting 3.1x Coinbase retention benchmark.

---

## What Was Built

`docs/plans/2026-03-23-j02-recovery-loyalty.md` — complete specification for:

### Recovery Track (1333 non-converters, 25.7% of FM base)

**Tipo A — Indeciso Activo (491 users, <30d):**
- Recovery A1: Push D+14, market-aware variants (ASSET_UP / NEUTRAL), 21:00h local
- Recovery A2: Email D+21, decision fatigue framing, two subject A/B variants
- Target: 15% conversion = ~74 second purchases

**Tipo B — Dormido con Saldo (547 users, 31-60d) — MANUAL ESTA SEMANA:**
- Recovery B1: Email D+30, portfolio value hook (price at purchase vs today), two subject A/B variants
- Recovery B2: Push D+37, trend-aware variants (positive/negative/neutral)
- Step-by-step manual launch: Marta SQL query (30 min) + Katy CleverTap one-off (45 min) + Diego batch approval
- Expected: 28% open rate = 153 opens, 8% conversion = 44 second purchases

**Tipo C — Caso Frio (295 users, 60+d) — FOMO Agent pool:**
- No automated journey (low conversion ROI + high unsubscribe risk)
- Entry condition: `dias_sin_2a_op >= 60 AND has_balance = true`
- Trigger criteria table: BTC +7%/7d (high), specific asset +10%/24h (high), general event (manual Daniel)
- Copy structure template provided for Daniel to adapt at send time
- KPI: >5% conversion in 90 days, tracking via BigQuery `fomo_pool_entry_date`

### J02.5 Loyalty (D+45 to D+90)

Entry: `second_purchase_confirmed = true AND DATEDIFF >= 45`

- T1 Email D+45: portfolio milestone (value at purchase vs today), DCA CTA secondary
- T2 Push D+60: market state hook, conditional on no third purchase since T1
- T3 Email D+90: 90-day identity milestone, conditional Earn CTA if earn_product_active = false

Benchmark anchor: Coinbase — 3+ trades in 90 days = 3.1x higher 12-month retention. Actual Bit2Me M1: 0.12% (CRISIS).

### Operations table

- Diego approval batch: 12 messages, all Tier 1, single batch recommended
- BigQuery fields: `first_purchase_price_eur` and `current_price_eur` are P0 for Tipo B launch
- `price_change_pct_7d` is P1 with neutral copy fallback (same pattern as Hub)

---

## Deviations from Plan

None — plan executed exactly as written. All 5 tasks completed in sequence. Copy, timing, personalization fields, KPIs, and operational instructions all included as specified.

---

## Self-Check

- [x] `docs/plans/2026-03-23-j02-recovery-loyalty.md` exists
- [x] Tipo A/B/C have distinct copy, timing, and channel strategy
- [x] Tipo B has highlighted manual launch instructions with SQL query and step-by-step Katy instructions
- [x] Tipo C explicitly routed to FOMO Agent pool with entry condition, trigger criteria, and KPI
- [x] J02.5 has 3 touchpoints (T1 email D+45, T2 push D+60, T3 email D+90) with full copy
- [x] Git commit b05c28f created

## Self-Check: PASSED
