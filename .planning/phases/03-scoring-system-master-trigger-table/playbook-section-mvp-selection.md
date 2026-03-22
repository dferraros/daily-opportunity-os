## 12. MVP Selection and Launch Prioritization

> **Purpose:** This section defines the Top 10 triggers NOT to launch in the 30-day MVP window, with concrete reasoning per trigger. It also provides a 30-day launch plan for the Top 10 MVP triggers (cross-referenced from Section 11.3) and a V2/V3 roadmap preview for deferred triggers.
>
> **Owners:** Daniel (prioritization decisions), Katy (CleverTap campaign execution), Alvaro (BigQuery data pipeline readiness), Diego (compliance approval gate)
>
> **Cross-references:**
> - Section 10 (Scoring Formulas): MVP scoring methodology and Send Score thresholds
> - Section 11 (Master Trigger Table): Complete trigger specifications, Top 10 MVP marked with [MVP]
> - Section 9 (Compliance Framework): ADVISORY_RISK classification rules, Diego review workflow
> - Section 2 (Frequency Caps): Priority tier system, DND hours, fatigue risk thresholds

---

### 12.1 MVP Scoring Framework Recap

Every trigger was scored on three dimensions (1-5 scale) using the following formula:

```
MVP_Score = Impact * 2 + (5 - Risk) * 1.5 + (5 - Implementation_Complexity) * 1

Maximum possible score: 5*2 + 4*1.5 + 4*1 = 10 + 6 + 4 = 20
```

**Scoring dimensions:**

| Dimension | Weight | Signals |
|-----------|--------|---------|
| Impact | x2 | Segment size, revenue proximity, retention lift |
| Risk (inverted) | x1.5 | Compliance class, data sensitivity, push permission risk |
| Implementation Complexity (inverted) | x1 | Data availability in BigQuery, CleverTap event instrumentation, Diego pre-approval feasibility |

**Top 10 MVP triggers** (documented in Section 11.3 of the Master Trigger Table):

| Rank | trigger_id | Name | MVP Score |
|------|-----------|------|-----------|
| 1 | A-01 | Price Target Alert (Above/Below) | 20.0 |
| 2 | A-02 | Percentage Change Alert | 20.0 |
| 3 | A-03 | Watchlist Price Move | 19.0 |
| 4 | F-01 | LTV Threshold Alert (System) | 19.0 |
| 5 | D-02 | Dormant With Balance | 17.0 |
| 6 | F-04 | Stablecoin De-Peg Alert | 17.0 |
| 7 | B-01 | Volatility Spike | 16.5 |
| 8 | D-01 | Active to At-Risk Transition | 16.0 |
| 9 | C-01 | Watched Not Bought | 14.0 |
| 10 | B-04 | Price Breakout | 13.5 |

For full specifications of these 10 triggers, see Section 11.2.2. This section focuses on the inverse: what NOT to build.

---

### 12.2 Top 10 Triggers Do Not Launch (30-Day Window)

These 10 triggers (or trigger categories) must NOT be launched in the MVP 30-day window. Each entry includes the specific reason, the timeline for future consideration, the prerequisite that must be met, and the concrete risk if launched prematurely.

---

**1. Any ADVISORY_RISK Classified Trigger**

- **trigger_id:** ADV-01 through ADV-06 (not yet assigned formal IDs -- these are V3 concepts)
- **Name:** All triggers that could be construed as suggesting an investment action
- **WHY NOT:** MiCA Art. 81 territory. ESMA is developing detailed guidance on what constitutes "investment advice" in the context of crypto-asset notifications, but this guidance has not been published as of March 2026. Launching a notification that crosses the INFORMATIONAL-to-ADVISORY boundary exposes Bit2Me to sanctions of up to EUR 5M or 10% of annual turnover (MiCA Art. 111). The compliance classification decision tree (Section 9.1.2) explicitly reserves ADVISORY_RISK for V3.
- **WHEN:** V3 (180 days) at the earliest, after ESMA publishes detailed guidance on the advisory boundary for CASPs.
- **PREREQUISITE:** (1) ESMA advisory guidance published and analyzed by Diego, (2) Diego approves a specific ADVISORY_RISK notification template, (3) internal legal review completed with written sign-off.
- **What happens if we launch anyway:** Potential EUR 5M fine or 10% annual turnover penalty from CNMV. Reputational damage with Spanish regulator. Possible suspension of marketing communications pending investigation.

