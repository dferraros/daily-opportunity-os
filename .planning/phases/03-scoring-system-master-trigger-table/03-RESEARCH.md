# Phase 3: Scoring System + Master Trigger Table - Research

**Researched:** 2026-03-22
**Domain:** Notification scoring formulas, trigger table design, channel routing, threshold calibration
**Confidence:** MEDIUM-HIGH

## Summary

Phase 3 transforms the trigger taxonomy (6 families, 24 triggers) from Phase 2 into a concrete, implementable system: 8 scoring formulas that determine whether to send a notification, a channel decision matrix, and a master trigger table with 30+ rows that an engineering/CRM team can execute from. The research covers scoring formula architecture patterns from production notification systems (Coinbase, Revolut), industry benchmarks for crypto volatility thresholds, channel selection algorithms, conflict resolution between simultaneous triggers, and MVP trigger prioritization methodology.

**Primary recommendation:** Build the 8 scoring formulas as composable BigQuery SQL expressions (not ML models) for V1 -- each formula outputs a 0-1 normalized score. The Send Score Final aggregates them with a hard compliance gate (pass/fail, not weighted). The master trigger table must have exactly the columns specified in TRIG-02, with 30+ rows covering all 6 families, and clearly flag the top 10 MVP triggers and top 10 "do NOT launch" triggers. Channel routing uses a simple decision tree (urgency x content depth x user engagement history), not an ML model.

Coinbase's production notification platform uses a two-tower ML model for user-asset affinity scoring at scale, but this is a V3 aspiration for Bit2Me. For V1, rule-based formulas with configurable weights and thresholds are the correct approach -- they are auditable (important for MiCA compliance), tunable without retraining, and implementable by Alvaro in BigQuery without ML infrastructure.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCORE-01 | Market Relevance Score -- pct_change, zscore, abnormal_volume_ratio | Formula pattern validated: z-score of price change + volume anomaly ratio. BTC avg daily vol is 2.24% (2025), provides baseline for z-score normalization. |
| SCORE-02 | User Asset Affinity Score -- holdings, watchlist, search, trade history | Coinbase two-tower model is gold standard but V3. V1 uses weighted feature sum: holdings (0.4) + watchlist (0.2) + trade recency (0.25) + view count (0.15). |
| SCORE-03 | Trigger Opportunity Score -- opportunity x relevance x propensity | Composite of SCORE-01 x SCORE-02 x trigger-family weight. Multiplicative, not additive -- any zero component kills the trigger. |
| SCORE-04 | Notification Pressure Score -- recent sends, opens, dismissals | Phase 1 fatigue formula (Section 2.5) already covers this. Extend with per-family pressure tracking. |
| SCORE-05 | Fatigue Risk Score -- decay from low engagement | Phase 1 formula validated. Research confirms 46% opt-out at 2-5 pushes/week. 3 consecutive ignores = pause reduces churn by 15%. |
| SCORE-06 | Cross-sell Eligibility Score -- product gap, balance, lifecycle | Product adoption gap matrix (11 products). Score = product_gap_count x balance_tier x lifecycle_weight. |
| SCORE-07 | Churn Risk Score -- days since last action, balance trend, frequency decline | RFM-based approach validated. Recency (0.4) + frequency_decline (0.3) + balance_trend (0.3). |
| SCORE-08 | Send Score Final -- composite with compliance gate | Weighted aggregate of SCORE-01 to SCORE-07 with hard compliance gate (binary pass/fail). If compliance fails, score = 0 regardless. |
| TRIG-01 | Master trigger table with 30+ rows | Research provides column structure, all 24 Phase 2 triggers + 6-10 additional triggers to reach 30+. |
| TRIG-02 | All required columns per trigger | 14 columns confirmed: trigger_id, family, business_objective, who_receives, who_never_receives, asset_scope, formula_used, threshold, cooldown, channel, deep_link, priority, estimated_value, estimated_risk. |
| TRIG-03 | Top 10 MVP triggers (30 days) | Impact x Risk x Implementation Complexity scoring framework. Family A and D triggers dominate MVP. |
| TRIG-04 | Top 10 triggers NOT to launch | ADVISORY_RISK compliance class, ML-dependent, or data-unavailable triggers. |
| CHAN-01 | Push vs in-app vs email vs no-send decision matrix | 4-factor decision tree: urgency, content depth, user opt-in status, engagement history. |
| CHAN-02 | Deep links by product and surface | 11 products x action type matrix. Pattern: `bit2me://[product]/[action]?asset=[symbol]`. |
| CHAN-03 | Quiet hours by timezone | Spain (22:00-08:00 CET), LatAm (22:00-08:00 local), EU (22:00-08:00 local). P0 exempt. |
| CHAN-04 | Conflict resolution: lifecycle journeys vs market alerts | Priority-based queue with `active_journey IS NULL` check for Families C/D/E. Family B simultaneous send overrides journey suppression. |
</phase_requirements>

