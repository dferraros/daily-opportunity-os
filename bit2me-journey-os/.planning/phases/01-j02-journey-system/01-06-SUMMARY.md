---
phase: 01-j02-journey-system
plan: "06"
subsystem: journey-architecture
tags: [b2b, j05, treasury, personas, email-sequence, compliance]
dependency_graph:
  requires: ["01-01"]
  provides: ["docs/plans/2026-03-23-j05-b2b.md"]
  affects: ["01-07", "01-08"]
tech_stack:
  added: []
  patterns: [b2b-email-sequence, persona-mapping, sales-cycle-architecture]
key_files:
  created:
    - docs/plans/2026-03-23-j05-b2b.md
  modified: []
decisions:
  - J05 is architecturally separate from J02 -- different trigger, tone, channels, owner, and KPIs
  - kyc_type = empresa is the primary entry trigger (Alvaro must surface this in CleverTap)
  - Three decision makers: CFO (risk/compliance), Legal (FATF/AEAT), Ops (API/workflow)
  - 3 emails over 20 days at max 1/week frequency (no push, no WhatsApp for B2B)
  - E3 uses honest close-the-loop tone -- no urgency, preserve relationship for future
  - Fee savings anchor in E1 (Bitstamp benchmark: +31% demo booking)
  - Escalation to Daniel for first operation > EUR 50,000
  - Diego review: 3-5 days batch (higher legal complexity than B2C)
  - Demo booked rate target: >5% of empresa accounts with first operation
metrics:
  duration: 18min
  completed_date: "2026-03-23"
  tasks_completed: 5
  files_created: 1
---

# Phase 01 Plan 06: B2B J05 Architecture Summary

## One-liner

B2B journey J05 with three-persona mapping (CFO/Legal/Ops), 3-email treasury-tone sequence in professional Spanish, and full separation from all B2C journeys via kyc_type = empresa trigger.

## What was built

`docs/plans/2026-03-23-j05-b2b.md` — 498 lines covering:

1. **Why B2B is architecturally separate** — comparative table (B2C vs B2B on 12 dimensions), explanation of why a empresa first operation is a proof-of-concept not an impulse purchase
2. **Entry trigger and stop conditions** — SQL-ready trigger conditions, 5 exit events with actions, prerequisite: Alvaro surfaces kyc_type in CleverTap
3. **Three decision maker personas** — CFO (risk/MiCA/balance), Legal (FATF/AEAT/audit trail), Ops (API/panel/SLA) — each with key message, frequent objections, and channel guidance
4. **Journey architecture** — ASCII flow diagram, frequency rules (max 1 email/week), personalization variables
5. **3-email sequence with full copy in Spanish** — E1 D+3 (capabilities intro), E2 D+10 (case study with savings table), E3 D+20 (honest close). Each includes tone notes, psychological principle, A/B test suggestion
6. **KPIs and owner map** — 7 metrics with targets, full RACI across Katy/Sales/Alvaro/Diego/Daniel
7. **What NOT to do** — 7 explicit prohibitions with rationale
8. **Benchmark validation table** — 8 decisions mapped to sources
9. **Diego approval protocol** — 5 high-sensitivity elements flagged, batch process recommended

## Key decisions made

- **No push, no WhatsApp for empresa accounts** — must be disabled at segment level in CleverTap before launch
- **Signed by named Sales lead** — not "Bit2Me Team" — +12% open rate (Klaviyo benchmark)
- **Fee savings anchor in E1** — Bitstamp validated +31% demo booking vs no anchor
- **E3 is zero-pressure** — preserves the relationship for a 12-month sales cycle; artificial urgency destroys B2B credibility
- **D+60 exit to manual Sales list** — automation opens the door, Sales closes it

## Deviations from Plan

None — plan executed exactly as written. All 5 tasks completed in sequence, producing the single output file specified.

## Self-Check

- [x] `docs/plans/2026-03-23-j05-b2b.md` exists
- [x] B2B architecture documented as separate from all B2C journeys (Section 1 + Section 4)
- [x] Three decision maker personas documented (Section 3)
- [x] Complete 3-email sequence with full copy in professional Spanish (Section 5)
- [x] B2B KPIs and owner map complete (Section 6)
- [x] What NOT to do section included (Section 7)
- [x] Git commit created: a04c828
