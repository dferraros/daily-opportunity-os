## 10. Scoring System Architecture

> **Purpose:** This section defines the 8 scoring formulas that determine whether a notification sends, who receives it, and how triggers are ranked when multiple fire simultaneously. Each formula outputs a 0-1 normalized score computed in BigQuery and synced to CleverTap via Hightouch. The Send Score Final (SCORE-08) uses a gated architecture: 3 binary gates (compliance, fatigue, cooldown) evaluated BEFORE the weighted composite score.
>
> **Owners:** Alvaro (BigQuery scheduled queries, view creation, Hightouch sync config), Katy (CleverTap campaign targeting using synced scores), Daniel (weight calibration, threshold tuning, formula iteration)
>
> **Cross-references:**
> - Section 2.5 (Fatigue Risk Score): SCORE-05 reproduces this formula unchanged
> - Section 6 (Trigger Taxonomy): Family-specific overrides reference family definitions
> - Section 9 (Compliance Framework): Gate 1 of Send Score Final references compliance classes

---

### 10.1 Scoring Pipeline Overview

All scores follow the same pipeline pattern established by the Phase 1 fatigue risk formula (Section 2.5):

```
BigQuery scheduled query (hourly or daily)
    |
    v
bit2me_lifecycle.user_scores (one row per user, one column per score)
    |
    v
Hightouch reverse ETL (30-min sync, upsert mode)
    |
    v
CleverTap user profile (custom properties: score_market_relevance, score_user_asset_affinity, etc.)
    |
    v
Campaign targeting: WHERE score > threshold AND compliance_gate = true
```

**Design principles:**
1. **Auditable:** Every score is a SQL expression, not a black box ML model. Critical for MiCA compliance and Diego review.
2. **Tunable:** Weights and thresholds are constants in the SQL, adjustable without code deployment. Daniel can recalibrate after A/B testing.
3. **Composable:** Each score is an independent BigQuery view. Send Score Final joins them. Adding a new score requires only a new view + one JOIN.
4. **Normalized:** Every formula outputs 0-1 using the `LEAST(1.0, GREATEST(0.0, ...))` pattern. No score exceeds 1.0 or drops below 0.0.

**Precedent:** The Phase 1 fatigue_risk score (Section 2.5) already uses this exact pipeline and has been validated in the architecture design. All 8 formulas follow the same pattern.

---

### 10.2 SCORE-01: Market Relevance Score

**What it measures:** How significant a market event is for notification purposes -- is this price move or volume spike noteworthy enough to alert users?

**Inputs:**

| Input | Source | Description |
|-------|--------|-------------|
| `pct_change_24h` | CoinGecko API via `bit2me_lifecycle.asset_market_stats` | Percentage price change in last 24 hours |
| `avg_pct_change_30d` | BigQuery 30-day rolling average | Mean daily percentage change over 30 days |
| `stddev_pct_change_30d` | BigQuery 30-day rolling stddev | Standard deviation of daily percentage change |
| `volume_24h` | CoinGecko API | Trading volume in last 24 hours (EUR) |
| `avg_volume_30d` | BigQuery 30-day rolling average | Mean daily trading volume over 30 days |

**Components:**

| Component | Formula | Interpretation |
|-----------|---------|---------------|
| `price_zscore_normalized` | `ABS(pct_change_24h - avg_pct_change_30d) / NULLIF(stddev_pct_change_30d, 0) / 4.0` | 2-sigma move = 0.50, 4-sigma move = 1.0 |
| `volume_anomaly_normalized` | `(volume_24h / NULLIF(avg_volume_30d, 0) - 1.0) / 3.0` | 2x average volume = 0.33, 4x average = 1.0 |

**Weights:** price_zscore 0.60, volume_anomaly 0.40

**BigQuery SQL:**

```sql
-- SCORE-01: Market Relevance Score
-- Runs: hourly via BigQuery scheduled query
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_market_relevance AS
SELECT
  asset_id,
  asset_symbol,
  -- Price change component (z-score of 24h change vs 30d distribution)
  LEAST(1.0, GREATEST(0.0,
    ABS(pct_change_24h - avg_pct_change_30d) / NULLIF(stddev_pct_change_30d, 0) / 4.0
  )) AS price_zscore_normalized,

  -- Volume anomaly component (ratio of current volume to 30d average)
  LEAST(1.0, GREATEST(0.0,
    (volume_24h / NULLIF(avg_volume_30d, 0) - 1.0) / 3.0
  )) AS volume_anomaly_normalized,

  -- Combined market relevance score
  LEAST(1.0, GREATEST(0.0,
    (ABS(pct_change_24h - avg_pct_change_30d) / NULLIF(stddev_pct_change_30d, 0) / 4.0) * 0.60
    + ((volume_24h / NULLIF(avg_volume_30d, 0) - 1.0) / 3.0) * 0.40
  )) AS market_relevance_score

FROM bit2me_lifecycle.asset_market_stats
WHERE tier IN ('T1', 'T3') AND median_daily_volume_eur_30d > 10000;
```

**Asset scope:** Only T1 (BTC, ETH) and T3 (mid-cap) assets with EUR 10K+ daily volume. T2 (stablecoins) use a separate de-peg threshold (absolute 2%, not z-score). T4 (memecoin) has no proactive alerts.