## Standard Stack

This is a strategy/playbook deliverable, not software. The "stack" is the set of tools and platforms that the formulas and trigger table will be implemented on.

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| BigQuery | Current | Scoring formula computation, scheduled queries | Already Bit2Me's data warehouse. All user data lives here. Alvaro owns. |
| CleverTap | Current | Campaign execution, Live Segments, Journeys | Already Bit2Me's CRM/engagement platform. Katy owns. |
| Hightouch | Current | Reverse ETL -- BigQuery scores synced to CleverTap user profiles | Already in use. 30-min sync cadence established in Phase 1. |
| CoinGecko API | v3 | Public market data for Family A/B triggers | Already decided in Phase 2. Public data source required by MiCA Art. 87. |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| Google Sheets | Trigger table review/collaboration with Katy, Diego | Initial trigger table authoring before formalization |
| Lark/Notion | Diego approval workflow, template library | Compliance checklist tracking (Section 9.5 from Phase 2) |

## Architecture Patterns

### Scoring Formula Architecture

All 8 formulas follow the same pattern: BigQuery scheduled query computes a 0-1 normalized score per user, stored in `bit2me_lifecycle.user_scores`, synced to CleverTap via Hightouch every 30 minutes.

```
Pattern: Composable Score Pipeline
===================================

[BigQuery daily/hourly query]
    |
    v
user_scores table (one row per user, one column per score)
    |
    v
[Hightouch reverse ETL -- 30 min sync]
    |
    v
CleverTap user profile (custom properties)
    |
    v
[Campaign targeting: WHERE score > threshold AND compliance_gate = true]
```

**Why this pattern:**
1. Auditable -- every score is a SQL expression, not a black box ML model. Critical for MiCA compliance.
2. Tunable -- weights and thresholds are constants in the SQL, adjustable without code deployment.
3. Separation of concerns -- BigQuery computes, Hightouch syncs, CleverTap targets.
4. Already proven -- Phase 1 fatigue_risk score uses this exact pipeline.

### Formula Design Pattern

Each formula follows the same template:

```sql
-- Pattern: Normalized weighted sum with floor/ceiling
score_name = LEAST(1.0, GREATEST(0.0,
    (component_1 / normalizer_1) * weight_1
  + (component_2 / normalizer_2) * weight_2
  + (component_3 / normalizer_3) * weight_3
))
```

**Normalization rule:** Every component is divided by a reference value that represents "typical" or "maximum expected" behavior. This ensures the component contributes a 0-1 range before weighting.

### Send Score Final Pattern (SCORE-08)

The Send Score Final is NOT a simple weighted average. It uses a gated architecture:

```
GATE 1: Compliance (binary)
  - Is user in suppression list? -> BLOCK
  - Does trigger require consent user hasn't given? -> BLOCK
  - Is trigger ADVISORY_RISK? -> BLOCK (V1)
  - Is user in active CleverTap journey for this family? -> BLOCK (Families C/D/E)

GATE 2: Fatigue (threshold)
  - notification_fatigue_score > tier_threshold? -> BLOCK

GATE 3: Cooldown (temporal)
  - Last send of this trigger family < cooldown period? -> BLOCK

SCORE: Weighted composite (only if all gates pass)
  send_score = trigger_opportunity_score * 0.35
             + user_asset_affinity * 0.25
             + (1 - notification_pressure) * 0.20
             + (1 - fatigue_risk) * 0.10
             + churn_risk_boost * 0.10

  For Family E: replace trigger_opportunity with cross_sell_eligibility
  For Family D: replace user_asset_affinity with lifecycle_urgency
```

**Key insight:** Gates are binary (pass/fail). The score only matters for ranking triggers when multiple pass all gates for the same user simultaneously.

### Channel Decision Tree

```
Channel Selection Algorithm
=============================
INPUT: trigger_family, priority_tier, user_push_enabled, user_email_enabled,
       user_engagement_recency, content_depth_required

STEP 1: Is priority P0 (security/transactional)?
  YES -> Push + Email (dual delivery, no fallback needed)

STEP 2: Is content_depth_required HIGH (e.g., cross-sell with details)?
  YES -> Email (primary) + In-App (secondary)

STEP 3: Is user_push_enabled AND engagement_recency < 7 days?
  YES -> Push (primary)
  NO  -> Is user_email_enabled?
    YES -> Email (fallback)
    NO  -> In-App only (if user opens app)

STEP 4: Is trigger_family B (Market) AND requires simultaneous send?
  YES -> Push to all eligible simultaneously (no staggering)
```

