## 11. Master Trigger Table

> **Purpose:** This section is the single source of truth for every trigger in Bit2Me's notification system. It expands the 24 triggers defined in Section 6 (Trigger Taxonomy) to 33 fully specified triggers, each with all 14 required columns. The table is designed so that Katy, Alvaro, Engineering, and Diego can implement any trigger by reading its row -- no additional context needed.
>
> **Owners:**
> - **Katy** -- CleverTap campaign setup, template creation, audience targeting
> - **Alvaro** -- BigQuery scoring queries, Hightouch sync configuration, data source validation
> - **Diego** -- Compliance review per trigger (Tier 1 template approval, Tier 2 campaign approval)
> - **Engineering** -- Deep link implementation, SDK event instrumentation, Cloud Function triggers
>
> **Dependencies:**
> - Section 6 (Trigger Taxonomy): family definitions, eligibility rules, compliance classes
> - Section 7 (Asset Universe): asset scope rules per family (Layer 1/2/3)
> - Section 9 (Compliance Framework): compliance class requirements, Diego review workflow, keyword blocklist
> - Section 10 (Scoring Formulas): formula names referenced in `formula_used` column
> - Section 2 (Frequency Caps): priority tiers P0-P5, cooldown rules, fatigue risk thresholds

---

### 11.1 Table Schema

Every trigger in the Master Trigger Table must contain all 14 columns. No column may be left empty.

| # | Column | Type | Valid Values | Description |
|---|--------|------|-------------|-------------|
| 1 | `trigger_id` | string | `[A-F]-\d{2}` | Unique identifier. Letter = family, number = sequence within family. |
| 2 | `family` | enum | A, B, C, D, E, F | Trigger family from Section 6. |
| 3 | `business_objective` | string | engagement, activation, retention, revenue, risk_protection, reactivation, discovery | Primary business goal this trigger drives. |
| 4 | `who_receives` | string | Segment/eligibility description | Who is eligible to receive this notification. |
| 5 | `who_never_receives` | string | Hard exclusion list | Who is always excluded, regardless of eligibility. Must reference C8_Whale_Suppression where applicable. |
| 6 | `asset_scope` | enum | Layer 1 (all listed), Layer 2 ([product]-eligible), Layer 3 (user holdings/interactions), N/A (lifecycle) | Asset eligibility rule from Section 7.3. |
| 7 | `formula_used` | string | Score name(s) from Section 10 | Which scoring formula(s) determine send eligibility. |
| 8 | `threshold` | string | Numeric threshold or "N/A" | Minimum send_score or market condition threshold required to fire. |
| 9 | `cooldown` | string | Duration per user | Minimum time between fires for the same user. |
| 10 | `channel` | string | push, email, in-app, push+email, multi | Primary delivery channel(s). |
| 11 | `deep_link` | string | `bit2me://[product]/[action]` pattern | Alert-to-action deep link. MANDATORY -- no trigger ships without one. |
| 12 | `priority` | enum | P0, P1, P2, P3, P4, P5 | Priority tier from Section 2.3. Determines cap exemption, fatigue filtering. |
| 13 | `estimated_value` | string | HIGH, MEDIUM, LOW | Estimated business value per send. HIGH = directly drives revenue/retention. MEDIUM = engagement driver. LOW = nice-to-have. |
| 14 | `estimated_risk` | string | LOW, MEDIUM, HIGH | Regulatory/deliverability risk. LOW = transactional/user-requested. MEDIUM = moderate regulatory exposure. HIGH = compliance-intensive. |

**Column dependencies:**
- `asset_scope` must conform to Section 7.3 family scope rules
- `formula_used` must reference formulas defined in Section 10
- `threshold` must align with Section 10 Send Score thresholds per family
- `priority` must align with Section 2.3 priority tier definitions
- `deep_link` must use patterns from CHAN-02 (Section 11.4)

---

### 11.2 Complete Trigger Table

#### 11.2.1 Compact Reference Table

This table provides a quick-scan view of all 33 triggers with the 8 most-referenced columns. For full 14-column specification, see Section 11.2.2.