---

**2. Family E Triggers with Return/Yield Comparisons**

- **trigger_id:** E-01 through E-06 (when copy includes comparative yield language)
- **Name:** Cross-sell notifications comparing crypto yields to traditional finance
- **WHY NOT:** Copy like "Earn 3.2% vs 0% in your Wallet" or "Earn beats your savings account" crosses from INFORMATIONAL/MARKETING into ADVISORY_RISK territory (Section 9.1, compliance decision tree Question 3). Phase 2 decision explicitly states: "Family E cross-sell must use product awareness framing only in V1; return comparisons deferred." The comparison implies Bit2Me is recommending one financial product over another -- this is investment advice under MiCA Art. 81.
- **WHEN:** V3 (180 days), after Diego dedicated legal review of comparative yield language.
- **PREREQUISITE:** (1) Diego issues a written opinion on which comparative language is permissible, (2) ESMA guidance on comparative marketing for CASPs is published, (3) a specific template passes Tier 1 Diego review.
- **What happens if we launch anyway:** Same regulatory risk as item 1 (EUR 5M / 10%). Additionally, Bit2Me's status as a regulated CASP in Spain means CNMV scrutiny is higher than for unregulated operators. One regulatory complaint could trigger a full marketing communications audit.

---

**3. Family B Triggers with Editorial Commentary**

- **trigger_id:** B-01 through B-05 (when copy includes editorial/opinion language)
- **Name:** Market triggers with subjective commentary ("Great entry point", "Don't miss this surge")
- **WHY NOT:** Editorial commentary transforms a factual INFORMATIONAL notification into ADVISORY_RISK territory. The keyword blocklist (Section 9.3.2) explicitly flags terms like "opportunity", "don't miss", "entry point", "bargain", and "undervalued". Phase 2 decision states: "A/B testing on Family B triggers PROHIBITED to prevent market abuse risk." Adding editorial language on top of market data compounds this risk.
- **WHEN:** NEVER for editorial/opinion language. Factual Family B triggers (pure market data) ARE in the MVP. The copy constraint is permanent, not timeline-dependent.
- **PREREQUISITE:** N/A -- editorial commentary in market notifications is a permanent prohibition under MiCA Art. 87-92 (market abuse prevention).
- **What happens if we launch anyway:** Market manipulation allegation from CNMV. If a user buys an asset after receiving "Great entry point for ETH" and loses money, Bit2Me faces potential civil liability AND regulatory sanction. This is the highest-risk item on the list.

---

**4. Portfolio-Level Alerts (A-05 Aggregate Portfolio Value)**

- **trigger_id:** A-05 (Portfolio Value Milestone)
- **Name:** Portfolio-level value tracking and milestone alerts
- **WHY NOT:** Requires BigQuery portfolio value aggregation across all assets per user. This data pipeline does not exist today. Alvaro would need to build a `user_portfolio_value` view that joins `user_holdings` with real-time price data across all held assets. Given Alvaro's current workload (3 P0 tasks: Hightouch sync, token-holder filter, attribution), adding portfolio aggregation in the 30-day window is not feasible.
- **WHEN:** V2 (90 days), after Alvaro delivers Hightouch sync and scoring formula views.
- **PREREQUISITE:** (1) `bit2me_lifecycle.user_portfolio_value` BigQuery view created and validated, (2) Hightouch sync includes aggregate portfolio value field, (3) CleverTap user profile has `portfolio_total_eur` property.
- **What happens if we launch anyway:** Engineering time diverted from MVP scoring infrastructure. Delayed delivery of the 8 scoring formulas that ALL other triggers depend on. Net negative ROI: one engagement trigger vs. blocking the entire scoring pipeline.

