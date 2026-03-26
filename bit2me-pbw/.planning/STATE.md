# STATE — Bit2Me @ Paris Blockchain Week 2026

**Last updated:** 2026-03-26
**Session:** Roadmap creation

---

## Project Reference

**Core value:** Every asset, campaign, and interaction at PBW must either capture a qualified lead, create a brand moment, or open a B2B conversation. Nothing generic.
**Positioning:** Spain's first MiCA-authorized exchange. Backed by Bankinter, BBVA, Cecabank. Europol's trusted crypto partner.
**Offer:** 60-day zero trading fees (PBW-exclusive, Diego-approvable, MiCA-safe)

---

## Current Position

**Active phase:** Phase 1 — Foundation
**Active plan:** None (not yet started)
**Status:** Roadmap created, awaiting plan-phase execution
**Days remaining:** 20 (event: April 15-16)

```
[Phase 1: Foundation  ] ░░░░░░░░░░  0%  Days 1-3
[Phase 2: Launch      ] ░░░░░░░░░░  0%  Days 4-10
[Phase 3: Amplify     ] ░░░░░░░░░░  0%  Days 11-16
[Phase 4: Execute     ] ░░░░░░░░░░  0%  Apr 15-16
[Phase 5: Convert     ] ░░░░░░░░░░  0%  Apr 17-24
```

---

## Team

| Person | Role | PBW Responsibility |
|--------|------|--------------------|
| Daniel | Growth (owner) | B2B outreach, ads, landing, runbook, post-event |
| Katy | CRM/CleverTap | Pre-configure all PBW sequences, on-site lead upload EOD |
| Diego | Legal | Batch copy review Day 3-5, hard approval deadline Day 7 |
| Alvaro | Data/BigQuery | PBW cohort pre-configured, UTM taxonomy |

---

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Offer: 60-day zero trading fees | MiCA-safe, no cash/token distribution, institutional-friendly framing | Mar 26 |
| Diego review: batch all copy Day 3-5, single package | Diego is known bottleneck; batching prevents timeline collapse | Mar 26 |
| B2B track: manual outreach + Google Sheet (no new CRM) | 20-day runway insufficient to configure new system | Mar 26 |
| Booth: dual-zone (B2C demo + B2B appointment table) | Different audiences, different messages, different follow-up | Mar 26 |
| Health Score tool: ~€3-5K dev, 10 days to build | High-value booth differentiator, starts Phase 2 | Mar 26 |
| Institutional dinner: "Estado del Crypto Espanol 2026", 15-20 guests, ~€8-12K | Spain-identity differentiation no competitor can replicate | Mar 26 |
| Speaking slot: parallel outreach (not blocking) | Check is pending with PBW organizers | Mar 26 |

---

## Hard Deadlines

| Deadline | What | Owner |
|----------|------|-------|
| Day 3 (Mar 28) | Diego package delivered | Daniel |
| Day 7 (Apr 1) | Diego approval received | Diego |
| Day 7 (Apr 1) | Landing page live | Dev + Design |
| Day 7 (Apr 1) | LinkedIn wave 1 sent | Daniel |
| Day 10 (Apr 4) | Ads running | Daniel |
| Day 10 (Apr 4) | Health Score build started | Dev |
| Day 10 (Apr 4) | Booth design brief complete | Design |
| Day 10 (Apr 4) | Institutional dinner venue confirmed | Daniel |
| Day 14 (Apr 8) | Booth files sent to print vendor (5-day lead time) | Design |
| Day 16 (Apr 10) | Health Score complete + tested | Dev |
| Day 16 (Apr 10) | CleverTap post-event sequences production-ready | Katy |
| Day 16 (Apr 10) | All B2B meetings confirmed | Daniel |
| Apr 14 (evening) | Institutional dinner | Daniel |
| Apr 15-16 | Event execution | All |
| Apr 17 (<1h post-event) | B2C CleverTap auto-fires | Katy |
| Apr 17 (<24h) | B2B hot lead personal follow-up | Daniel |

---

## Blockers / Risks

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| Diego bandwidth (known bottleneck across 7+ journeys) | Everything goes live late if Day 3-5 package misses | Confirm Diego can prioritize PBW by Mar 28; brief him on event context |
| Google Ads crypto certification | Google ads track may be blocked | Verify EU eligibility before scoping; X/Twitter is primary |
| PBW badge scanner (organizer app) | Changes on-site capture architecture | Confirm with PBW organizers before Apr 1 |
| B2B outreach ownership | Daniel cannot own list + outreach + booth + campaigns alone | Identify second B2B outreach owner by Day 2 |
| Institutional dinner venue (must book ASAP) | Venue availability in Paris during PBW week is constrained | Shortlist 3 options by Day 2, confirm by Day 5 |

---

## Accumulated Context

### Positioning (must run through ALL assets)
- "Spain's first MiCA-authorized exchange. Backed by Bankinter, BBVA, Cecabank. Europol's trusted crypto partner."
- CNMV authorization date on all collateral. "Spain's first, since [date]" beats generic MiCA claims.
- Bank logos on booth = institutional conversation-stopper.
- Europol signal: "We handle seized crypto for Europol and Interpol. Compliance is the product."

### Competitive Context
- Bybit EU is title sponsor (~€150-300K spend), CEO on main stage. Out-spend them on differentiation, not volume.
- PBW audience is 70%+ C-suite, €999-3699 tickets. Not a retail crowd. Institutional tone on everything.
- No other exchange at PBW holds Spanish CNMV authorization or Europol trust signal.

### B2C Conversion Mechanics
- Landing page CVR target: 8-15% (industry benchmark for event-specific offers)
- CleverTap pbw_lead tag fires on form submit; journey auto-triggers within 1h
- Qualifying question at booth: "Personal trading or B2B API?" — routes to correct track
- Premium swag gated behind QR scan (not free distribution)

### B2B Mechanics
- 50-100 LinkedIn targets: banks with crypto desks, fintechs on crypto rails, EU asset managers, custody providers
- Lead message: "Spain's first MiCA CASP. B2B revenue 27% of total. Building regulated EU bank infrastructure. 20 min at PBW?"
- Google Sheet tracking: Name / Company / Role / Meeting held / Temp (H/M/C) / Next action
- EOD each event day: hot leads get Daniel personal message same evening

### Tools in Use
- CleverTap: email/push sequences (Katy owns)
- BigQuery: PBW cohort tracking + UTM attribution (Alvaro)
- Calendly: B2B meeting booking (20-min slots, Apr 15-16)
- Google Sheet: B2B lead tracking
- Buffer: social scheduling
- Luma: side event discovery
- Popl/Wave Connect: NFC cards for booth reps
- Typeform + Zapier: on-site lead form (3 fields: email + name + track toggle)

---

## Next Action

Run `/gsd:plan-phase 1` to decompose Phase 1: Foundation into executable plans.

Phase 1 scope:
- Plan 1.1: Offer brief + Diego package (copy for landing, ads, emails, booth)
- Plan 1.2: B2B ICP list build (50-100 LinkedIn targets, segmented by persona)
- Plan 1.3: Institutional dinner venue outreach + speaking slot inquiry