| trigger_id | family | business_objective | priority | channel | deep_link | threshold | cooldown | MVP |
|------------|--------|-------------------|----------|---------|-----------|-----------|----------|-----|
| A-01 | A | engagement | P1 | push | `bit2me://brokerage/trade?asset={symbol}` | N/A | 1/asset/4h | [MVP] |
| A-02 | A | engagement | P1 | push | `bit2me://brokerage/trade?asset={symbol}` | N/A | 1/asset/4h | [MVP] |
| A-03 | A | engagement | P1 | push | `bit2me://wallet/asset?symbol={symbol}` | N/A | 1/asset/4h; max 3/day | [MVP] |
| A-04 | A | risk_protection | P1 | push+email | `bit2me://loan/collateral?loan_id={id}` | N/A | 1/loan/4h | |
| A-05 | A | engagement | P1 | push | `bit2me://portfolio/overview` | N/A | 1/day | |
| B-01 | B | engagement | P3 | push | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.40 | 1/day; 3/week | [MVP] |
| B-02 | B | engagement | P3 | push | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.40 | 1/day; 3/week | |
| B-03 | B | discovery | P3 | push | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.40 | 1/day; 3/week | |
| B-04 | B | engagement | P3 | push | `bit2me://pro/chart?pair={symbol}-EUR` | send_score >= 0.40 | 1/day; 3/week | [MVP] |
| B-05 | B | discovery | P3 | push | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.40 | 1/listing event | |
| C-01 | C | revenue | P3 | in-app | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.50 | 1/week/asset; 2/week C-family | [MVP] |
| C-02 | C | activation | P3 | in-app | `bit2me://brokerage/trade?asset=BTC` | send_score >= 0.50 | 1/deposit event | |
| C-03 | C | revenue | P3 | in-app | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.50 | 1/week/asset; 2/week | |
| C-04 | C | engagement | P4 | in-app | `bit2me://portfolio/overview` | send_score >= 0.50 | 1/month | |
| C-05 | C | activation | P3 | push+email | `bit2me://settings/notifications` | send_score >= 0.50 | 1/week; 3 max total | |
| D-01 | D | retention | P2 | push+email | `bit2me://portfolio/overview` | send_score >= 0.35 | 1/transition event | [MVP] |
| D-02 | D | reactivation | P5 | email | `bit2me://portfolio/overview` | send_score >= 0.35 | 1/month | [MVP] |
| D-03 | D | activation | P2 | push | `bit2me://brokerage/trade?asset={symbol}` | send_score >= 0.35 | once (first trade ever) | |
| D-04 | D | retention | P2 | push+email | `bit2me://settings/notifications` | send_score >= 0.35 | 1/week until resolved | |
| D-05 | D | retention | P2 | push+email | `bit2me://portfolio/overview` | send_score >= 0.35 | 1/week | |
| D-06 | D | retention | P2 | push | `bit2me://portfolio/overview` | send_score >= 0.35 | once per reactivation | |
| E-01 | E | revenue | P4 | email | `bit2me://earn/stake?asset={symbol}` | send_score >= 0.55 | 1/week; 2/month | |
| E-02 | E | revenue | P4 | email | `bit2me://loan/collateral?loan_id={id}` | send_score >= 0.55 | 1/week; 2/month | |
| E-03 | E | engagement | P4 | in-app | `bit2me://space-center/missions` | send_score >= 0.55 | 1/week; 2/month | |
| E-04 | E | revenue | P4 | email | `bit2me://pro/chart?pair={symbol}-EUR` | send_score >= 0.55 | 1/week; 2/month | |
| E-05 | E | revenue | P4 | email | `bit2me://card/activate` | send_score >= 0.55 | 1/week; 2/month | |
| E-06 | E | revenue | P4 | in-app | `bit2me://pay/merchants` | send_score >= 0.55 | 1/week; 2/month | |
| F-01 | F | risk_protection | P0-P1 | multi | `bit2me://loan/collateral?loan_id={id}` | N/A | 1/tier/4h | [MVP] |
| F-02 | F | risk_protection | P1 | push+email | `bit2me://portfolio/overview` | N/A | 1/30 days | |
| F-03 | F | risk_protection | P1 | push+email | `bit2me://settings/notifications` | N/A | 1/failure event | |
| F-04 | F | risk_protection | P0 | push+email | `bit2me://wallet/asset?symbol={symbol}` | N/A | 1/24h per stablecoin | [MVP] |
| F-05 | F | risk_protection | P0 | push+email | `bit2me://settings/notifications` | N/A | 1/event | |
| F-06 | F | risk_protection | P1 | push+email | `bit2me://wallet/asset?symbol={symbol}` | N/A | 1/transaction | |

**Family distribution:** A=5, B=5, C=5, D=6, E=6, F=6. Total: 33 triggers.

---

#### 11.2.2 Detailed Trigger Specifications

Each trigger is specified below with all 14 columns in vertical key-value format for readability. Triggers are grouped by family.

---

##### Family A: User Configured

**A-01: Price Target Alert (Above/Below)** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | A-01 |
| family | A |
| business_objective | engagement |
| who_receives | Any user who created a price alert via Price_Alert_Set event |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | Layer 1 (all listed) -- user selects asset explicitly |
| formula_used | N/A (user-requested, always fires when condition met) |
| threshold | N/A (always sends when price crosses target) |
| cooldown | 1 per asset per 4 hours |
| channel | push (primary), email (fallback if push disabled) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P1 |
| estimated_value | HIGH -- highest engagement driver, proven pattern across all competitors |
| estimated_risk | LOW -- TRANSACTIONAL, user-requested, no compliance concern |

---

**A-02: Percentage Change Alert** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | A-02 |
| family | A |
| business_objective | engagement |
| who_receives | Any user who created a percentage alert via Price_Alert_Set event (condition_type = 'pct_change') |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | Layer 1 (all listed) |
| formula_used | N/A (user-requested) |
| threshold | N/A (always sends when % threshold crossed) |
| cooldown | 1 per asset per 4 hours |
| channel | push (primary), email (fallback) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P1 |
| estimated_value | HIGH -- volatility awareness drives trading activation |
| estimated_risk | LOW -- TRANSACTIONAL, user-requested |

---

**A-03: Watchlist Price Move** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | A-03 |
| family | A |
| business_objective | engagement |
| who_receives | Any user with watchlisted assets AND watchlist alerts enabled |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | Layer 1 (all listed) -- scoped to user's watchlist |
| formula_used | N/A (user-requested via watchlist) |
| threshold | N/A (fires when watchlisted asset moves > user-configured %, default 5% in 24h) |
| cooldown | 1 per asset per 4 hours; max 3 watchlist alerts per day |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://wallet/asset?symbol={symbol}` |
| priority | P1 |
| estimated_value | HIGH -- Coinbase gold standard pattern, drives daily engagement |
| estimated_risk | LOW -- TRANSACTIONAL, user-requested |

