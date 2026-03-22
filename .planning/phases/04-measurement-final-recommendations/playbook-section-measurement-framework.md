## 14. Measurement Framework

> **Purpose:** This section defines how Bit2Me measures the impact of every trigger, detects channel damage before it becomes permanent, and calculates the net business value of each notification. Without measurement, the trigger system cannot prove ROI or justify continued investment. These metrics, dashboards, and test designs give Alvaro and Katy exact specifications to implement from Day 1.
>
> **Owners:**
> - **Alvaro** -- BigQuery dashboard views, NNV calculation queries, holdout assignment logic
> - **Katy** -- CleverTap A/B test configuration, deliverability monitoring, weekly KPI pulls
> - **Daniel** -- Escalation owner for RED thresholds, weekly review cadence
> - **Diego** -- Informed on compliance-related metric trends (opt-out spikes, complaint rates)
>
> **Cross-references:**
> - Section 2.5 (Fatigue Risk Score): formula definition and thresholds used in health metrics
> - Section 2.7 (Monitoring and Alerting): 6 base KPIs this section extends
> - Section 11 (Master Trigger Table): 33 triggers across 6 families (A-F) that KPIs map against
> - Section 12 (MVP Selection): Top 10 MVP triggers and 4-wave launch plan

---

### 14.1 KPI Framework Per Trigger Family

The KPI tree has 4 levels, measured at increasing granularity from send-level operational metrics up to business impact. Every trigger family (A-F) has specific targets calibrated to the intent profile of that family.

#### 14.1.1 KPI Tree Structure

```
Level 1: Send Metrics (per trigger, daily)
  - sends, deliveries, delivery_rate
  - opens, open_rate, CTR (clicks / deliveries)
  - dismissals, dismissal_rate (dismissals / deliveries)

Level 2: Engagement Metrics (per trigger, weekly)
  - session_rate: sessions within 1h of open / opens
  - trade_rate: trades within 24h of open / opens
  - deposit_rate: deposits within 24h of open / opens (Family D only)
  - action_rate: target action within 24h / opens (family-specific action)

Level 3: Health Metrics (per family, weekly)
  - push_disable_lift: opt-outs within 24h of send / sends
  - negative_action_rate: (dismissals + disables + spam reports) / sends
  - fatigue_score_avg: average fatigue_risk for recipients of that family

Level 4: Business Impact (aggregate, weekly)
  - incremental_revenue: treatment vs holdout revenue difference
  - incremental_sessions: treatment vs holdout session difference
  - NNV: Net Notification Value (Section 14.4)
  - push_permission_rate_trend: iOS opt-in % week-over-week
```

#### 14.1.2 Per-Family KPI Targets

**Family A -- User Configured Alerts (A-01 to A-05)**

User explicitly requested these alerts. Highest intent = highest expected engagement.

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| Push CTR | > 5% | 3-5% | < 3% | Daily |
| Session rate (1h) | > 40% | 25-40% | < 25% | Weekly |
| Trade rate (24h) | > 8% | 5-8% | < 5% | Weekly |
| Push disable lift | < 0.5% | 0.5-1% | > 1% = investigate | Weekly |
| Negative action rate | < 5% | 5-8% | > 8% | Weekly |
| Avg fatigue_risk of recipients | < 0.3 | 0.3-0.5 | > 0.5 | Weekly |

**Family B -- Market Triggered Alerts (B-01 to B-05)**

Time-sensitive market data. Users expect relevance but did not explicitly request. Moderate-high intent.

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| Push CTR | > 3% | 2-3% | < 2% | Daily |
| Session rate (1h) | > 25% | 15-25% | < 15% | Weekly |
| Trade rate (24h) | > 3% | 1.5-3% | < 1.5% | Weekly |
| Push disable lift | < 0.5% | 0.5-1% | > 1% = STOP family B for 7 days | Weekly |
| Negative action rate | < 5% | 5-8% | > 8% = review copy + frequency | Weekly |
| Avg fatigue_risk of recipients | < 0.4 | 0.4-0.6 | > 0.6 = reduce B frequency | Weekly |

**Family C -- Behavioral Triggers (C-01 to C-05)**

In-app behavioral signals. User demonstrated interest through actions, not explicit configuration.

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| In-app CTR | > 4% | 2.5-4% | < 2.5% | Daily |
| Session rate (1h) | > 30% | 20-30% | < 20% | Weekly |
| Trade rate (24h) | > 3% | 1.5-3% | < 1.5% | Weekly |
| Push disable lift | < 0.5% | 0.5-1% | > 1% = investigate | Weekly |
| Negative action rate | < 5% | 5-8% | > 8% | Weekly |
| Avg fatigue_risk of recipients | < 0.4 | 0.4-0.6 | > 0.6 = reduce C frequency | Weekly |