---

**5. AI Market Insights (Concept: ML-Based Alert Timing)**

- **trigger_id:** ADV-02 (concept, not in master table)
- **Name:** Machine learning-based trigger timing optimization
- **WHY NOT:** Requires ML infrastructure that Bit2Me does not have. The Coinbase two-tower model (user embedding + context embedding) for notification timing optimization took a dedicated ML team 6+ months to build and validate. Bit2Me has zero ML infrastructure, no model training pipeline, and no model serving layer. This is a V3 aspiration, not a V1 possibility.
- **WHEN:** V3 (180 days), and only if ML engineering headcount is hired.
- **PREREQUISITE:** (1) ML engineering team hired (minimum 1 ML engineer), (2) model training infrastructure (Vertex AI or equivalent), (3) model serving layer for real-time scoring, (4) 90+ days of notification engagement data to train on.
- **What happens if we launch anyway:** Cannot launch -- the infrastructure literally does not exist. Attempting to build it diverts 100% of Alvaro's capacity for 3+ months with no notification system delivered.

---

**6. Space Center Mission Triggers (E-03)**

- **trigger_id:** E-03
- **Name:** Space Center mission available / tier progression notification
- **WHY NOT:** Space Center data is not yet in BigQuery. No Hightouch sync is configured for Space Center entities (missions, tiers, points). Maxim is currently analyzing Space Center (assigned Feb 25) but has not delivered the data model. Without `space_center_tier`, `space_center_points`, and `available_missions` in BigQuery, there is no data source to power this trigger.
- **WHEN:** V2 (90 days), after Space Center BigQuery integration is complete.
- **PREREQUISITE:** (1) Space Center entities (users, tiers, missions, points) are synced to BigQuery, (2) Hightouch sync includes Space Center fields, (3) CleverTap user profile has `space_center_tier` and `available_missions` properties, (4) deep link `bit2me://space-center/missions` is tested and working.
- **What happens if we launch anyway:** Trigger would fire with null data or incorrect eligibility. Users could receive "Complete your next mission" when they have no missions available. Trust erosion + support ticket volume increase.

---

**7. Earn Rate Change Alerts (Concept: Earn APY Notifications)**

- **trigger_id:** Not yet assigned (concept trigger for Earn APY changes)
- **Name:** Notification when Earn staking APY changes for an asset the user holds or has staked
- **WHY NOT:** The Earn APY data pipeline has not been confirmed as available in BigQuery. Need Alvaro to confirm: (a) whether Earn APY rates are stored in any BigQuery table, (b) whether historical APY changes are logged (needed for "rate changed" detection), (c) whether the data updates in real-time or batch. Without confirmed data source, the trigger cannot be built.
- **WHEN:** V2 (90 days), after Alvaro confirms Earn APY data source.
- **PREREQUISITE:** (1) Alvaro confirms Earn APY data exists in BigQuery or identifies the source system, (2) `bit2me_lifecycle.earn_apy_history` view is created, (3) Change detection logic is implemented (current APY vs. previous APY).
- **What happens if we launch anyway:** Cannot launch -- no data source. If we fabricate APY data from external sources, we risk displaying incorrect rates, which violates MiCA Art. 66 (fair, clear, not misleading).

---

**8. Chart-Integrated Alerts (Concept: Visual Overlays on Pro Charts)**

- **trigger_id:** ADV-03 (concept, not in master table)
- **Name:** Price alert markers overlaid on Pro trading charts (Kraken-style feature)
- **WHY NOT:** Requires Pro app UI changes to overlay alert markers on trading charts. This is a frontend engineering dependency -- the notification system cannot implement it alone. Kraken's chart-integrated alerts took their team 2 release cycles. Bit2Me's Pro app development team has not scoped this work.
- **WHEN:** V3 (180 days), requires Product and Engineering roadmap alignment.
- **PREREQUISITE:** (1) Pro app team scopes chart overlay feature, (2) API endpoint for alert marker data, (3) Frontend implementation in Pro charting library, (4) QA testing across mobile and web.
- **What happens if we launch anyway:** Cannot launch -- requires code changes in a separate team's codebase. Attempting to force-ship would create a half-implemented feature (alerts without visual context), worse than no feature.