**Evaluation frequency:** Hourly

**Threshold calibration by asset tier:**

| Asset Tier | Avg Daily Vol (2025) | Default % Threshold (24h) | Z-Score Trigger | Rationale |
|-----------|---------------------|--------------------------|----------------|-----------|
| T1 (BTC, ETH) | ~2.2% (BTC), ~3.5% (ETH) | 5% | 2.0 sigma | BTC moves 2.2% daily; 5% is ~2.3 sigma. Triggers ~once per 2-3 weeks. |
| T2 (Stablecoins) | ~0.1% | 2% (de-peg alert) | N/A -- absolute | 2% deviation from peg for >1 hour = risk event. Classified CAT-SEC P0. |
| T3 (Mid-cap) | ~4-8% | 8% | 2.0 sigma | Higher baseline volatility. 8% filters noise while catching significant moves. |
| T4 (Memecoin) | ~10-30% | User-configured only | N/A | No proactive alerts for T4. Too noisy for platform-initiated notifications. |

---

### 10.3 SCORE-02: User Asset Affinity Score

**What it measures:** How much a specific user cares about a specific asset -- combining holdings, watchlist presence, trading recency, and viewing behavior.

**Inputs:**

| Input | Source | Description |
|-------|--------|-------------|
| `balance_eur` | BigQuery user holdings | User's current balance in this asset (EUR equivalent) |
| `on_watchlist` | CleverTap SDK event `Watchlist_Add` | Whether user has this asset on their watchlist |
| `days_since_last_trade` | BigQuery transaction history | Days since user last traded this asset |
| `views_last_30d` | CleverTap `Product_Viewed` events | Number of times user viewed this asset's page in last 30 days |

**Components:**

| Component | Formula | Interpretation |
|-----------|---------|---------------|
| `holdings_score` | `CASE WHEN balance_eur > 0 THEN LEAST(1.0, balance_eur / 500.0) ELSE 0.0 END` | EUR 500+ balance = max score |
| `watchlist_score` | `CASE WHEN on_watchlist THEN 0.50 ELSE 0.0 END` | Binary: on watchlist or not |
| `trade_recency_score` | `LEAST(1.0, GREATEST(0.0, 1.0 - (days_since_last_trade / 90.0)))` | 0 days = 1.0, 90+ days = 0.0 |
| `view_frequency_score` | `LEAST(1.0, views_last_30d / 10.0)` | 10+ views in 30 days = max score |

**Weights:** holdings 0.40, watchlist 0.20, trade_recency 0.25, views 0.15

**Note:** This is a per-user per-asset score, not per-user global. The BigQuery view produces one row per (user_id, asset_id) pair.

**BigQuery SQL:**

```sql
-- SCORE-02: User Asset Affinity Score
-- Runs: daily via BigQuery scheduled query
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_user_asset_affinity AS
SELECT
  user_id,
  asset_id,
  -- Holdings component: does user hold this asset?
  CASE WHEN balance_eur > 0 THEN
    LEAST(1.0, balance_eur / 500.0)  -- EUR 500+ balance = max score
  ELSE 0.0 END AS holdings_score,

  -- Watchlist component
  CASE WHEN on_watchlist = true THEN 0.50 ELSE 0.0 END AS watchlist_score,

  -- Trade recency component
  CASE WHEN days_since_last_trade IS NOT NULL THEN
    LEAST(1.0, GREATEST(0.0, 1.0 - (days_since_last_trade / 90.0)))
  ELSE 0.0 END AS trade_recency_score,

  -- View frequency component
  LEAST(1.0, COALESCE(views_last_30d, 0) / 10.0) AS view_frequency_score,

  -- Combined affinity score
  LEAST(1.0, GREATEST(0.0,
    CASE WHEN balance_eur > 0 THEN LEAST(1.0, balance_eur / 500.0) ELSE 0.0 END * 0.40
    + CASE WHEN on_watchlist THEN 0.50 ELSE 0.0 END * 0.20
    + COALESCE(LEAST(1.0, GREATEST(0.0, 1.0 - (days_since_last_trade / 90.0))), 0.0) * 0.25
    + LEAST(1.0, COALESCE(views_last_30d, 0) / 10.0) * 0.15
  )) AS user_asset_affinity_score

FROM bit2me_lifecycle.user_asset_interactions;
```

---

### 10.4 SCORE-03: Trigger Opportunity Score

**What it measures:** The combined opportunity of sending a specific trigger to a specific user -- is there a relevant market event AND does the user care about this asset AND is this trigger family appropriate?

**Formula:** MULTIPLICATIVE, not additive. Any zero component kills the trigger.

```sql
trigger_opportunity = market_relevance_score * user_asset_affinity_score * trigger_family_weight
```

**Why multiplicative:** A user with high affinity (0.9) for an asset with zero market movement (0.0) should NOT receive a market alert. Similarly, a significant market event (0.9) for an asset the user has never interacted with (0.0) should not trigger. Multiplication ensures both conditions must be present.

**Trigger family weights:**

