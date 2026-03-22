## 6. Trigger Taxonomy

> **Purpose:** This section defines the six trigger families that form the structural backbone of Bit2Me's trigger-based notification system. Each family groups triggers by their activation logic (user action, market condition, behavioral pattern, lifecycle transition, product gap, or risk condition). Phase 3 uses these family definitions to score and tabulate 30+ individual triggers in the Master Trigger Table.
>
> **Owners:** Katy (CleverTap campaign configuration), Alvaro (BigQuery data sources + Hightouch sync), Diego (compliance review per trigger)
>
> **Cross-references:**
> - Section 1 (Preference Center Architecture): consent categories CAT-SEC through CAT-PRO
> - Section 2 (Frequency Cap Policy): priority tiers P0 through P5, cooldown rules, fatigue risk formula
> - Section 3 (Suppression System): C8 whale suppression, quiet hours, escalating cooldowns

---

### 6.1 Taxonomy Overview

The trigger taxonomy organizes all notifications Bit2Me sends into six families. Every trigger belongs to exactly one family. Families are distinguished by their **activation source** -- what causes the trigger to fire:

| Family | Name | Activation Source | Consent Category | Priority Tier | Compliance Class |
|--------|------|------------------|-----------------|---------------|-----------------|
| A | User Configured | User explicitly creates an alert | CAT-USR | P1 | TRANSACTIONAL |
| B | Market Triggered | Market condition detected (not user-configured) | CAT-MKT | P3 | INFORMATIONAL |
| C | Behavioral | In-app user behavior pattern detected | CAT-MKT / CAT-PRO | P3-P4 | MARKETING |
| D | Lifecycle | Lifecycle stage transition detected | CAT-MKT / CAT-PRO | P2 / P5 | MARKETING |
| E | Product Cross-sell | Product eligibility gap detected | CAT-PRO | P4 | MARKETING |
| F | Risk and Protective | Risk condition detected (account security or financial risk) | CAT-SEC / CAT-TXN | P0-P1 | TRANSACTIONAL |

---

#### Standardized Trigger Definition Template

Every trigger in every family must follow this template structure. This ensures Phase 3 can tabulate all triggers uniformly in the Master Trigger Table.

```
TRIGGER DEFINITION TEMPLATE
============================
- trigger_id: [FAM]-[NN] (e.g., A-01, B-05, D-03)
- family: A|B|C|D|E|F
- trigger_name: Human-readable name
- business_objective: What business outcome this drives
- description: What fires the trigger

ELIGIBILITY CRITERIA
- who_receives: Segment/lifecycle/product conditions
- who_never_receives: Hard exclusions
- consent_category: CAT-SEC|CAT-TXN|CAT-USR|CAT-MKT|CAT-PRD|CAT-PRO (from Section 1)
- consent_required: boolean (false for CAT-SEC, CAT-TXN)
- asset_scope: Which assets this trigger applies to

DELIVERY RULES
- priority_tier: P0|P1|P2|P3|P4|P5 (from Section 2)
- channel: push|email|in-app|multi
- cooldown: Minimum time between fires for same user
- quiet_hours_exempt: boolean (true only for P0)

DATA REQUIREMENTS
- data_source: BigQuery view | CleverTap Live Segment | Cloud Function | SDK event
- required_events: Which events from Phase 1 event schema are needed
- required_user_properties: Which Hightouch-synced fields are needed
- evaluation_frequency: Real-time | Hourly | Daily

COMPLIANCE
- compliance_class: TRANSACTIONAL | INFORMATIONAL | MARKETING | ADVISORY_RISK
- diego_approval: REQUIRED | NOT_REQUIRED | TEMPLATE_PRE_APPROVED
- mica_risk_level: NONE | LOW | MEDIUM | HIGH
- risk_warning_required: boolean
- keyword_blocklist_applies: boolean
```

---

#### Compliance Classification System

Every trigger must be classified into one of four compliance classes. This classification determines the Diego review workflow and MiCA obligations.

| Compliance Class | Definition | Diego Review | MiCA Art. 66 | Risk Warning | Examples |
|------------------|-----------|-------------|-------------|-------------|---------|
| TRANSACTIONAL | Confirms a user-initiated action or protects account security | NOT_REQUIRED | Not applicable (contractual) | No | Trade filled, withdrawal confirmed, login alert |
| INFORMATIONAL | States a fact about market or portfolio state without suggesting action | TEMPLATE_PRE_APPROVED | Applies -- must be fair, clear, not misleading | Link to risk page | "BTC crossed $70,000", "Your BTC holding is up 12%" |
| MARKETING | Promotes a Bit2Me product or encourages a commercial action | REQUIRED per template | Full compliance -- identifiable as marketing, disclaimers, risk warnings | Yes -- in or linked | Cross-sell, reactivation, new listing promo |
| ADVISORY_RISK | Could be construed as suggesting an investment action -- HIGH regulatory risk | REQUIRED per message + legal review | Full compliance + possible MiCA Art. 81 suitability concerns | Yes -- mandatory inline | DO NOT USE without explicit legal clearance. Reserve for V3. |

**Conservative rule for the informational-vs-advisory boundary:**

Since MiCA does NOT provide a bright-line test (ESMA is still developing guidance as of March 2026), Bit2Me must adopt this internal rule:

1. A notification is INFORMATIONAL if it states a verifiable fact without suggesting any action. Examples: "BTC is at $70,000", "Your portfolio changed by X%", "ETH Earn APY is currently 3.2%"
2. A notification crosses into ADVISORY_RISK territory if it: (a) pairs a fact with a value judgment ("great entry point", "beats savings accounts"), (b) implies urgency around a financial action ("don't miss out", "last chance"), (c) compares crypto-asset returns to non-crypto alternatives, or (d) suggests the user should buy, sell, hold, or move assets.
3. When in doubt, classify as MARKETING and require Diego approval. It is always safer to over-classify than under-classify.

**Keyword blocklist for automated pre-screening:**

```
PROHIBITED in notification copy (any compliance class):
  "guaranteed", "risk-free", "pump", "moon", "100x"

FLAGGED -- requires Diego review:
  "should", "opportunity", "don't miss", "good time to", "beats",
  "outperforms", "recommended", "consider buying", "last chance",
  "entry point", "bargain", "undervalued", "profit"

REQUIRED in marketing notifications:
  Risk warning text or link: "Capital at risk. Not investment advice."
  MiCA mandatory disclaimer: "This crypto-asset marketing communication
  has not been reviewed or approved by any competent authority in any
  Member State of the European Union."
```

---

#### Phase 1 Cross-Reference Map

How Phase 1 constructs apply to each trigger family:

| Phase 1 Construct | How It Applies to Triggers |
|-------------------|---------------------------|
| **Consent Categories** (Section 1) | Each trigger's `consent_category` maps to a CAT-XX from Section 1. This determines whether marketing consent is required (`consent_marketing_[channel] = true`) and which CleverTap Subscription Group the user must be subscribed to. |
| **Priority Tiers** (Section 2.3) | Each trigger's `priority_tier` maps to P0-P5 from Section 2.3. This determines: (a) whether the trigger is exempt from global frequency caps (P0-P1), (b) what campaign-level cooldown applies, (c) at what fatigue_risk threshold the trigger is suppressed. |
| **Fatigue Risk Score** (Section 2.5) | Triggers with priority P3+ are suppressed when `notification_fatigue_score` exceeds the tier threshold. GREEN (<0.3): all tiers send. AMBER (0.3-0.7): P5 suppressed. RED (0.7-0.9): P3+ suppressed. CRITICAL (>0.9): P2+ suppressed. |
| **Suppression Layers** (Section 3) | Every trigger passes through 4 suppression layers in sequence: (1) Segment exclusion (C8 whale, excluded users), (2) Quiet hours DND, (3) Opt-out handling, (4) Escalating cooldowns. All layers are additive -- any single block prevents delivery. |
| **Cooldown Escalation** (Section 2.4) | After dismissed notifications: 24h family cooldown after 1 dismiss, 7-day family cooldown after 3 consecutive dismissals, P0-P1-only mode after 5 consecutive dismissals across any family. Reset on any open/click. |

---

### 6.2 Family A: User Configured