### Conflict Resolution Pattern

When multiple triggers fire for the same user in the same evaluation window:

```
1. Score all eligible triggers for the user
2. Sort by priority_tier (P0 first, P5 last)
3. Within same priority, sort by send_score (highest first)
4. Apply daily/weekly caps:
   - If user has remaining cap budget: send highest-scored trigger
   - If cap exhausted: queue for next available slot (or discard P5)
5. Special rule: Family B triggers bypass lifecycle journey check
   (market data is time-sensitive; lifecycle nudges can wait)
6. Special rule: P0/P1 always send regardless of caps
```

### Anti-Patterns to Avoid

- **ML scoring in V1:** Coinbase uses a two-tower model, but they have a dedicated ML infra team. Bit2Me does not. Rule-based formulas are correct for V1.
- **Single composite score without gates:** A user might score 0.9 on opportunity but be in a compliance-blocked state. Gates must be checked first, score second.
- **Hard-coded asset lists in formulas:** Asset tiers and product eligibility must reference BigQuery views (Phase 2 decision), never inline constants.
- **Same threshold for all asset tiers:** BTC (T1) at 2.24% daily vol needs a 5%+ threshold to be meaningful. A T4 memecoin might move 20% daily -- threshold must scale by tier.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Z-score computation | Custom stats functions | BigQuery STDDEV_POP + AVG over 30-day window | Built-in, tested, handles NULLs and edge cases |
| Notification pressure tracking | Custom event pipeline | CleverTap engagement reports + BigQuery export | CleverTap already tracks sends, opens, dismissals natively |
| User-asset interaction history | Custom tracking table | CleverTap events (Product_Viewed, Purchase_Completed) + BigQuery session data | Events already flowing via SDK and backend |
| Quiet hours timezone handling | Custom timezone logic | CleverTap DND settings (22:00-08:00 user local time) | CleverTap handles timezone conversion natively |
| Consent verification | Custom consent checks | CleverTap Subscription Groups + BigQuery consent fields | Already designed in Phase 1 (Section 1.3) |

## Common Pitfalls

### Pitfall 1: Revolut's Fixed Threshold Anti-Pattern
**What goes wrong:** Setting a fixed percentage threshold (e.g., 2%) for all assets generates daily spam for BTC, which moves 2.24% on an average day.
**Why it happens:** Designers pick a round number without calibrating against actual volatility.
**How to avoid:** Tier-based thresholds. T1 (BTC/ETH): default 5% in 24h. T3 (mid-cap): default 8%. T4 (memecoin): user-configured only (no proactive alerts). Use z-score of 2.0 (2 standard deviations above 30-day mean) as the statistical trigger, not a fixed percentage.
**Warning signs:** Daily alert volume per user exceeds 1 for Family B triggers.

### Pitfall 2: Additive Scoring Without Gates
**What goes wrong:** A user scores high on opportunity + affinity but is in a compliance-blocked state. The notification sends anyway because the composite score is above threshold.
**Why it happens:** Treating compliance as just another weighted component instead of a hard gate.
**How to avoid:** Gates are binary (pass/fail) and evaluated BEFORE scoring. Score only matters for ranking, not for eligibility.
**Warning signs:** Notifications sent to users without required consent.