| Family | Weight | Rationale |
|--------|--------|-----------|
| A (User Configured) | 1.0 | User requested -- always fires if conditions met |
| B (Market Triggered) | 0.80 | Market data, moderately selective |
| C (Behavioral) | 0.60 | Behavioral nudges, more selective to protect permissions |
| D (Lifecycle) | 0.90 | Lifecycle transitions are rare and high-value when they fire |
| E (Cross-sell) | 0.50 | Most selective -- highest bar to protect push permissions |
| F (Risk & Protective) | 1.0 | Protective alerts always fire if conditions met |

**BigQuery pseudocode:**

```sql
-- SCORE-03: Trigger Opportunity Score
-- Joins market relevance and user asset affinity
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_trigger_opportunity AS
SELECT
  ua.user_id,
  ua.asset_id,
  mr.market_relevance_score,
  ua.user_asset_affinity_score,
  t.trigger_family_weight,

  -- Multiplicative combination
  LEAST(1.0, GREATEST(0.0,
    COALESCE(mr.market_relevance_score, 0.0)
    * ua.user_asset_affinity_score
    * t.trigger_family_weight
  )) AS trigger_opportunity_score

FROM bit2me_lifecycle.score_user_asset_affinity ua
LEFT JOIN bit2me_lifecycle.score_market_relevance mr
  ON ua.asset_id = mr.asset_id
CROSS JOIN (
  -- Trigger family weights (parameterized)
  SELECT 'A' AS family, 1.0 AS trigger_family_weight UNION ALL
  SELECT 'B', 0.80 UNION ALL
  SELECT 'C', 0.60 UNION ALL
  SELECT 'D', 0.90 UNION ALL
  SELECT 'E', 0.50 UNION ALL
  SELECT 'F', 1.0
) t;
```

---

### 10.5 SCORE-04: Notification Pressure Score

**What it measures:** How much notification pressure the user is currently under -- combining global send volume, per-family send volume, and engagement behavior. Higher pressure = less likely to send.

**Extends:** Phase 1 fatigue formula (Section 2.5) with per-family tracking.

**Inputs:**

| Input | Source | Description |
|-------|--------|-------------|
| `notifications_sent_7d` | BigQuery notification log | Total notifications sent to user in last 7 days |
| `notifications_opened_7d` | CleverTap engagement data | Notifications opened by user in last 7 days |
| `notifications_dismissed_7d` | CleverTap engagement data | Notifications dismissed (swiped away) in last 7 days |
| `per_family_sent_7d` | BigQuery per-family tracking | Notifications sent from specific trigger family in last 7 days |
| `family_weekly_cap` | Config table | Weekly cap for the specific trigger family |

**Components:**

| Component | Formula | Interpretation |
|-----------|---------|---------------|
| `global_pressure` | `notifications_sent_7d / 5.0` | Normalized against 5/week safe ceiling (Phase 1 Section 2.2) |
| `family_pressure` | `per_family_sent_7d / family_weekly_cap` | Family-specific normalization against its own cap |
| `open_rate_inverse` | `1.0 - (notifications_opened_7d / GREATEST(notifications_sent_7d, 1))` | Low open rate = high pressure signal |

**Weights:** global_pressure 0.40, family_pressure 0.30, open_rate_inverse 0.30

**Key rule:** Higher pressure = less likely to send. In Send Score Final, notification_pressure is used as `(1 - notification_pressure)` to invert the relationship.

**BigQuery pseudocode:**

```sql
-- SCORE-04: Notification Pressure Score
-- Extends Phase 1 fatigue formula with per-family tracking
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_notification_pressure AS
SELECT
  user_id,
  trigger_family,

  -- Global pressure: total sends normalized against weekly safe ceiling
  LEAST(1.0, GREATEST(0.0, notifications_sent_7d / 5.0)) AS global_pressure,

  -- Family pressure: family-specific sends normalized against family cap
  LEAST(1.0, GREATEST(0.0, per_family_sent_7d / NULLIF(family_weekly_cap, 0))) AS family_pressure,

  -- Open rate inverse: low engagement = high pressure
  LEAST(1.0, GREATEST(0.0,
    1.0 - (notifications_opened_7d / GREATEST(notifications_sent_7d, 1))
  )) AS open_rate_inverse,

  -- Combined notification pressure score
  LEAST(1.0, GREATEST(0.0,
    LEAST(1.0, notifications_sent_7d / 5.0) * 0.40
    + LEAST(1.0, per_family_sent_7d / NULLIF(family_weekly_cap, 0)) * 0.30
    + (1.0 - (notifications_opened_7d / GREATEST(notifications_sent_7d, 1))) * 0.30
  )) AS notification_pressure_score

FROM bit2me_lifecycle.user_notification_summary;
```

---

### 10.6 SCORE-05: Fatigue Risk Score

**What it measures:** How likely the user is to opt out if sent another notification. Combines send volume, dismissal behavior, and engagement recency.

> **Note:** This formula is unchanged from Phase 1 Section 2.5. It is reproduced here for completeness and cross-reference. DO NOT CHANGE -- already in production design.

**Formula:**

```
fatigue_risk = (notifications_sent_7d / 5) * 0.4
             + (notifications_dismissed_7d / max(notifications_sent_7d, 1)) * 0.3
             + (days_since_last_open / 7) * 0.3
```