---

**A-04: LTV Threshold Alert (User-Configured)**

| Column | Value |
|--------|-------|
| trigger_id | A-04 |
| family | A |
| business_objective | risk_protection |
| who_receives | Users with active loans who configured a custom LTV alert |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | Layer 2 (Loan-eligible) -- collateral assets only (BTC, ETH, stablecoins) |
| formula_used | N/A (user-requested monitoring) |
| threshold | N/A (fires at user-defined LTV level) |
| cooldown | 1 per loan per 4 hours |
| channel | push (immediate), email (persistent record) |
| deep_link | `bit2me://loan/collateral?loan_id={id}` |
| priority | P1 |
| estimated_value | MEDIUM -- niche audience (loan users), high per-user value |
| estimated_risk | LOW -- TRANSACTIONAL, user-configured |

---

**A-05: Portfolio Value Milestone** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | A-05 |
| family | A |
| business_objective | engagement |
| who_receives | Any user who configured a portfolio value target via Portfolio_Alert_Set event |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | Layer 1 (all listed) -- aggregate portfolio value across all held assets |
| formula_used | N/A (user-requested) |
| threshold | N/A (fires when total portfolio EUR value crosses user-defined milestone) |
| cooldown | 1 per day |
| channel | push (primary) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P1 |
| estimated_value | MEDIUM -- engagement driver, reinforces portfolio monitoring habit |
| estimated_risk | LOW -- TRANSACTIONAL, user-requested |

---

##### Family B: Market Triggered

**B-01: Volatility Spike** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | B-01 |
| family | B |
| business_objective | engagement |
| who_receives | consent_marketing_push = true AND (holds_asset OR asset_on_watchlist) |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed B-family in last 7 days |
| asset_scope | Layer 1 filtered by volume (T1 + top T3 with daily volume > EUR 10K) |
| formula_used | Market Relevance Score + User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.40 |
| cooldown | 1/day; 3/week |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | HIGH -- market engagement during high-activity periods drives trading volume |
| estimated_risk | MEDIUM -- INFORMATIONAL class, MiCA Art. 87-92 market abuse protocol applies. Public data source mandatory. Simultaneous send mandatory. No A/B testing. |

---

**B-02: Volume Spike**

| Column | Value |
|--------|-------|
| trigger_id | B-02 |
| family | B |
| business_objective | engagement |
| who_receives | consent_marketing_push = true AND (holds_asset OR asset_on_watchlist) |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed B-family in last 7 days |
| asset_scope | Layer 1 filtered by volume (T1 + top T3 with daily volume > EUR 10K) |
| formula_used | Market Relevance Score + User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.40 |
| cooldown | 1/day; 3/week |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | MEDIUM -- volume anomalies indicate unusual interest but less actionable than volatility |
| estimated_risk | MEDIUM -- INFORMATIONAL, MiCA market abuse protocol applies |

---

**B-03: Trending Asset**

| Column | Value |
|--------|-------|
| trigger_id | B-03 |
| family | B |
| business_objective | discovery |
| who_receives | consent_marketing_push = true AND (holds_asset OR asset_on_watchlist OR traded_similar_category_last_90d) |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed B-family in last 7 days |
| asset_scope | Layer 1 filtered by volume (T1 + top T3 with daily volume > EUR 10K) |
| formula_used | Market Relevance Score + User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.40 |
| cooldown | 1/day; 3/week |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | MEDIUM -- discovery driver, expands user interest in new assets |
| estimated_risk | MEDIUM -- INFORMATIONAL, copy must be purely factual ("ETH is trending on CoinGecko"). MiCA market abuse protocol applies. |

---

**B-04: Price Breakout** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | B-04 |
| family | B |
| business_objective | engagement |
| who_receives | consent_marketing_push = true AND (holds_asset OR asset_on_watchlist) |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed B-family in last 7 days |
| asset_scope | Layer 1 filtered by volume (T1 + top T3 with daily volume > EUR 10K) |
| formula_used | Market Relevance Score + User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.40 |
| cooldown | 1/day; 3/week |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://pro/chart?pair={symbol}-EUR` |
| priority | P3 |
| estimated_value | MEDIUM -- simple technical signal, lower conversion rate than volatility but high engagement |
| estimated_risk | MEDIUM -- INFORMATIONAL, breakout language must be neutral. MiCA market abuse protocol applies. |

---

**B-05: New Listing Announcement** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | B-05 |
| family | B |
| business_objective | discovery |
| who_receives | consent_marketing_push = true AND opted into Market Alerts (CAT-MKT) |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7 |
| asset_scope | Layer 1 (the newly listed asset) |
| formula_used | N/A (event-driven, one-time announcement) |
| threshold | send_score >= 0.40 |
| cooldown | 1 per listing event (fires once per new asset) |
| channel | push (primary), in-app (secondary) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | MEDIUM -- drives early trading volume for new listings |
| estimated_risk | MEDIUM -- INFORMATIONAL/MARKETING boundary. Must not imply opportunity. Copy: "New asset available: {name}." MiCA market abuse protocol applies: no pre-announcement timing. |

---

##### Family C: Behavioral

