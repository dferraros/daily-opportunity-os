## 15. Final Recommendations

> **Purpose:** This is the section Pablo Campos reads first. It conveys the business case for the trigger notification system, the implementation path across three horizons (30 / 90 / 180 days), the structural blockers that must be resolved, the top risks with mitigations, and the exact first 10 actions to take on Day 1. No technical background required.
>
> **Audience:** CEO (Pablo Campos), C-suite, department heads
>
> **Owners:**
> - **Daniel** -- Strategic direction, KPI targets, escalation owner
> - **Katy** -- CleverTap execution, campaign operations, deliverability monitoring
> - **Alvaro** -- BigQuery infrastructure, scoring formulas, holdout architecture
> - **Diego** -- Legal/compliance gate for all CRM communications
> - **Engineering** -- SDK event instrumentation, deep link implementation
>
> **Cross-references:**
> - Section 12 (MVP Selection): 30-day launch plan, Top 10 MVP triggers, Top 10 Do-Not-Launch
> - Section 14 (Measurement Framework): NNV formula, holdout design, KPI targets per family
> - Section 11 (Master Trigger Table): 33 triggers across 6 families with full specifications
> - Section 10 (Scoring Formulas): Send Score Final, per-family scoring
> - Section 2 (Frequency Caps): Priority tiers, fatigue risk, DND hours
> - Section 9 (Compliance Framework): MiCA constraints, Diego review workflow

---

### 15.1 Executive Summary for Pablo Campos

Pablo, the notification system addresses three revenue gaps that together represent the largest near-term growth opportunity for [external]. Each gap is quantified with current [external] data, and the trigger system provides a concrete, measurable intervention for each.

---

#### Gap 1: The Retention Gap (The Silent Bleed)

**Current state:** M1 retention is 0.12%. For every 1,000 users who make their first trade, only 1.2 return for a second trade within 30 days.

**Benchmark:** Coinbase M1 retention is 25%. That is a 208x gap.

**Root cause:** ZERO post-first-trade notifications exist today. There is no lifecycle trigger between "first purchase" and "dormant." Users complete their first trade and enter a communication void. No congratulation, no next-step guidance, no price alert suggestion, no second-purchase nudge. They drift into dormancy in silence.

**What the trigger system does:** Creates 6 lifecycle triggers (D-01 through D-06) that intervene at the exact moment users drift. D-01 fires when a user transitions from Active to At-Risk (no trade in 14 days). D-03 fires for users who completed KYC but never traded. D-05 detects engagement decline before the user goes fully dormant. These triggers fill the post-first-trade silence with relevant, personalized notifications.

**Conservative estimate:** 3-5x M1 retention lift in 90 days. This is conservative -- industry data shows push-engaged users are 4x more engaged and 2x more retained (Airship 2025 Mobile Push Benchmarks). Even reaching 0.5% M1 retention (still 50x below Coinbase) would represent a 4x improvement and hundreds of additional monthly active traders.

---

#### Gap 2: The Dormant Revenue Gap (EUR 19.5M Sitting Idle)

**Current state:** 72,400 users hold EUR 19.5M in assets but have not traded in 90+ days. These are not churned users -- they have money in the platform. They chose [external], deposited, bought crypto, and stopped. The assets are still there.

**What the trigger system does:** Family D triggers (especially D-02 Dormant with Balance) target reactivation directly. D-02 sends a monthly email to dormant users with balance, showing portfolio performance and providing a one-tap deep link back to their portfolio.

**Revenue impact at conservative reactivation rates:**

| Reactivation Rate | Users Returning | Monthly Incremental Revenue (EUR 12/user/month avg) | Annual Impact |
|-------------------|-----------------|------------------------------------------------------|---------------|
| 1% (conservative) | 724 | EUR 8,688/month | EUR 104,256/year |
| 3% (moderate) | 2,172 | EUR 26,064/month | EUR 312,768/year |
| 5% (aggressive but achievable) | 3,620 | EUR 43,440/month | EUR 521,280/year |