> **Definition:** Alerts that the user explicitly creates through an in-app action. The user chooses the asset, the condition (above/below/% move), and optionally the channel. Because the user requested the service, these are contractual (Art. 6(1)(b)) and do not require marketing consent.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-USR (Art. 6(1)(b) -- contract performance: user requested this service) |
| priority_tier | P1 (user-configured -- exempt from global caps via "Exclude from Global campaign limits") |
| compliance_class | TRANSACTIONAL (user-requested service) |
| channel | Push (primary), Email (fallback if push disabled) |
| cooldown | 1 per asset per 4 hours (prevent spam during volatile sideways markets) |
| quiet_hours_exempt | No (unless user opts into 24/7 delivery via Notification Preferences) |
| diego_approval | NOT_REQUIRED (transactional) |
| data_source | Cloud Function + CoinGecko API (public price data) |

**Entry Criteria:** User creates an alert via `Price_Alert_Set` SDK event (captures: asset_symbol, condition_type, target_value, alert_frequency).

**Exit Criteria:** Alert fires and is consumed (one-off mode) OR alert remains active (persistent mode, re-arms after cooldown).

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | Any user who has created a price alert via `Price_Alert_Set` event |
| who_never_receives | `C8_Whale_Suppression` segment, `Excluded_Users` segment (Section 3.2) |
| asset_scope | All listed assets (Layer 1 -- no restriction). Any asset listed on Bit2Me can have a user-configured alert. |

---

#### Trigger A-01: Price Target Alert (Above/Below)

```
TRIGGER DEFINITION: A-01 Price Target Alert
=============================================
trigger_id: A-01
family: A (User Configured)
trigger_name: Price Target Alert (Above/Below)
business_objective: Engagement, trading activation
description: User sets a price target for a specific asset. Notification fires
             when the asset price crosses the target (above or below).

ELIGIBILITY CRITERIA
- who_receives: Any user who has created a price alert via Price_Alert_Set event
- who_never_receives: C8_Whale_Suppression, Excluded_Users
- consent_category: CAT-USR (Art. 6(1)(b) -- contract performance)
- consent_required: false (user explicitly requested this)
- asset_scope: All listed assets (Layer 1 -- no restriction)

DELIVERY RULES
- priority_tier: P1 (user-configured -- exempt from global caps)
- channel: Push (primary), Email (fallback if push disabled)
- cooldown: 1 per asset per 4 hours (prevent spam during volatile markets)
- quiet_hours_exempt: false (unless user opts into 24/7 delivery)

DATA REQUIREMENTS
- data_source: Cloud Function (Price_Alert_Triggered event)
- required_events: Price_Alert_Set (SDK), Price_Alert_Triggered (Cloud Function)
- required_user_properties: None (alert config stored separately)
- evaluation_frequency: Real-time (Cloud Function polls CoinGecko every 5 min)

COMPLIANCE
- compliance_class: TRANSACTIONAL (user-requested service)
- diego_approval: NOT_REQUIRED (transactional -- user asked for this)
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

---

#### Trigger A-02: Percentage Change Alert

```
TRIGGER DEFINITION: A-02 Percentage Change Alert
==================================================
trigger_id: A-02
family: A (User Configured)
trigger_name: Percentage Change Alert
business_objective: Engagement, volatility awareness
description: User sets a percentage change threshold for a specific asset (e.g., +5%, -10%).
             Notification fires when the asset moves by that percentage within the configured
             timeframe (1h, 4h, 24h).

ELIGIBILITY CRITERIA
- who_receives: Any user who has created a percentage alert via Price_Alert_Set event
                (condition_type = 'pct_change')
- who_never_receives: C8_Whale_Suppression, Excluded_Users
- consent_category: CAT-USR (Art. 6(1)(b) -- contract performance)
- consent_required: false
- asset_scope: All listed assets (Layer 1)

DELIVERY RULES
- priority_tier: P1
- channel: Push (primary), Email (fallback)
- cooldown: 1 per asset per 4 hours
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (polls CoinGecko, computes % change over configured window)
- required_events: Price_Alert_Set (SDK, with pct_threshold and timeframe properties)
- required_user_properties: None
- evaluation_frequency: Real-time (every 5 min poll)

COMPLIANCE
- compliance_class: TRANSACTIONAL
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

---

#### Trigger A-03: Watchlist Price Move

```
TRIGGER DEFINITION: A-03 Watchlist Price Move
==============================================
trigger_id: A-03
family: A (User Configured)
trigger_name: Watchlist Price Move
business_objective: Engagement, portfolio awareness
description: User adds assets to their watchlist (star icon). When any watchlisted asset
             moves more than a user-configured threshold (default 5%) in 24h, notification fires.
             Inspired by Coinbase watchlist-first model (star + bell = two-step mental model).

ELIGIBILITY CRITERIA
- who_receives: Any user with watchlisted assets AND watchlist alerts enabled
- who_never_receives: C8_Whale_Suppression, Excluded_Users
- consent_category: CAT-USR (Art. 6(1)(b))
- consent_required: false
- asset_scope: All listed assets on user's watchlist

DELIVERY RULES
- priority_tier: P1
- channel: Push (primary), In-App (secondary)
- cooldown: 1 per asset per 4 hours; max 3 watchlist alerts per day across all assets
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (monitors watchlisted assets against CoinGecko)
- required_events: Watchlist_Add (SDK), Watchlist_Remove (SDK)
- required_user_properties: watchlist_assets (array of asset symbols)
- evaluation_frequency: Hourly (less urgent than price target alerts)

COMPLIANCE
- compliance_class: TRANSACTIONAL
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

---

#### Trigger A-04: LTV Threshold Alert (Loan Users)

```
TRIGGER DEFINITION: A-04 LTV Threshold Alert (User-Configured)
================================================================
trigger_id: A-04
family: A (User Configured)
trigger_name: LTV Threshold Alert (User-Configured)
business_objective: Risk management, user empowerment
description: Loan users can set a custom LTV (Loan-to-Value) threshold alert. When their
             active loan LTV reaches the user-defined level, notification fires. This is
             distinct from Family F system LTV alerts -- this is user-configured.

ELIGIBILITY CRITERIA
- who_receives: Users with active loans who have configured a custom LTV alert
- who_never_receives: C8_Whale_Suppression, Excluded_Users
- consent_category: CAT-USR (Art. 6(1)(b) -- user requested monitoring)
- consent_required: false
- asset_scope: Collateral-eligible assets only (BTC, ETH, stablecoins -- from Loan product)

DELIVERY RULES
- priority_tier: P1
- channel: Push (immediate), Email (persistent record)
- cooldown: 1 per loan per 4 hours (LTV can fluctuate rapidly)
- quiet_hours_exempt: false (system LTV alerts in Family F are exempt; user-configured are not)

DATA REQUIREMENTS
- data_source: BigQuery (loan_ltv_current field via Hightouch sync)
- required_events: LTV_Alert_Set (SDK -- user configures threshold)
- required_user_properties: active_loan_id, loan_ltv_current, ltv_alert_threshold
- evaluation_frequency: Hourly (loan LTV changes with collateral price)

COMPLIANCE
- compliance_class: TRANSACTIONAL
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

---

### 6.3 Family B: Market Triggered

> **Definition:** Proactive alerts driven by market conditions that the user did NOT explicitly configure. Unlike Family A, these are platform-initiated based on market data analysis. Because they are not user-requested, they require marketing consent and are subject to global frequency caps.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-MKT (Art. 6(1)(a) -- explicit consent required for marketing) |
| priority_tier | P3 (market triggers -- subject to global caps + campaign limit) |
| compliance_class | INFORMATIONAL (states market facts without suggesting action) |
| channel | Push (primary), In-App (secondary) |
| cooldown | 1/day, 3/week per user |
| quiet_hours_exempt | No |
| diego_approval | TEMPLATE_PRE_APPROVED (pre-approve template; no per-send review) |
| data_source | Cloud Function + CoinGecko API (public data -- MANDATORY per MiCA Art. 87-92) |

**Entry Criteria:** Market condition detected: volatility exceeds threshold, volume spikes above 2x 30-day average, asset trending on social/exchange data, or price breakout from range.

**Exit Criteria:** Market condition normalizes (falls below threshold for 4 consecutive hours).

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | Users with `consent_marketing_push = true` AND who hold or have on watchlist the affected asset |
| who_never_receives | `C8_Whale_Suppression`, `Excluded_Users`, users with `notification_fatigue_score > 0.7` (RED/CRITICAL), users who dismissed a B-family notification in the last 7 days |
| asset_scope | Top 50-100 assets by Bit2Me trading volume (NOT all 420+ assets -- avoid noise from illiquid microcaps) |