**C-01: Watched Not Bought** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | C-01 |
| family | C |
| business_objective | revenue |
| who_receives | Users who viewed asset page 3+ times in 7 days AND did NOT purchase that asset AND consent_marketing_inapp = true OR consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | Layer 3 (user interactions) -- the specific asset(s) the user viewed |
| formula_used | User Asset Affinity Score + Trigger Opportunity Score -> Send Score Final |
| threshold | send_score >= 0.50 |
| cooldown | 1/week per asset; max 2 behavioral nudges per week across all C-family |
| channel | in-app (primary), push (secondary) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | HIGH -- proven conversion pattern across industries, directly drives purchase |
| estimated_risk | MEDIUM -- MARKETING class, Diego Tier 1 required. Copy must avoid action suggestion. |

---

**C-02: Deposit No Trade (72h)**

| Column | Value |
|--------|-------|
| trigger_id | C-02 |
| family | C |
| business_objective | activation |
| who_receives | Users who completed a deposit AND no Purchase_Completed in 72h after deposit AND consent_marketing_inapp = true OR consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | Layer 3 (user interactions) -- not asset-specific (user has not chosen yet) |
| formula_used | Trigger Opportunity Score + Churn Risk Score -> Send Score Final |
| threshold | send_score >= 0.50 |
| cooldown | Once per deposit event |
| channel | in-app (primary), push (secondary) |
| deep_link | `bit2me://brokerage/trade?asset=BTC` (default to BTC as most common first trade) |
| priority | P3 |
| estimated_value | HIGH -- deposit-to-first-trade is a critical activation funnel step |
| estimated_risk | MEDIUM -- MARKETING class, Diego Tier 1 required |

---

**C-03: Abandoned Order**

| Column | Value |
|--------|-------|
| trigger_id | C-03 |
| family | C |
| business_objective | revenue |
| who_receives | Users who triggered Order_Started event AND no Purchase_Completed within 30 min for the same asset AND consent_marketing_inapp = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | Layer 3 (user interactions) -- the specific asset from the abandoned order |
| formula_used | User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.50 |
| cooldown | 1/week per asset; max 2 abandoned order nudges per week |
| channel | in-app (primary), push (secondary -- only if user does not return within 4h) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P3 |
| estimated_value | HIGH -- highest-intent behavioral signal (user was about to purchase) |
| estimated_risk | MEDIUM -- MARKETING class, Diego Tier 1 required |

---

**C-04: Repeated Login Without Action**

| Column | Value |
|--------|-------|
| trigger_id | C-04 |
| family | C |
| business_objective | engagement |
| who_receives | Users with 5+ App_Launched events in 14 days AND zero value actions in same period AND consent_marketing_inapp = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7, lifecycle_stage IN (DORMANT_BAL, DORMANT_ZERO, CHURNED) |
| asset_scope | N/A (lifecycle) -- engagement-based, not asset-based |
| formula_used | Churn Risk Score + Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.50 |
| cooldown | 1/month |
| channel | in-app (primary -- feature discovery card on next login) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P4 |
| estimated_value | LOW -- soft engagement nudge, low direct revenue impact |
| estimated_risk | LOW -- MARKETING class but low MiCA risk (feature discovery, no asset mention) |

---

**C-05: KYC Started Not Completed** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | C-05 |
| family | C |
| business_objective | activation |
| who_receives | Users who started KYC process (KYC_Started event) AND did NOT complete (no KYC_Completed within 48h) AND consent_marketing_push = true OR consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | N/A (lifecycle) -- onboarding stage, not asset-related |
| formula_used | Trigger Opportunity Score -> Send Score Final |
| threshold | send_score >= 0.50 |
| cooldown | 1/week; max 3 total across the KYC recovery sequence |
| channel | push (primary), email (secondary) |
| deep_link | `bit2me://settings/notifications` (deep link to KYC resume screen; using settings as fallback until KYC deep link is built) |
| priority | P3 |
| estimated_value | HIGH -- 32% phone drop-off is the biggest onboarding gap. Recovering even 5% has massive downstream revenue impact. |
| estimated_risk | LOW -- MARKETING class but low regulatory risk (onboarding reminder, no financial product mention) |

---

##### Family D: Lifecycle

**D-01: Active to At-Risk Transition** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | D-01 |
| family | D |
| business_objective | retention |
| who_receives | Users whose lifecycle_stage changed from ACTIVE to AT_RISK AND consent_marketing_email = true OR consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | N/A (lifecycle) -- targets user state, not specific assets |
| formula_used | Churn Risk Score -> Send Score Final |
| threshold | send_score >= 0.35 |
| cooldown | 1 per transition event (fires ONCE per stage transition) |
| channel | push (primary), email (secondary -- longer format for re-engagement) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P2 |
| estimated_value | HIGH -- highest-value retention intervention point. User is still reachable but disengaging. 72.4K dormant users with EUR 19.5M AUC at stake. |
| estimated_risk | MEDIUM -- MARKETING class, Diego Tier 1 required. Copy must avoid urgency. |

---

**D-02: Dormant With Balance** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | D-02 |
| family | D |
| business_objective | reactivation |
| who_receives | lifecycle_stage = DORMANT_BAL AND total_balance_eur > 50 AND consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | N/A (lifecycle) |
| formula_used | Churn Risk Score -> Send Score Final |
| threshold | send_score >= 0.35 |
| cooldown | 1/month |
| channel | email (primary -- non-intrusive for dormant users) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P5 |
| estimated_value | HIGH -- 72.4K users hold EUR 19.5M AUC. Gentle reactivation preserves assets on platform. |
| estimated_risk | MEDIUM -- MARKETING class. Copy must avoid implied opportunity or urgency. Over-messaging drives permanent opt-out. |

