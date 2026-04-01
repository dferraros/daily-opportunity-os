# Bit2Me Strategic Context — LC-OS Full Intelligence Brief
Last updated: 2026-03-05
Source: Full desktop file audit (Bit2me 3, Bit2me LC, Bit2me Lifecycle 2, Bit2me)

---

## 1. The Five Crises That Created LC-OS

These are the business problems driving the entire Lifecycle Operating System project.

| Crisis | Metric | Benchmark | Gap |
|--------|--------|-----------|-----|
| M1 Retention | 0.12% | Coinbase 25% | 200x |
| Dormant AUC | €19.5M locked in 4,414 users | — | Opportunity |
| Revenue concentration | 96% from LC (not new users) | — | Fragile |
| Card penetration | 0.26% | Industry 42-48% | 160x |
| No lifecycle comms system | Zero journeys running | — | Gap |

The cost of inaction on lifecycle vs. acquisition: FM revenue €486K vs LC revenue €11.6M = 24:1 ratio.

---

## 2. LC-OS Architecture (4-Layer Stack)

```
Layer 1: BigQuery Gold Layer — raw data → user classification (11 views)
Layer 2: Qlik Dashboard — LC-OS Dashboard v2 (8 tabs, live)
Layer 3: CleverTap — 6 journeys (J1-J6), 30-50 CRM actions/week
Layer 4: Council + CRM — weekly reporting, Pablo Campos stakeholder loop
```

Schema prefix: `bit2me_lifecycle.*`

### BigQuery Gold Layer — 11 Views (V0a through V10)

| View | Name | Priority | Deadline |
|------|------|----------|---------|
| V0a | user_fm | P0 | Mar 10 |
| V0b | monthly_revenue | P0 | Mar 10 |
| V0c | monthly_thresholds | P0 | Mar 10 |
| V1 | lifecycle_stage | P0 | Mar 10 |
| V2 | user_daily_snapshot | P0 | Mar 10 |
| V3 | activation_funnel | P0 | Mar 10 |
| V4 | stage_distribution_weekly | P1 | Mar 24 |
| V5 | stage_transitions_weekly | P1 | Mar 24 |
| V6 | revenue_by_stage_product | P1 | Mar 24 |
| V7 | ab_test_results | P1 | Mar 31 |
| V8 | reactivation_targets | P1 | Mar 31 |
| V9 | cross_product_adoption | P2 | Mar 31 |
| V10 | cohort_revenue_curves | P2 | Mar 31 |

Production-ready SQL: `Bit2me Lifecycle 2/02_bigquery_fixes.sql` (671 lines)
Deployment guide: `Bit2me Lifecycle 2/02_DEPLOYMENT_GUIDE.md` (298 lines, ~40 min total)

---

## 3. FM (First Monetization / EMA) Definition

**EMA = Economically Meaningful Action.** Requires revenue generation of at least €0.50.

### What COUNTS as FM by product:

| Product | FM Event | Notes |
|---------|----------|-------|
| Brokerage | First swap/sell/purchase | Any crypto trade |
| Pro | First trade executed (buy or sell) | |
| Earn | First deposit into Earn product | |
| Card | First interchange transaction | Card spending |
| Loan | First loan REQUEST (even if not approved) | |
| Staking | First staking reward received | |
| Launchpad | First Launchpad participation | |
| **Fiat Deposit** | **First non-SEPA deposit (Card/PayPal/Wire)** | **NEW: 1.99% fee = EMA** |

### What DOES NOT count as FM:
- SEPA deposits (0% fee = no revenue)
- B2M token purchases (explicitly excluded)
- Funding/depositing alone without a monetizable event

### FIX-001 (deployed Feb 2026): Added fiat deposit fees to EMA
- Revenue impact: +€50,000-100,000/month
- New FM users: 5-10% of deposit user base
- View: `bit2me_lifecycle.user_fm` (UPDATED)

---

## 4. Lifecycle Stage Model (13 Stages)

Full state machine in `bit2me_lifecycle.lifecycle_stage` view.