**Family D -- Lifecycle Triggers (D-01 to D-06)**

Lifecycle stage transitions. Lower intent (user is drifting away), but high business value (retention/reactivation).

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| Push/Email CTR | > 2% | 1-2% | < 1% | Daily |
| Session rate (1h) | > 25% | 15-25% | < 15% | Weekly |
| Trade rate (24h) | > 5% | 2-5% | < 2% | Weekly |
| Deposit rate (24h) | > 2% | 1-2% | < 1% | Weekly |
| Push disable lift | < 0.5% | 0.5-1% | > 1% = review D cadence | Weekly |
| Negative action rate | < 5% | 5-8% | > 8% | Weekly |
| Avg fatigue_risk of recipients | < 0.5 | 0.5-0.7 | > 0.7 = reduce D frequency | Weekly |

**Family E -- Cross-sell Triggers (E-01 to E-06)**

Product adoption expansion. Lower urgency, product awareness framing only (V1 restriction).

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| Email CTR | > 2.5% | 1.5-2.5% | < 1.5% | Daily |
| Session rate (1h) | > 30% | 20-30% | < 20% | Weekly |
| Trade rate (24h) | > 3% | 1.5-3% | < 1.5% | Weekly |
| Push disable lift | < 0.5% | 0.5-1% | > 1% = review E copy | Weekly |
| Negative action rate | < 5% | 5-8% | > 8% | Weekly |
| Avg fatigue_risk of recipients | < 0.4 | 0.4-0.6 | > 0.6 = reduce E frequency | Weekly |

**Family F -- Risk & Protective Triggers (F-01 to F-06)**

Safety-critical. User expects immediate action. Highest urgency, no marketing framing.

| KPI | Target (GREEN) | Warning (AMBER) | Critical (RED) | Frequency |
|-----|----------------|-----------------|----------------|-----------|
| Push CTR | > 8% | 5-8% | < 5% = check copy urgency | Daily |
| Session rate (1h) | > 40% | 25-40% | < 25% | Weekly |
| Trade rate (24h) | N/A | N/A | N/A | N/A |
| Action rate (24h) | > 15% | 8-15% | < 8% = check deep link | Weekly |
| Push disable lift | < 0.3% | 0.3-0.5% | > 0.5% = ESCALATE (safety alerts causing opt-outs is critical) | Weekly |
| Negative action rate | < 3% | 3-5% | > 5% = ESCALATE | Weekly |

#### 14.1.3 Cross-Family Aggregate KPIs

These metrics are tracked across ALL families combined, weekly:

| KPI | Target | AMBER | RED | Owner |
|-----|--------|-------|-----|-------|
| Total push sends / active user / week | < 5 | 5-8 | > 8 = cap misconfiguration | Katy |
| Overall push CTR (all families) | > 3.5% | 2-3.5% | < 2% = systemic relevance issue | Katy |
| Global push opt-out rate (weekly) | < 0.5% | 0.5-0.8% | > 1% = STOP all P3+ | Katy + Daniel |
| Fatigue risk > 0.7 user count | < 5% of MMU | 5-10% | > 10% = systemic over-messaging | Alvaro |
| NNV total (all triggers, weekly) | > EUR 0 | EUR 0 to -500 | < EUR -500 = net negative system | Daniel |

**Cross-reference:** Section 2.7 already defines 6 monitoring KPIs. This section extends those with per-family granularity and adds Level 2 (engagement) and Level 4 (business impact) metrics not covered in Section 2.7.

---

### 14.2 Deliverability Health Metrics

Deliverability is the foundation of the entire notification system. If push tokens expire, email reputation degrades, or opt-in rates decline, the trigger system loses its delivery channel permanently. These metrics are monitored independently of trigger performance.

#### 14.2.1 Deliverability Dashboard