**CRITICAL -- MiCA Art. 87-92 Market Abuse Constraints:**

1. **Data source MUST be publicly available** (CoinGecko API, not internal order book data). Using internal trading data to generate market alerts could constitute market manipulation.
2. **All eligible users receive the notification simultaneously** -- no staggered delivery, no A/B test timing differences. Staggering could give early recipients an unfair trading advantage.
3. **Notification timing must NOT coincide with internal platform events** (listings, delistings, maintenance). This avoids the appearance of insider information dissemination.
4. **Audit log required:** Every market trigger must log: trigger_id, timestamp, user_count_sent, data_source_url, market_condition_snapshot. Retained for 5 years (MiCA record-keeping).

**Copy constraints:** State facts only. "BTC is up 10% in 24h" = SAFE. "BTC is surging -- great time to buy" = ADVISORY_RISK, DO NOT USE.

---

#### Trigger B-01: Volatility Spike

```
TRIGGER DEFINITION: B-01 Volatility Spike
==========================================
trigger_id: B-01
family: B (Market Triggered)
trigger_name: Volatility Spike Alert
business_objective: Engagement, trading activation during high-activity periods
description: Fires when an asset's realized volatility over 24h exceeds 2 standard
             deviations above its 30-day rolling average. Targets users who hold or
             watch the asset.

ELIGIBILITY CRITERIA
- who_receives: consent_marketing_push = true AND (holds_asset OR asset_on_watchlist)
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed B-family in last 7 days
- consent_category: CAT-MKT (Art. 6(1)(a) -- explicit consent)
- consent_required: true
- asset_scope: Top 50-100 by Bit2Me volume

DELIVERY RULES
- priority_tier: P3
- channel: Push (primary), In-App (secondary)
- cooldown: 1/day, 3/week
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (CoinGecko API -- public volatility data)
- required_events: None (state-based market condition)
- required_user_properties: consent_marketing_push, asset_holdings, watchlist_assets,
                            notification_fatigue_score
- evaluation_frequency: Hourly

COMPLIANCE
- compliance_class: INFORMATIONAL
- diego_approval: TEMPLATE_PRE_APPROVED
- mica_risk_level: LOW (factual -- "BTC volatility is elevated")
- risk_warning_required: false (informational, no action suggested)
- keyword_blocklist_applies: true (scan for prohibited/flagged terms)

MiCA ART. 87-92 REQUIREMENTS:
- Data source: CoinGecko API (public)
- Simultaneous delivery: YES (no staggering)
- Audit log: trigger_id, timestamp, user_count, volatility_value, data_source_url
```

---

#### Trigger B-02: Volume Spike

```
TRIGGER DEFINITION: B-02 Volume Spike
======================================
trigger_id: B-02
family: B (Market Triggered)
trigger_name: Volume Spike Alert
business_objective: Trading activation, market awareness
description: Fires when an asset's 24h trading volume on Bit2Me exceeds 2x its
             30-day average volume. Indicates unusual market interest.

ELIGIBILITY CRITERIA
- who_receives: consent_marketing_push = true AND (holds_asset OR asset_on_watchlist)
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed B-family in last 7 days
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: Top 50-100 by Bit2Me volume

DELIVERY RULES
- priority_tier: P3
- channel: Push (primary), In-App (secondary)
- cooldown: 1/day, 3/week
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (CoinGecko API for market volume; BigQuery for Bit2Me volume)
- required_events: None
- required_user_properties: consent_marketing_push, asset_holdings, watchlist_assets,
                            notification_fatigue_score
- evaluation_frequency: Hourly

COMPLIANCE
- compliance_class: INFORMATIONAL
- diego_approval: TEMPLATE_PRE_APPROVED
- mica_risk_level: LOW
- risk_warning_required: false
- keyword_blocklist_applies: true

MiCA ART. 87-92 REQUIREMENTS:
- Data source: CoinGecko API (public) + Bit2Me aggregate volume (not individual orders)
- Simultaneous delivery: YES
- Audit log: trigger_id, timestamp, user_count, volume_value, volume_30d_avg, data_source_url
```

---

#### Trigger B-03: Trending Asset

```
TRIGGER DEFINITION: B-03 Trending Asset
========================================
trigger_id: B-03
family: B (Market Triggered)
trigger_name: Trending Asset Alert
business_objective: Discovery, engagement with new assets
description: Fires when an asset enters the Top 10 trending on CoinGecko (social
             mentions + search volume + price performance composite). Targets users
             who hold or watch the asset, OR users whose trading history suggests
             interest in similar asset categories (e.g., DeFi, L1, stablecoins).

ELIGIBILITY CRITERIA
- who_receives: consent_marketing_push = true AND
                (holds_asset OR asset_on_watchlist OR traded_similar_category_last_90d)
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed B-family in last 7 days
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: Top 50-100 by Bit2Me volume (trending asset must be in this scope)

DELIVERY RULES
- priority_tier: P3
- channel: Push (primary), In-App (secondary)
- cooldown: 1/day, 3/week
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (CoinGecko trending endpoint -- /search/trending)
- required_events: None
- required_user_properties: consent_marketing_push, asset_holdings, watchlist_assets,
                            trading_categories (computed), notification_fatigue_score
- evaluation_frequency: Every 4 hours (trending list updates slowly)

COMPLIANCE
- compliance_class: INFORMATIONAL
- diego_approval: TEMPLATE_PRE_APPROVED
- mica_risk_level: MEDIUM (trending could imply recommendation -- copy must be purely factual)
- risk_warning_required: false (if copy is factual: "ETH is trending on CoinGecko")
- keyword_blocklist_applies: true

MiCA ART. 87-92 REQUIREMENTS:
- Data source: CoinGecko trending API (public)
- Simultaneous delivery: YES
- Audit log: trigger_id, timestamp, user_count, trending_rank, data_source_url
```

---

#### Trigger B-04: Price Breakout

```
TRIGGER DEFINITION: B-04 Price Breakout
========================================
trigger_id: B-04
family: B (Market Triggered)
trigger_name: Price Breakout Alert
business_objective: Trading activation, technical signal awareness
description: Fires when an asset breaks above its 30-day high or below its 30-day low
             (range breakout). Simple technical signal that does not require charting knowledge.

ELIGIBILITY CRITERIA
- who_receives: consent_marketing_push = true AND (holds_asset OR asset_on_watchlist)
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed B-family in last 7 days
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: Top 50-100 by Bit2Me volume

DELIVERY RULES
- priority_tier: P3
- channel: Push (primary), In-App (secondary)
- cooldown: 1/day, 3/week
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: Cloud Function (CoinGecko API -- 30d high/low vs current price)
- required_events: None
- required_user_properties: consent_marketing_push, asset_holdings, watchlist_assets,
                            notification_fatigue_score
- evaluation_frequency: Hourly

COMPLIANCE
- compliance_class: INFORMATIONAL
- diego_approval: TEMPLATE_PRE_APPROVED
- mica_risk_level: MEDIUM (breakout language could imply opportunity -- copy must be neutral)
- risk_warning_required: false (if copy is factual: "BTC has reached a new 30-day high")
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "BTC has reached a new 30-day high of $72,400."
  UNSAFE: "BTC just broke out! Don't miss this opportunity." (urgency + implied action)

MiCA ART. 87-92 REQUIREMENTS:
- Data source: CoinGecko API (public)
- Simultaneous delivery: YES
- Audit log: trigger_id, timestamp, user_count, breakout_direction, price_value, data_source_url
```

---

### 6.4 Family C: Behavioral

> **Definition:** Triggers based on in-app user behavior patterns detected through CleverTap event analysis or BigQuery session data. These fire when a user demonstrates a pattern that suggests intent without completion (e.g., viewed an asset multiple times but did not purchase). Because they are platform-initiated and promote commercial actions, they are classified as MARKETING and require explicit consent.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-MKT (for market-related behaviors) or CAT-PRO (for product-related behaviors) |
| priority_tier | P3 (engagement behaviors) or P4 (product-related behaviors) |
| compliance_class | MARKETING (encourages a commercial action based on observed behavior) |
| channel | In-App (primary -- lower permission risk), Push (secondary) |
| cooldown | 1/week per behavioral pattern |
| quiet_hours_exempt | No |
| diego_approval | REQUIRED per template (Tier 1) |
| data_source | CleverTap Live Segments (real-time) or BigQuery session analysis (daily) |