---

**D-03: First Trade Celebration**

| Column | Value |
|--------|-------|
| trigger_id | D-03 |
| family | D |
| business_objective | activation |
| who_receives | Users whose lifecycle_stage just changed from DEPOSITED to FM AND consent_marketing_push = true OR consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users (no fatigue filter -- celebration messages have high positive reception) |
| asset_scope | Layer 3 (user holdings/interactions) -- the asset the user traded (for personalization) |
| formula_used | N/A (event-driven milestone, always fires) |
| threshold | send_score >= 0.35 |
| cooldown | Once (fires only on first trade ever) |
| channel | push (primary -- immediate positive reinforcement) |
| deep_link | `bit2me://brokerage/trade?asset={symbol}` |
| priority | P2 |
| estimated_value | MEDIUM -- reinforces habit formation, proven to increase 2nd trade probability |
| estimated_risk | LOW -- MARKETING class but celebration frame has near-zero regulatory risk |

---

**D-04: Recurring Purchase Lapsed**

| Column | Value |
|--------|-------|
| trigger_id | D-04 |
| family | D |
| business_objective | retention |
| who_receives | recurring_buy_active = true AND days_since_last_recurring_execution > 30 AND consent_marketing_push = true OR consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | Layer 3 (user holdings/interactions) -- the asset(s) in the lapsed recurring buy |
| formula_used | Churn Risk Score -> Send Score Final |
| threshold | send_score >= 0.35 |
| cooldown | 1/week until resolved or user cancels recurring buy |
| channel | push (primary), email (secondary -- needs explanation) |
| deep_link | `bit2me://settings/notifications` |
| priority | P2 |
| estimated_value | MEDIUM -- protects recurring revenue stream, small but high-value segment |
| estimated_risk | LOW -- MARKETING class, low MiCA risk (service status notification) |

---

**D-05: Pre-Dormancy Warning** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | D-05 |
| family | D |
| business_objective | retention |
| who_receives | lifecycle_stage = PRE_DORMANCY AND total_balance_eur > 0 AND consent_marketing_push = true OR consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, active_journey IS NOT NULL, notification_fatigue_score > 0.7 |
| asset_scope | N/A (lifecycle) |
| formula_used | Churn Risk Score -> Send Score Final |
| threshold | send_score >= 0.35 |
| cooldown | 1/week |
| channel | push (primary), email (secondary) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P2 |
| estimated_value | HIGH -- L3 Near-Dormant = highest revenue velocity segment. Intervention here prevents transition to DORMANT. Targets part of the 72.4K user pool before they become unreachable. |
| estimated_risk | MEDIUM -- MARKETING class. Copy must frame as check-in, not urgency. |

---

**D-06: Reactivation Success Celebration** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | D-06 |
| family | D |
| business_objective | retention |
| who_receives | Users whose lifecycle_stage just changed from DORMANT_BAL or DORMANT_ZERO to REACTIVATED AND consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users |
| asset_scope | N/A (lifecycle) |
| formula_used | N/A (event-driven milestone) |
| threshold | send_score >= 0.35 |
| cooldown | Once per reactivation event |
| channel | push (primary -- immediate positive reinforcement) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P2 |
| estimated_value | MEDIUM -- reinforces return behavior, increases probability of sustained re-engagement |
| estimated_risk | LOW -- celebration frame, no regulatory concern |

---

##### Family E: Product Cross-sell

**E-01: Stablecoins Not in Earn**

| Column | Value |
|--------|-------|
| trigger_id | E-01 |
| family | E |
| business_objective | revenue |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND holds_stablecoins = true AND 'earn' NOT IN products_active AND consent_marketing_email = true OR consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days, lifecycle_stage IN (AT_RISK, PRE_DORMANCY, DORMANT_BAL, DORMANT_ZERO, CHURNED) |
| asset_scope | Layer 2 (Earn-eligible) -- Earn-eligible stablecoins (USDT, USDC, DAI) |
| formula_used | Cross-sell Eligibility Score + User Asset Affinity Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | email (primary -- richer context), in-app (secondary) |
| deep_link | `bit2me://earn/stake?asset={symbol}` |
| priority | P4 |
| estimated_value | HIGH -- highest-value cross-sell pattern (idle stablecoins earning 0% = guaranteed relevance) |
| estimated_risk | MEDIUM -- MARKETING class. V1: product awareness framing ONLY. Must NOT compare yields to savings. Must include "APY is variable. Capital at risk." |

---

**E-02: Loan Eligible (Collateral Sufficient)**

| Column | Value |
|--------|-------|
| trigger_id | E-02 |
| family | E |
| business_objective | revenue |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND collateral_eligible_balance_eur > minimum_collateral_threshold AND 'loan' NOT IN products_active AND consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days |
| asset_scope | Layer 2 (Loan-eligible) -- BTC, ETH, stablecoins |
| formula_used | Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | email (primary), in-app (secondary) |
| deep_link | `bit2me://loan/collateral?loan_id={id}` |
| priority | P4 |
| estimated_value | MEDIUM -- niche but high per-user value; conservative collateral policy limits audience |
| estimated_risk | MEDIUM -- MARKETING class. Copy must explain liquidation risk. Must include risk warning. |

---