| Metric | GREEN | AMBER | RED | Action on RED | Data Source |
|--------|-------|-------|-----|---------------|-------------|
| Push delivery rate | > 95% | 85-95% | < 85% = token hygiene needed | Run stale token cleanup; investigate FCM/APNS errors | CleverTap delivery reports |
| Push opt-out rate (weekly) | < 0.5% | 0.5-0.8% | > 1% = STOP P3+ campaigns | Immediately pause all P3-P5 pushes; investigate which trigger family caused spike | CleverTap > Push > Unsubscribe Rate |
| Email spam complaint rate | < 0.1% | 0.08-0.1% | > 0.1% = pause email campaigns | Pause all marketing emails; check Google Postmaster for domain reputation drop | Google Postmaster Tools |
| iOS push permission rate | > 60% | 50-60% | < 50% = consent UX issue | Review in-app consent prompt timing and copy; check if over-messaging is driving revocations | CleverTap > Users > Push Reachability |
| Notification dismissal rate | < 40% | 40-50% | > 50% = relevance issue | Review notification copy, personalization, and timing across families | CleverTap engagement reports |
| Avg fatigue_risk score (active users) | < 0.4 | 0.4-0.6 | > 0.6 = reduce P3-P5 frequency | Reduce P3-P5 sends by 50% for 2 weeks; monitor fatigue trend | BigQuery: `SELECT AVG(notification_fatigue_score) FROM bit2me_lifecycle.user_profiles WHERE lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')` |

#### 14.2.2 Opt-In Trend Tracking

Track iOS push permission rate week-over-week to detect slow erosion that individual metrics miss:

```
Week-over-week opt-in change = (ios_opt_in_rate_this_week - ios_opt_in_rate_last_week) / ios_opt_in_rate_last_week * 100

Alert thresholds:
  > -0.5%/week: GREEN (normal churn)
  -0.5% to -1%/week: AMBER (accelerating opt-out, investigate)
  < -1%/week: RED (critical -- something is actively driving users to disable notifications)
```

**Owner:** Katy pulls weekly from CleverTap > Users > Push Reachability (filter by iOS platform).

#### 14.2.3 Token Hygiene Protocol

Stale push tokens waste delivery capacity and inflate delivery failure rates.

| Action | Cadence | Owner | Criteria |
|--------|---------|-------|----------|
| Identify stale tokens | Monthly | Alvaro (BigQuery) | Tokens with no successful delivery in 90 days |
| Remove stale tokens from targeting | Monthly | Katy (CleverTap) | Exclude users with `last_push_delivery > 90 days ago` from P3-P5 campaigns |
| Android FCM token refresh | Automatic | FCM infrastructure | FCM auto-unsubscribes tokens inactive > 270 days (FCM policy, May 2024) |
| iOS token re-registration prompt | Quarterly | Product (app update) | On app update, re-register APNS token to refresh |

**BigQuery query for stale token identification:**
```sql
SELECT user_id, platform, last_push_delivery_date,
  DATE_DIFF(CURRENT_DATE(), last_push_delivery_date, DAY) AS days_since_delivery
FROM `bit2me_lifecycle.user_profiles`
WHERE last_push_delivery_date < DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND push_token IS NOT NULL
  AND lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')
ORDER BY days_since_delivery DESC
```

#### 14.2.4 Google Postmaster Integration

For email channel health, integrate Google Postmaster Tools to monitor domain reputation:

| Metric | Where | Alert |
|--------|-------|-------|
| Domain reputation | Google Postmaster > Domain Reputation | Any drop below "Medium" = pause marketing emails |
| Spam rate | Google Postmaster > Spam Rate | > 0.1% = RED (Section 14.2.1) |
| Delivery errors | Google Postmaster > Delivery Errors | Spike > 5% = investigate DNS/SPF/DKIM |
| Authentication rate | Google Postmaster > Authentication | < 99% = check SPF/DKIM/DMARC configuration |

**Owner:** Katy checks Google Postmaster weekly alongside CleverTap email metrics.

---

### 14.3 Holdout + A/B Test Design

Holdout tests are the ONLY way to measure incremental lift -- the revenue that would NOT have happened without the notification. Without holdouts, all attribution is correlation, not causation. This is critical because Bit2Me's ghost conversion problem (93% paid attribution = existing users) demonstrates that non-incremental attribution is deeply misleading.

#### 14.3.1 Global Holdout Architecture

```
Total addressable users (MMU): ~23,000

Global holdout (10%): 2,300 users
  - Receives NO P2-P5 trigger-based notifications
  - Still receives P0 transactional and P1 user-configured
  - Purpose: measure aggregate trigger system lift on revenue, sessions, retention
  - Duration: PERMANENT (maintained across all waves and trigger launches)
```

**Holdout assignment via BigQuery (deterministic, reproducible):**