---

**9. Technical Indicator Triggers (Concept: RSI Oversold, MACD Crossover)**

- **trigger_id:** ADV-06 (concept, not in master table)
- **Name:** Notifications based on technical analysis indicators (RSI below 30, MACD bullish crossover, Bollinger Band breach)
- **WHY NOT:** Requires a technical analysis computation pipeline. RSI, MACD, and Bollinger Bands need continuous calculation across all T1+T3 assets using OHLCV candle data. This is a significant data engineering project: (a) OHLCV data ingestion at 1-hour or 15-minute intervals, (b) indicator computation (rolling windows, exponential moving averages), (c) threshold detection. Additionally, technical indicator alerts have HIGH ADVISORY_RISK classification -- "RSI below 30 (oversold)" implies a buy signal.
- **WHEN:** V3 (180 days), depends on both data pipeline AND ESMA advisory guidance.
- **PREREQUISITE:** (1) OHLCV candle data pipeline in BigQuery (hourly minimum), (2) Technical indicator computation views (RSI, MACD, Bollinger), (3) ADVISORY_RISK cleared by Diego (see item 1), (4) Copy templates that present indicators as factual data without implied action.
- **What happens if we launch anyway:** Double risk: (a) data pipeline does not exist, so cannot compute indicators, (b) even if computed, "RSI oversold" is the textbook example of investment advice -- guaranteed CNMV regulatory action.

---

**10. WhatsApp Channel Triggers**

- **trigger_id:** ADV-05 (concept, not in master table)
- **Name:** Notifications delivered via WhatsApp Business API
- **WHY NOT:** WhatsApp as a notification channel is not available at Bit2Me. Requires: (a) WhatsApp Business API integration, (b) Meta Business verification, (c) user phone number collection and consent management, (d) CleverTap WhatsApp channel configuration. This is an infrastructure and partnership dependency, not a content or logic issue.
- **WHEN:** V3 (180 days), requires Product roadmap commitment and Meta partnership.
- **PREREQUISITE:** (1) WhatsApp Business API account approved by Meta, (2) CleverTap WhatsApp channel configured, (3) User consent flow for WhatsApp notifications built (separate from push/email consent), (4) Phone number data quality validated in BigQuery.
- **What happens if we launch anyway:** Cannot launch -- channel does not exist. No technical workaround possible. Users in LatAm markets (where WhatsApp dominates) receive push/email instead, which is the current plan for V1.

---

### 12.3 30-Day Launch Plan Summary

The Top 10 MVP triggers launch in 4 waves over 30 days. Wave sequencing is based on implementation dependencies, compliance review sequencing, and data pipeline readiness.

| Wave | trigger_ids | Name | Owner | First Action | Target Launch |
|------|------------|------|-------|-------------|---------------|
| Wave 1 (Days 1-7) | A-01, A-02, A-03 | Family A: User Configured Alerts | Katy (CleverTap), Engineering (SDK events) | Confirm Price_Alert_Set event exists in CleverTap | Day 7 |
| Wave 2 (Days 7-14) | F-01, F-04 | Family F: Protective Alerts | Katy (CleverTap), Alvaro (LTV data) | Validate LTV data pipeline in BigQuery; confirm stablecoin peg monitoring | Day 14 |
| Wave 3 (Days 14-21) | D-01, D-02, B-01, B-04 | Family D (Lifecycle) + Family B (Market) | Katy (templates), Diego (copy approval), Alvaro (scoring views) | Submit D-01 and D-02 templates to Diego for Tier 1 approval | Day 21 |
| Wave 4 (Days 21-30) | C-01 | Family C: Behavioral | Katy (CleverTap), Engineering (SDK events) | Confirm Product_Viewed and Purchase events exist; build behavioral targeting segment | Day 30 |