Even the 1% scenario -- reactivating 724 users who already have money in the platform -- generates over EUR 100,000/year in incremental revenue. The cost to send these notifications is near zero (CleverTap email sends).

---

#### Gap 3: The A/B Revenue Gap (EUR 6k vs EUR 30k/week)

**Current state:** A/B testing generates EUR 6,000/week. Target is EUR 30,000/week.

**Bottleneck:** Not enough testable surfaces. The current A/B program runs tests on existing journeys and campaigns, but the testing surface is limited. Each test needs a distinct audience, a meaningful variation, and enough volume for statistical significance.

**What the trigger system does:** Creates 33 testable notification variants across 6 families. Each trigger becomes a permanent testing surface for copy optimization, timing experiments, channel preference tests, and frequency calibration. MVP alone provides 10 triggers x 4 implementation waves = 40+ testable variants in 30 days. Each trigger can run concurrent copy A/B tests (built into CleverTap), generating learning velocity that compounds.

**Path to EUR 30k/week:** The trigger system does not directly produce EUR 30k/week in A/B revenue. It provides the testing infrastructure -- the surfaces, the audiences, the measurement framework -- that makes EUR 30k/week achievable by multiplying the number of concurrent tests from ~3/week to 15-20/week.

---

#### Summary Table: Three Gaps

| Gap | Current State | Target State | Trigger System Impact | Timeline |
|-----|---------------|--------------|----------------------|----------|
| M1 Retention | 0.12% (1.2 users per 1,000 return) | 0.5-1.0% (3-5x lift) | 6 lifecycle triggers (D-01 to D-06) fill post-first-trade silence | 90 days for measurable lift |
| Dormant AUC | EUR 19.5M idle across 72.4k users | 1-5% reactivation = EUR 104k-521k/year | D-02 Dormant with Balance monthly reactivation trigger | 30 days to first sends |
| A/B Revenue | EUR 6k/week | EUR 30k/week | 33 triggers = 40+ testable variants in MVP alone | 30 days for expanded test surface |

---

### 15.2 MVP (30d) / V2 (90d) / V3 (180d) Phased Roadmap

The trigger system launches in three phases. Each phase builds on the infrastructure of the previous one. No phase requires capabilities that do not exist or people who are not on the team today (until V3, which requires one new hire).

---

#### 15.2.1 MVP: 30 Days -- 10 Triggers in 4 Waves

The MVP launches 10 triggers across 4 waves. Wave sequencing is based on implementation dependency, not priority -- we start with the triggers that have zero compliance requirements and build toward triggers that need Diego's approval.

| Wave | Timeline | Triggers | Family | Channel | Owner | Dependencies | Estimated Effort |
|------|----------|----------|--------|---------|-------|-------------|-----------------|
| Wave 1 | Days 1-7 | A-01 Price Target Alert, A-02 Percentage Change Alert, A-03 Watchlist Price Move | A (User Configured) | Push | Katy (3 person-days) + Engineering (2 person-days) | Price_Alert_Set and Price_Alert_Triggered events must exist in CleverTap SDK | 5 person-days total |
| Wave 2 | Days 7-14 | F-01 LTV Threshold Alert, F-04 Stablecoin De-Peg Alert | F (Protective) | Multi-channel | Katy (2 person-days) + Alvaro (3 person-days for LTV data pipeline) | LTV data available in BigQuery; stablecoin peg monitoring data source confirmed | 5 person-days total |
| Wave 3 | Days 14-21 | D-01 Active to At-Risk, D-02 Dormant with Balance, B-01 Volatility Spike, B-04 Price Breakout | D (Lifecycle) + B (Market) | Push + Email | Katy (3 person-days for templates), Diego (2 person-days for template review), Alvaro (3 person-days for scoring views) | Diego Tier 1 template approval (48h SLA); scoring formula views deployed in BigQuery | 8 person-days total |
| Wave 4 | Days 21-30 | C-01 Watched Not Bought | C (Behavioral) | In-app | Katy (2 person-days) + Engineering (2 person-days for SDK events) | Product_Viewed event instrumented in CleverTap SDK; behavioral targeting segment built | 4 person-days total |