| Stage | Definition | Spain Population | Revenue |
|-------|-----------|-----------------|---------|
| NEW | Registration started | — | €0 |
| REGISTERED_ONLY | Registered, no KYC | 213,863 (49.1%) | €0 |
| KYC_COMPLETE | KYC approved, no deposit | 29,010 (6.7%) | €0 potential |
| DEPOSITED_ONLY | Deposited, no FM yet | Sub-segment of L1 | €0 |
| FIRST_MONETIZATION | FM done, <2 tx, ≤30d | 36,866 (8.5%) | Low |
| ACTIVE | Revenue-generating, last 90d | 50,416 (11.6%) | Core revenue |
| POWER_USER | High frequency + balance | Sub-segment | High |
| AT_RISK | Declining activity pattern | — | At risk |
| PRE_DORMANCY | 30d before dormancy threshold | NEW in v2 | Reactivation target |
| PRE_DORMANCY_FEE | 30d before €10 fee threshold | NEW in v2 | Highest urgency |
| DORMANT_WITH_BALANCE | 90-365d inactive, balance >0 | 4,414 (1.0%) | €19.5M AUC |
| DORMANT_ZERO | 90d+ inactive, no balance | 101,029 (23.2%) | Low (win-back) |
| REACTIVATED | Returned after dormancy | — | High LTV potential |
| CHURNED | 180d+ inactive, no login, no balance | — | Minimal |

L0-L5 mapping (older model still used in CleverTap/W09 briefs):
- L0 = REGISTERED_ONLY, L1 = KYC_COMPLETE, L2 = FIRST_MONETIZATION, L3 = ACTIVE, L4 = DORMANT_WITH_BALANCE, L5 = CHURNED

Weekly funnel flows (Spain approximate):
- New → L0: ~1,400/week
- L0 → L1: ~850/week
- L1 → L2: ~610/week
- L2-L3-L4-L5 transitions: pending BigQuery V5

---

## 5. Health Score (0-100 Points)

Calculated per user. Determines stage classification thresholds.

| Component | Points | Threshold Logic |
|-----------|--------|----------------|
| Recency | 30 pts | Days since last transaction |
| 4W Activity Trend | 25 pts | Frequency trend vs. prior 4 weeks |
| Balance Trajectory | 20 pts | Balance direction over 30d |
| Product Density | 15 pts | Number of products used |
| DCA / Space Center | 10 pts | Has active DCA or Space Center tier |
| B2M Holdings | 5 pts | Any B2M: 2pts, Top 20% holders: 5pts |
| **TOTAL** | **100 pts** | |

Thresholds:
- <30 = AT_RISK
- 30-70 = ACTIVE
- ≥70 = POWER_USER

---

## 6. 37-Segment Model

Full model: `Bit2me Lifecycle 2/03_37_segment_model.html`
Summary: `Bit2me Lifecycle 2/README_37_SEGMENTS.txt`

10 segment groups (SEG-01 to SEG-37), MECE. Each segment has: LTV profile, CRM action, priority badge (P0/P1/P2), SLA.

### Top 5 Priority Segments:

| Segment | Name | Users | Priority | SLA |
|---------|------|-------|----------|-----|
| SEG-24 | AT_RISK_DCA_CANCELLED | ~500-1k | P0 | 24h |
| SEG-33 | DORMANT_BALANCE_WHALE | ~500 | P0 | 24h, €10M+ AUC |
| SEG-14 | ACTIVE_DCA | Large | P0 | Target: 50% adoption |
| SEG-04 | DEPOSITED_FIAT_NO_TRADE | Medium | P0 | 24h nudge |
| SEG-28-30 | PRE_FEE_HIGH_BALANCE | ~1k | P0 | 30d window |

Revenue impact forecast: +€2,230-€4,460/month in first 30 days from top segments.

---

## 7. Journey Architecture (J1-J6)

All journeys execute in CleverTap. Owners: Katy Gildemeister + Miguel.
Critical window: 48 hours post-FM (J1-J3 must trigger within 48h).

| Journey | Name | Trigger | Target | Status |
|---------|------|---------|--------|--------|
| J1 | BROKER_2M | Brokerage FM | 2nd Brokerage tx in 7d | Design complete |
| J2 | PRO_2M | Pro FM | 2nd Pro trade in 7d | Design complete |
| J3 | EARN_2M | Earn FM | 2nd Earn deposit in 7d | Design complete |
| J4 | CARD_2M | Card FM | Card habit formation | PAUSED (card penetration crisis) |
| J5 | B2B_2M | B2B FM | B2B account deepening | Design complete |
| J6 | MULTI_PRODUCT_2M | Any FM | Cross-product adoption | Design complete |