```sql
-- Deterministic holdout: same user always in same group
-- Uses FARM_FINGERPRINT for reproducible hashing
-- No randomness = no drift over time = consistent measurement
SELECT
  user_id,
  CASE
    WHEN MOD(ABS(FARM_FINGERPRINT(CAST(user_id AS STRING))), 10) = 0
    THEN 'holdout'
    ELSE 'treatment'
  END AS holdout_group
FROM `bit2me_lifecycle.user_profiles`
WHERE lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')
```

**Properties of FARM_FINGERPRINT holdout:**
- Deterministic: same user_id always maps to same group
- Uniform: 10% split is statistically balanced across user attributes
- Permanent: no re-randomization needed; new users are auto-assigned
- Reproducible: any team member can verify a user's assignment

#### 14.3.2 Per-Family Holdout Design

Within the treatment group (90%), each family maintains its own holdout for family-level lift measurement:

| Family | Per-Family Holdout | Rationale |
|--------|-------------------|-----------|
| Family A (User Configured) | NO holdout | User explicitly requested these alerts. Withholding them violates the user contract (Art. 6(1)(b)). |
| Family B (Market) | 10% within treatment | Proactive market alerts; need to measure if they drive incremental trading. |
| Family C (Behavioral) | 10% within treatment | In-app behavioral nudges; need to measure conversion lift vs organic behavior. |
| Family D (Lifecycle) | 10% within treatment | Highest-value holdout -- measures reactivation/retention lift directly. |
| Family E (Cross-sell) | 10% within treatment | Product adoption nudges; need to measure cross-sell conversion. |
| Family F (Protective) | NO holdout | Safety/compliance notifications. Cannot withhold LTV alerts or security warnings. |

**Per-family holdout assignment (BigQuery):**
```sql
-- Per-family holdout uses a different hash offset to ensure independence
SELECT
  user_id,
  CASE
    WHEN MOD(ABS(FARM_FINGERPRINT(CONCAT(CAST(user_id AS STRING), '_family_B'))), 10) = 0
    THEN 'family_B_holdout'
    ELSE 'family_B_treatment'
  END AS family_b_group
FROM `bit2me_lifecycle.user_profiles`
WHERE holdout_group = 'treatment'  -- only within treatment group
  AND lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')
```

#### 14.3.3 Statistical Requirements

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Test type | Welch's t-test (unequal variances) | More robust than Student's t-test; CleverTap computes natively |
| Significance level | p < 0.05 | Industry standard for CRM A/B tests |
| Power | 80% minimum | Standard power for detecting meaningful effects |
| Minimum test duration | 4 weeks | Captures weekly cyclicality in crypto trading behavior |
| MDE (segments > 5,000 users) | ~2 percentage points | Achievable with 10% holdout at 80% power |
| MDE (segments < 2,000 users) | Aggregate at family level | Per-trigger tests underpowered; extend to 8 weeks minimum |

**Decision rules:**
- After 4 weeks: if p < 0.05 and treatment > holdout, declare trigger effective. Scale to 100%.
- After 4 weeks: if p < 0.05 and holdout > treatment, STOP trigger. Investigate negative impact.
- After 4 weeks: if p > 0.05 (non-significant), extend to 8 weeks before deciding.
- After 8 weeks: if still p > 0.05, consider the trigger neutral. Keep if no negative health metrics; remove if any AMBER/RED health signals.

#### 14.3.4 CleverTap Holdout Implementation

**Global holdout segment in CleverTap:**

```
Segment name: holdout_global_10pct

Source: BigQuery holdout_group = 'holdout'
Sync: Hightouch every 30 minutes (upsert)
CleverTap property: holdout_global = true/false

Campaign targeting (all P2-P5 campaigns must include):
  holdout_global = false
  AND consent_marketing_push = true
  AND notification_fatigue_score < [threshold_per_tier]
  AND C8_Whale_Suppression = false
  AND Excluded_Users = false
```

**Per-family holdout segments follow the same pattern:**
- `holdout_family_B = true/false`
- `holdout_family_C = true/false`
- `holdout_family_D = true/false`
- `holdout_family_E = true/false`

Each synced from BigQuery via Hightouch. Family-specific campaigns add the corresponding holdout exclusion filter.

---

### 14.4 Net Notification Value (NNV) Formula

NNV is the single metric that answers: "Is this trigger making or losing money after accounting for channel damage?" It combines incremental revenue (the good) with opt-out cost and complaint cost (the bad).

#### 14.4.1 Formula Definition