**Entry Criteria:** Behavioral pattern detected: viewed asset 3+ times without purchase, deposited without trading within 72h, started order but abandoned, repeated login without action.

**Exit Criteria:** User completes the suggested action OR 30 days pass from pattern detection.

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | Users matching the behavioral pattern with `consent_marketing_push = true` or `consent_marketing_inapp = true` |
| who_never_receives | `C8_Whale_Suppression`, `Excluded_Users`, users in an active CleverTap journey (J1-J6 -- check `active_journey` property), `notification_fatigue_score > 0.7` |
| asset_scope | Assets the user has interacted with (viewed, traded, held) -- from Layer 3 of asset universe |

**Copy constraints:** Describe the user's behavior factually. "You viewed ETH 3 times this week" = SAFE. "ETH is a great opportunity since you keep looking at it" = ADVISORY_RISK, DO NOT USE.

---

#### Trigger C-01: Watched Not Bought

```
TRIGGER DEFINITION: C-01 Watched Not Bought
=============================================
trigger_id: C-01
family: C (Behavioral)
trigger_name: Watched Not Bought
business_objective: Conversion (view-to-purchase), revenue
description: User has viewed an asset detail page 3+ times in 7 days without making
             a purchase. Indicates interest without action -- gentle nudge toward
             completing the conversion.

ELIGIBILITY CRITERIA
- who_receives: Users who viewed asset page 3+ times in 7 days AND
                did NOT purchase that asset in the same period AND
                consent_marketing_inapp = true OR consent_marketing_push = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL (in CleverTap journey),
                      notification_fatigue_score > 0.7
- consent_category: CAT-MKT (Art. 6(1)(a))
- consent_required: true
- asset_scope: The specific asset(s) the user viewed (Layer 3)

DELIVERY RULES
- priority_tier: P3
- channel: In-App (primary), Push (secondary)
- cooldown: 1/week per asset; max 2 behavioral nudges per week across all C-family
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: CleverTap Live Segment (Product_Viewed event count >= 3 in 7d,
               no Purchase_Completed for same asset in same period)
- required_events: Product_Viewed (SDK), Purchase_Completed (Backend)
- required_user_properties: consent_marketing_push, consent_marketing_inapp,
                            active_journey, notification_fatigue_score
- evaluation_frequency: Daily (CleverTap Live Segment with lookback window)

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1 -- template pre-approval)
- mica_risk_level: LOW (behavioral nudge, not price-based)
- risk_warning_required: true (link to risk page for any asset purchase suggestion)
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "You have been looking at ETH recently. Here is the current price: $3,450."
  UNSAFE: "You keep looking at ETH -- now is a great time to buy!" (action suggestion + urgency)
```

---

#### Trigger C-02: Deposit No Trade (72h)

```
TRIGGER DEFINITION: C-02 Deposit No Trade
==========================================
trigger_id: C-02
family: C (Behavioral)
trigger_name: Deposit Without Trade (72h)
business_objective: Activation (deposit-to-first-trade conversion)
description: User deposited funds (fiat or crypto) but has not made any trade within
             72 hours. Indicates the user completed a high-intent action (funding) but
             stalled before trading.

ELIGIBILITY CRITERIA
- who_receives: Users who completed a deposit (Deposit_Completed event) AND
                no Purchase_Completed or Trade_Executed in 72h after deposit AND
                consent_marketing_push = true OR consent_marketing_inapp = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: Not asset-specific (user has not chosen an asset yet)

DELIVERY RULES
- priority_tier: P3
- channel: In-App (primary), Push (secondary)
- cooldown: Once per deposit event (do not repeat for the same deposit)
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: CleverTap Live Segment (Deposit_Completed in last 72h,
               no Purchase_Completed or Trade_Executed after deposit timestamp)
- required_events: Deposit_Completed (Backend), Purchase_Completed (Backend),
                   Trade_Executed (Backend)
- required_user_properties: consent_marketing_push, consent_marketing_inapp,
                            active_journey, notification_fatigue_score
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW
- risk_warning_required: true (link to risk page)
- keyword_blocklist_applies: true
```

---

#### Trigger C-03: Abandoned Order

```
TRIGGER DEFINITION: C-03 Abandoned Order
==========================================
trigger_id: C-03
family: C (Behavioral)
trigger_name: Abandoned Order
business_objective: Conversion recovery, revenue
description: User started a buy/sell order flow (reached order preview or confirmation
             screen) but did not complete the transaction within 30 minutes. Classic
             e-commerce cart abandonment pattern applied to crypto trading.

ELIGIBILITY CRITERIA
- who_receives: Users who triggered Order_Started event AND
                no Purchase_Completed within 30 minutes for the same asset AND
                consent_marketing_inapp = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: The specific asset from the abandoned order

DELIVERY RULES
- priority_tier: P3
- channel: In-App (primary -- contextual, shows when user returns to app),
           Push (secondary -- only if user does not return within 4h)
- cooldown: 1/week per asset; max 2 abandoned order nudges per week
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: CleverTap Live Segment (Order_Started event with no matching
               Purchase_Completed within 30 min)
- required_events: Order_Started (SDK), Purchase_Completed (Backend)
- required_user_properties: consent_marketing_inapp, consent_marketing_push,
                            active_journey, notification_fatigue_score
- evaluation_frequency: Real-time (CleverTap inaction segment -- 30 min after event)

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW
- risk_warning_required: true (link to risk page)
- keyword_blocklist_applies: true
```

---

#### Trigger C-04: Repeated Views No Action

```
TRIGGER DEFINITION: C-04 Repeated Views No Action
===================================================
trigger_id: C-04
family: C (Behavioral)
trigger_name: Repeated Login Without Action
business_objective: Engagement, activation
description: User has logged in 5+ times in 14 days without performing any value action
             (no trade, no deposit, no alert creation, no product exploration). Indicates
             a user who opens the app but does not engage -- potential early disengagement signal.

ELIGIBILITY CRITERIA
- who_receives: Users with 5+ App_Launched events in 14 days AND
                zero value actions (Purchase_Completed, Deposit_Completed,
                Price_Alert_Set, Earn_Subscribed) in same period AND
                consent_marketing_inapp = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7,
                      lifecycle_stage IN (DORMANT_BAL, DORMANT_ZERO, CHURNED)
- consent_category: CAT-PRO (product discovery -- help user find relevant features)
- consent_required: true
- asset_scope: Not asset-specific (engagement-based, not asset-based)

DELIVERY RULES
- priority_tier: P4 (product exploration nudge)
- channel: In-App (primary -- show feature discovery card on next login)
- cooldown: 1/month (very low frequency -- this is a soft engagement nudge)
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery session analysis (count App_Launched events vs value actions
               over 14-day rolling window)
- required_events: App_Launched (SDK), Purchase_Completed (Backend),
                   Deposit_Completed (Backend), Price_Alert_Set (SDK),
                   Earn_Subscribed (Backend)
- required_user_properties: consent_marketing_inapp, active_journey,
                            notification_fatigue_score, lifecycle_stage
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: NONE (feature discovery, not asset-related)
- risk_warning_required: false (no asset or investment mentioned)
- keyword_blocklist_applies: true
```


### 6.5 Family D: Lifecycle

> **Definition:** Triggers driven by lifecycle stage transitions from Bit2Me's 13-stage lifecycle model (EXCLUDED, REGISTERED, KYC, DEPOSITED, FM, ACTIVE, POWER, AT_RISK, PRE_DORMANCY, DORMANT_BAL, DORMANT_ZERO, REACTIVATED, CHURNED). These fire when a user moves between stages or meets time-based conditions within a stage. Because they promote engagement and retention actions, they are classified as MARKETING.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-MKT (stage transition awareness) or CAT-PRO (product re-engagement) |
| priority_tier | P2 (critical transitions like ACTIVE to AT_RISK) or P5 (reactivation campaigns for dormant users) |
| compliance_class | MARKETING (encourages re-engagement or continued use) |
| channel | Email (primary -- richer context for lifecycle messages), Push (secondary), In-App (tertiary) |
| cooldown | 1/week per journey |
| quiet_hours_exempt | No |
| diego_approval | REQUIRED per template (Tier 1) |
| data_source | BigQuery `lifecycle_stage` field (via Hightouch sync to CleverTap) |