**Component breakdown:**
- **Send volume (weight 0.40):** `notifications_sent_7d / 5` -- normalized against 5 sends/week (the safe ceiling from Section 2.2). A user who received 5 pushes this week scores 0.40 on this component.
- **Dismissal rate (weight 0.30):** `notifications_dismissed_7d / max(notifications_sent_7d, 1)` -- fraction of notifications dismissed (swiped away without opening). A user who dismissed 3 of 5 notifications scores 0.18 on this component.
- **Engagement recency (weight 0.30):** `days_since_last_open / 7` -- how many days since the user last opened any notification, normalized against 7 days.

**Thresholds and tier suppression rules:**

| Fatigue Level | Score Range | Allowed Tiers | Suppression Action |
|---------------|-------------|---------------|--------------------|
| GREEN | < 0.3 | P0, P1, P2, P3, P4, P5 | All tiers can send |
| AMBER | 0.3 - 0.7 | P0, P1, P2, P3, P4 | Suppress P5 notifications |
| RED | 0.7 - 0.9 | P0, P1, P2 | Suppress P3+ for 48 hours |
| CRITICAL | > 0.9 | P0, P1 only | Suppress P2+ for 7 days |

**Cross-reference:** This score feeds Gate 2 of Send Score Final (Section 10.9).

**Where this runs:** Computed daily in BigQuery as a scheduled query. Stored in `bit2me_lifecycle.user_profiles` as `notification_fatigue_score` (float, 0-1). Synced to CleverTap via Hightouch every 30 minutes.

**BigQuery pseudocode:**

```sql
-- SCORE-05: Fatigue Risk Score
-- EXACT formula from Phase 1 Section 2.5
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_fatigue_risk AS
SELECT
  user_id,
  notifications_sent_7d,
  notifications_dismissed_7d,
  days_since_last_open,

  -- Fatigue risk score (Phase 1 formula, unchanged)
  LEAST(1.0, GREATEST(0.0,
    (notifications_sent_7d / 5.0) * 0.40
    + (notifications_dismissed_7d / GREATEST(notifications_sent_7d, 1)) * 0.30
    + (days_since_last_open / 7.0) * 0.30
  )) AS fatigue_risk_score

FROM bit2me_lifecycle.user_notification_engagement;
```

---

### 10.7 SCORE-06: Cross-sell Eligibility Score

**What it measures:** How eligible and receptive a user is to a cross-sell notification -- combining product adoption gaps, balance relevance, and lifecycle stage appropriateness.

**Inputs:**

| Input | Source | Description |
|-------|--------|-------------|
| `product_gap_count` | BigQuery product usage table | Number of products user does NOT use from the 5 cross-sell-eligible set (Earn, Pro, Card, Loan, Space Center) |
| `total_balance_eur` | BigQuery user holdings | User's total portfolio balance (EUR) |
| `lifecycle_stage` | BigQuery lifecycle classification | Current lifecycle stage (13 stages from LC-OS) |

**Components:**

| Component | Formula | Interpretation |
|-----------|---------|---------------|
| `product_gap_normalized` | `product_gap_count / 5.0` | Max 5 cross-sell-eligible products. 5 gaps = highest opportunity |
| `balance_relevance` | `LEAST(1.0, total_balance_eur / 1000.0)` | EUR 1,000+ balance = max relevance for cross-sell |
| `lifecycle_weight` | CASE on lifecycle_stage (see below) | Not all lifecycle stages are appropriate for cross-sell |

**Lifecycle weight by stage:**

| Lifecycle Stage | Weight | Rationale |
|----------------|--------|-----------|
| ACTIVE | 1.0 | Fully engaged, most receptive to new products |
| POWER | 0.80 | Already using multiple products, slightly lower opportunity |
| FM (First Monetization) | 0.90 | Just converted, high openness to product discovery |
| AT_RISK | 0.30 | Low -- cross-sell may feel tone-deaf when user is disengaging |
| All others | 0.10 | REGISTERED, KYC, DEPOSITED (too early), DORMANT/CHURNED (not receptive) |

**Weights:** product_gap 0.40, balance_relevance 0.35, lifecycle_weight 0.25

**V1 constraint:** Cross-sell copy must use product awareness framing only (Phase 2 decision, compliance Section 9.3.4). No return comparisons, no yield numbers. "Did you know about Bit2Me Earn? Stake your crypto." NOT "Your USDT could earn 3.2% in Earn."

**BigQuery pseudocode:**

```sql
-- SCORE-06: Cross-sell Eligibility Score
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_cross_sell_eligibility AS
SELECT
  user_id,

  -- Product gap: how many cross-sell-eligible products user doesn't use
  LEAST(1.0, product_gap_count / 5.0) AS product_gap_normalized,

  -- Balance relevance: higher balance = more relevant for cross-sell
  LEAST(1.0, GREATEST(0.0, total_balance_eur / 1000.0)) AS balance_relevance,

  -- Lifecycle weight: not all stages appropriate for cross-sell
  CASE lifecycle_stage
    WHEN 'ACTIVE' THEN 1.0
    WHEN 'POWER' THEN 0.80
    WHEN 'FM' THEN 0.90
    WHEN 'AT_RISK' THEN 0.30
    ELSE 0.10
  END AS lifecycle_weight,

  -- Combined cross-sell eligibility score
  LEAST(1.0, GREATEST(0.0,
    LEAST(1.0, product_gap_count / 5.0) * 0.40
    + LEAST(1.0, GREATEST(0.0, total_balance_eur / 1000.0)) * 0.35
    + CASE lifecycle_stage
        WHEN 'ACTIVE' THEN 1.0
        WHEN 'POWER' THEN 0.80
        WHEN 'FM' THEN 0.90
        WHEN 'AT_RISK' THEN 0.30
        ELSE 0.10
      END * 0.25
  )) AS cross_sell_eligibility_score

FROM bit2me_lifecycle.user_product_adoption;
```