**Critical dependencies that must be resolved BEFORE any trigger launches:**

1. **C8 Whale Suppression CSV:** Must be uploaded to CleverTap as a suppression segment. Currently NOT uploaded (flagged in LC-OS Phase A audit). Without this, P2-P5 triggers risk sending to high-value dormant users who require white-glove treatment. **Owner: Katy. Deadline: Day 1.**

2. **Hightouch sync configuration:** Must include all scoring formula fields (`market_relevance_score`, `user_asset_affinity_score`, `notification_fatigue_score`, `churn_risk_score`, `send_score_final`) before trigger activation. Without these fields in CleverTap, campaign targeting cannot apply score thresholds. **Owner: Alvaro. Deadline: Day 7.**

3. **Diego template pre-approval:** Family D and B triggers require Diego Tier 1 template approval (48-hour SLA). Templates must be submitted by Day 12 to meet Wave 3 deadline. **Owner: Katy (template creation), Diego (review).**

---

### 12.4 V2/V3 Roadmap Preview

#### V2 (90 Days): Data Pipeline Expansion

Triggers that move from "Do Not Launch" to "Launchable" in V2:

| # | Trigger | Prerequisite That Must Be Met | Owner |
|---|---------|-------------------------------|-------|
| 4 | A-05 Portfolio Value Milestone | `user_portfolio_value` BigQuery view + Hightouch sync | Alvaro |
| 6 | E-03 Space Center Missions | Space Center entities in BigQuery + Hightouch sync | Alvaro + Maxim |
| 7 | Earn Rate Change Alerts | Earn APY data source confirmed + `earn_apy_history` view | Alvaro |

**V2 also enables:** All remaining non-MVP triggers from the master table (B-02, B-03, B-05, C-02 through C-05, D-03 through D-06, E-01, E-02, E-04 through E-06, F-02, F-03, F-05, F-06) that have data available but were not prioritized for the 30-day window. These triggers have scored lower on the MVP framework but are implementable with V1 infrastructure.

#### V3 (180 Days): Advanced Features + Regulatory Clarity

Triggers that remain blocked until V3:

| # | Trigger | Prerequisite That Must Be Met | Owner |
|---|---------|-------------------------------|-------|
| 1 | ADVISORY_RISK triggers | ESMA advisory guidance published + Diego legal review | Diego + External |
| 2 | Yield comparison copy | Diego written opinion on comparative language | Diego |
| 5 | AI Market Insights (ML scoring) | ML engineer hired + training infrastructure + 90d data | Engineering + HR |
| 8 | Chart-Integrated Alerts | Pro app team scopes + implements chart overlay | Engineering (Pro) |
| 9 | Technical Indicator Triggers | OHLCV pipeline + indicator computation + ADVISORY_RISK clearance | Alvaro + Diego |
| 10 | WhatsApp Channel | WhatsApp Business API + Meta verification + consent flow | Product + Engineering |

**V3 aspirations (beyond 180 days):**
- Coinbase-style two-tower ML model for notification timing optimization
- Portfolio-level risk scoring combining LTV, diversification, and volatility exposure
- Cross-channel orchestration (push + email + WhatsApp + in-app unified journey)

---

### 12.5 Cross-References

- **Section 11 (Master Trigger Table):** Complete specifications for all 33 triggers, including the 10 MVP triggers marked with [MVP] tags
- **Section 10 (Scoring Formulas):** Threshold calibration for send_score per family (A: N/A, B: 0.40, C: 0.50, D: 0.35, E: 0.55, F: N/A)
- **Section 9 (Compliance Framework):** ADVISORY_RISK classification rules (Section 9.1), Diego review workflow (Section 9.2), keyword blocklist (Section 9.3.2)
- **Section 2 (Frequency Caps):** Priority tier override rules, DND hours, fatigue risk thresholds
- **REQUIREMENTS.md:** v2 acceptance criteria and Out of Scope items for deferred features