### Second Monetization (2M) Framework Targets:
- Move 55-60% of FM users to 2M within 90 days (current ~35-40%)
- Industry benchmark: Coinbase/Kraken 60%+ reach 2M within 48h
- Conversion targets: 25-35% in 48h, +15-20% by D+7, +10% by D+30, +5% by D+90
- A/B test proposed: 2M-005

### CRM Playbooks (full operational guide in crm_playbooks.html):

| Playbook | Stage | Focus | Key Metric |
|----------|-------|-------|-----------|
| REGISTERED_ONLY | L0 | KYC completion | KYC rate |
| KYC_COMPLETE | L1 | First deposit | Deposit rate |
| DEPOSITED_ONLY | Between L1-L2 | First trade | FM rate |
| FIRST_MONETIZATION | L2 | 2nd EMA within 7d | 2M rate |
| ACTIVE | L3 | DCA enablement, retention | DCA adoption % |
| AT_RISK | L3 declining | Win-back before churn | Churn prevention |
| DORMANT_WITH_BALANCE | L4 | High-value retention | Reactivation rate |
| CARD_ACTIVATION | Card | Card habit | Card 30d retention |
| PRE_DORMANCY_FEE | NEW | Prevent fee | Reactivation before fee |

### PRE_DORMANCY_FEE Playbook (highest urgency):
Sequence: D-30 → D-14 → D-7 email sequence before €10 inactivity fee hits.
Fee triggers: 12 months no transaction OR 3 months no login.
Target reactivation before fee: 25-35%.
Revenue impact of FIX-002: +€10,000-20,000/month.

---

## 8. Weekly CRM Operations Framework

30-50 CRM actions/week. Scoring: Impact × (1/Effort) × (Segment Size / 10,000).

Weekly calendar:
- Monday 9 AM: Planning (approved action list output)
- Tuesday 4 PM: CleverTap setup (segments, personalization, A/B tests)
- Wednesday 8 AM: QA and launch (5% → 25% → 100% rollout)

Effort scale: 1 = template ready (2h), 2 = copy needed (4h), 3 = copy + design (1 day).

---

## 9. Revenue Attribution Model (W-Shaped)

Attribution model: W-Shaped (4 touchpoints).

| Touchpoint | Weight | Definition |
|-----------|--------|-----------|
| First Touch | 30% | First campaign contact |
| KYC Assist | 20% | Last touch before KYC completion |
| Deposit Assist | 20% | Last touch before first deposit |
| FM Last Touch | 30% | Last touch before FM event |

4 Revenue Pools:
- New User Revenue: ~4% of total
- Retention Revenue: ~96% of total (LC users)
- Reactivation Revenue: ~0% (untapped)
- Expansion Revenue: unmeasured

Flash Revenue Report structure (SQL parameterized, daily):
- Section A: FM revenue (new users, acquisition)
- Section B: LC revenue (MMU, Churn, NRR, GRR, LT)
- Section C: Decisions (SCALE/HOLD/CUT/REVIEW based on ROAS thresholds)
- Portugal: own column (separate from España)

---

## 10. Space Center (Loyalty System)

7 tiers: Explorer → Astronaut → Cosmonaut → Pioneer → Star → Galaxy → Universe.
- B2M token holders advance 100x faster than non-holders.
- Top tier (Universe): 7% cashback.
- CRM action: Include Space Center tier + progress bar in every lifecycle email to ACTIVE and POWER_USER segments.
- Manual vs. auto activation: TBD (pending decision).

---

## 11. Key Metrics — Feb 2026 Snapshot

### Revenue
| Metric | Value |
|--------|-------|
| Revenue España 2025 | €11,795,882 (89.8% of global) |
| Revenue Global 2025 | ~€21,563,333 |
| Revenue YTD (early 2026) | ~€1.39M España |
| Revenue share: LC vs FM | 96% LC, 4% FM new users |

### Users (España)
| Stage | Count |
|-------|-------|
| Total España | 435,598 |
| L3 Active | 50,416 (11.6%) |
| L4 Dormant with balance | 4,414 (€19.5M AUC) |
| L5 Churned | 101,029 (23.2%) |
| Global total users | ~1.8M |
| Excluded (banned etc.) | ~600K |
| MMU (Monthly Monetizable) | 23,000 actual, 30,000 target |