---

### 10.8 SCORE-07: Churn Risk Score

**What it measures:** How likely a user is to churn -- combining recency of last action, frequency decline, and balance trend. Higher score = higher churn risk.

**Key difference from other scores:** Churn risk is used as a BOOST in Send Score Final. High churn risk = MORE reason to send lifecycle triggers (Family D), not less. A user at high churn risk who might benefit from a reactivation nudge should score higher on Send Score Final.

**Inputs:**

| Input | Source | Description |
|-------|--------|-------------|
| `days_since_last_action` | BigQuery activity log | Days since last meaningful action (trade, deposit, or Earn interaction) |
| `actions_last_30d` | BigQuery activity count | Number of meaningful actions in last 30 days |
| `actions_prev_30d` | BigQuery activity count | Number of meaningful actions in the 30 days before that (days 31-60) |
| `balance_eur_current` | BigQuery user holdings | Current total balance (EUR) |
| `balance_eur_30d_ago` | BigQuery historical snapshot | Total balance 30 days ago (EUR) |

**Components (higher = higher churn risk):**

| Component | Formula | Interpretation |
|-----------|---------|---------------|
| `recency_risk` | `days_since_last_action / 90.0` | 90+ days since last action = max risk |
| `frequency_decline_risk` | `1.0 - (actions_last_30d / NULLIF(actions_prev_30d, 0))` | Activity halved = 0.5 risk; activity stopped = 1.0 risk |
| `balance_decline_risk` | `(balance_eur_30d_ago - balance_eur_current) / NULLIF(balance_eur_30d_ago, 0)` | Balance withdrawn = positive risk; balance increased = 0 |

**Weights:** recency 0.40, frequency_decline 0.30, balance_decline 0.30

**BigQuery SQL:**

```sql
-- SCORE-07: Churn Risk Score
-- RFM framework adapted for crypto lifecycle
-- Higher score = higher churn risk
-- Schema: bit2me_lifecycle

CREATE OR REPLACE VIEW bit2me_lifecycle.score_churn_risk AS
SELECT
  user_id,
  -- Recency: days since last meaningful action (trade, deposit, or Earn interaction)
  LEAST(1.0, GREATEST(0.0, days_since_last_action / 90.0)) AS recency_risk,

  -- Frequency decline: comparing last-30d action count to previous-30d
  CASE
    WHEN actions_prev_30d = 0 THEN 0.5  -- no baseline, moderate risk
    ELSE LEAST(1.0, GREATEST(0.0,
      1.0 - (actions_last_30d / NULLIF(actions_prev_30d, 0))
    ))
  END AS frequency_decline_risk,

  -- Balance trend: is balance decreasing?
  CASE
    WHEN balance_eur_30d_ago = 0 THEN 0.3  -- no historical balance
    ELSE LEAST(1.0, GREATEST(0.0,
      (balance_eur_30d_ago - balance_eur_current) / NULLIF(balance_eur_30d_ago, 0)
    ))
  END AS balance_decline_risk,

  -- Combined churn risk score
  LEAST(1.0, GREATEST(0.0,
    LEAST(1.0, days_since_last_action / 90.0) * 0.40
    + CASE WHEN actions_prev_30d = 0 THEN 0.5
        ELSE LEAST(1.0, GREATEST(0.0, 1.0 - (actions_last_30d / NULLIF(actions_prev_30d, 0))))
      END * 0.30
    + CASE WHEN balance_eur_30d_ago = 0 THEN 0.3
        ELSE LEAST(1.0, GREATEST(0.0, (balance_eur_30d_ago - balance_eur_current) / NULLIF(balance_eur_30d_ago, 0)))
      END * 0.30
  )) AS churn_risk_score

FROM bit2me_lifecycle.user_activity_summary;
```

---

### 10.9 SCORE-08: Send Score Final (Gated Architecture)

**THIS IS THE MOST CRITICAL SECTION.** The Send Score Final determines whether a notification actually sends. It uses a gated architecture: 3 binary gates must ALL pass before the weighted composite score is even computed.

#### Gate Architecture Diagram

```
GATE 1: Compliance (binary) -----> BLOCK if fails
GATE 2: Fatigue (threshold) -----> BLOCK if fails
GATE 3: Cooldown (temporal) -----> BLOCK if fails
  |
  v (all gates pass)
WEIGHTED SCORE (0-1) -----> Compare to family threshold
  |
  v (above threshold)
SEND
```

**Key insight:** Gates are binary (pass/fail). The score only matters for ranking triggers when multiple pass all gates for the same user simultaneously.