**Total MVP effort:** 22 person-days across 30 calendar days.

**Why this wave order:**
- **Wave 1 first:** Family A triggers are user-requested. Zero compliance risk, zero Diego dependency, highest expected engagement (>5% CTR target). Quick win that proves the infrastructure works.
- **Wave 2 second:** Family F triggers are protective/safety-critical. They build trust and demonstrate that the system protects users, not just markets to them.
- **Wave 3 third:** Family D and B require Diego template approval. Submitting templates on Day 12 gives Diego the full 48h SLA to review before Day 14 target. Batching all 4 templates in one submission (not one at a time) respects Diego's time.
- **Wave 4 last:** Family C requires SDK instrumentation (Product_Viewed event). Engineering has 21 days to instrument while Katy and Diego work on Waves 1-3.

**Pre-launch prerequisites (must be complete before Wave 1):**
1. C8 whale suppression CSV uploaded to CleverTap (Katy, 1 hour)
2. Holdout segment configured in BigQuery and synced to CleverTap (Alvaro, 2 hours)
3. Push reachability baseline pulled from CleverTap (Katy, 30 minutes)

---

#### 15.2.2 V2: 90 Days -- Data Pipeline Expansion

V2 unlocks triggers that were blocked in MVP by missing data pipelines. No new compliance categories are introduced -- V2 stays within the TRANSACTIONAL/INFORMATIONAL/MARKETING classification established in V1.

| Timeline | Triggers | New Capabilities Required | Owner | Dependencies | Estimated Effort |
|----------|----------|--------------------------|-------|-------------|-----------------|
| Days 31-45 | Remaining B-family (B-02 Sudden Volume Spike, B-03 New Asset Listed, B-05 Correlation Break) | Volume spike detection query; new listing event stream | Alvaro (2 person-days) + Katy (2 person-days) | BigQuery `vw_volume_anomaly` view | 4 person-days |
| Days 31-45 | Remaining C-family (C-02 Deposit No Trade, C-03 Repeat Viewer, C-04 Inactive Alert Configs, C-05 Push Permission Nudge) | Enhanced behavioral event tracking | Katy (3 person-days) + Engineering (2 person-days) | Extended SDK events for repeat views and inactive configs | 5 person-days |
| Days 45-60 | A-05 Portfolio Value Milestone | Portfolio value aggregation across all assets per user | Alvaro (3 person-days): `user_portfolio_value` BigQuery view + Hightouch sync | `[external]_lifecycle.user_portfolio_value` view created and validated | 5 person-days |
| Days 45-60 | D-03 through D-06 (remaining lifecycle triggers) | Lifecycle stage tracking refinements | Katy (3 person-days) + Alvaro (2 person-days) | Scoring views from MVP must be validated | 5 person-days |
| Days 60-75 | E-03 Space Center Mission Alerts | Space Center entity sync to BigQuery | Alvaro (2 person-days) + Maxim (3 person-days for data model) | Space Center entities (users, tiers, missions, points) synced to BigQuery | 5 person-days |
| Days 60-75 | Earn APY Change Alerts (new trigger) | Earn APY data pipeline confirmed and instrumented | Alvaro (2 person-days) | Alvaro confirms Earn APY data exists in BigQuery; `earn_apy_history` view created | 2 person-days |
| Days 75-90 | E-01, E-02, E-04, E-05, E-06 (remaining cross-sell) | Product eligibility rules per product | Katy (3 person-days) + Diego (1 person-day for new templates) | Product awareness copy only (no yield comparisons -- that is V3) | 4 person-days |

**Total V2 effort:** ~30 person-days spread across 60 calendar days (Days 31-90).

**V2 resources by person:**
- Alvaro: 1 person-week (scoring views, portfolio aggregation, Space Center sync, Earn APY)
- Katy: 1 person-week (CleverTap campaigns for new triggers)
- Diego: 0.5 person-week (template reviews for new families)
- Maxim: 3 person-days (Space Center data model delivery)
- Engineering: 2 person-days (extended SDK events)

**V2 measurement milestone:** By Day 90, per-family holdout results are available. First NNV calibration with real [external] data replaces the EUR 2.50 industry estimate. Weekly review cadence established.