### Product Performance (2025 Actuals)
| Product | Revenue | Churn Rate | Notes |
|---------|---------|-----------|-------|
| Brokerage | €18.5M (86%) | Low | Dominant |
| Pro | €530K | Medium | |
| Card | €245K | 6.74%/week HIGHEST | Crisis product |
| Loan | 939 users | — | |
| Earn | Lowest revenue | 1.0%/week (lowest churn) | Best retention |

### 2026 Targets
| Metric | 2025 Actual | 2026 Target |
|--------|------------|------------|
| Revenue | €21.6M | €35.4M (+64%) |
| TAU | 96,735 | 155,000 (+60%) |
| M1 Retention | 0.12% | 5% (Q2) |
| Dormant reactivation | ~0% | 15% |
| Card penetration | 0.26% | 2%+ |
| DCA adoption (ACTIVE) | ~0% baseline | 20-30% (stretch 40-60%) |
| A/B tests running | 8 | 40+ |
| NRR | — | >110% |
| Payback period | — | <60d |

### Unit Economics
| Metric | Value |
|--------|-------|
| LTV España | €388 |
| LTV Global blended | €218.87 |
| LTV Resto EU | €195 |
| LTV No EU | €165 |
| CAC Paid | €140 |
| CAC Blended | €56 |
| Payback period | 7.5 months |
| ARPU Annual blended | €222.91 |
| Monthly Churn | 8.0% |
| Lifetime (Blended) | 50.93 weeks |

---

## 12. A/B Testing Machine

Files: `Bit2me LC/ab-test-bot.jsx` (React component, production-ready)
Framework: `Bit2me LC/ab-machine-framework-mar26.docx`

Statistical method: Two-sided z-test.
Decision outputs: SHIP VARIANT / CONSIDER SHIPPING / NEED MORE DATA / HOLD/ITERATE / DO NOT SHIP.
Confidence levels: 90%/95%/99%.

W09 active tests:
- T1: Loan CTA (5,523 users in segment)
- T2: DCA vs Institutional anchor (6,681 users)
- T3: Decision elimination for L1 deposited-no-trade (566 users)
- W08 winner: T2B (institutional anchor) 13% CTR, 4 conversions, €96 avg ticket

Minimum viable A/B: 1,550/variant = 3,100 total (5% baseline, 10% MDE, 80% power).
C8 suppression: MANDATORY before any L3 push (Juan Fornell exports → Katy uploads to CT).
Split: ALWAYS 50/50.
Conversion window: 7 days (10,080 min), NOT CleverTap's 1-hour default.

CTR Benchmarks:
- Generic: 4.19%
- Contextual: 14.4%
- W08 T1A (Bit2Me): 14.7%

---

## 13. Competitive Intelligence (Jan 2026)

| Metric | Bit2Me | Binance | Coinbase | Kraken |
|--------|--------|---------|---------|--------|
| Monthly Traffic | 613K | 58.81M | 35.74M | 9.87M |
| Organic Traffic | 333.9K | 13.71M | — | — |
| Authority Score | 50 | 82-83 | — | — |
| Backlinks | 1.49M | 132.31M (88.7x) | — | — |
| Bounce Rate | 70.15% | 39.81% | — | — |
| AI Search Traffic | 1,764 | 88,000 | — | — |

Key risk: Finland = #1 traffic source (31%) vs Spain (22.66%). GEO risk (Gartner 15-30% prediction on AI search disruption).

---

## 14. Pending Strategic Decisions (P0)

Three decisions requiring Pablo Campos approval:

**Decision 1 — BigQuery Access (URGENT)**
ISA departure = access loss. Grant to Daniel + Álvaro before departure.
Cost of inaction: €0 lifecycle attribution.

**Decision 2 — EMA Definition: Count Fiat Deposits?**
€500 deposit at 1.99% = €9.95 revenue = monetization event.
Impact: Fixes 20-30% invisible monetization.
SQL fix already written in FIX-001.

**Decision 3 — Inactivity Fee Strategy**
Option C recommended: Reactivation-first (D-30/D-14/D-7 sequence, fee only on non-engagement).
Net impact: +€2.1M vs current -€98K/month.
Fee: €10/month after 12 months no transaction OR 3 months no login.