**E-03: Space Center Mission Available**

| Column | Value |
|--------|-------|
| trigger_id | E-03 |
| family | E |
| business_objective | engagement |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND space_center_missions_available > 0 AND consent_marketing_inapp = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days |
| asset_scope | Layer 2 (Space Center-eligible) -- B2M token primarily |
| formula_used | Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | in-app (primary -- gamification is in-app native), push (secondary) |
| deep_link | `bit2me://space-center/missions` |
| priority | P4 |
| estimated_value | MEDIUM -- gamification engagement, drives B2M utility |
| estimated_risk | LOW -- MARKETING class, gamification frame has lower MiCA risk |

**NOTE:** Space Center data availability in BigQuery is an open question. If data is not accessible, this trigger moves to V2. See TRIG-04 "NOT to launch" list.

---

**E-04: Pro Eligible (Volume Threshold Met)**

| Column | Value |
|--------|-------|
| trigger_id | E-04 |
| family | E |
| business_objective | revenue |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND trading_volume_30d_eur > pro_volume_threshold AND 'pro' NOT IN products_active AND consent_marketing_email = true OR consent_marketing_push = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days |
| asset_scope | Layer 2 (Pro-eligible) -- trading pairs with sufficient liquidity |
| formula_used | Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | email (primary), in-app (secondary) |
| deep_link | `bit2me://pro/chart?pair={symbol}-EUR` |
| priority | P4 |
| estimated_value | MEDIUM -- converts active traders to Pro, reduces their fees, increases platform stickiness |
| estimated_risk | LOW -- MARKETING class, feature awareness (not financial product per se) |

---

**E-05: Card Activation** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | E-05 |
| family | E |
| business_objective | revenue |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND total_balance_eur > 100 AND 'card' NOT IN products_active AND consent_marketing_email = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days |
| asset_scope | Layer 2 (Card-eligible) -- all held assets (user can spend any crypto via Card) |
| formula_used | Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | email (primary -- needs content depth to explain Card value prop) |
| deep_link | `bit2me://card/activate` |
| priority | P4 |
| estimated_value | MEDIUM -- Card increases perceived value of holdings and drives transaction revenue |
| estimated_risk | LOW -- MARKETING class, product awareness framing |

---

**E-06: Pay Discovery** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | E-06 |
| family | E |
| business_objective | revenue |
| who_receives | lifecycle_stage IN (ACTIVE, POWER) AND 'pay' NOT IN products_active AND consent_marketing_inapp = true |
| who_never_receives | C8_Whale_Suppression, Excluded_Users, notification_fatigue_score > 0.7, dismissed E-family in last 7 days |
| asset_scope | Layer 2 (Pay-eligible) -- payment-eligible assets |
| formula_used | Cross-sell Eligibility Score -> Send Score Final |
| threshold | send_score >= 0.55 |
| cooldown | 1/week; 2/month maximum |
| channel | in-app (primary -- contextual discovery), email (secondary) |
| deep_link | `bit2me://pay/merchants` |
| priority | P4 |
| estimated_value | LOW -- Pay adoption is early stage, merchant network still growing |
| estimated_risk | LOW -- MARKETING class, product awareness framing |

---

##### Family F: Risk and Protective

**F-01: LTV Warning (3-Tier Graduated)** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | F-01 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users with active loans whose LTV reaches any tier threshold (71.4% / 74.1% / 76.9%) |
| who_never_receives | NONE for P0 (Tier 3 CRITICAL). Excluded_Users only for P1 (Tiers 1-2). C8 whale accounts RECEIVE this -- protective alert. |
| asset_scope | Layer 3 (user holdings/interactions) -- collateral assets the user has at risk |
| formula_used | N/A (threshold-based, always fires when LTV condition met) |
| threshold | N/A (fires at LTV >= 71.4% / 74.1% / 76.9%) |
| cooldown | No cooldown between tiers. Within same tier: 1 per 4 hours. Reset when LTV drops below tier. |
| channel | multi (progressive: Tier 1 = push+in-app, Tier 2 = push+email+in-app, Tier 3 = push+email+in-app+SMS) |
| deep_link | `bit2me://loan/collateral?loan_id={id}` |
| priority | P1 (Tiers 1-2), P0 (Tier 3 CRITICAL) |
| estimated_value | HIGH -- prevents liquidation, protects user trust, preserves AUC |
| estimated_risk | LOW -- TRANSACTIONAL (contractual necessity), no consent required, no compliance concern |

---

**F-02: Large Balance Inactivity (60d)**

| Column | Value |
|--------|-------|
| trigger_id | F-02 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users with total_balance_eur > 1000 AND days_since_last_activity > 60 |
| who_never_receives | Excluded_Users only (C8 whale accounts RECEIVE this -- protective alert) |
| asset_scope | Layer 3 (user holdings/interactions) -- all assets the user holds (aggregate balance check) |
| formula_used | N/A (threshold-based) |
| threshold | N/A (fires when balance > EUR 1,000 AND inactive > 60 days) |
| cooldown | 1 per 30 days |
| channel | push (primary), email (secondary -- persistent record) |
| deep_link | `bit2me://portfolio/overview` |
| priority | P1 |
| estimated_value | MEDIUM -- security awareness, secondary reactivation benefit |
| estimated_risk | LOW -- TRANSACTIONAL (account security). Copy must NOT include cross-sell disguised as security. |

---

**F-03: Failed Recurring Buy Alert**