---

#### GATE 1: Compliance Gate (binary pass/fail)

ANY Gate 1 failure = score is 0, notification does NOT send.

| Check | Condition | Action |
|-------|-----------|--------|
| Suppression list | Is user in `C8_Whale_Suppression` OR `Excluded_Users`? | BLOCK |
| Consent verification | Does trigger require `consent_marketing_[channel]` AND user hasn't given it? (applies to P2-P5) | BLOCK |
| ADVISORY_RISK block | Is trigger classified `ADVISORY_RISK`? | BLOCK (V1 -- all ADVISORY_RISK deferred) |
| Active journey conflict | Is user in active CleverTap journey AND trigger is Family C, D, or E? | BLOCK (check `active_journey IS NULL`) |

**P0-P1 exemption:** P0 (transactional/security) and P1 (user-configured) triggers bypass consent verification because they use Art. 6(1)(b) lawful basis (contract performance), not Art. 6(1)(a) (consent).

---

#### GATE 2: Fatigue Gate (threshold)

Reads the `fatigue_risk` score from SCORE-05 and compares against the tier-specific threshold.

| Priority Tier | Fatigue Threshold | Rule |
|--------------|-------------------|------|
| P0-P1 | Exempt | P0-P1 are exempt from fatigue gate |
| P2 | fatigue_risk < 0.9 | Only blocked at CRITICAL level |
| P3 | fatigue_risk < 0.7 | Blocked at RED and CRITICAL |
| P4 | fatigue_risk < 0.7 | Blocked at RED and CRITICAL |
| P5 | fatigue_risk < 0.3 | Blocked at AMBER, RED, and CRITICAL |

---

#### GATE 3: Cooldown Gate (temporal)

Has this trigger family sent to this user within the cooldown window?

| Check | Mechanism |
|-------|-----------|
| Timestamp comparison | `last_sent_[family]` timestamp compared to family cooldown period |
| Family A cooldown | 1 per asset per 4 hours |
| Family B cooldown | Per trigger-specific definition (B-01: 4h, B-02: 4h, B-03: 24h) |
| Family C cooldown | 24 hours between sends of same family |
| Family D cooldown | 7 days between lifecycle nudges (P2); 14 days for P5 re-engagement |
| Family E cooldown | 7 days between cross-sell attempts |
| Family F cooldown | Immediate for P0 (no cooldown); 24h for system LTV alerts |

**Escalating cooldowns (from Phase 1 Section 2.4):**
- After 1 dismissal: 24h family cooldown
- After 3 consecutive dismissals (same family): 7-day family cooldown
- After 5 consecutive dismissals (any family): P0-P1 only for 14 days
- Reset on any open/click

---

#### Weighted Score (only computed if ALL gates pass)

```sql
send_score = trigger_opportunity_score * 0.35
           + user_asset_affinity * 0.25
           + (1 - notification_pressure) * 0.20
           + (1 - fatigue_risk) * 0.10
           + churn_risk_boost * 0.10
```

**Weight rationale:**
- `trigger_opportunity` (0.35): The strongest signal -- is there a real opportunity to deliver value?
- `user_asset_affinity` (0.25): Is the user likely to care about this specific content?
- `(1 - notification_pressure)` (0.20): How much room is there to send without fatigue?
- `(1 - fatigue_risk)` (0.10): Direct fatigue signal (redundant with gate 2, but provides gradation)
- `churn_risk_boost` (0.10): Users at risk of churning get a sending boost for lifecycle triggers

---

#### Family-Specific Overrides

| Family | Override | Rationale |
|--------|----------|-----------|
| A (User Configured) | `send_score = 1.0` (always sends, gated by cooldown only) | User explicitly requested this alert |
| B (Market Triggered) | Standard formula, but bypass `active_journey IS NULL` check in Gate 1 | Market data is time-sensitive; MiCA requires simultaneous send |
| D (Lifecycle) | Replace `user_asset_affinity` with `lifecycle_urgency` | Lifecycle triggers are about user state, not asset affinity |
| E (Cross-sell) | Replace `trigger_opportunity` with `cross_sell_eligibility` | Cross-sell opportunity is about product gaps, not market events |
| F (Risk & Protective) | `send_score = 1.0` (always sends, protective) | User safety overrides all scoring |

**Lifecycle urgency (Family D override):**

```sql
lifecycle_urgency = CASE lifecycle_stage
  WHEN 'AT_RISK' THEN 0.90       -- highest urgency: user disengaging
  WHEN 'PRE_DORMANCY' THEN 0.80  -- approaching dormancy
  WHEN 'FM' THEN 0.70            -- just converted, critical engagement window
  WHEN 'ACTIVE' THEN 0.50        -- stable, moderate urgency
  WHEN 'POWER' THEN 0.30         -- low urgency, already engaged
  ELSE 0.10                      -- other stages
END
```

---

#### Minimum Send Score Thresholds by Family

| Family | Minimum Send Score | Rationale |
|--------|-------------------|-----------|
| A (User Configured) | N/A (always sends) | User requested |
| B (Market Triggered) | 0.40 | Time-sensitive market data |
| C (Behavioral) | 0.50 | Behavioral nudges less urgent |
| D (Lifecycle) | 0.35 | Lifecycle transitions rare and high-value |
| E (Cross-sell) | 0.55 | Highest bar to protect push permission |
| F (Risk & Protective) | N/A (always sends) | Protective |

