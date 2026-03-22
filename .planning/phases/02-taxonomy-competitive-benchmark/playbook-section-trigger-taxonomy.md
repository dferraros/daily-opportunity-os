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

<!-- CONTINUATION POINT: Families D-F and Cross-Reference Matrix appended by Task 2b -->