---

#### 15.2.3 V3: 180 Days -- Advanced Features + Regulatory Clarity

V3 introduces capabilities that require either new infrastructure, new hires, or regulatory clarity that does not exist today. V3 is aspirational but sequenced so that each dependency has a clear trigger for activation.

| Timeline | Triggers / Capabilities | New Infrastructure Required | Owner | Dependencies | Estimated Effort |
|----------|------------------------|-----------------------------|-------|-------------|-----------------|
| Days 91-120 | ADVISORY_RISK classified triggers | ESMA advisory guidance analysis; Diego legal framework | Diego (1 person-week for legal analysis) + External (ESMA timeline) | ESMA publishes detailed CASP advisory guidance; Diego approves ADVISORY_RISK notification template with written sign-off | 1 person-week Diego |
| Days 91-120 | Family E yield comparison copy | Diego written opinion on comparative yield language | Diego (2 person-days) | ESMA guidance on comparative marketing for CASPs published | 2 person-days |
| Days 120-150 | ML-based notification timing optimization | ML infrastructure: model training pipeline (Vertex AI or equivalent), model serving layer, 90+ days of engagement data | ML Engineer (new hire, 1 FTE) + Alvaro (1 person-week for data extraction) | ML engineer hired; training infrastructure provisioned; 90+ days of notification engagement data available | 1 FTE ongoing + 1 person-week Alvaro |
| Days 120-150 | Technical indicator triggers (RSI, MACD, Bollinger) | OHLCV candle data pipeline in BigQuery (hourly); indicator computation views | Alvaro (1 person-week) + Engineering (1 person-week) | OHLCV data ingestion pipeline built; ADVISORY_RISK clearance from Diego | 2 person-weeks |
| Days 150-180 | WhatsApp Business API channel | WhatsApp Business API integration; Meta Business verification; consent flow | Engineering (2 person-weeks) + Product (1 person-week for consent UX) | WhatsApp Business API account approved by Meta; CleverTap WhatsApp channel configured; separate consent flow built | 3 person-weeks |
| Days 150-180 | Chart-integrated alerts (Pro app) | Pro app UI changes for alert marker overlays on trading charts | Engineering - Pro team (2 release cycles) | Pro app team scopes chart overlay feature; API endpoint for alert marker data | 2 release cycles |

**V3 resources:**
- 1 ML engineer (new hire) -- required for ML scoring; no workaround
- 2 person-weeks Engineering (WhatsApp integration)
- 1 person-week Diego (ADVISORY_RISK templates + yield comparison opinion)
- 1 person-week Alvaro (OHLCV pipeline, ML data extraction)
- Pro app team (chart overlays -- separate from notification team)

**V3 aspirations (beyond 180 days):**
- Coinbase-style two-tower ML model for notification timing optimization
- Portfolio-level risk scoring combining LTV, diversification, and volatility exposure
- Cross-channel orchestration (push + email + WhatsApp + in-app unified journey)

---

### 15.3 Critical Path and Blockers

Three structural bottlenecks affect ALL phases of the trigger system. They are not technical limitations -- they are organizational constraints that must be actively managed.

---

#### Blocker 1: Diego Bottleneck (Legal Gate)

**What:** Diego Barreira is the single legal gate for ALL CRM messages at [external]. Every notification that contains marketing or informational content requires Diego's review before it can be sent. 7 of 9 existing CleverTap journeys are currently behind Diego's approval queue.

**Impact on trigger system:** Every Family B trigger (market data) and every Family D trigger (lifecycle) requires Tier 1 template approval from Diego. In the MVP, Wave 3 (4 triggers) depends entirely on Diego's review. If Diego's SLA slips from 48h to 1 week, Wave 3 shifts from Day 14-21 to Day 21-28, compressing Wave 4.