---

#### Complete Send Score Final BigQuery Pseudocode

```sql
-- SCORE-08: Send Score Final (Gated Architecture)
-- Schema: bit2me_lifecycle
-- This is the master query that determines whether a notification sends

CREATE OR REPLACE VIEW bit2me_lifecycle.score_send_final AS
WITH gate_checks AS (
  SELECT
    u.user_id,
    t.trigger_id,
    t.trigger_family,
    t.priority_tier,
    t.compliance_class,

    -- GATE 1: Compliance (binary)
    CASE
      WHEN u.is_excluded = true THEN false               -- Excluded_Users
      WHEN u.is_c8_whale = true THEN false                -- C8_Whale_Suppression
      WHEN t.compliance_class = 'ADVISORY_RISK' THEN false -- V1: all ADVISORY_RISK blocked
      WHEN t.priority_tier IN ('P0', 'P1') THEN true      -- P0-P1 exempt from consent check
      WHEN u.consent_marketing_push = false
           AND t.channel = 'push' THEN false               -- Missing push consent
      WHEN u.consent_marketing_email = false
           AND t.channel = 'email' THEN false              -- Missing email consent
      WHEN t.trigger_family IN ('C', 'D', 'E')
           AND u.active_journey IS NOT NULL THEN false     -- Active journey conflict
      ELSE true
    END AS gate_1_compliance,

    -- GATE 2: Fatigue (threshold)
    CASE
      WHEN t.priority_tier IN ('P0', 'P1') THEN true      -- P0-P1 exempt
      WHEN t.priority_tier = 'P2'
           AND f.fatigue_risk_score >= 0.9 THEN false      -- P2 blocked at CRITICAL
      WHEN t.priority_tier IN ('P3', 'P4')
           AND f.fatigue_risk_score >= 0.7 THEN false      -- P3-P4 blocked at RED
      WHEN t.priority_tier = 'P5'
           AND f.fatigue_risk_score >= 0.3 THEN false      -- P5 blocked at AMBER
      ELSE true
    END AS gate_2_fatigue,

    -- GATE 3: Cooldown (temporal)
    CASE
      WHEN TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), u.last_sent_family,
           HOUR) < t.cooldown_hours THEN false
      ELSE true
    END AS gate_3_cooldown,

    -- Component scores (for weighted computation)
    COALESCE(opp.trigger_opportunity_score, 0.0) AS trigger_opportunity_score,
    COALESCE(aff.user_asset_affinity_score, 0.0) AS user_asset_affinity_score,
    COALESCE(prs.notification_pressure_score, 0.0) AS notification_pressure_score,
    COALESCE(f.fatigue_risk_score, 0.0) AS fatigue_risk_score,
    COALESCE(chr.churn_risk_score, 0.0) AS churn_risk_score,
    COALESCE(cse.cross_sell_eligibility_score, 0.0) AS cross_sell_eligibility_score,
    -- Lifecycle urgency (Family D override)
    CASE u.lifecycle_stage
      WHEN 'AT_RISK' THEN 0.90
      WHEN 'PRE_DORMANCY' THEN 0.80
      WHEN 'FM' THEN 0.70
      WHEN 'ACTIVE' THEN 0.50
      WHEN 'POWER' THEN 0.30
      ELSE 0.10
    END AS lifecycle_urgency

  FROM bit2me_lifecycle.user_profiles u
  CROSS JOIN bit2me_lifecycle.trigger_definitions t
  LEFT JOIN bit2me_lifecycle.score_fatigue_risk f ON u.user_id = f.user_id
  LEFT JOIN bit2me_lifecycle.score_trigger_opportunity opp
    ON u.user_id = opp.user_id AND t.asset_id = opp.asset_id
  LEFT JOIN bit2me_lifecycle.score_user_asset_affinity aff
    ON u.user_id = aff.user_id AND t.asset_id = aff.asset_id
  LEFT JOIN bit2me_lifecycle.score_notification_pressure prs
    ON u.user_id = prs.user_id AND t.trigger_family = prs.trigger_family
  LEFT JOIN bit2me_lifecycle.score_churn_risk chr ON u.user_id = chr.user_id
  LEFT JOIN bit2me_lifecycle.score_cross_sell_eligibility cse ON u.user_id = cse.user_id
)

SELECT
  user_id,
  trigger_id,
  trigger_family,
  priority_tier,
  gate_1_compliance,
  gate_2_fatigue,
  gate_3_cooldown,

  -- All gates must pass
  (gate_1_compliance AND gate_2_fatigue AND gate_3_cooldown) AS all_gates_pass,

  -- Weighted score (only meaningful if all gates pass)
  CASE
    -- Family A: always sends (user requested)
    WHEN trigger_family = 'A' THEN 1.0
    -- Family F: always sends (protective)
    WHEN trigger_family = 'F' THEN 1.0
    -- Family E: replace trigger_opportunity with cross_sell_eligibility
    WHEN trigger_family = 'E' THEN LEAST(1.0, GREATEST(0.0,
      cross_sell_eligibility_score * 0.35
      + user_asset_affinity_score * 0.25
      + (1.0 - notification_pressure_score) * 0.20
      + (1.0 - fatigue_risk_score) * 0.10
      + churn_risk_score * 0.10
    ))
    -- Family D: replace user_asset_affinity with lifecycle_urgency
    WHEN trigger_family = 'D' THEN LEAST(1.0, GREATEST(0.0,
      trigger_opportunity_score * 0.35
      + lifecycle_urgency * 0.25
      + (1.0 - notification_pressure_score) * 0.20
      + (1.0 - fatigue_risk_score) * 0.10
      + churn_risk_score * 0.10
    ))
    -- Standard formula (Families B, C)
    ELSE LEAST(1.0, GREATEST(0.0,
      trigger_opportunity_score * 0.35
      + user_asset_affinity_score * 0.25
      + (1.0 - notification_pressure_score) * 0.20
      + (1.0 - fatigue_risk_score) * 0.10
      + churn_risk_score * 0.10
    ))
  END AS send_score,

  -- Final decision
  CASE
    WHEN NOT (gate_1_compliance AND gate_2_fatigue AND gate_3_cooldown) THEN 'BLOCKED'
    WHEN trigger_family = 'A' THEN 'SEND'
    WHEN trigger_family = 'F' THEN 'SEND'
    ELSE 'SCORE_CHECK'  -- compare send_score against family threshold
  END AS send_decision

FROM gate_checks;
```