**Entry Criteria:** Lifecycle stage transition detected in BigQuery: user moves from one stage to another, or meets a time-based condition within their current stage (e.g., 30 days inactive in ACTIVE stage triggers AT_RISK transition).

**Exit Criteria:** User transitions to a different stage OR completes the suggested re-engagement action.

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | Users who transitioned stages with `consent_marketing_email = true` or `consent_marketing_push = true` |
| who_never_receives | `C8_Whale_Suppression`, `Excluded_Users`, users in an active CleverTap journey (J1-J6 -- check `active_journey` property is NOT NULL), `notification_fatigue_score > 0.7` (CRITICAL for lifecycle: sending to fatigued users accelerates churn) |
| asset_scope | Not asset-specific (lifecycle stage-based triggers target the user's overall engagement state, not a specific asset) |

**IMPORTANT -- Active Journey Conflict Avoidance:**

Every Family D trigger must check whether the user is currently in an active CleverTap journey (J1 Brokerage, J2 Pro, J3 Earn, J4 Card, J5 B2B, J6 Multi, or J-Post-FM). If `active_journey IS NOT NULL`, suppress all Family D triggers for that user. This prevents conflicting lifecycle messages (e.g., a "you are becoming inactive" trigger firing while the user is in the middle of an onboarding journey).

**Implementation:** Add `active_journey` as a Hightouch-synced user property from BigQuery. BigQuery tracks journey entry/exit events from CleverTap webhook exports. When a user enters a journey, `active_journey` is set to the journey name. When they exit (completion or timeout), it is set to NULL.

---

#### Trigger D-01: Active to At-Risk Transition

```
TRIGGER DEFINITION: D-01 Active to At-Risk Transition
=======================================================
trigger_id: D-01
family: D (Lifecycle)
trigger_name: Active to At-Risk Transition
business_objective: Retention, churn prevention
description: Fires when a user's lifecycle stage transitions from ACTIVE to AT_RISK
             (triggered by 30+ days without a value action). This is the highest-value
             retention intervention point -- the user is still reachable but disengaging.

ELIGIBILITY CRITERIA
- who_receives: Users whose lifecycle_stage changed from ACTIVE to AT_RISK AND
                consent_marketing_email = true OR consent_marketing_push = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7
- consent_category: CAT-MKT (Art. 6(1)(a))
- consent_required: true
- asset_scope: Not asset-specific

DELIVERY RULES
- priority_tier: P2 (lifecycle critical -- highest marketing priority)
- channel: Email (primary -- longer format for re-engagement), Push (secondary)
- cooldown: 1/week per journey; this trigger fires ONCE per stage transition
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (lifecycle_stage transition detected in daily scheduled query)
- required_events: None (state transition, not event-based)
- required_user_properties: lifecycle_stage, days_since_last_activity, health_score,
                            total_balance_eur, active_journey, consent_marketing_email,
                            consent_marketing_push, notification_fatigue_score
- evaluation_frequency: Daily (BigQuery lifecycle stage computation runs daily)

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW (re-engagement, not asset-specific)
- risk_warning_required: false (no asset or investment mentioned)
- keyword_blocklist_applies: true
```

---

#### Trigger D-02: Dormant With Balance

```
TRIGGER DEFINITION: D-02 Dormant With Balance
===============================================
trigger_id: D-02
family: D (Lifecycle)
trigger_name: Dormant With Balance Reminder
business_objective: Reactivation, AUC mobilization
description: Fires when a user is in DORMANT_BAL stage (inactive 90+ days) with a
             balance above EUR 50. These 72.4K users hold EUR 19.5M in AUC -- gentle
             reminders can reactivate dormant capital without aggressive tactics.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage = DORMANT_BAL AND total_balance_eur > 50 AND
                consent_marketing_email = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7
- consent_category: CAT-PRO (promotional re-engagement)
- consent_required: true
- asset_scope: Not asset-specific

DELIVERY RULES
- priority_tier: P5 (reactivation -- lowest marketing priority)
- channel: Email (primary -- non-intrusive for dormant users)
- cooldown: 1/month (very low frequency for dormant users -- over-messaging drives permanent opt-out)
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (lifecycle_stage + total_balance_eur)
- required_events: None
- required_user_properties: lifecycle_stage, total_balance_eur, days_since_last_activity,
                            active_journey, consent_marketing_email,
                            notification_fatigue_score
- evaluation_frequency: Weekly (dormant users do not need daily evaluation)

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW
- risk_warning_required: false
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "Your Bit2Me account still holds EUR 342. Log in to check your portfolio."
  UNSAFE: "Your crypto might be growing! Log in before you miss out." (implied opportunity + urgency)
```

---

#### Trigger D-03: First Trade Celebration

```
TRIGGER DEFINITION: D-03 First Trade Celebration
==================================================
trigger_id: D-03
family: D (Lifecycle)
trigger_name: First Trade Celebration
business_objective: Activation reinforcement, habit formation
description: Fires when a user completes their first trade (lifecycle transition from
             DEPOSITED to FM -- First Monetization). Celebrates the milestone and
             suggests next steps to build trading habit.

ELIGIBILITY CRITERIA
- who_receives: Users whose lifecycle_stage just changed from DEPOSITED to FM AND
                consent_marketing_push = true OR consent_marketing_email = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users
                      (no fatigue filter -- celebration messages have high positive reception)
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: The asset the user traded (personalization)

DELIVERY RULES
- priority_tier: P2 (lifecycle critical -- first trade is highest-value moment)
- channel: Push (primary -- immediate positive reinforcement), Email (secondary -- persistent)
- cooldown: Once (fires only on first trade ever)
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (lifecycle_stage transition DEPOSITED -> FM)
- required_events: Purchase_Completed (Backend -- first ever)
- required_user_properties: lifecycle_stage, first_trade_asset, first_trade_amount_eur,
                            consent_marketing_push, consent_marketing_email
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: NONE (celebration, no suggestion)
- risk_warning_required: false
- keyword_blocklist_applies: true
```

---

#### Trigger D-04: Recurring Purchase Lapsed

```
TRIGGER DEFINITION: D-04 Recurring Purchase Lapsed
====================================================
trigger_id: D-04
family: D (Lifecycle)
trigger_name: Recurring Purchase Lapsed
business_objective: Retention, recurring revenue protection
description: Fires when a user with an active recurring buy (DCA -- Dollar Cost Averaging)
             has not had a successful execution in 30+ days. Could indicate: failed payment
             method, insufficient funds, or user cancelled without awareness.

ELIGIBILITY CRITERIA
- who_receives: Users with recurring_buy_active = true AND
                days_since_last_recurring_execution > 30 AND
                consent_marketing_push = true OR consent_marketing_email = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      active_journey IS NOT NULL,
                      notification_fatigue_score > 0.7
- consent_category: CAT-MKT
- consent_required: true
- asset_scope: The asset(s) in the lapsed recurring buy

DELIVERY RULES
- priority_tier: P2 (lifecycle critical -- recurring revenue at risk)
- channel: Email (primary -- needs explanation of what happened), Push (secondary)
- cooldown: 1/week until resolved or user cancels recurring buy
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (recurring_buy_active + last_recurring_execution_date)
- required_events: Recurring_Buy_Executed (Backend), Recurring_Buy_Failed (Backend)
- required_user_properties: recurring_buy_active, days_since_last_recurring_execution,
                            recurring_buy_assets, active_journey,
                            consent_marketing_push, consent_marketing_email,
                            notification_fatigue_score
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: NONE (service status, not investment suggestion)
- risk_warning_required: false
- keyword_blocklist_applies: true
```

---

### 6.6 Family E: Product Cross-sell

> **Definition:** Triggers that encourage adoption of Bit2Me products the user does not currently use. These fire when a product eligibility gap is detected -- the user meets the criteria for a product but has not activated it. Because they promote specific commercial products, they are classified as MARKETING and require explicit consent. Some cross-sell copy risks crossing into ADVISORY_RISK territory -- strict copy guidelines apply.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-PRO (promotional -- Art. 6(1)(a) explicit consent) |
| priority_tier | P4 (cross-sell -- subject to global caps + campaign limit) |
| compliance_class | MARKETING (must be carefully classified -- some cross-sell copy risks ADVISORY_RISK) |
| channel | Email (primary -- richer context for product description), In-App (secondary) |
| cooldown | 1/week, 2/month maximum |
| quiet_hours_exempt | No |
| diego_approval | REQUIRED per template (Tier 1) |
| data_source | BigQuery (`products_active` field + asset holdings via Hightouch sync) |

**Entry Criteria:** Product eligibility gap detected: user holds stablecoins but has no Earn subscription, user is eligible for Loan based on collateral, Space Center mission is available, user is eligible for Pro based on trading volume.

**Exit Criteria:** User adopts the suggested product OR 90 days pass from trigger activation.

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | `lifecycle_stage IN (ACTIVE, POWER)` AND `consent_marketing_email = true` or `consent_marketing_push = true` AND product gap exists |
| who_never_receives | `C8_Whale_Suppression`, `Excluded_Users`, `notification_fatigue_score > 0.7`, users who dismissed an E-family notification in last 7 days, `lifecycle_stage IN (AT_RISK, PRE_DORMANCY, DORMANT_BAL, DORMANT_ZERO, CHURNED)` -- do NOT cross-sell to disengaged users |
| asset_scope | Product-specific subsets from Layer 2 of asset universe: Earn-eligible assets, Loan collateral-eligible assets, Pro-eligible trading pairs |

**CRITICAL -- MiCA Investment Advice Boundary:**

Cross-sell triggers sit at the boundary between MARKETING and ADVISORY_RISK. The classification depends entirely on the copy:

| Copy Example | Classification | Safe? |
|-------------|---------------|-------|
| "Your USDT could be earning rewards in Bit2Me Earn. Current APY: 3.2%. Variable rate. Capital at risk." | MARKETING | YES |
| "Earn 3.2% on your USDT -- more than most savings accounts!" | ADVISORY_RISK | NO -- compares crypto yield to non-crypto alternative |
| "Did you know Bit2Me offers a Loan product? Use your BTC as collateral." | MARKETING | YES |
| "Don't miss this opportunity to earn passive income on your stablecoins." | ADVISORY_RISK | NO -- urgency language + "passive income" framing |
| "You are eligible for Bit2Me Pro based on your trading volume. Try advanced order types." | MARKETING | YES |
| "Pro traders are making more with limit orders -- upgrade now!" | ADVISORY_RISK | NO -- implies financial advantage + urgency |

**Copy rule:** Describe the product factually. State current terms (APY, features). Include risk warnings. Never compare crypto yields to non-crypto alternatives. Never use urgency language.

---

#### Trigger E-01: Stablecoins Not in Earn

```
TRIGGER DEFINITION: E-01 Stablecoins Not in Earn
==================================================
trigger_id: E-01
family: E (Product Cross-sell)
trigger_name: Stablecoin Earn Opportunity
business_objective: Product adoption (Earn), revenue expansion
description: User holds stablecoins (USDT, USDC, DAI) in Wallet but has not
             subscribed to Earn for any of them.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage IN (ACTIVE, POWER) AND
                holds_stablecoins = true AND
                'earn' NOT IN products_active AND
                consent_marketing_push = true OR consent_marketing_email = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      users who dismissed E-family notification in last 7 days
- consent_category: CAT-PRO (promotional -- requires explicit consent)
- consent_required: true
- asset_scope: Earn-eligible stablecoins only (USDT, USDC, DAI -- from Layer 2)

DELIVERY RULES
- priority_tier: P4 (cross-sell)
- channel: Email (primary -- richer context), In-App (secondary)
- cooldown: 1/week, 2/month maximum
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (Hightouch sync -- products_active, asset holdings)
- required_events: None (state-based, not event-based)
- required_user_properties: products_active, total_balance_eur,
                            lifecycle_stage, holds_stablecoins (computed),
                            notification_fatigue_score
- evaluation_frequency: Daily (Hightouch sync)

COMPLIANCE
- compliance_class: MARKETING (promotes Earn product)
- diego_approval: REQUIRED (Tier 1 -- template pre-approval)
- mica_risk_level: MEDIUM (mentions yield -- must not compare to savings accounts)
- risk_warning_required: true ("APY is variable. Capital at risk.")
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "Your USDT could be earning rewards in Bit2Me Earn. Current APY: 3.2%.
         Variable rate. Capital at risk."
  UNSAFE: "Earn more than your bank with Bit2Me Earn!" (comparative = advisory risk)
  UNSAFE: "Don't miss this opportunity to earn passive income" (urgency + advisory)
```

---

#### Trigger E-02: Loan Eligible (Collateral Sufficient)

```
TRIGGER DEFINITION: E-02 Loan Eligible
========================================
trigger_id: E-02
family: E (Product Cross-sell)
trigger_name: Loan Eligible (Collateral Sufficient)
business_objective: Product adoption (Loan), revenue expansion
description: User holds sufficient crypto assets (BTC, ETH, or stablecoins) to qualify
             as collateral for a Bit2Me Loan but has not used the Loan product.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage IN (ACTIVE, POWER) AND
                collateral_eligible_balance_eur > minimum_collateral_threshold AND
                'loan' NOT IN products_active AND
                consent_marketing_email = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed E-family in last 7 days
- consent_category: CAT-PRO
- consent_required: true
- asset_scope: Collateral-eligible assets (BTC, ETH, stablecoins -- from Loan product Layer 2)

DELIVERY RULES
- priority_tier: P4
- channel: Email (primary), In-App (secondary)
- cooldown: 1/week, 2/month maximum
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (asset holdings + collateral eligibility rules)
- required_events: None (state-based)
- required_user_properties: products_active, collateral_eligible_balance_eur,
                            lifecycle_stage, notification_fatigue_score
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: MEDIUM (loan product -- must explain risks clearly)
- risk_warning_required: true ("Loan terms apply. Collateral may be liquidated if LTV exceeds threshold.")
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "Your BTC holding qualifies you for a Bit2Me Loan. Borrow EUR against your crypto.
         LTV and liquidation terms apply."
  UNSAFE: "Unlock the value of your BTC -- borrow cash without selling!" (implies guaranteed benefit)
```

---

#### Trigger E-03: Space Center Mission Available

```
TRIGGER DEFINITION: E-03 Space Center Mission Available
=========================================================
trigger_id: E-03
family: E (Product Cross-sell)
trigger_name: Space Center Mission Available
business_objective: Gamification engagement, B2M token utility, retention
description: User has an uncompleted Space Center mission available that would advance
             their tier. Encourages engagement with the gamification layer. B2M holders
             advance 100x faster -- this trigger also implicitly promotes B2M holding.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage IN (ACTIVE, POWER) AND
                space_center_missions_available > 0 AND
                consent_marketing_inapp = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed E-family in last 7 days
- consent_category: CAT-PRO
- consent_required: true
- asset_scope: B2M token primarily (Space Center progression tied to B2M holding)

DELIVERY RULES
- priority_tier: P4
- channel: In-App (primary -- gamification is in-app native), Push (secondary)
- cooldown: 1/week, 2/month maximum
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (Space Center data -- TBD, may require backend API if not in BigQuery)
- required_events: Mission_Completed (Backend), Tier_Advanced (Backend)
- required_user_properties: space_center_tier, space_center_missions_available,
                            b2m_holdings, lifecycle_stage, notification_fatigue_score
- evaluation_frequency: Daily (if BigQuery) or Real-time (if backend push)

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW (gamification, not direct investment suggestion)
- risk_warning_required: false (gamification missions, not financial product)
- keyword_blocklist_applies: true

NOTE: Space Center data availability in BigQuery is an open question (see 02-RESEARCH.md
Open Questions #3). If data is not in BigQuery, this trigger moves to V2.
```

---

#### Trigger E-04: Pro Eligible (Volume Threshold Met)

```
TRIGGER DEFINITION: E-04 Pro Eligible
=======================================
trigger_id: E-04
family: E (Product Cross-sell)
trigger_name: Pro Eligible (Volume Threshold Met)
business_objective: Product adoption (Pro), power user conversion
description: User's 30-day trading volume exceeds the threshold where Pro features
             (limit orders, order book, lower fees) become beneficial. Nudge toward
             trying Pro trading interface.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage IN (ACTIVE, POWER) AND
                trading_volume_30d_eur > pro_volume_threshold AND
                'pro' NOT IN products_active AND
                consent_marketing_email = true OR consent_marketing_push = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      dismissed E-family in last 7 days
- consent_category: CAT-PRO
- consent_required: true
- asset_scope: Pro-eligible trading pairs (subset with sufficient liquidity)

DELIVERY RULES
- priority_tier: P4
- channel: Email (primary), In-App (secondary)
- cooldown: 1/week, 2/month maximum
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (trading_volume_30d_eur computed from trade events)
- required_events: Trade_Executed (Backend -- for volume computation)
- required_user_properties: products_active, trading_volume_30d_eur,
                            lifecycle_stage, notification_fatigue_score
- evaluation_frequency: Daily

COMPLIANCE
- compliance_class: MARKETING
- diego_approval: REQUIRED (Tier 1)
- mica_risk_level: LOW (feature awareness, not investment suggestion)
- risk_warning_required: false (Pro is a trading interface upgrade, not a financial product per se)
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "Based on your trading volume, you qualify for Bit2Me Pro. Access limit orders,
         order book view, and reduced fees."
  UNSAFE: "Pro traders are making smarter trades -- upgrade now!" (implies financial advantage)
```

---

### 6.7 Family F: Risk and Protective

> **Definition:** Alerts that protect the user from financial risk or inform them of account risk conditions. These are the highest-priority notifications in the system. Because they protect user interests rather than promote Bit2Me products, they are classified as TRANSACTIONAL and do NOT require marketing consent. Some (P0 security alerts) are exempt from ALL delivery restrictions including quiet hours and frequency caps.

**Family Properties:**

| Property | Value |
|----------|-------|
| consent_category | CAT-SEC (security/protective alerts) or CAT-TXN (LTV alerts for Loan product) |
| priority_tier | P0 (security -- always delivers, no restrictions) or P1 (risk awareness -- exempt from global caps but respects quiet hours) |
| compliance_class | TRANSACTIONAL (contractual necessity -- Art. 6(1)(b)) |
| channel | Push (immediate -- time-critical), Email (persistent record for audit) |
| cooldown | F-01: progressive escalation (no cooldown between tiers); F-02: 1/30 days; F-03/F-04: immediate |
| quiet_hours_exempt | P0 = YES (security alerts send at any hour); P1 = NO |
| diego_approval | NOT_REQUIRED (transactional -- contractual necessity) |
| data_source | Backend events (real-time for security), BigQuery (for balance/LTV monitoring) |

**Entry Criteria:** Risk condition detected: LTV approaching liquidation threshold, large balance with 60+ days inactivity, failed recurring buy, failed withdrawal, unusual login activity.

**Exit Criteria:** Risk condition resolved: LTV decreases below threshold, user takes action, failed action succeeds on retry, security concern investigated.

**Eligibility Rules:**

| Rule | Value |
|------|-------|
| who_receives | ALL users meeting the risk condition -- NO marketing consent required for protective alerts (Art. 6(1)(b) contractual necessity) |
| who_never_receives | **None for P0 security alerts** -- security ALWAYS sends, even to C8 whale accounts. For P1 risk awareness: `Excluded_Users` only. |
| asset_scope | Assets the user currently holds or has collateralized |

**Frequency cap exemption:** P0 and P1 are exempt from global caps via "Exclude from Global campaign limits" checkbox in CleverTap (see Section 2.3).

**Quiet hours exemption:** P0 security alerts (F-04 Unusual Login Activity, certain F-01 tiers) are NOT subject to quiet hours -- they send at any time. P1 risk awareness alerts respect quiet hours.

---

#### Trigger F-01: LTV Warning (3-Tier Graduated)

```
TRIGGER DEFINITION: F-01 LTV Warning (Graduated)
==================================================
trigger_id: F-01
family: F (Risk and Protective)
trigger_name: LTV Warning (3-Tier Graduated Alert)
business_objective: Risk management, liquidation prevention, user trust
description: For Loan users, monitors LTV (Loan-to-Value) ratio and sends graduated
             warnings as LTV approaches the liquidation threshold. Modeled on Nexo's
             proven 3-tier system. Each tier escalates in urgency and channel.

TIER 1 -- CAUTION (LTV >= 71.4%):
  Copy: "Your loan LTV has reached 71.4%. Consider adding collateral to reduce risk."
  Channel: Push + In-App
  Priority: P1

TIER 2 -- WARNING (LTV >= 74.1%):
  Copy: "Your loan LTV is at 74.1%. Liquidation risk is increasing. Add collateral now."
  Channel: Push + Email + In-App
  Priority: P1

TIER 3 -- CRITICAL (LTV >= 76.9%):
  Copy: "URGENT: Your loan LTV is at 76.9%. Liquidation will occur at 80%. Add collateral immediately."
  Channel: Push (P0 -- sends at any hour) + Email + In-App + SMS (if available)
  Priority: P0 (quiet hours exempt)

ELIGIBILITY CRITERIA
- who_receives: ALL users with active loans whose LTV reaches any tier threshold
- who_never_receives: NONE (P0 security/risk -- always delivers)
- consent_category: CAT-TXN (loan monitoring is contractual -- Art. 6(1)(b))
- consent_required: false (contractual necessity)
- asset_scope: Collateral-eligible assets (BTC, ETH, stablecoins)

DELIVERY RULES
- priority_tier: P1 (Tiers 1-2), P0 (Tier 3 -- CRITICAL)
- channel: Progressive escalation per tier (see above)
- cooldown: No cooldown between tiers (each tier is a separate notification).
            Within same tier: 1 per 4 hours (LTV can fluctuate).
            Reset when LTV drops below tier threshold.
- quiet_hours_exempt: Tier 3 = YES (P0); Tiers 1-2 = NO (P1)

DATA REQUIREMENTS
- data_source: BigQuery (loan_ltv_current computed from collateral price + loan balance)
- required_events: None (state-based -- LTV computed from price feed)
- required_user_properties: active_loan_id, loan_ltv_current, loan_balance_eur,
                            collateral_asset, collateral_amount
- evaluation_frequency: Every 15 minutes (critical -- price moves can trigger liquidation)

COMPLIANCE
- compliance_class: TRANSACTIONAL (contractual risk notification)
- diego_approval: NOT_REQUIRED (transactional)
- mica_risk_level: NONE (protective, not promotional)
- risk_warning_required: false (the notification IS the risk warning)
- keyword_blocklist_applies: false
```

---

#### Trigger F-02: Large Balance Inactivity (60d)

```
TRIGGER DEFINITION: F-02 Large Balance Inactivity
===================================================
trigger_id: F-02
family: F (Risk and Protective)
trigger_name: Large Balance Inactivity Warning
business_objective: User protection, dormant account security awareness
description: Fires when a user with a balance exceeding EUR 1,000 has been inactive
             for 60+ days. Serves as a security check ("is this still you?") and a
             gentle reminder that they hold significant value on the platform.

ELIGIBILITY CRITERIA
- who_receives: ALL users with total_balance_eur > 1000 AND
                days_since_last_activity > 60
- who_never_receives: Excluded_Users (C8 whale accounts RECEIVE this -- protective alert)
- consent_category: CAT-SEC (account security awareness -- Art. 6(1)(b))
- consent_required: false (contractual -- protecting user's assets)
- asset_scope: All assets the user holds (aggregate balance check)

DELIVERY RULES
- priority_tier: P1 (risk awareness -- exempt from global caps)
- channel: Email (primary -- persistent record), Push (secondary)
- cooldown: 1 per 30 days (do not repeat frequently for dormant users)
- quiet_hours_exempt: false (P1 -- not urgent enough for night delivery)

DATA REQUIREMENTS
- data_source: BigQuery (total_balance_eur + days_since_last_activity)
- required_events: None (state-based)
- required_user_properties: total_balance_eur, days_since_last_activity, lifecycle_stage
- evaluation_frequency: Weekly (dormant user check does not need daily frequency)

COMPLIANCE
- compliance_class: TRANSACTIONAL (account security awareness)
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false

COPY CONSTRAINTS:
  SAFE: "Your Bit2Me account holds EUR 5,420 and has been inactive for 67 days.
         For your security, please verify your account is secure."
  UNSAFE: "Your crypto is sitting idle! Put it to work in Earn." (cross-sell disguised as security)
```

---

#### Trigger F-03: Failed Recurring Buy

```
TRIGGER DEFINITION: F-03 Failed Recurring Buy
===============================================
trigger_id: F-03
family: F (Risk and Protective)
trigger_name: Failed Recurring Buy Alert
business_objective: Service continuity, user awareness
description: Fires when a user's scheduled recurring buy (DCA) fails to execute.
             Failure reasons: insufficient balance, expired payment method, payment
             processor error. The user needs to know their DCA strategy was interrupted.

ELIGIBILITY CRITERIA
- who_receives: ALL users whose Recurring_Buy_Failed event fired
- who_never_receives: Excluded_Users only
- consent_category: CAT-TXN (transaction failure -- Art. 6(1)(b))
- consent_required: false (contractual -- service the user set up failed)
- asset_scope: The specific asset in the failed recurring buy

DELIVERY RULES
- priority_tier: P1 (user-configured service failure)
- channel: Push (immediate awareness), Email (persistent record with failure details)
- cooldown: Immediate (one notification per failure event)
- quiet_hours_exempt: false (P1 -- failure is important but not security-critical)

DATA REQUIREMENTS
- data_source: Backend event (Recurring_Buy_Failed -- real-time)
- required_events: Recurring_Buy_Failed (Backend -- with failure_reason property)
- required_user_properties: recurring_buy_active, recurring_buy_assets
- evaluation_frequency: Real-time (event-driven)

COMPLIANCE
- compliance_class: TRANSACTIONAL
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

---

#### Trigger F-04: Unusual Login Activity

```
TRIGGER DEFINITION: F-04 Unusual Login Activity
=================================================
trigger_id: F-04
family: F (Risk and Protective)
trigger_name: Unusual Login Activity Alert
business_objective: Account security, fraud prevention
description: Fires when a login is detected from a new device, new location (country/city),
             or at an unusual time (outside user's typical login hours). This is the
             highest-priority notification in the entire system -- P0, no restrictions.

ELIGIBILITY CRITERIA
- who_receives: ALL users when unusual login is detected
- who_never_receives: NONE (P0 security -- ALWAYS delivers to everyone, including C8 whales)
- consent_category: CAT-SEC (account security -- Art. 6(1)(b))
- consent_required: false (contractual necessity -- account protection)
- asset_scope: Not asset-specific (account-level security)

DELIVERY RULES
- priority_tier: P0 (security -- highest priority, no restrictions whatsoever)
- channel: Push (immediate) + Email (persistent record)
- cooldown: Immediate (one per suspicious event, no cooldown)
- quiet_hours_exempt: YES (P0 -- security alerts send at 3 AM if needed)

DATA REQUIREMENTS
- data_source: Backend event (Login_New_Device or Login_New_Location -- real-time)
- required_events: Login_New_Device (Backend), Login_New_Location (Backend)
- required_user_properties: known_devices (array), known_locations (array),
                            typical_login_hours (computed)
- evaluation_frequency: Real-time (event-driven, zero delay)

COMPLIANCE
- compliance_class: TRANSACTIONAL
- diego_approval: NOT_REQUIRED
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false

NOT SUBJECT TO:
- Frequency caps (P0 exempt via CleverTap "Exclude from Global campaign limits")
- Quiet hours (P0 security sends at any hour)
- Fatigue risk filtering (security always sends regardless of fatigue score)
- Suppression layers (only segment-level exclusion for Excluded_Users; C8 whales RECEIVE security alerts)
```

---

### 6.8 Cross-Reference Matrix

This matrix maps each trigger family to the Phase 1 constructs that govern its delivery. Use this as a quick reference when designing new triggers or auditing existing ones.

#### Family-to-Phase 1 Mapping

| Family | consent_category | priority_tier | compliance_class | diego_approval | typical_channel | typical_cooldown | asset_scope_type |
|--------|-----------------|---------------|-----------------|----------------|----------------|-----------------|-----------------|
| A (User Configured) | CAT-USR | P1 | TRANSACTIONAL | NOT_REQUIRED | Push, Email fallback | 1 per asset per 4h | All listed (Layer 1) |
| B (Market Triggered) | CAT-MKT | P3 | INFORMATIONAL | TEMPLATE_PRE_APPROVED | Push, In-App | 1/day, 3/week | Top 50-100 by volume |
| C (Behavioral) | CAT-MKT / CAT-PRO | P3-P4 | MARKETING | REQUIRED (Tier 1) | In-App, Push | 1/week per pattern | User-interacted assets (Layer 3) |
| D (Lifecycle) | CAT-MKT / CAT-PRO | P2 / P5 | MARKETING | REQUIRED (Tier 1) | Email, Push | 1/week per journey | Not asset-specific |
| E (Product Cross-sell) | CAT-PRO | P4 | MARKETING | REQUIRED (Tier 1) | Email, In-App | 1/week, 2/month | Product-specific (Layer 2) |
| F (Risk/Protective) | CAT-SEC / CAT-TXN | P0-P1 | TRANSACTIONAL | NOT_REQUIRED | Push, Email | Varies (progressive/immediate) | User-held assets |

#### Consent and Cap Rules by Family

| Family | Marketing Consent Required? | Subject to Global Frequency Caps? | Subject to Quiet Hours? | Subject to Fatigue Risk Suppression? | C8 Whale Suppressed? |
|--------|---------------------------|----------------------------------|------------------------|--------------------------------------|---------------------|
| A | No (contractual -- CAT-USR) | No (P1 exempt) | Yes (unless user opts 24/7) | No | Yes |
| B | Yes (CAT-MKT) | Yes (P3) | Yes | Yes (suppressed at > 0.7) | Yes |
| C | Yes (CAT-MKT / CAT-PRO) | Yes (P3-P4) | Yes | Yes (suppressed at > 0.7) | Yes |
| D | Yes (CAT-MKT / CAT-PRO) | Yes (P2) or Yes (P5) | Yes | Yes (suppressed at > 0.7) | Yes |
| E | Yes (CAT-PRO) | Yes (P4) | Yes | Yes (suppressed at > 0.7) | Yes |
| F | No (contractual -- CAT-SEC/CAT-TXN) | No (P0-P1 exempt) | P0: No, P1: Yes | No (security always sends) | P0: No (always sends), P1: No |

#### Suppression Layer Application by Family

| Family | Layer 1: Segment Exclusion | Layer 2: Quiet Hours (DND) | Layer 3: Opt-Out Handling | Layer 4: Escalating Cooldowns |
|--------|---------------------------|---------------------------|--------------------------|------------------------------|
| A | C8 + Excluded | Applied (22:00-08:00) | MSG-push/MSG-email DND checked | Dismissal cooldown applies |
| B | C8 + Excluded + Fatigue > 0.7 | Applied | Marketing consent checked | Dismissal cooldown applies; 7d family cooldown after 3 dismissals |
| C | C8 + Excluded + Fatigue > 0.7 + Active Journey | Applied | Marketing consent checked | Dismissal cooldown applies |
| D | C8 + Excluded + Fatigue > 0.7 + Active Journey | Applied | Marketing consent checked | Dismissal cooldown applies |
| E | C8 + Excluded + Fatigue > 0.7 + Dismissed E-family 7d | Applied | Marketing consent checked | Dismissal cooldown applies |
| F (P0) | None (always sends) | NOT applied (sends any hour) | MSG-push DND NOT checked for P0 | No cooldown (progressive escalation) |
| F (P1) | Excluded only | Applied | MSG-push/MSG-email DND checked | Cooldown varies per trigger |

---

### Cross-References

- **Section 1 (Preference Center Architecture):** Consent categories (CAT-SEC through CAT-PRO) determine which triggers require marketing consent and which CleverTap Subscription Groups users must be subscribed to.
- **Section 2 (Frequency Cap Policy):** Priority tiers (P0-P5) determine cap exemption, campaign-level limits, and fatigue risk thresholds per trigger.
- **Section 3 (Suppression System):** Suppression layers (segment exclusion, quiet hours, opt-out, cooldowns) apply differentially by family as documented in the Cross-Reference Matrix above.
- **Section 4 (Event Schema):** Required events listed in each trigger definition (e.g., Price_Alert_Set, Purchase_Completed, Deposit_Completed) must be tracked per the Phase 1 event schema.
- **Section 5 (Hightouch Reverse ETL):** User properties listed in each trigger definition (e.g., lifecycle_stage, products_active, notification_fatigue_score) must be included in the Hightouch sync configuration from BigQuery to CleverTap.