```
NNV_per_trigger_weekly = incremental_revenue - opt_out_cost - complaint_cost

Where:
  incremental_revenue = (treatment_revenue_per_send - holdout_revenue_per_send) * weekly_sends
  opt_out_cost = opt_outs_24h * EUR 2.50  (estimated annual push revenue per user)
  complaint_cost = spam_reports * EUR 0.10  (email channel only, per complaint handling cost)

Component definitions:
  treatment_revenue_per_send = SUM(attributed_revenue for treatment users) / COUNT(treatment_sends)
  holdout_revenue_per_send = SUM(attributed_revenue for holdout users) / COUNT(holdout_users_eligible)
  opt_outs_24h = COUNT(push_disable events within 24h of send)
  spam_reports = COUNT(email spam reports within 48h of send)  -- email channel only

Constants:
  EUR 2.50 = estimated annual push revenue per user (fintech benchmark; calibrate after 30 days with Bit2Me data)
  EUR 0.10 = complaint handling cost per spam report (industry standard)
```

**Why EUR 2.50?** This represents the estimated annual revenue contribution of the push channel per user. When a user opts out of push, Bit2Me permanently loses the ability to drive that user to sessions/trades via push. At avg EUR 12/user/month revenue and push contributing ~1.7% of sessions-to-trade conversion, EUR 2.50/year is a conservative lower bound. Calibrate with actual data after 30 days of MVP.

#### 14.4.2 Worked Example 1: Family D-02 (Dormant with Balance) -- POSITIVE NNV

**Scenario:** Monthly reactivation email to dormant users with balance.

| Parameter | Value | Source |
|-----------|-------|--------|
| Eligible users | 72,400 | Bit2Me data: dormant users with balance holding EUR 19.5M AUC |
| Holdout size | 10% = 7,240 users | Per-family holdout |
| Treatment size | 90% = 65,160 users | Remaining eligible |
| Send cadence | Monthly (1 send/month, D-02 cooldown) | Master Trigger Table, Section 11 |
| Monthly sends | 65,160 | One email per treatment user |
| Treatment trade rate (24h post-open) | 1.2% | Estimated: low-intent dormant users |
| Holdout trade rate (24h, organic) | 0.3% | Baseline organic trading by dormant users |
| Avg trade revenue | EUR 12 | Bit2Me avg revenue per trading user per month |
| Opt-out rate (push disable within 24h) | 0.3% | Below 0.5% GREEN threshold |

**Step-by-step calculation:**

```
Treatment trades = 65,160 * 1.2% = 781.9 trades
Holdout trades = 7,240 * 0.3% = 21.7 trades (scaled equivalent)

Treatment revenue = 781.9 * EUR 12 = EUR 9,383
Holdout revenue (scaled to treatment size) = (21.7 / 7,240) * 65,160 * EUR 12 = EUR 2,346

Incremental revenue = EUR 9,383 - EUR 2,346 = EUR 7,037

Opt-out cost = 65,160 * 0.3% * EUR 2.50 = 195.5 * EUR 2.50 = EUR 489

Complaint cost = 65,160 * 0.02% * EUR 0.10 = 13 * EUR 0.10 = EUR 1.30
(Email spam rate assumed at 0.02%, well below 0.1% RED threshold)

NNV_D02_monthly = EUR 7,037 - EUR 489 - EUR 1.30 = EUR 6,547
```

**Result: NNV = EUR 6,547/month (POSITIVE)**

This trigger is worth running. Even with 0.3% opt-out rate, the incremental revenue from reactivating dormant users far exceeds the channel damage cost. The 72,400 dormant users holding EUR 19.5M AUC represent significant untapped value.

#### 14.4.3 Worked Example 2: Family B-01 (Volatility Spike) -- CAUTIONARY NNV

**Scenario:** Weekly push notifications during volatility spikes. Higher opt-out risk due to proactive sending.

| Parameter | Value | Source |
|-----------|-------|--------|
| Weekly eligible users | 5,000 | Active users with holdings in volatile assets |
| Holdout size | 10% = 500 users | Per-family holdout |
| Treatment size | 90% = 4,500 users | Remaining eligible |
| Weekly sends | 4,500 | One push per eligible user per spike event |
| Treatment session rate (1h) | 30% | Higher than baseline due to market urgency |
| Holdout session rate (1h, organic) | 22% | Users check app during volatility regardless |
| Avg revenue per session | EUR 0.85 | Estimated from total weekly revenue / sessions |
| Opt-out rate (push disable within 24h) | 0.8% | AMBER zone -- proactive market pushes trigger higher opt-out |

**Step-by-step calculation:**