### Pitfall 3: Trigger Table Without Deep Links
**What goes wrong:** User receives "BTC hit your target" push, taps it, lands on generic home screen instead of BTC trade screen.
**Why it happens:** Deep links are treated as "nice to have" instead of mandatory column.
**How to avoid:** Every trigger row in the master table MUST have a deep_link value. No trigger ships without a tested deep link. This was elevated to MVP architectural decision in Phase 2 (benchmark Section 8.7, Gap #6).
**Warning signs:** Notification CTR is high but conversion-to-action is low.

### Pitfall 4: Family B A/B Testing
**What goes wrong:** Running A/B tests on market triggers means some users get the alert early, creating potential insider information distribution.
**Why it happens:** Normal optimization instinct to test notification copy/timing.
**How to avoid:** A/B testing on Family B triggers is PROHIBITED (Phase 2 decision). All eligible users must receive simultaneously. Test copy variants on Family C/D/E instead.
**Warning signs:** Compliance audit finds staggered send times for market triggers.

### Pitfall 5: Cross-sell Copy Crossing Advisory Line
**What goes wrong:** Family E trigger says "Your USDT could earn 3.2% in Earn vs. 0% in Wallet" -- this is a return comparison and crosses from MARKETING into ADVISORY_RISK under MiCA.
**Why it happens:** Natural instinct to show value proposition with numbers.
**How to avoid:** V1 Family E copy must use product awareness framing ONLY. "Did you know about Bit2Me Earn? Stake your crypto." No yield numbers, no comparisons. (Phase 2 decision, compliance Section 9.3.4.)
**Warning signs:** Diego rejects template; worst case: MiCA Art. 66 violation (up to EUR 5M fine).

### Pitfall 6: Scoring All 420+ Assets for Market Triggers
**What goes wrong:** Computing volatility z-scores for 420+ assets when most have less than EUR 1K daily volume on Bit2Me, producing noisy signals from illiquid micro-caps.
**Why it happens:** Completeness instinct -- "more data is better."
**How to avoid:** Family B asset scope is T1 + top T3 with EUR 10K/day minimum volume (Phase 2 decision). The BigQuery view `bit2me_lifecycle.asset_classification` already filters this.
**Warning signs:** Family B alerts firing for assets with fewer than 5 trades/day on Bit2Me.

### Pitfall 7: Ignoring Active Journey Conflicts
**What goes wrong:** User is in CleverTap Journey J1 (Brokerage onboarding) AND receives a Family D lifecycle trigger simultaneously, confusing the user with competing nudges.
**Why it happens:** Triggers and journeys evaluated independently without coordination.
**How to avoid:** Families C, D, and E must check `active_journey IS NULL` before sending (Phase 2 decision). Family B overrides because market data is time-sensitive.
**Warning signs:** Users in J1-J6 journeys receiving duplicate/competing lifecycle nudges.

## Code Examples

### SCORE-01: Market Relevance Score

```sql
-- Source: Research synthesis of z-score + volume anomaly patterns
-- Computes how relevant a market event is for notification purposes
-- Runs: hourly via BigQuery scheduled query

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
    (ABS(pct_change_24h - avg_pct_change_30d) / NULLIF(stddev_pct_change_30d, 0) / 4.0) * 0.6
    + ((volume_24h / NULLIF(avg_volume_30d, 0) - 1.0) / 3.0) * 0.4
  )) AS market_relevance_score

FROM bit2me_lifecycle.asset_market_stats
WHERE tier IN ('T1', 'T3') AND median_daily_volume_eur_30d > 10000;
```

**Component explanation:**
- `price_zscore_normalized`: A 2-sigma move (z=2) scores 0.5. A 4-sigma move (z=4) scores 1.0. Divided by 4 to normalize.
- `volume_anomaly_normalized`: Volume at 2x average scores 0.33. Volume at 4x average scores 1.0. Divided by 3 to normalize (since we subtract 1 for the baseline).
- Weights: price change 60%, volume anomaly 40%. Price is the primary signal; volume confirms.

### SCORE-02: User Asset Affinity Score

```sql
-- Source: Simplified version of Coinbase two-tower pattern (rule-based for V1)
-- Computes how much a specific user cares about a specific asset

CREATE OR REPLACE VIEW bit2me_lifecycle.score_user_asset_affinity AS
SELECT
  user_id,
  asset_id,
  -- Holdings component: does user hold this asset?
  CASE WHEN balance_eur > 0 THEN
    LEAST(1.0, balance_eur / 500.0)  -- EUR 500+ balance = max score
  ELSE 0.0 END AS holdings_score,

  -- Watchlist component
  CASE WHEN on_watchlist = true THEN 0.5 ELSE 0.0 END AS watchlist_score,

  -- Trade recency component
  CASE WHEN days_since_last_trade IS NOT NULL THEN
    LEAST(1.0, GREATEST(0.0, 1.0 - (days_since_last_trade / 90.0)))
  ELSE 0.0 END AS trade_recency_score,

  -- View frequency component
  LEAST(1.0, COALESCE(views_last_30d, 0) / 10.0) AS view_frequency_score,

  -- Combined affinity score
  LEAST(1.0, GREATEST(0.0,
    CASE WHEN balance_eur > 0 THEN LEAST(1.0, balance_eur / 500.0) ELSE 0.0 END * 0.40
    + CASE WHEN on_watchlist THEN 0.5 ELSE 0.0 END * 0.20
    + COALESCE(LEAST(1.0, GREATEST(0.0, 1.0 - (days_since_last_trade / 90.0))), 0.0) * 0.25
    + LEAST(1.0, COALESCE(views_last_30d, 0) / 10.0) * 0.15
  )) AS user_asset_affinity_score

FROM bit2me_lifecycle.user_asset_interactions;
```

### SCORE-07: Churn Risk Score

```sql
-- Source: RFM framework adapted for crypto lifecycle
-- Higher score = higher churn risk

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

### Channel Decision Matrix (Pseudocode)

```python
# Source: Research synthesis of channel selection patterns
def select_channel(trigger, user):
    # Gate: P0 always dual-delivers
    if trigger.priority == 'P0':
        return ['push', 'email']

    # Gate: Family B must be simultaneous push
    if trigger.family == 'B':
        if user.consent_marketing_push:
            return ['push']
        elif user.consent_marketing_email:
            return ['email']
        else:
            return ['in_app']

    # Content depth determines primary channel
    if trigger.content_depth == 'HIGH':  # cross-sell details, earn rates
        channels = ['email']
        if user.consent_marketing_inapp:
            channels.append('in_app')
        return channels

    # Default: push-first with fallback
    if user.consent_marketing_push and user.days_since_last_push_open < 7:
        return ['push']
    elif user.consent_marketing_email:
        return ['email']
    else:
        return ['in_app']
```

## Threshold Calibration Benchmarks

### Price/Volatility Thresholds by Asset Tier

| Asset Tier | Avg Daily Vol (2025) | Default % Threshold (24h) | Z-Score Trigger | Rationale |
|-----------|---------------------|--------------------------|----------------|-----------|
| T1 (BTC, ETH) | ~2.2% (BTC), ~3.5% (ETH) | 5% | 2.0 sigma | BTC moves 2.2% daily; 5% is ~2.3 sigma. Triggers ~once per 2-3 weeks. |
| T2 (Stablecoins) | ~0.1% | 2% (de-peg alert) | N/A -- absolute | 2% deviation from peg for >1 hour = risk event (Phase 2 decision). |
| T3 (Mid-cap) | ~4-8% | 8% | 2.0 sigma | Higher baseline volatility. 8% filters noise while catching significant moves. |
| T4 (Memecoin) | ~10-30% | User-configured only | N/A | No proactive alerts for T4 (Phase 2 decision). Too noisy. |

**Volume Spike Threshold:** 2x the 30-day average daily volume on Bit2Me (Phase 2 trigger B-02). This catches genuine interest spikes while filtering normal fluctuation.

### Fatigue/Pressure Thresholds (from Phase 1)

| Fatigue Level | Score Range | Allowed Tiers |
|---------------|-------------|---------------|
| GREEN | < 0.3 | All (P0-P5) |
| AMBER | 0.3 - 0.7 | P0-P4 |
| RED | 0.7 - 0.9 | P0-P2 |
| CRITICAL | > 0.9 | P0-P1 only |

### Send Score Thresholds

| Trigger Family | Minimum Send Score | Rationale |
|----------------|-------------------|-----------|
| A (User Configured) | N/A -- always sends (user requested) | Gated by cooldown only |
| B (Market) | 0.40 | Moderate bar; market events are time-sensitive |
| C (Behavioral) | 0.50 | Higher bar; behavioral nudges are less urgent |
| D (Lifecycle) | 0.35 | Lower bar; lifecycle transitions are rare and high-value |
| E (Cross-sell) | 0.55 | Highest bar for marketing triggers; protect push permission |
| F (Risk/Protective) | N/A -- always sends (protective) | Gated by compliance class only |

## MVP Trigger Selection Framework (TRIG-03, TRIG-04)

### MVP Scoring Methodology

Each trigger is scored on 3 dimensions (1-5 scale):

```
MVP_Score = Impact * 2 + (5 - Risk) * 1.5 + (5 - Implementation_Complexity) * 1

Impact: estimated business value (reactivation, revenue, retention)
Risk: regulatory, deliverability, user trust risk
Implementation_Complexity: data availability, engineering effort, Diego approval effort
```

**Impact signals:**
- Segment size (how many users are eligible)
- Revenue proximity (how close to a monetization event)
- Retention lift (does it prevent churn)

**Risk signals:**
- Compliance class (TRANSACTIONAL = low risk, MARKETING = medium, ADVISORY_RISK = high)
- Data sensitivity (public market data = low, behavioral data = medium)
- Push permission risk (high-frequency trigger = high risk)

**Implementation complexity signals:**
- Data already in BigQuery? (yes = low complexity)
- CleverTap event already instrumented? (yes = low complexity)
- Diego pre-approval possible? (template = low, per-campaign = medium)

### Top 10 MVP Trigger Candidates (30-day launch)

Based on the framework above, these triggers should score highest for MVP:

1. **A-01 Price Target Alert** -- user requested, TRANSACTIONAL, zero regulatory risk, highest engagement driver
2. **A-02 Percentage Change Alert** -- same rationale as A-01, adds volatility awareness
3. **A-03 Watchlist Price Move** -- Coinbase gold standard, low risk, high engagement
4. **F-01 LTV Threshold Alert** (system) -- protective, TRANSACTIONAL, Nexo validated pattern
5. **D-01 Active-to-At-Risk** -- lifecycle critical (P2), 72.4K dormant users with EUR 19.5M AUC
6. **D-02 Dormant with Balance** -- retention critical, directly targets AUC preservation
7. **B-01 Volatility Spike** -- market engagement, INFORMATIONAL, template pre-approved
8. **C-01 Watched Not Bought** -- behavioral conversion, proven pattern across industries
9. **F-04 Stablecoin De-Peg** -- CAT-SEC P0, no consent required, protects user trust
10. **B-04 Price Breakout** -- simple market signal, INFORMATIONAL, low regulatory burden

### Top 10 Triggers NOT to Launch (TRIG-04)

1. **Any ADVISORY_RISK trigger** -- MiCA Art. 81 territory, deferred to V3
2. **E-xx with return comparisons** -- "Earn 3.2% vs 0% in Wallet" = ADVISORY_RISK
3. **B-xx with editorial commentary** -- "Great entry point" = advisory
4. **Portfolio-level alerts** -- requires BigQuery portfolio value calculation (not built)
5. **AI Market Insights** -- requires ML infrastructure (Nexo V3 feature)
6. **Space Center mission triggers** -- Space Center data not in BigQuery yet
7. **Earn rate change alerts** -- Earn APY data pipeline not confirmed
8. **Chart-integrated alerts** -- requires Pro app UI changes (Kraken V3 feature)
9. **Technical indicator triggers** (RSI, MACD) -- V3 advanced feature
10. **WhatsApp channel triggers** -- channel not available, ADV-05 deferred

## Channel Policy Details (CHAN-01 through CHAN-04)

### CHAN-01: Channel Decision Matrix

| Trigger Family | Primary Channel | Secondary Channel | Fallback | Rationale |
|---------------|----------------|-------------------|----------|-----------|
| A (User Configured) | Push | Email | In-App | User expects immediate delivery; push is fastest |
| B (Market) | Push | In-App | Email | Time-sensitive; must be simultaneous for all users |
| C (Behavioral) | In-App | Push | Email | Lower permission risk; user is likely in-app context |
| D (Lifecycle) | Push | Email | In-App | Re-engagement requires reaching inactive users |
| E (Cross-sell) | Email | In-App | Push (last resort) | Needs content depth; push copy too short for value prop |
| F (Risk/Protective) | Push + Email | -- | -- | Dual delivery for risk alerts (no fallback needed) |

### CHAN-02: Deep Link Structure

| Product | Deep Link Pattern | Example |
|---------|------------------|---------|
| Brokerage | `bit2me://brokerage/trade?asset={symbol}` | `bit2me://brokerage/trade?asset=BTC` |
| Pro | `bit2me://pro/chart?pair={symbol}-EUR` | `bit2me://pro/chart?pair=ETH-EUR` |
| Earn | `bit2me://earn/stake?asset={symbol}` | `bit2me://earn/stake?asset=USDT` |
| Card | `bit2me://card/activate` | `bit2me://card/activate` |
| Loan | `bit2me://loan/collateral?loan_id={id}` | `bit2me://loan/collateral?loan_id=123` |
| Space Center | `bit2me://space-center/missions` | `bit2me://space-center/missions` |
| Wallet | `bit2me://wallet/asset?symbol={symbol}` | `bit2me://wallet/asset?symbol=BTC` |
| Launchpad | `bit2me://launchpad/event?id={id}` | `bit2me://launchpad/event?id=456` |
| Pay | `bit2me://pay/merchants` | `bit2me://pay/merchants` |
| Settings | `bit2me://settings/notifications` | `bit2me://settings/notifications` |
| Portfolio | `bit2me://portfolio/overview` | `bit2me://portfolio/overview` |

**Rule:** Every trigger in the master table MUST have a deep_link value. The deep link takes the user to the most relevant action screen, not a generic page. This is Bit2Me's MVP differentiator vs. all 6 competitors (Phase 2 benchmark Section 8.7, Gap #6).

### CHAN-03: Quiet Hours by Region

| Region | Quiet Hours (Local Time) | P0 Exempt | Delivery Action |
|--------|------------------------|-----------|-----------------|
| Spain (CET/CEST) | 22:00 - 08:00 | Yes | Delay (queue for 08:00) |
| LatAm (multiple TZ) | 22:00 - 08:00 local | Yes | Delay (queue for 08:00) |
| EU (CET/EET/WET) | 22:00 - 08:00 local | Yes | Delay (queue for 08:00) |
| Other | 22:00 - 08:00 local | Yes | Delay (queue for 08:00) |

**CleverTap implementation:** Set DND hours in campaign settings. Action = Delay (not Discard). P0 campaigns have "Do Not Disturb" = OFF.

### CHAN-04: Journey vs. Alert Conflict Resolution

| Scenario | Resolution | Rationale |
|----------|-----------|-----------|
| User in J1-J6 + Family C trigger fires | SUPPRESS Family C | Behavioral nudge can wait; journey has priority |
| User in J1-J6 + Family D trigger fires | SUPPRESS Family D | Lifecycle nudge can wait; journey is lifecycle |
| User in J1-J6 + Family E trigger fires | SUPPRESS Family E | Cross-sell can wait; journey may already cross-sell |
| User in J1-J6 + Family B trigger fires | SEND Family B | Market data is time-sensitive and MiCA requires simultaneous send |
| User in J1-J6 + Family A trigger fires | SEND Family A | User explicitly requested this alert |
| User in J1-J6 + Family F trigger fires | SEND Family F | Protective alert -- user safety overrides journey |
| Two triggers same family, same window | Send highest send_score only | Avoid double-nudging in same category |
| P2 lifecycle + P3 market in same day | Send both (different families) | Different caps apply per family |

**Implementation:** Check `active_journey IS NULL` in targeting SQL for Families C, D, E. Families A, B, F bypass this check.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed % thresholds (Revolut 2%) | Z-score relative to asset volatility | 2024-2025 | Eliminates daily spam for volatile assets |
| Global send score (single number) | Gated architecture (gates + score) | 2024 | Compliance-first, score only for ranking |
| Manual segment targeting | User embedding + affinity scoring | 2023-2025 (Coinbase) | 10x more precise targeting. V3 for Bit2Me. |
| Batch daily computation | Near-real-time scoring (Coinbase two-tower) | 2024 | Sub-minute alerting. V3 aspiration for Bit2Me. |
| One-size-fits-all cooldowns | Escalating cooldowns based on dismissals | 2024-2025 | 15% churn reduction from auto-pause after 3 ignores |
| Push-only or email-only | Push-first with intelligent fallback | 2024-2025 | 3-4x higher conversion per message vs email |

## Open Questions

1. **CleverTap External Trigger API stability**
   - What we know: API is in Public Beta (noted in STATE.md blockers)
   - What is unclear: Whether it supports the throughput needed for Family B simultaneous sends to all eligible users
   - Recommendation: Design with CleverTap campaign API as primary, External Trigger API as fallback. Include this as a risk item in the plan.

2. **BigQuery user_asset_interactions table completeness**
   - What we know: Some events (Product_Viewed, Purchase_Completed) are instrumented via CleverTap SDK
   - What is unclear: Whether Watchlist_Add, Watchlist_Remove, and Price_Alert_Set events are currently instrumented
   - Recommendation: Plan assumes these events need instrumentation. Flag as dependency for Engineering.

3. **Alvaro capacity for new BigQuery views**
   - What we know: Alvaro is SPOF with 3 P0 tasks already (V0a + token-holder filter + attribution)
   - What is unclear: Whether adding 8 scoring formula views + asset_market_stats is feasible in current sprint
   - Recommendation: Scoring formulas should be documented as SQL pseudocode in the playbook. Alvaro implements when capacity allows. Do not block playbook completion on implementation.

4. **C8 Whale Suppression CSV status**
   - What we know: CSV not uploaded to CleverTap (flagged in STATE.md)
   - What is unclear: Whether this will be resolved before Phase 3 triggers launch
   - Recommendation: Include C8 upload as a hard dependency in the plan. No marketing trigger (P2-P5) launches without C8 suppression active.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | python3 (validation script) |
| Config file | None -- standalone script |
| Quick run command | `python3 .planning/phases/03-scoring-system-master-trigger-table/validate_phase3.py` |
| Full suite command | Same as quick run |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCORE-01 to SCORE-08 | 8 scoring formulas documented with components and weights | content check | Validate section headings + formula presence | Wave 0 |
| TRIG-01 | Master trigger table with 30+ rows | content check | Count trigger_id entries >= 30 | Wave 0 |
| TRIG-02 | All 14 columns present per trigger | content check | Validate column headers in table | Wave 0 |
| TRIG-03 | Top 10 MVP triggers identified | content check | Validate "MVP" section with 10 entries | Wave 0 |
| TRIG-04 | Top 10 NOT-to-launch triggers | content check | Validate "NOT to launch" section with 10 entries | Wave 0 |
| CHAN-01 | Channel decision matrix | content check | Validate channel matrix table | Wave 0 |
| CHAN-02 | Deep links by product | content check | Validate deep link table with 10+ products | Wave 0 |
| CHAN-03 | Quiet hours by timezone | content check | Validate quiet hours table | Wave 0 |
| CHAN-04 | Conflict resolution rules | content check | Validate conflict resolution table | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 validate_phase3.py`
- **Per wave merge:** Full validation suite
- **Phase gate:** All checks pass before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `validate_phase3.py` -- validation script (create during Phase 3 execution)
- [ ] No framework install needed (python3 available)

### Validation Script Specification

The validation script should check:

```python
# validate_phase3.py -- specification for Phase 3 deliverable validation
#
# 1. Check all expected playbook section files exist in phase 3 output
# 2. For scoring sections: verify 8 formula headings (SCORE-01 through SCORE-08)
# 3. For each formula: verify components, weights, normalizers documented
# 4. For trigger table: count rows with trigger_id pattern [A-F]-\d{2}, verify >= 30
# 5. For trigger table: verify all 14 required columns present
# 6. For MVP section: verify 10 triggers listed
# 7. For NOT-to-launch section: verify 10 triggers listed
# 8. For channel matrix: verify all 6 families have channel assignments
# 9. For deep links: verify 10+ product deep link patterns
# 10. For quiet hours: verify timezone regions documented
# 11. For conflict resolution: verify all 6 family combinations documented
# 12. Cross-reference: every trigger_id in trigger table maps to a family in taxonomy
```

## Sources

### Primary (HIGH confidence)
- Phase 1 outputs: frequency-caps.md, preference-center.md -- directly inform SCORE-04, SCORE-05, CHAN-03
- Phase 2 outputs: trigger-taxonomy.md (24 triggers, 6 families), asset-universe.md (T1-T4 tiers), compliance-per-trigger.md (4 compliance classes), competitor-benchmark.md (COPY/AVOID/INNOVATE)
- [Coinbase: Building a Notification Platform](https://www.coinbase.com/blog/building-a-notification-platform-at-coinbase) -- architecture patterns, Iris CMS, two-tower model
- [Coinbase: Smart Targeting Engine](https://www.coinbase.com/blog/from-intuition-to-precision-how-coinbase-built-a-general-purpose-targeting-engine) -- user embeddings, cold-start scoring

### Secondary (MEDIUM confidence)
- [Pushwoosh 2025 Benchmarks](https://www.pushwoosh.com/blog/push-notification-benchmarks/) -- 46% opt-out at 2-5 pushes/week, opt-in rates
- [KuCoin/K33 Research: BTC Volatility 2025](https://www.kucoin.com/news/flash/bitcoin-volatility-drops-to-2-24-in-2025-lower-than-nvidia) -- BTC avg daily vol 2.24% in 2025
- [OneSignal: When to Use Push vs SMS vs In-App](https://onesignal.com/blog/app-communication-when-to-use-push-notifications-sms-and-in-app-messaging/) -- channel selection patterns
- [Dynamic Yield: Channel Selection Guide](https://www.dynamicyield.com/article/email-sms-and-push-done-right-a-marketing-leaders-guide-to-channel-selection/amp/) -- channel orchestration
- [System Design Handbook: Notification System](https://www.systemdesignhandbook.com/guides/design-a-notification-system/) -- priority queue patterns, conflict resolution
- [AlgoMaster: Scalable Notification Service](https://blog.algomaster.io/p/design-a-scalable-notification-service) -- priority separation, worker pool isolation
- [Courier: Notification Fatigue 2026](https://courier-com.medium.com/notification-fatigue-is-about-to-get-10x-worse-60c151909440) -- fatigue multiplier from AI agents

### Tertiary (LOW confidence)
- RFM churn scoring patterns -- synthesized from multiple academic/industry sources, no single authoritative reference for crypto-specific application
- Deep link URL patterns -- proposed structure, needs validation with Bit2Me mobile engineering team
- Send score weights (0.35/0.25/0.20/0.10/0.10) -- research-informed starting point, requires A/B calibration post-launch

## Metadata

**Confidence breakdown:**
- Scoring formula architecture: MEDIUM-HIGH -- pattern validated by Coinbase engineering blog + Phase 1 fatigue formula precedent. Specific weights are starting points.
- Threshold calibration: HIGH -- BTC volatility data from K33 Research is authoritative. Z-score approach is standard.
- Channel policy: MEDIUM-HIGH -- patterns from OneSignal, Pushwoosh, Dynamic Yield align. Specific to Bit2Me context.
- Trigger table design: HIGH -- columns directly from REQUIREMENTS.md. 24 triggers already defined in Phase 2.
- MVP selection: MEDIUM -- framework is sound but ultimate prioritization depends on Bit2Me-specific capacity and data availability.
- Conflict resolution: MEDIUM -- `active_journey IS NULL` check validated by Phase 2 decision. Specific priority ordering is prescriptive.

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days -- stable domain, formulas don't change rapidly)