| Column | Value |
|--------|-------|
| trigger_id | F-03 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users whose Recurring_Buy_Failed event fired |
| who_never_receives | Excluded_Users only |
| asset_scope | Layer 3 (user holdings/interactions) -- the specific asset in the failed recurring buy |
| formula_used | N/A (event-driven, always fires) |
| threshold | N/A (fires on every failure event) |
| cooldown | 1 per failure event (immediate) |
| channel | push (immediate awareness), email (persistent record with failure details) |
| deep_link | `bit2me://settings/notifications` |
| priority | P1 |
| estimated_value | MEDIUM -- service continuity, prevents silent DCA interruption |
| estimated_risk | LOW -- TRANSACTIONAL (service the user set up failed) |

---

**F-04: Stablecoin De-Peg Alert** [MVP]

| Column | Value |
|--------|-------|
| trigger_id | F-04 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users holding the affected stablecoin |
| who_never_receives | NONE (P0 security -- ALWAYS delivers to everyone, including C8 whales) |
| asset_scope | Layer 3 (user holdings/interactions) -- T2 (stablecoin) assets the user holds |
| formula_used | N/A (condition-based, always fires when de-peg detected) |
| threshold | N/A (fires when stablecoin deviates >2% from peg for >1 hour, confirmed on 2+ price sources) |
| cooldown | 1 per 24 hours per stablecoin per user |
| channel | push (immediate), email (persistent record) |
| deep_link | `bit2me://wallet/asset?symbol={symbol}` |
| priority | P0 |
| estimated_value | HIGH -- protects user from financial risk, builds institutional trust |
| estimated_risk | LOW -- TRANSACTIONAL (CAT-SEC, no consent required). P0 = no restrictions. |

---

**F-05: Login from New Device** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | F-05 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users when login detected from a new device or new location |
| who_never_receives | NONE (P0 security -- ALWAYS delivers to everyone, including C8 whales) |
| asset_scope | N/A (lifecycle) -- account-level security, not asset-specific |
| formula_used | N/A (event-driven, always fires) |
| threshold | N/A (fires on every new device/location login event) |
| cooldown | 1 per suspicious event (no cooldown) |
| channel | push (immediate), email (persistent record) |
| deep_link | `bit2me://settings/notifications` |
| priority | P0 |
| estimated_value | HIGH -- account security is table-stakes; absence would be a trust violation |
| estimated_risk | LOW -- TRANSACTIONAL (CAT-SEC), no consent required. P0 = exempt from all restrictions. |

**NOTE:** This trigger overlaps with F-04 (Unusual Login Activity) from the original taxonomy. F-05 is the renamed and clarified version for the master table. The original F-04 "Unusual Login Activity" from Section 6 is now F-05 in this table to avoid ID collision with F-04 "Stablecoin De-Peg Alert."

---

**F-06: Withdrawal Confirmation** (NEW)

| Column | Value |
|--------|-------|
| trigger_id | F-06 |
| family | F |
| business_objective | risk_protection |
| who_receives | ALL users who initiated a withdrawal (crypto or fiat) |
| who_never_receives | Excluded_Users only |
| asset_scope | Layer 3 (user holdings/interactions) -- the specific asset being withdrawn |
| formula_used | N/A (event-driven, always fires) |
| threshold | N/A (fires on every withdrawal event) |
| cooldown | 1 per transaction |
| channel | push (immediate confirmation), email (persistent record with transaction details) |
| deep_link | `bit2me://wallet/asset?symbol={symbol}` |
| priority | P1 |
| estimated_value | MEDIUM -- transactional confirmation, builds trust and provides audit trail |
| estimated_risk | LOW -- TRANSACTIONAL (contractual), no compliance concern |

---

### 11.3 MVP Trigger Identification

#### 11.3.1 MVP Scoring Methodology

Each trigger is scored on 3 dimensions (1-5 scale) using the framework from Phase 3 research:

```
MVP_Score = Impact * 2 + (5 - Risk) * 1.5 + (5 - Implementation_Complexity) * 1
```

**Dimension definitions:**

| Dimension | 1 (Low) | 3 (Medium) | 5 (High) |
|-----------|---------|------------|----------|
| **Impact** | Nice-to-have, small segment | Engagement driver, medium segment | Revenue/retention critical, large segment |
| **Risk** | TRANSACTIONAL, no compliance | INFORMATIONAL, template pre-approved | MARKETING/ADVISORY_RISK, full Diego review |
| **Implementation Complexity** | Data in BQ, event instrumented, no new infra | Some data gaps, partial instrumentation | New data pipeline, new API, missing events |

#### 11.3.2 MVP Scoring Table

