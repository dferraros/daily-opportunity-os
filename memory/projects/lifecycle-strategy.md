# Lifecycle Strategy — Bit2Me
**Last updated:** 2026-02-27
**Sources:** Pablo Campos + Daniel Ferraro call (Feb 24), LC Sync (Feb 25), LC Weekly (Feb 19)

---

## Core Mandate (Pablo Campos, Feb 24 2026)
"El dinero viene del Ciclo de Vida."
- ADQ: volume + quality of leads (ratios, not revenue)
- Conversión: binary — did they monetize? (no revenue metric)
- LC / Ciclo de Vida: ALL revenue, ALL monetization post-FM

---

## Lifecycle Framework — Pablo's Vision (iPad drawing, Feb 24)

```
ADQUISICIÓN → CONVERSIÓN → [FM EVENT] → LIFE CYCLE
                                           |
                             ACTIVACIÓN (FM → X = ~1 mes)
                                  |
                           ┌──────┴───────┐
                        Fase 1         Fases Iterativas
                        Fase 2         (market-triggered)
                        Fase 3
                           |
                   Product columns:
                   Wallet/Broker | Loan/Earn | ?
                           |
                  FASE DESPIERTA (D+35 días sin actividad)
                  FASE DESPIERTA HOT (D+60 días sin actividad)
```

### Phase Definitions (decided Feb 24)
| Phase | Definition | Timing | Actions |
|-------|-----------|--------|---------|
| **Activación** | Post-FM phase. Explain all products, cross-sell, make offers | FM → X (~1 month) | Journeys: explain Loan, Pro, Earn, Card. Incentives. |
| **Fase 1** | Second monetization window. CRITICAL — most users leave here | Post-activation | Push second purchase within 48h, 7d, 30d |
| **Fase 2** | Retention deepening | Ongoing | Product usage depth, DCA setup |
| **Fase 3** | Power user development | Ongoing | Multi-product, high ticket |
| **Fases Iterativas** | Market/behavior triggered | Any time | Market drop → Loan offer. Market up → harvest offer |
| **Fase Despierta** | 35+ days inactive | Rolling | Re-engagement journey |
| **Fase Despierta Hot** | 60+ days inactive | Rolling | FOMO Agent, win-back incentives |

### Key Decisions (Feb 24, Pablo + Daniel)
1. **First Monetization (FM) is NOT a time threshold** — it's an event. Can happen hours or months after registration. Don't measure by median days (confounded by Bitcoin cycle). Measure: rate of FM per acquisition channel.
2. **Activación is the FIRST phase of LC** — not a Conversión function. Moved here because Pablo García (Conversión) is technical, not lifecycle-oriented.
3. **All money/revenue metrics live in LC.** ADQ reports ratios (FM rate, ARPU quality, LTV quality). Never raw revenue.
4. **LC must have a weekly backlog of actions** for Salvia + Màxim to execute every week.
5. **2-week sprint** to fully define the LC framework before any org changes.
6. **500K contactable users** not being offered anything. "CAC de reactivación es más barato que cualquier adquisición."

### Product-Level Lifecycle (Pablo's note)
Different products = different lifecycle phases:
- Wallet/Brokerage users: standard lifecycle
- Loan users: different phases (collateral-based triggers)
- Earn users: DCA retention path (60-70% lower churn)
- Card users: cashback mechanics (highest cashback in market, not being used)

---

## LC Framework — L-Segment Model (Spain, Feb 2026)
| Segment | Definition | Count (Spain) | Revenue |
|---------|-----------|--------------|---------|
| L0 | No KYC | 213,863 (49.1%) | €0 |
| L1 | KYC, no FM | 29,010 (6.7%) | €0 potential |
| L2 | FM, no retention | 36,866 (8.5%) | €26M+ potential |
| L3 | Active (last 90d) | 50,416 (11.6%) | Core revenue |
| L4 | Dormant + balance | 4,414 (1.0%) | €3.1M+ |
| L5 | Churned 180d+ | 101,029 (23.2%) | Win-back |
**Total Spain:** 435,598 | Global contactable: ~500K