```
Treatment sessions = 4,500 * 30% = 1,350 sessions
Holdout sessions (scaled) = (500 * 22% / 500) * 4,500 = 990 sessions

Incremental sessions = 1,350 - 990 = 360 sessions
Incremental revenue = 360 * EUR 0.85 = EUR 306

Opt-out cost = 4,500 * 0.8% * EUR 2.50 = 36 * EUR 2.50 = EUR 90

Complaint cost = EUR 0 (push channel, no spam reports)

NNV_B01_weekly = EUR 306 - EUR 90 = EUR 216
```

**Result: NNV = EUR 216/week (POSITIVE but fragile)**

The trigger is marginally positive. However, if opt-out rate rises to 1.2% (RED zone):

```
Opt-out cost at 1.2% = 4,500 * 1.2% * EUR 2.50 = 54 * EUR 2.50 = EUR 135
NNV = EUR 306 - EUR 135 = EUR 171 (still positive, but margin shrinking)
```

And if opt-out rate hits 2% during a high-send week:

```
Opt-out cost at 2% = 4,500 * 2% * EUR 2.50 = 90 * EUR 2.50 = EUR 225
NNV = EUR 306 - EUR 225 = EUR 81 (barely positive -- approaching negative)
```

**Key insight:** Family B triggers are sensitive to opt-out rate. The incremental revenue per send is modest (EUR 0.068 per send) while the per-opt-out cost is fixed (EUR 2.50). Small changes in opt-out rate can flip NNV negative. This is why B-01 has a 0.40 send_score threshold and 1/day + 3/week frequency cap.

#### 14.4.4 BigQuery NNV Calculation Query

This query runs weekly as a scheduled query in BigQuery. It computes NNV for every active trigger.

```sql
-- Net Notification Value per trigger per week
-- Scheduled: every Monday at 06:00 UTC
-- Output: bit2me_lifecycle.vw_nnv_weekly

WITH trigger_sends AS (
  SELECT
    trigger_id,
    COUNT(*) AS total_sends,
    COUNTIF(user_opened = TRUE) AS opens,
    COUNTIF(user_converted = TRUE) AS conversions,
    COUNTIF(user_opted_out_24h = TRUE) AS opt_outs,
    SUM(CASE WHEN user_converted THEN attributed_revenue ELSE 0 END) AS gross_revenue
  FROM `bit2me_lifecycle.notification_events`
  WHERE send_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
    AND holdout_group = 'treatment'
  GROUP BY trigger_id
),
holdout_baseline AS (
  SELECT
    trigger_id,
    COUNT(*) AS holdout_users,
    COUNTIF(user_converted = TRUE) AS holdout_conversions,
    SUM(CASE WHEN user_converted THEN attributed_revenue ELSE 0 END) AS holdout_revenue
  FROM `bit2me_lifecycle.notification_events`
  WHERE send_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
    AND holdout_group = 'holdout'
  GROUP BY trigger_id
)
SELECT
  t.trigger_id,
  t.total_sends,
  t.opens,
  t.conversions,
  t.gross_revenue,
  -- Incremental revenue: (treatment rate - holdout rate) * treatment sends
  ROUND(
    (SAFE_DIVIDE(t.gross_revenue, t.total_sends)
     - SAFE_DIVIDE(h.holdout_revenue, h.holdout_users)
    ) * t.total_sends, 2
  ) AS incremental_revenue,
  -- Opt-out cost: opt_outs * EUR 2.50 annual push value per user
  ROUND(t.opt_outs * 2.50, 2) AS opt_out_cost,
  -- Complaint cost: not applicable for push (set to 0; extend for email triggers)
  0.00 AS complaint_cost,
  -- NNV = incremental_revenue - opt_out_cost - complaint_cost
  ROUND(
    (SAFE_DIVIDE(t.gross_revenue, t.total_sends)
     - SAFE_DIVIDE(h.holdout_revenue, h.holdout_users)
    ) * t.total_sends - (t.opt_outs * 2.50), 2
  ) AS nnv_weekly,
  -- Supplementary metrics
  ROUND(SAFE_DIVIDE(t.opens, t.total_sends) * 100, 2) AS ctr_pct,
  ROUND(SAFE_DIVIDE(t.opt_outs, t.total_sends) * 100, 2) AS opt_out_rate_pct,
  CURRENT_DATE() AS calculation_date
FROM trigger_sends t
LEFT JOIN holdout_baseline h USING (trigger_id)
ORDER BY nnv_weekly DESC
```

#### 14.4.5 NNV Decision Rules