| Rank | trigger_id | Trigger Name | Impact (1-5) | Risk (1-5) | Impl. Complexity (1-5) | MVP_Score | Justification |
|------|------------|-------------|:------------:|:----------:|:----------------------:|:---------:|--------------|
| 1 | A-01 | Price Target Alert | 5 | 1 | 1 | **20.0** | User-requested, TRANSACTIONAL, CoinGecko API ready, zero regulatory risk. Highest engagement driver across all 6 competitors. |
| 2 | A-02 | Percentage Change Alert | 5 | 1 | 1 | **20.0** | Same infrastructure as A-01, adds volatility awareness. Near-zero marginal implementation cost. |
| 3 | A-03 | Watchlist Price Move | 5 | 1 | 2 | **19.0** | Coinbase gold standard. Requires watchlist data sync (minor), otherwise same pipeline as A-01/A-02. |
| 4 | F-01 | LTV Warning (Graduated) | 5 | 1 | 2 | **19.0** | Protective/contractual. Nexo-validated 3-tier model. LTV data already in BigQuery via loan system. Prevents liquidation = direct value. |
| 5 | F-04 | Stablecoin De-Peg | 4 | 1 | 2 | **17.0** | P0 CAT-SEC, no consent needed. CoinGecko price feed + cross-reference. Protects user trust. Low frequency but critical when needed. |
| 6 | D-01 | Active to At-Risk | 5 | 3 | 2 | **16.0** | Highest retention intervention value. lifecycle_stage already computed daily in BQ. 72.4K users with EUR 19.5M AUC at stake. MARKETING class = Diego review needed. |
| 7 | D-02 | Dormant With Balance | 5 | 3 | 1 | **17.0** | Directly targets AUC preservation. Data fully available in BQ. Lower impl. complexity than D-01 (simpler targeting). MARKETING class = Diego review needed. |
| 8 | B-01 | Volatility Spike | 4 | 2 | 2 | **16.5** | Market engagement during high-activity periods. CoinGecko API (public). Template pre-approved path. MiCA market abuse protocol adds operational overhead but is well-documented. |
| 9 | C-01 | Watched Not Bought | 4 | 3 | 2 | **14.0** | Proven conversion pattern. Requires Product_Viewed event instrumentation (may need SDK update). MARKETING class. |
| 10 | B-04 | Price Breakout | 3 | 2 | 2 | **13.5** | Simple technical signal. Same infrastructure as B-01. Low incremental cost. Template pre-approved path. |

**Top 10 MVP triggers sorted by MVP_Score:**

1. A-01 (20.0), 2. A-02 (20.0), 3. A-03 (19.0), 4. F-01 (19.0), 5. D-02 (17.0), 6. F-04 (17.0), 7. B-01 (16.5), 8. D-01 (16.0), 9. C-01 (14.0), 10. B-04 (13.5)

#### 11.3.3 MVP Implementation Sequence

| Wave | Triggers | Timeline | Dependencies | Owner |
|------|----------|----------|-------------|-------|
| **MVP Wave 1** (Week 1-2) | A-01, A-02, A-03 | Days 1-14 | CoinGecko API, Cloud Function, watchlist data | Engineering (Cloud Function), Katy (CleverTap templates) |
| **MVP Wave 2** (Week 2-3) | F-01, F-04, F-05 | Days 14-21 | Loan LTV data (BQ), stablecoin price feeds, login events | Alvaro (BQ queries), Engineering (event instrumentation) |
| **MVP Wave 3** (Week 3-4) | D-01, D-02, B-01, B-04 | Days 21-30 | lifecycle_stage computation (BQ), Market Relevance Score, Diego template approval | Alvaro (scoring queries), Katy (templates), Diego (Tier 1 approval) |
| **MVP Wave 4** (Week 4+) | C-01 | Days 28-35 | Product_Viewed event (SDK), User Asset Affinity Score | Engineering (SDK event), Alvaro (scoring query) |

---

### 11.4 Cross-References

| Reference | Section | Relationship |
|-----------|---------|-------------|
| **Section 6: Trigger Taxonomy** | Phase 2 | Family definitions, eligibility rules, compliance class defaults. Each trigger in this table inherits its family properties from Section 6. |
| **Section 7: Asset Universe** | Phase 2 | `asset_scope` column values (Layer 1/2/3/N/A) reference the scope rules defined in Section 7.3. Asset tier assignments (T1-T4) from Section 7.1 determine which assets qualify for Family B triggers. |
| **Section 9: Compliance Framework** | Phase 2 | Compliance class per trigger determines Diego review level (Section 9.2), keyword blocklist applicability (Section 9.3.3), market abuse protocol (Section 9.4 for Family B), and per-trigger checklist (Section 9.5). |
| **Section 10: Scoring Formulas** | Phase 3 | `formula_used` column references scoring formulas: Market Relevance Score (SCORE-01), User Asset Affinity Score (SCORE-02), Trigger Opportunity Score (SCORE-03), Cross-sell Eligibility Score (SCORE-06), Churn Risk Score (SCORE-07), Send Score Final (SCORE-08). |
| **Section 2: Frequency Caps** | Phase 1 | `priority` column maps to P0-P5 tiers (Section 2.3). P0-P1 exempt from global caps. `cooldown` values align with Section 2.4 escalating cooldown rules. Fatigue risk thresholds (Section 2.5) determine suppression at each fatigue level. |
| **Section 3: Suppression System** | Phase 1 | `who_never_receives` includes C8_Whale_Suppression and Excluded_Users from Section 3.2. All triggers pass through 4 suppression layers (segment exclusion, quiet hours, opt-out, escalating cooldowns). |
| **CHAN-02: Deep Link Structure** | Phase 3 | `deep_link` column uses the product-specific patterns: Brokerage (`bit2me://brokerage/trade`), Pro (`bit2me://pro/chart`), Earn (`bit2me://earn/stake`), Card (`bit2me://card/activate`), Loan (`bit2me://loan/collateral`), Space Center (`bit2me://space-center/missions`), Wallet (`bit2me://wallet/asset`), Pay (`bit2me://pay/merchants`), Settings (`bit2me://settings/notifications`), Portfolio (`bit2me://portfolio/overview`). |