**Mitigations:**
1. **Batch template submissions.** Submit all Wave 3 templates (D-01, D-02, B-01, B-04) to Diego on Day 12 as a single package, not one at a time. This gives Diego one review session instead of four.
2. **Pre-approved template library.** After Diego approves the first batch, create a template pattern library. Future triggers can reuse approved copy patterns with variable substitution (asset name, price, percentage) without requiring full re-review.
3. **Escalation path.** If Diego's SLA exceeds 72 hours, Daniel escalates to ensure the trigger roadmap is not blocked. Diego should be aware of the 30-day launch timeline from Day 1.

---

#### Blocker 2: Alvaro SPOF (Single Point of Failure)

**What:** Alvaro Munoz currently carries 3 P0 tasks (Hightouch sync configuration, token-holder filter, W-shaped attribution model) plus the 8 scoring formula BigQuery views required by the trigger system. Adding 5 dashboard monitoring views (Section 14.5) creates 16 deliverables on a single person.

**Impact on trigger system:** If Alvaro is blocked on any P0 task, the scoring views are delayed. Without scoring views, Wave 2 (F-01 needs LTV data) and Wave 3 (D-01/D-02/B-01/B-04 need send_score) cannot launch. Alvaro is the critical path for 8 of 10 MVP triggers.

**Mitigations:**
1. **Prioritize scoring views first.** Alvaro's first deliverable should be the BigQuery scoring formula views (Section 10). These unblock ALL trigger families. Dashboard monitoring views (Section 14.5) can be deferred to Week 3-4 without blocking launches.
2. **David Sales as backup.** David Sales is building the BigQuery Gold Layer. Simpler views (like `vw_trigger_send_metrics`) can be delegated to David if Alvaro is blocked. David has BigQuery context and can handle straightforward aggregation queries.
3. **Sequence Alvaro's work.** Days 1-7: holdout assignment view + Hightouch sync config. Days 7-14: LTV and scoring formula views. Days 14-21: dashboard views. This sequencing aligns with wave dependencies.

---

#### Blocker 3: C8 Whale Suppression Gap

**What:** The C8 whale suppression CSV -- a list of high-value users who require white-glove treatment and must NOT receive automated marketing notifications -- is NOT uploaded to CleverTap. This was flagged in the LC-OS Phase A audit (March 10) and remains unresolved.

**Impact on trigger system:** Without C8 suppression, ANY P2-P5 trigger risks sending automated notifications to whale accounts. A dormant whale receiving a generic "Come back to [external]" email (D-02) instead of a personal call from their account manager is a trust violation that could result in asset withdrawal. These users hold disproportionate AUC.

**Mitigation:**
- **Day 1 prerequisite:** Katy uploads the C8 whale suppression CSV to CleverTap as a suppression segment. Estimated effort: 1 hour. This is non-negotiable -- no P2-P5 trigger launches until C8 suppression is live in CleverTap.
- **Ongoing maintenance:** C8 list must be refreshed monthly. Add to Katy's monthly operations checklist.

---

### 15.4 Top 5 Risks and Mitigations

