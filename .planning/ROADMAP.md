# Roadmap: Playbook Maestro de Trigger Based Notifications

## Overview

This roadmap delivers a complete strategic playbook for [external]'s trigger-based notification system across 4 phases. Each phase produces a section of the master document, ordered by dependency: safety rails before triggers, taxonomy before scoring, scoring before measurement. The output is a document deliverable, not software -- each phase is "done" when its playbook section is written, reviewed, and internally consistent with prior phases.

## Phases

- [x] **Phase 1: Foundation + Safety Architecture** - Preference center design, frequency caps, suppression system, data architecture, Reverse ETL design
 (completed 2026-03-22)
- [ ] **Phase 2: Taxonomy + Competitive Benchmark** - 6 trigger families with eligibility, asset universe mapping, competitor matrix, compliance checklist
- [ ] **Phase 3: Scoring System + Master Trigger Table** - 8 scoring formulas, 30+ trigger table, channel policy matrix, Top 10 MVP and Top 10 NOT to launch
- [ ] **Phase 4: Measurement + Final Recommendations** - KPIs, incremental lift framework, Net Notification Value, MVP/V2/V3 roadmap, executive summary

## Phase Details

### Phase 1: Foundation + Safety Architecture
**Goal**: The playbook's safety rails are fully documented -- anyone reading the playbook knows exactly how notifications are capped, suppressed, consented, tracked, and synced before seeing a single trigger definition.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05
**Success Criteria** (what must be TRUE):
  1. Preference Center architecture is documented with data model (channel flags, consent categories, storage schema, UI wireframe description)
  2. Frequency cap policy is specified with exact numbers per channel, per day/week/month, with priority tier override rules (P0-P5)
  3. Suppression system is documented covering C8 whale list, quiet hours by timezone, opt-out handling, and escalating dismissal cooldowns
  4. Event schema is defined with minimum required events and properties for trigger activation (CleverTap SDK + Backend Upload Events API)
  5. Hightouch Reverse ETL integration design is documented (BigQuery source tables, CleverTap destination fields, sync cadence, error handling)
**Plans**: 2 plans (Wave 1, parallel)

Plans:
- [x] 01-01-PLAN.md — Preference Center Architecture + Frequency Cap Policy (FOUND-01, FOUND-02)
- [ ] 01-02-PLAN.md — Suppression System + Event Schema + Hightouch Reverse ETL Design (FOUND-03, FOUND-04, FOUND-05)

### Phase 2: Taxonomy + Competitive Benchmark
**Goal**: Every trigger family is defined with eligibility criteria, the asset universe is mapped to products, competitors are benchmarked, and compliance constraints are codified per trigger type -- so Phase 3 can score and tabulate triggers against a complete framework.
**Depends on**: Phase 1
**Requirements**: TAX-01, TAX-02, TAX-03, TAX-04, TAX-05, TAX-06, TAX-07, TAX-08, BENCH-01, BENCH-02, BENCH-03, COMP-01, COMP-02, COMP-03, COMP-04
**Success Criteria** (what must be TRUE):
  1. All 6 trigger families (User Configured, Market, Behavioral, Lifecycle, Cross-sell, Risk/Protective) are defined with entry criteria, exit criteria, and user eligibility rules
  2. Asset universe mapping exists showing which assets are eligible for which trigger families and which products (Brokerage, Pro, Earn, Card, Loan, Space Center)
  3. Competitor matrix covers 6 competitors (Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo) with per-competitor analysis of alert types, preference center, channels, gaps
  4. Actionable competitive recommendations are documented: what to copy, what to avoid, what to innovate
  5. Compliance checklist exists per trigger type with MiCA Art. 66, GDPR, ePrivacy, CNMV references, Diego review workflow, investment advice bright-line test, and market abuse protocol
**Plans**: 4 plans (Wave 1, all parallel)

Plans:
- [ ] 02-01-PLAN.md -- Trigger Taxonomy: 6 families with eligibility, example triggers, compliance classification (TAX-01 through TAX-07)
- [x] 02-02-PLAN.md -- Asset Universe Mapping: product-asset eligibility matrix, trigger-family scope rules (TAX-08)
- [ ] 02-03-PLAN.md -- Competitive Benchmark: 6-competitor matrix, copy/avoid/innovate recommendations (BENCH-01, BENCH-02, BENCH-03)
- [ ] 02-04-PLAN.md -- Compliance Framework: per-trigger checklist, Diego workflow, bright-line test, market abuse protocol (COMP-01 through COMP-04)

### Phase 3: Scoring System + Master Trigger Table
**Goal**: The playbook contains concrete, implementable scoring formulas and a complete trigger table that an engineering/CRM team could execute from -- every trigger has a score, a channel, a threshold, a cooldown, and a priority.
**Depends on**: Phase 2
**Requirements**: SCORE-01, SCORE-02, SCORE-03, SCORE-04, SCORE-05, SCORE-06, SCORE-07, SCORE-08, TRIG-01, TRIG-02, TRIG-03, TRIG-04, CHAN-01, CHAN-02, CHAN-03, CHAN-04
**Success Criteria** (what must be TRUE):
  1. All 8 scoring formulas are documented with inputs, weights, thresholds, and pseudocode (Market Relevance, User Asset Affinity, Trigger Opportunity, Notification Pressure, Fatigue Risk, Cross-sell Eligibility, Churn Risk, Send Score Final)
  2. Send Score Final integrates all component scores with a compliance gate that blocks sends when conditions are not met
  3. Master trigger table contains 30+ triggers, each with all columns: trigger_id, family, business objective, who receives, who never receives, asset scope, formula, threshold, cooldown, channel, deep link, priority, estimated value, estimated risk
  4. Top 10 MVP triggers (30-day launch) are identified and justified with estimated impact
  5. Top 10 triggers NOT to launch are identified with reasoning (compliance risk, fatigue risk, low value)
  6. Channel policy matrix documents when to use push vs in-app vs email vs no-send, deep links per product, quiet hours per timezone, and conflict resolution between lifecycle journeys and market alerts
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

### Phase 4: Measurement + Final Recommendations
**Goal**: The playbook closes with a measurement framework that proves trigger value, a phased implementation roadmap (MVP/V2/V3), and an executive summary that a non-technical stakeholder can act on.
**Depends on**: Phase 3
**Requirements**: MEAS-01, MEAS-02, MEAS-03, MEAS-04, MEAS-05, REC-01, REC-02, REC-03, REC-04, REC-05
**Success Criteria** (what must be TRUE):
  1. KPI framework is defined per trigger and per family with specific metrics (CTR, session rate, trade rate, deposit rate, push disable lift, negative action rate)
  2. Deliverability health metrics are specified (push token health, email reputation, opt-in rate trend) with alert thresholds
  3. Incremental lift framework is documented with holdout design (10% control), A/B test design per trigger, and statistical requirements
  4. Net Notification Value formula is defined (incremental revenue minus opt-out cost minus complaint cost) with example calculations
  5. Executive summary states estimated business impact on reactivation, retention, and revenue with supporting logic
  6. MVP (30d), V2 (90d), V3 (180d) roadmap specifies triggers, channels, required resources, and dependencies per team (Katy, Alvaro, Diego, Engineering)
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation + Safety Architecture | 1/2 | Complete    | 2026-03-22 |
| 2. Taxonomy + Competitive Benchmark | 3/4 | In Progress|  |
| 3. Scoring System + Master Trigger Table | 0/3 | Not started | - |
| 4. Measurement + Final Recommendations | 0/2 | Not started | - |