| NNV Range | Status | Action |
|-----------|--------|--------|
| > EUR 100/week | GREEN | Continue trigger. Monitor health metrics. |
| EUR 0 to 100/week | AMBER | Monitor closely. Trigger is marginally positive. Optimize copy/timing. |
| EUR -50 to 0/week | WARNING | Trigger is net negative. Reduce frequency or tighten targeting. 2-week review. |
| < EUR -50/week | RED | STOP trigger immediately. Investigate which component (low revenue or high opt-out) is the driver. |

---

### 14.5 BigQuery Dashboard Spec

Alvaro builds these 5 views in BigQuery. Each view supports a specific measurement need. Together they form the trigger monitoring dashboard.

#### View 1: vw_trigger_send_metrics

| Property | Value |
|----------|-------|
| **Name** | `bit2me_lifecycle.vw_trigger_send_metrics` |
| **Purpose** | Daily operational monitoring of send volume, delivery, and engagement per trigger |
| **Refresh cadence** | Daily at 06:00 UTC |
| **Downstream consumer** | Katy (daily check), Daniel (weekly review), Qlik dashboard |

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Send date |
| `trigger_id` | STRING | Trigger identifier (A-01 through F-06) |
| `family` | STRING | Trigger family (A-F) |
| `total_sends` | INT64 | Total notifications sent |
| `deliveries` | INT64 | Successfully delivered |
| `delivery_rate` | FLOAT64 | deliveries / sends |
| `opens` | INT64 | Notifications opened |
| `ctr` | FLOAT64 | opens / deliveries |
| `dismissals` | INT64 | Notifications dismissed |
| `dismissal_rate` | FLOAT64 | dismissals / deliveries |
| `channel` | STRING | push, email, in-app |

#### View 2: vw_trigger_engagement_metrics

| Property | Value |
|----------|-------|
| **Name** | `bit2me_lifecycle.vw_trigger_engagement_metrics` |
| **Purpose** | Weekly engagement depth: did the notification drive sessions, trades, deposits? |
| **Refresh cadence** | Weekly (Monday 07:00 UTC, after vw_trigger_send_metrics) |
| **Downstream consumer** | Daniel (weekly review), NNV calculation |

| Column | Type | Description |
|--------|------|-------------|
| `week_start` | DATE | ISO week start (Monday) |
| `trigger_id` | STRING | Trigger identifier |
| `family` | STRING | Trigger family |
| `opens` | INT64 | Total opens that week |
| `sessions_within_1h` | INT64 | App sessions within 1 hour of open |
| `session_rate` | FLOAT64 | sessions_within_1h / opens |
| `trades_within_24h` | INT64 | Trade events within 24 hours of open |
| `trade_rate` | FLOAT64 | trades_within_24h / opens |
| `deposits_within_24h` | INT64 | Deposit events within 24 hours of open |
| `deposit_rate` | FLOAT64 | deposits_within_24h / opens |
| `attributed_revenue` | FLOAT64 | Revenue from trades within 24h attribution window (EUR) |

#### View 3: vw_deliverability_health

| Property | Value |
|----------|-------|
| **Name** | `bit2me_lifecycle.vw_deliverability_health` |
| **Purpose** | Weekly deliverability and fatigue monitoring per family |
| **Refresh cadence** | Weekly (Monday 07:00 UTC) |
| **Downstream consumer** | Katy (deliverability check), Daniel (escalation), Diego (informed on complaint trends) |

| Column | Type | Description |
|--------|------|-------------|
| `week_start` | DATE | ISO week start |
| `family` | STRING | Trigger family (A-F) or 'ALL' for aggregate |
| `total_sends` | INT64 | Total sends that week |
| `push_token_health_pct` | FLOAT64 | Valid push tokens / total targeted users |
| `push_opt_out_count` | INT64 | Push disables within 24h of send |
| `push_opt_out_rate` | FLOAT64 | opt_out_count / total_push_sends |
| `email_complaint_count` | INT64 | Spam reports within 48h of send |
| `email_complaint_rate` | FLOAT64 | complaint_count / total_email_sends |
| `avg_fatigue_risk` | FLOAT64 | Average fatigue_risk score of recipients |
| `users_fatigue_red` | INT64 | Count of recipients with fatigue_risk > 0.7 |
| `negative_action_rate` | FLOAT64 | (dismissals + disables + spam) / sends |
| `ios_opt_in_rate` | FLOAT64 | iOS users with push enabled / total iOS users |
| `ios_opt_in_wow_change` | FLOAT64 | Week-over-week change in iOS opt-in rate |