| # | Risk | Severity | Likelihood | Mitigation | Owner |
|---|------|----------|------------|------------|-------|
| 1 | **Push opt-out cliff** -- 46% of users opt out when receiving 2-5 push notifications per week (Pushwoosh 2025). Over-sending triggers could permanently destroy the push channel for a significant portion of users. | HIGH | MEDIUM | Frequency caps enforced at 3 levels: 2/day hard cap, 8/week soft cap, 20/month absolute cap. P0-P1 triggers (transactional, user-configured) are exempt via CleverTap Exclude checkbox. fatigue_risk score (Section 2.5) gates P3-P5 sends: users with fatigue_risk > 0.6 receive NO P3-P5 triggers until score recovers. Weekly monitoring of push_disable_lift per family -- if any family exceeds 1% opt-out rate, STOP that family for 7 days. | Katy (monitoring) + Daniel (escalation) |
| 2 | **MiCA regulatory exposure** -- Family B market triggers containing editorial commentary ("Great entry point", "Don't miss this surge") constitute market manipulation under MiCA Art. 87-92. Fine: up to EUR 5M or 10% annual turnover. | CRITICAL | LOW (if mitigations hold) | Permanent prohibition on editorial language in Family B triggers (Phase 3 decision). Keyword blocklist (Section 9.3.2) enforced in all B-family copy. A/B testing on Family B copy is PROHIBITED to prevent accidental insertion of opinion language in test variants. Diego reviews all B-family templates before launch. | Diego (approval gate) + Daniel (enforcement) |
| 3 | **Holdout contamination** -- Holdout users receiving trigger notifications through alternate channels (e.g., excluded from push but receiving the same content via email lifecycle journey). This invalidates the incremental lift measurement, making NNV unreliable. | MEDIUM | MEDIUM | Global holdout suppresses ALL P2-P5 triggers across ALL channels (push, email, in-app) for the holdout segment. Implemented via deterministic FARM_FINGERPRINT hash in BigQuery, synced to CleverTap via Hightouch as `holdout_group` field. CleverTap campaigns target `holdout_global_10pct = false` as a mandatory filter. Family A and F have no holdout (user-requested and safety-critical). | Alvaro (holdout integrity) + Katy (campaign filters) |
| 4 | **NNV calibration error** -- The EUR 2.50 annual push revenue per user constant used in the NNV opt-out cost calculation is an industry estimate, not [external]-specific data. If [external]'s actual value is EUR 10/user, the NNV formula underestimates opt-out damage by 4x, potentially greenlighting triggers that destroy more value than they create. | MEDIUM | MEDIUM | Alvaro runs a calibration query after 30 days of MVP data: `total_push_attributed_revenue / total_push_reachable_users`. This replaces the EUR 2.50 estimate with actual [external] data. Until calibration, apply a 2x safety margin (treat opt-out cost as EUR 5.00 instead of EUR 2.50). | Alvaro (calibration query) + Daniel (safety margin enforcement) |
| 5 | **CleverTap External Trigger API instability** -- The CleverTap External Trigger API is in Public Beta. API instability could cause missed sends, duplicate sends, or data loss during the MVP window. | LOW | MEDIUM | Do not depend on the External Trigger API for MVP. Use segment-based targeting via Hightouch sync instead: BigQuery computes eligibility and scores, Hightouch syncs segments to CleverTap every 30 minutes, CleverTap campaigns target segments directly. API-dependent triggers are deferred to V2 after API reaches General Availability. | Alvaro (Hightouch sync) + Katy (segment-based campaigns) |

---

### 15.5 Start Here Checklist -- 10 Ordered Day-1 Actions

This checklist gives every stakeholder their first concrete action. Complete these 10 steps in order on Day 1 and the trigger system is ready for Wave 1 launch by Day 7.

---

- [ ] **1. Katy: Upload C8 whale suppression CSV to CleverTap** (1 hour)
  Upload the C8 whale account list as a suppression segment in CleverTap. Name: `C8_Whale_Suppression`. This blocks all P2-P5 automated triggers from reaching whale accounts. Non-negotiable prerequisite -- no trigger launches without this.

- [ ] **2. Katy: Pull current push reachability rate from CleverTap** (30 minutes)
  Export the current push reachability percentage (iOS and Android separately). This becomes the MEAS-03 baseline. Record the number in the measurement dashboard. If below 60% on iOS, flag for consent UX review before Wave 1.

- [ ] **3. Alvaro: Create holdout_global_10pct segment in BigQuery** (1 hour)
  Run the FARM_FINGERPRINT holdout assignment query (Section 14.3):
  ```sql
  SELECT user_id,
    CASE WHEN MOD(ABS(FARM_FINGERPRINT(CAST(user_id AS STRING))), 10) = 0
    THEN 'holdout' ELSE 'treatment' END AS holdout_group
  FROM [external]_lifecycle.user_profiles
  WHERE lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')
  ```
  Save as `[external]_lifecycle.holdout_global_10pct` materialized view.

- [ ] **4. Alvaro: Configure Hightouch sync to include holdout_group field** (1 hour)
  Add `holdout_group` as a synced field in the existing Hightouch-to-CleverTap user profile sync. Ensure it updates on each 30-minute sync cycle. Verify one test user appears with `holdout_group = 'holdout'` in CleverTap.