---

### 10.10 Conflict Resolution When Multiple Triggers Fire

When multiple triggers fire for the same user in the same evaluation window:

1. **Score all eligible triggers** for the user (compute Send Score Final for each)
2. **Sort by priority_tier** (P0 first, P5 last)
3. **Within same priority**, sort by `send_score` (highest first)
4. **Apply daily/weekly caps** per Phase 1 Section 2.2:
   - If user has remaining cap budget: send highest-scored trigger
   - If cap exhausted: queue for next available slot (or discard P5)
5. **Special rules:**
   - Family B bypasses lifecycle journey check (market data is time-sensitive)
   - P0/P1 always send regardless of caps
   - Two triggers from the same family in the same window: send highest-scored only (avoid double-nudging)

---

### 10.11 Cross-References

#### Score to Phase 1/2 Reference Map

| Score | Phase 1 Reference | Phase 2 Reference | Notes |
|-------|------------------|-------------------|-------|
| SCORE-01 (Market Relevance) | -- | Section 7 (Asset Universe): T1-T4 tiers, volume thresholds | Asset scope filter uses Phase 2 tier definitions |
| SCORE-02 (User Asset Affinity) | -- | Section 6.2-6.7 (Trigger families): eligibility rules | Per-user per-asset affinity drives family-specific targeting |
| SCORE-03 (Trigger Opportunity) | -- | Section 6.1 (Family properties): family weights | Multiplicative: market x affinity x family weight |
| SCORE-04 (Notification Pressure) | Section 2.2 (Global Caps): 5/week ceiling | Section 6.1 (Family properties): per-family caps | Extends Phase 1 with per-family tracking |
| SCORE-05 (Fatigue Risk) | Section 2.5 (Fatigue Formula): exact formula | -- | UNCHANGED from Phase 1 |
| SCORE-06 (Cross-sell Eligibility) | -- | Section 6.6 (Family E): product gap, compliance | V1: product awareness framing only |
| SCORE-07 (Churn Risk) | Section 2.4 (Cooldown Rules): dismissal patterns | Section 6.5 (Family D): lifecycle transitions | RFM-based, boosts Send Score for lifecycle triggers |
| SCORE-08 (Send Score Final) | Section 2.3 (Priority Tiers): P0-P5 exempt rules | Section 9.1 (Compliance Classes): gate 1 logic | Gated architecture: 3 gates before weighted score |

#### Score to BigQuery View and Sync Map

| Score | BigQuery View Name | Evaluation Frequency | Hightouch Sync | CleverTap Property |
|-------|-------------------|---------------------|----------------|-------------------|
| SCORE-01 | `bit2me_lifecycle.score_market_relevance` | Hourly | 30 min | `score_market_relevance` |
| SCORE-02 | `bit2me_lifecycle.score_user_asset_affinity` | Daily | 30 min | `score_user_asset_affinity` |
| SCORE-03 | `bit2me_lifecycle.score_trigger_opportunity` | Hourly (depends on SCORE-01) | 30 min | `score_trigger_opportunity` |
| SCORE-04 | `bit2me_lifecycle.score_notification_pressure` | Daily | 30 min | `score_notification_pressure` |
| SCORE-05 | `bit2me_lifecycle.score_fatigue_risk` | Daily | 30 min | `notification_fatigue_score` |
| SCORE-06 | `bit2me_lifecycle.score_cross_sell_eligibility` | Daily | 30 min | `score_cross_sell_eligibility` |
| SCORE-07 | `bit2me_lifecycle.score_churn_risk` | Daily | 30 min | `score_churn_risk` |
| SCORE-08 | `bit2me_lifecycle.score_send_final` | On-demand (trigger evaluation) | Not synced (computed at send time) | -- |