#### View 4: vw_nnv_weekly

| Property | Value |
|----------|-------|
| **Name** | `bit2me_lifecycle.vw_nnv_weekly` |
| **Purpose** | Weekly Net Notification Value per trigger -- the single most important business metric |
| **Refresh cadence** | Weekly (Monday 08:00 UTC, after engagement + health views) |
| **Downstream consumer** | Daniel (business review), Pablo Campos (executive reporting) |

| Column | Type | Description |
|--------|------|-------------|
| `week_start` | DATE | ISO week start |
| `trigger_id` | STRING | Trigger identifier |
| `family` | STRING | Trigger family |
| `total_sends` | INT64 | Treatment sends that week |
| `gross_revenue` | FLOAT64 | Total attributed revenue (treatment) |
| `holdout_revenue_rate` | FLOAT64 | Revenue per holdout user |
| `incremental_revenue` | FLOAT64 | (treatment rate - holdout rate) * sends |
| `opt_out_cost` | FLOAT64 | opt_outs * EUR 2.50 |
| `complaint_cost` | FLOAT64 | spam_reports * EUR 0.10 |
| `nnv_weekly` | FLOAT64 | incremental_revenue - opt_out_cost - complaint_cost |
| `nnv_cumulative` | FLOAT64 | Running total NNV since trigger launch |
| `ctr_pct` | FLOAT64 | Click-through rate |
| `opt_out_rate_pct` | FLOAT64 | Opt-out rate |
| `nnv_status` | STRING | GREEN (>100), AMBER (0-100), WARNING (-50-0), RED (<-50) |

**SQL:** Uses the NNV calculation query from Section 14.4.4.

#### View 5: vw_holdout_comparison

| Property | Value |
|----------|-------|
| **Name** | `bit2me_lifecycle.vw_holdout_comparison` |
| **Purpose** | Treatment vs holdout conversion rates per family per week -- the causal lift measurement |
| **Refresh cadence** | Weekly (Monday 08:00 UTC) |
| **Downstream consumer** | Daniel (lift analysis), Alvaro (statistical significance check) |

| Column | Type | Description |
|--------|------|-------------|
| `week_start` | DATE | ISO week start |
| `family` | STRING | Trigger family (A-F) |
| `treatment_users` | INT64 | Users in treatment group (received notifications) |
| `holdout_users` | INT64 | Users in holdout group (no P2-P5 triggers) |
| `treatment_session_rate` | FLOAT64 | Sessions per treatment user that week |
| `holdout_session_rate` | FLOAT64 | Sessions per holdout user that week |
| `session_lift_pct` | FLOAT64 | (treatment - holdout) / holdout * 100 |
| `treatment_trade_rate` | FLOAT64 | Trades per treatment user |
| `holdout_trade_rate` | FLOAT64 | Trades per holdout user |
| `trade_lift_pct` | FLOAT64 | (treatment - holdout) / holdout * 100 |
| `treatment_revenue_per_user` | FLOAT64 | Revenue per treatment user (EUR) |
| `holdout_revenue_per_user` | FLOAT64 | Revenue per holdout user (EUR) |
| `revenue_lift_pct` | FLOAT64 | (treatment - holdout) / holdout * 100 |
| `p_value_sessions` | FLOAT64 | Welch t-test p-value for session rate difference |
| `p_value_trades` | FLOAT64 | Welch t-test p-value for trade rate difference |
| `p_value_revenue` | FLOAT64 | Welch t-test p-value for revenue difference |
| `significant_at_05` | BOOLEAN | TRUE if any p_value < 0.05 |
| `weeks_elapsed` | INT64 | Weeks since holdout started |

---

### Cross-References

- **Section 2.5 (Fatigue Risk Score):** The fatigue_risk formula defined there feeds directly into Level 3 health metrics (Section 14.1) and deliverability monitoring (Section 14.2). Same formula, same thresholds.
- **Section 2.7 (Monitoring and Alerting):** Section 14.1 extends those 6 base KPIs with per-family granularity and adds engagement + business impact layers. Section 14.2 provides deeper deliverability tracking.
- **Section 11 (Master Trigger Table):** All 33 triggers are mapped to KPI targets via their family assignment. Per-trigger KPIs inherit from their family's table in Section 14.1.2.
- **Section 12 (MVP Selection):** The 4-wave launch plan determines when each family's KPIs start being measured. Wave 1 (Family A, Days 1-7) KPIs activate first.