### Stage Machine (11 stages + EXCLUDED)
```
EXCLUDED (600K) → not addressable
REGISTERED_ONLY → KYC_COMPLETE → DEPOSITED_ONLY → FIRST_MONETIZATION
    → ACTIVE → POWER_USER
    → AT_RISK → REACTIVATED → DORMANT_WITH_BALANCE → DORMANT_ZERO → CHURNED
```
- DEPOSITED_ONLY = NEW stage not in Salvia's model. User has deposited but hasn't traded. P0 trigger: "Your €X is ready" within 48h.
- REACTIVATED = temporary 30-day stage after returning from dormancy.

---

## Space Center (Gamification) — LC Sync Feb 25
**Status:** Being redesigned (look & feel + management platform). Original creator Nil left the company.
**Critical unknown:** Does Space Center activate manually or automatically?
- Daniel assumes: MANUAL (users need to stake B2M tokens)
- Màxim to investigate: full flow, how users advance levels, if users know their level

**Màxim's tasks (from LC Sync Feb 25):**
- [ ] Extract data: users per Space Center tier, drop rate per tier, products held, trading frequency/volume, AUC
- [ ] Map all CleverTap journeys for Space Center (email, push, in-app, frequency)
- [ ] Understand full Space Center flow (manual vs auto activation, level-up criteria)
- Goal: full universe analysis ready for week of Mar 2 meeting with Pablo

---

## Key Metrics Framework (Pablo's Vision)
### ADQ metrics (ratios only, no revenue)
- Number of new users / leads
- FM Rate: % who monetized within acquisition window
- ARPU quality: avg revenue per acquired user
- LTV quality: lifecycle value of acquired cohort
- Time-to-FM: how long avg user takes to FM (by channel)

### LC metrics
- MMU: Monthly Monetizable Users (target: 30K by Mar 31; actual: 23K)
- M1 Retention: % who make second purchase within 30d of FM (actual: 0.12% — CRISIS)
- Revenue by phase: Activación vs Retención vs Reactivación
- Health Score: 100pt (Recency 30 + Frequency 20 + Product 15 + Balance 20 + Engagement 15)

---

## Critical Data Points
- M1 Retention: **0.12% actual** vs **25% Coinbase benchmark** → CRISIS
- DCA users churn **60-70% less** than non-DCA users (market data, Daniel)
- 72.4K dormant users hold **€19.5M AUC**
- 93% paid attribution = existing users (Ghost Conversions). Real new-user ROAS = 62%
- Phone drop-off during onboarding: **32%** (biggest gap)
- Spain 2025: 73,541 reg → 44,262 KYC → 31,749 purchase (45% conversion)
- C8 whales: 90.91% of Loan revenue. NEVER mass push.
- LC vs ADQ revenue split: €11.6M (LC) vs €486K (ADQ) = **24x impact**

---

## Weekly Operating Model
| Cadence | Meeting | Attendees |
|---------|---------|-----------|
| Daily 9:45am | LC Daily sync | Daniel + Salvia + Màxim |
| Thursday 11am | LC Weekly | Daniel + Salvia + Màxim + Pablo (weekly check) |
| Friday Council | Growth Council | Daniel + Patri + Pablo Campos |

**LC Daily format:** Salvia leads backlog, Màxim executes data tasks, Daniel reviews A/B results and designs new tests.

---

## FOMO Agent (Priority — READY to launch)
- Target: c6+c7 dormant users (16,116 users)
- Daily push triggered by market signals (CoinGecko API: Fear & Greed + volatility)
- Blockers: Katy (CleverTap passcode + segment), Diego (copy approval), Infra (cron server)
- File: Desktop/fomo_agent_overview.html

---

## Active Journeys (CleverTap)
| Journey | Status | Notes |
|---------|--------|-------|
| J1 Brokerage | Active | Smart holders c6/c7 |
| J2 Pro | Active | No traceability — can't measure |
| J3 Earn | Active | DCA = retention anchor |
| J4 Card | PAUSED | Cashback highest in market, not leveraged |
| J5 B2B | Active | — |
| J6 Multi | Active | Cross-product |
| Loan Journey | LAUNCHING | Email + push + in-app, ~1 month, full segment |

---

## Pablo's Strategic Principles (from multiple sessions)
1. "El dinero viene del Ciclo de Vida." — every peso of growth comes from LC.
2. Metrics exist to change your work. If a metric doesn't drive action, remove it.
3. Before any action: understand the full universe of users first.
4. Activate something (anything) now, improve iteratively.
5. Reactivating an existing user is ALWAYS cheaper CAC than acquiring a new one.
6. "Tenemos 500K usuarios contactables y no les mandamos nada."