---

## 15. Ghost Conversions Crisis

ROAS measurement distortion:
- ROAS total (existing + new users): 1,004%
- ROAS new users only: 62%
- Gap: ~93% of paid attribution = existing users clicking brand ads

Impact: Paid budget partially wasted on non-incremental conversions.
Solution: iROAS (Incremental ROAS) methodology needs definition. W-shaped attribution partially addresses this.
North Star metric fix: Add "ROAS New Users Only" to REFERIDOS PRINCIPALES.

---

## 16. pSEO Pilot (Active Decision This Week)

Target: €9K pilot approval from Pablo Campos.
Build vs. Buy decision: ALL components → BUY.
ROI claim: €4.27M LTV, 35,417% ROI.
Negotiation options: A (€9K) through D (€19K).
Key conversion inputs: CAC €140 paid / €56 blended, LTV €388 España, 20.35% retail conversion rate.
Build cost comparison: DIY would cost €23K-€48K vs €9K external.

---

## 17. People and Owners

| Person | Role | LC-OS Responsibility |
|--------|------|---------------------|
| Pablo Campos | CMO/Growth Director | Strategic stakeholder, P0 decisions |
| David Sales | Head of Data/BI | BigQuery Gold Layer, LTV/Churn metrics, LT algorithm |
| Pablo Talamantes | BI/Data Engineering | Qlik dashboards, BigQuery pipelines |
| Marta del Olmo | Analytics/Marketing Ops | Qlik pulls, data validation, LC MVP owner |
| Katy Gildemeister | CRM/CleverTap exec | Journey execution, segment uploads |
| Miguel | CRM/CleverTap exec | Journey execution alongside Katy |
| S. Rut / Salvia | LC product owner | Cluster definitions, 37 segments, Salvia brief |
| Juan Fornell | Product/Brokerage | C8 suppression export, cluster owner |
| Diego Barreira | Legal | Pre-send approval for ALL CRM messages |
| Álvaro Muñoz | Data infra | BigQuery attribution, Earn/Loan data |
| Maxim | Growth analyst | Space Center analysis |
| Consuelo | Paid acquisition | Google, Meta spend |

---

## 18. Technical Blockers (Active)

1. ISA access transfer: URGENT. BigQuery V1 owner unclear after ISA departure.
2. state_transition_history table: Missing. Required for V5 (stage_transitions_weekly).
3. Salvia clusters: Unavailable in BigQuery yet. 37-segment model partially blocked.
4. DCA/recurring_orders table: Missing from Qlik/BigQuery.
5. Academy user linking: Cross-product FM view blocked.
6. Card transaction history per user: P1 gap.

---

## Files Reference Map

| File | Location | What |
|------|----------|------|
| lifecycle_OS_dashboard.html | Bit2me Lifecycle 2/ | Live 8-tab HTML dashboard |
| crm_playbooks.html | Bit2me Lifecycle 2/ | 9 CRM playbooks, full operational guide |
| 02_bigquery_fixes.sql | Bit2me Lifecycle 2/ | Production SQL, 671 lines, 3 fixes |
| 02_DEPLOYMENT_GUIDE.md | Bit2me Lifecycle 2/ | 40-min deployment checklist |
| 03_37_segment_model.html | Bit2me Lifecycle 2/ | Full 37-segment detail |
| 07_pablo_decision_brief.html | Bit2me Lifecycle 2/ | 3 P0 decisions for Pablo |
| 08_second_monetization_framework.html | Bit2me Lifecycle 2/ | 2M framework, J1-J6 |
| ab-test-bot.jsx | Bit2me LC/ | React A/B decision tool |
| chunk-2-lifecycle-metrics.md | Bit2me LC/ | Stage specs, Salvia integration |
| chunk-3-reporting-attribution-testing.md | Bit2me LC/ | Flash report, attribution |
| chunk-4-data-infrastructure-roadmap.md | Bit2me LC/ | Data gaps, BigQuery gap table |
| AUDIT_v8_NORTH_STARS_AND_PRINCIPALES.txt | Bit2me 3/ | v8 metrics architecture audit |
| Marketing_Metricas_2026_COMPLETE.xlsx | Bit2me Lifecycle 2/ | v8 corrected metrics file |
