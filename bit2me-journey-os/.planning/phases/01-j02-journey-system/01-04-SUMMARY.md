---
phase: 01-j02-journey-system
plan: 04
subsystem: journey-copy
tags: [latam, whatsapp, usd-framing, crm, clevertap]
dependency_graph:
  requires: [01-01, 01-02, 01-03]
  provides: [j02-latam-spec]
  affects: [01-07, 01-08]
tech_stack:
  added: []
  patterns: [whatsapp-first-crm, usd-framing, country-segmentation, meta-template-approval]
key_files:
  created:
    - docs/plans/2026-03-23-j02-latam.md
  modified: []
decisions:
  - WhatsApp replaces push as primary channel for S1 and S4 in all LatAm markets
  - USD-denominated value throughout -- never EUR, never local currency for portfolio value
  - SP-01 Earn loss framing expected to outperform gain framing more strongly in LatAm than Spain (inflation amplifies loss aversion)
  - Venezuela requires kyc_enhanced_confirmed gate before any financial messaging (OFAC/FATF)
  - Argentina framing: "activos digitales" over "criptomonedas" to avoid BCRA regulatory friction
  - Frequency cap: max 1 WhatsApp/week per user (protect sender reputation with Meta)
  - Fallback: if WhatsApp not delivered in 2h, send push with equivalent copy
  - 22 WhatsApp templates must be pre-approved by Meta (48-72h process) -- Katy to initiate immediately
metrics:
  duration_seconds: 308
  tasks_completed: 5
  files_created: 1
  files_modified: 0
  completed_date: 2026-03-23
---

# Phase 01 Plan 04: J02-LATAM — WhatsApp-first CRM for LatAm Markets

**One-liner:** LatAm variant of J02 Hub using WhatsApp as primary channel (S1/S4), USD/inflation-protection copy, and country-specific compliance notes for Venezuela (OFAC), Mexico (CNBV), Colombia (SFC), and Argentina (BCRA).

---

## What was built

`docs/plans/2026-03-23-j02-latam.md` — complete specification for executing J02 in Venezuela, Mexico, Colombia, and Argentina. 9 sections, 796 lines.

The document covers:
1. Why LatAm is different from Spain (channel, motivation, timing, regulation)
2. Hub architecture J02-LATAM (identical structure, different channels and copy)
3. All 6 Hub touchpoints with LatAm copy (S0, S0.5, S1 WhatsApp, S2, S3 Email, S4 WhatsApp)
4. Spokes SP-01 Earn, SP-03 DCA, SP-04 Diversify with inflation-protection angles
5. WhatsApp implementation checklist for Katy (templates, opt-in, frequency, fallback, CleverTap steps)
6. Country-specific notes (Venezuela, Mexico, Colombia, Argentina)
7. Diego approval table — 22 messages ready for batch legal review
8. Blockers and dependencies table (8 items, owners, priorities)
9. KPIs and benchmarks table

---

## Key decisions made

**WhatsApp as primary channel:** S1 (D+1) and S4 (D+7) use WhatsApp templates instead of push notifications. Rationale: 85-95% open rate vs 20-30% push in LatAm. Bnext benchmark 4.3x open rate confirmed. Push remains as fallback if delivery fails in 2h.

**USD framing everywhere:** All portfolio values shown in USD. Local currencies (VES, MXN, COP, ARS) used only for inflation context, never as denomination of portfolio value. Bitso benchmark: +22% engagement with USD framing vs local currency.

**Inflation-protection copy angle:** LatAm copy is structured around "tu dinero no pierde valor" (your money does not lose value), not "tu dinero trabaja para ti" (your money works for you). The loss-aversion angle is amplified by the real inflation context in each market.

**Venezuela OFAC gate:** `kyc_enhanced_confirmed` field must be true before any financial touchpoint fires for Venezuelan users. This is a compliance requirement, not a UX choice.

**Argentina framing constraint:** "activos digitales" is the safer term due to BCRA restrictions on foreign currency. "Criptomonedas" is also acceptable. Avoid "divisas", "dolar oficial", "dolar blue", "tipo de cambio".

**22 WhatsApp templates for Meta pre-approval:** All templates listed with IDs in Section 5. Katy must initiate the Meta approval process immediately (48-72h). No WhatsApp messages can be sent until templates are approved.

**SP-03 DCA reframed as savings protection:** In LatAm, DCA is positioned as "compra mensual automatica en USD" -- a savings account that does not lose value -- not as a periodic investment strategy. This directly addresses the inflation-protection motivation.

---

## Deviations from Plan

None. Plan executed exactly as written. All 5 tasks completed in sequence:
- Task 1: LatAm context and channel differences (Section 1)
- Task 2: Hub touchpoints rewritten for LatAm (Section 3)
- Task 3: Spokes SP-01, SP-03, SP-04 rewritten for LatAm (Section 4)
- Task 4: Country-specific notes VE/MX/CO/AR (Section 6)
- Task 5: WhatsApp implementation notes for Katy (Section 5)

Additional sections added (not in plan, value-add):
- Section 7: Diego approval table with 22 messages (improves execution speed)
- Section 8: Blockers and dependencies table (8 blockers with owners and priorities)
- Section 9: KPIs and benchmarks table

---

## Self-Check: PASSED

- docs/plans/2026-03-23-j02-latam.md: FOUND
- Commit ff1d7b8: FOUND