- [ ] **5. Katy: Create CleverTap segment "Trigger Eligible"** (30 minutes)
  Build a segment with these conditions:
  - `holdout_global_10pct` = false (not in holdout)
  - `C8_Whale_Suppression` = false (not a whale account)
  - `consent_marketing_push` = true (user has opted in to marketing push)
  This segment is the base audience for ALL P2-P5 trigger campaigns.

- [ ] **6. Engineering: Confirm Price_Alert_Set and Price_Alert_Triggered events exist in CleverTap SDK** (2 hours)
  Verify that both events fire correctly when a user creates a price alert (Price_Alert_Set) and when the alert condition is met (Price_Alert_Triggered). If events do not exist, instrument them. These are the data source for Wave 1 triggers A-01, A-02, and A-03.

- [ ] **7. Katy: Build A-01/A-02/A-03 campaigns in CleverTap** (3 hours)
  Create 3 push notification campaigns for Wave 1 triggers. Each campaign must:
  - Target the "Trigger Eligible" segment (step 5)
  - Include a 10% A/B control group (built-in CleverTap feature)
  - Use deep link `[external]://brokerage/trade?asset={symbol}` as the CTA
  - Set cooldown: 1 per asset per 4 hours
  - Set priority: P1
  Do NOT activate yet -- activation happens after Engineering confirms events (step 6).

- [ ] **8. Diego: Pre-review Family D template copy** (2 hours)
  Review the following notification templates for Tier 1 compliance approval:
  - **D-01 (At-Risk):** "Tu portafolio ha estado inactivo {days} dias. Revisa el rendimiento de tus activos." Deep link: `[external]://portfolio/overview`
  - **D-02 (Dormant with Balance):** "Tienes EUR {balance} en tu cartera [external]. Tu portafolio se ha movido {pct_change}% este mes." Deep link: `[external]://portfolio/overview`
  Submit approval by Day 5 so templates are ready for Wave 3 (Day 14). Batch review preferred.

- [ ] **9. Alvaro: Build vw_trigger_send_metrics BigQuery view** (2 hours)
  Create the monitoring view specified in Section 14.5 that aggregates:
  - sends, deliveries, opens, clicks, dismissals, opt-outs per trigger_id per day
  - Joins with holdout_group to enable treatment vs holdout comparison
  This view powers the Day 7 monitoring review for Wave 1 performance.

- [ ] **10. Daniel: Schedule Week 2 review meeting** (15 minutes)
  Schedule a 30-minute meeting for Day 8 (after Wave 1 has 7 days of data). Agenda:
  - Wave 1 CTR vs Family A target (>5%)
  - Push disable lift vs threshold (<0.5%)
  - Holdout group baseline engagement
  - Go/no-go decision for Wave 2 activation
  Attendees: Daniel, Katy, Alvaro. Diego optional (for Wave 3 planning).

---

**Total Day-1 effort across all stakeholders:** ~12 person-hours (Katy: 5h, Alvaro: 4h, Engineering: 2h, Diego: prep awareness only, Daniel: 15 min). By end of Day 1, the infrastructure is ready. By Day 7, Wave 1 is live.

---

### Cross-References

| Section in This Document | References | Purpose |
|--------------------------|-----------|---------|
| 15.1 Executive Summary | Section 14 (NNV formula), Section 11 (33 triggers), CLAUDE.md ([external] numbers) | Business case with quantified gaps |
| 15.2 Phased Roadmap | Section 12.3 (30-day plan), Section 12.4 (V2/V3 preview), Section 10 (scoring) | Implementation timeline with owners and effort |
| 15.3 Critical Path | Section 14.3 (holdout design), LC-OS Phase A audit (C8 gap), STATE.md (Alvaro SPOF) | Organizational bottleneck identification |
| 15.4 Risks | Section 2.5 (fatigue risk), Section 9 (MiCA compliance), Section 14.4 (NNV) | Risk quantification with mitigations |
| 15.5 Start Here | Section 14.3 (holdout SQL), Section 14.5 (monitoring views), Section 12.3 (wave plan) | Actionable Day-1 checklist |
