---
phase: 01-j02-journey-system
plan: 03
subsystem: product-spokes
tags: [crm, email-copy, clevertap, ab-testing, earn, pro, dca, diversify, referidos]
dependency_graph:
  requires: []
  provides: [spokes-01-05-spec]
  affects: [01-04, 01-05, 01-08]
tech_stack:
  added: []
  patterns: [hub-spokes, loss-aversion, peak-end-rule, social-proof, anchoring]
key_files:
  created:
    - docs/plans/2026-03-23-j02-spokes-01-05.md
  modified: []
decisions:
  - SP-01 Earn A/B is THE most important test in the system — loss vs gain framing, 2k per variant
  - SP-05 Referidos must NEVER trigger before 2nd purchase confirmed (behavioral economics basis)
  - Spoke priority order: SP-01 > SP-02 > SP-03 > SP-04 > SP-05 (by monetary impact)
  - Diego batch approval by spoke (not by individual message) for efficiency
  - SP-01 and SP-05 are implementation priorities 1 and 2 (SP-05 needs no new BigQuery events)
metrics:
  duration: 12m
  completed: "2026-03-23"
  tasks_completed: 6
  files_created: 1
---

# Phase 01 Plan 03: J02 Product Spokes SP-01 to SP-05 Summary

**One-liner:** 5 product cross-sell spokes fully specified — SP-01 Earn (loss/gain A/B on 72.4k users), SP-02 Pro (fee savings), SP-03 DCA (timing anxiety), SP-04 Diversify (social proof), SP-05 Referidos (post-2nd-purchase only) — complete Spanish copy, CleverTap config, A/B tests, KPIs.

## What Was Built

Single output file: `docs/plans/2026-03-23-j02-spokes-01-05.md` (1085 lines).

Complete specification for 5 product spokes, structured for Katy (CleverTap execution) and Diego (batch legal approval). Each spoke contains:
- Psychological principle with benchmark source
- Trigger logic with exact BigQuery field references
- Full Spanish email copy with personalization tokens
- CleverTap journey configuration (entry events, wait nodes, exit conditions)
- A/B test spec (hypothesis, sample size, duration, metric, KPI target)
- Frequency capping rules and Hub interaction protocol

## Spokes Delivered

| Spoke | Segment | Key A/B | KPI Target | Benchmark |
|-------|---------|---------|------------|-----------|
| SP-01 Earn | 72.4k users, EUR 19.5M AUC | Loss vs Gain framing | >8% activation | Braze 6-12% |
| SP-02 Pro | Traders 3+ ops/week or 500 EUR/month | Fee savings vs identity | >5% upgrade | Kraken 12-15% |
| SP-03 DCA | 3+ logins without trade in 14 days | Risk-reduction vs effortless | >12% DCA setup | Coinbase 2.3x retention |
| SP-04 Diversify | Single-asset portfolio 30+ days | Social proof vs risk reduction | >10% 2nd purchase | Revolut +31% |
| SP-05 Referidos | 48h post 2nd purchase ONLY | Incentive vs social framing | >15% link click | Binance 35% new users |

## Critical Design Decisions

**SP-01 Earn A/B is the most important test in the system.** 72.4k eligible users, EUR 19.5M idle AUC. Loss framing hypothesis: "Tus [ASSET] llevan [N] dias parados. Podrian haber generado EUR [Y]" vs gain framing: "Activa Earn y genera [APY]% anual." Kahneman Prospect Theory predicts 2x advantage for loss framing. This test will inform copy strategy across the entire spoke system.

**SP-05 timing rule is hard.** The Peak-End Rule (Kahneman) makes post-2nd-purchase the optimal ask moment. The `referral_spoke_triggered` flag must be set on entry to prevent re-activation. This is documented both in the trigger logic and in a dedicated behavioral explanation section so Katy and Diego understand the reasoning.

**Frequency capping documented as system rules.** Max 2 emails/week, 72h gap same-channel, Hub pauses when any spoke is active, only 1 spoke active per user at a time. These are pre-conditions that Katy must configure in CleverTap before activating any spoke.

**BigQuery events table for Alvaro** with P0/P1/P2 priorities: `balance_idle_days` and `earn_product_active` are P0 (block SP-01 launch without them), `second_purchase_confirmed` is P0 for SP-05.

## Deviations from Plan

None. Plan executed exactly as written. All 6 tasks completed (SP-01 through SP-05 + frequency capping section).

## Self-Check

- [x] docs/plans/2026-03-23-j02-spokes-01-05.md exists (1085 lines)
- [x] All 5 spokes fully specified with trigger, copy, CleverTap spec, A/B, KPI
- [x] SP-01 Earn has complete 3-email sequence with loss/gain A/B documented
- [x] SP-05 Referidos explicitly notes NEVER trigger before 2nd purchase (with behavioral rationale)
- [x] Frequency capping interaction documented as system rules table
- [x] Git commit: b2956c0

## Self-Check: PASSED
