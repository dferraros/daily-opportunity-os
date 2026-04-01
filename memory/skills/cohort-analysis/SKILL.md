# Cohort Analysis Skill

**Domain:** Lifecycle Marketing / Growth Analytics
**Warehouse:** Google BigQuery (Standard SQL)
**Owner:** Daniel Ferraro, Head of Growth / LC Lead
**Updated:** 2026-03-25

---

## When to Use This Skill

Use this skill when you need to:
- Understand retention patterns across user groups over time
- Build LTV curves by acquisition wave or product entry point
- Identify the "aha moment" timing (when users who stay are different from those who leave)
- Feed retention inputs into the Markov growth calculator (NURR, CURR)
- Compare product lines (Brokerage vs Earn vs Pro) on user quality, not just volume
- Diagnose M1 Retention crisis root cause by isolating variables

---

## 1. What Is Cohort Analysis

A cohort is a group of users who share a common experience **at the same point in time**. You then track that group's behavior over subsequent time periods.

The defining constraint: cohort membership is fixed at birth. A user assigned to the Jan-2025 acquisition cohort stays in that cohort forever — you track them at Week 1, Week 4, Week 12, regardless of when you run the query.

This contrasts with cross-sectional analysis (snapshot of all users today), which mixes users at very different lifecycle stages and produces meaningless averages.

**The core question cohort analysis answers:** "Of the users who started with us in period X, how many are still doing Y at time T?"

---

## 2. Cohort Types

### 2.1 Acquisition Cohorts (by registration week/month)

Group users by when they registered (`created_at` or `registered_at`).

Best for:
- Tracking funnel conversion over time (registration → KYC → FM)
- Measuring how acquisition quality changes by period (Bull market cohorts vs Bear market cohorts)
- Comparing M1 Retention across campaign vintages

Bit2Me note: Acquisition cohorts are heavily confounded by BTC price cycle. Jan-2021 cohort registered during bull run — their behavior is not comparable to Jan-2023 bear market cohort without controlling for market condition. Always annotate cohort charts with BTC price overlay.

### 2.2 Behavioral Cohorts (by first monetization event)

Group users by when they completed their First Monetizable event (FM). This is the more useful cohort for LC analysis.

Best for:
- M1 Retention (did they transact again within 30d of FM?)
- True LTV curve (revenue accumulation starting from FM, not registration)
- Identifying which FM-month cohorts retained better (product improvements, journey improvements)

Bit2Me note: FM date != registration date. A user may register in Jan-2025 and FM in Mar-2025. For LC purposes, the **FM cohort** is what matters. NURR and CURR are both FM-cohort metrics.

### 2.3 Size Cohorts (by first deposit amount)

Group users by how much they deposited in their first transaction.

Tiers (Bit2Me context):
| Tier | First Deposit | Label |
|------|--------------|-------|
| Micro | < €50 | Tester |
| Small | €50–€500 | Entry |
| Mid | €500–€5,000 | Engaged |
| Large | > €5,000 | High-value |

Best for:
- Predicting LTV from first signal (high-deposit users have 3-4x LTV)
- Prioritizing activation nudge investment
- Sizing the reactivation AUC opportunity (Dormant users hold €19.5M — size cohort tells you where the money is)

### 2.4 Product Cohorts (by first product used)

Group users by which product they first monetized in.

| Product | FM Definition | Traceability |
|---------|--------------|-------------|
| Brokerage | Commission > €0.50 | 80% |
| Pro | Any executed trade | ~70% |
| Earn | First yield event | 50% |
| Loan | First loan request | 60% |

Best for:
- Comparing retention by product entry point (Earn users retain better due to DCA-like lock-in)
- Cross-sell analysis (Brokerage → Pro migration rate)
- Identifying which product generates the highest-quality first customer

Bit2Me note: DCA users (auto-buy configured) churn 60-70% less regardless of product. Always separate DCA-configured from non-DCA within product cohorts.

---

## 3. Key Charts

### 3.1 Retention Curve

**What it shows:** % of cohort still active at each time period after their start event.

X-axis: Weeks since FM (or registration), typically W0 through W12+
Y-axis: % of original cohort that transacted in that week (or cumulative %)
One line per cohort (or one line for the average)

**Reading the curve:**
- A healthy curve flattens and stabilizes above zero (the "smile" base)
- A death curve continues declining to 0% — the product has no retention
- The Week 1 value is your NURR input
- Where the curve flattens is approximately where "retained" users have differentiated from "lost" users

**Bit2Me M1 Retention crisis context:** Current curve goes to near-zero by W4. Target is a curve that flattens at 20%+ by W8 (Coinbase benchmark: 25% M1 retention).

### 3.2 Revenue Per Cohort Over Time (LTV Curve)

**What it shows:** Cumulative revenue per user (ARPU) for each cohort as time progresses.

X-axis: Months since FM
Y-axis: Cumulative revenue per user (EUR)
One line per cohort (or product / size tier)

**Reading the curve:**
- The slope at Month 1 reflects early engagement quality
- Where curves separate = the LTV divergence point (high-value cohorts pull away early)
- Flattening indicates churn dominates new revenue
- Use this to calculate payback period: if CAC = €X and Month-3 LTV = €Y, payback = X/Y months

### 3.3 Cohort Heatmap

**What it shows:** A grid where each row is a cohort, each column is a time period, and each cell is the retention % (or revenue) for that cohort at that time.

Format:
```
              W0    W1    W2    W4    W8    W12
Jan-2025     100%   14%    9%    5%    3%    2%
Feb-2025     100%   16%   11%    6%    4%    3%
Mar-2025     100%   19%   13%    8%    5%    4%
Apr-2025     100%   22%   15%   10%    7%    5%
```

Color scale: green = high retention, red = low retention (conditional formatting in Sheets/Qlik).

**Reading the heatmap:**
- Diagonal trends = seasonal effects (all cohorts behave worse in the same calendar month)
- Row trends = improvement in product quality over time (newer cohorts retain better)
- Sudden column drops = a product incident or market crash
- The bottom-right corner should be getting greener as the product improves

---

## 4. BigQuery SQL Patterns

### 4.1 Building the Base Cohort Table

```sql
-- Step 1: Define FM cohort (behavioral cohort by FM date)
-- Replace monetizable_events with actual Gold Layer table name
CREATE OR REPLACE TABLE `bit2me_lifecycle.cohort_fm_base` AS
SELECT
  u.user_id,
  DATE_TRUNC(fm.fm_date, WEEK(MONDAY)) AS cohort_week,
  DATE_TRUNC(fm.fm_date, MONTH) AS cohort_month,
  fm.fm_date,
  fm.first_product,        -- 'brokerage', 'earn', 'pro', 'loan'
  fm.first_deposit_eur,    -- size cohort input
  u.country_code,
  u.is_dca_configured
FROM `bit2me.gold.users` u
INNER JOIN (
  -- Subquery: first monetizable event per user
  SELECT
    user_id,
    MIN(event_date) AS fm_date,
    FIRST_VALUE(product) OVER (
      PARTITION BY user_id ORDER BY event_date
    ) AS first_product,
    FIRST_VALUE(amount_eur) OVER (
      PARTITION BY user_id ORDER BY event_date
    ) AS first_deposit_eur
  FROM `bit2me.gold.monetizable_events`
  WHERE commission_eur > 0.50
    AND product != 'b2m_token'         -- ALWAYS exclude B2M token
  GROUP BY user_id, product, event_date, amount_eur
) fm ON u.user_id = fm.user_id
WHERE u.status = 'enabled'
  AND u.is_banned = false
  AND u.is_internal = false
  AND u.is_test = false
  AND u.user_id NOT IN (
    SELECT user_id FROM `bit2me.suppression.c8_suppression_all`  -- ALWAYS exclude C8
  );
```

### 4.2 Self-Join Pattern for Retention Calculation

The canonical pattern: join the cohort base against all subsequent activity, then calculate what % returned at each interval.

```sql
-- Step 2: Calculate weekly retention per FM cohort
WITH cohort_base AS (
  SELECT
    user_id,
    cohort_week,
    fm_date
  FROM `bit2me_lifecycle.cohort_fm_base`
),

-- All monetizable activity after FM (including FM week itself)
activity AS (
  SELECT
    user_id,
    DATE_TRUNC(event_date, WEEK(MONDAY)) AS activity_week
  FROM `bit2me.gold.monetizable_events`
  WHERE commission_eur > 0.50
    AND product != 'b2m_token'
  GROUP BY user_id, activity_week
),

-- Self-join: for each cohort user, find their activity N weeks after FM
cohort_activity AS (
  SELECT
    c.cohort_week,
    a.activity_week,
    DATE_DIFF(a.activity_week, c.cohort_week, WEEK) AS weeks_since_fm,
    COUNT(DISTINCT c.user_id) AS active_users
  FROM cohort_base c
  INNER JOIN activity a ON c.user_id = a.user_id
  WHERE DATE_DIFF(a.activity_week, c.cohort_week, WEEK) >= 0
  GROUP BY c.cohort_week, a.activity_week, weeks_since_fm
),

-- Cohort sizes (denominator for % calculation)
cohort_sizes AS (
  SELECT
    cohort_week,
    COUNT(DISTINCT user_id) AS cohort_size
  FROM cohort_base
  GROUP BY cohort_week
)

SELECT
  ca.cohort_week,
  cs.cohort_size,
  ca.weeks_since_fm,
  ca.active_users,
  ROUND(ca.active_users / cs.cohort_size * 100, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_week = cs.cohort_week
WHERE ca.weeks_since_fm <= 12   -- limit to first 12 weeks
ORDER BY ca.cohort_week, ca.weeks_since_fm;
```

### 4.3 Windowed Aggregation for Cumulative LTV

```sql
-- Step 3: Cumulative LTV per cohort
WITH revenue_events AS (
  SELECT
    me.user_id,
    c.cohort_month,
    DATE_DIFF(DATE_TRUNC(me.event_date, MONTH), c.cohort_month, MONTH) AS months_since_fm,
    SUM(me.commission_eur) AS revenue_eur
  FROM `bit2me.gold.monetizable_events` me
  INNER JOIN `bit2me_lifecycle.cohort_fm_base` c ON me.user_id = c.user_id
  WHERE me.event_date >= c.fm_date
    AND me.commission_eur > 0
    AND me.product != 'b2m_token'
  GROUP BY me.user_id, c.cohort_month, months_since_fm
),

monthly_cohort_revenue AS (
  SELECT
    cohort_month,
    months_since_fm,
    COUNT(DISTINCT user_id) AS paying_users,
    SUM(revenue_eur) AS total_revenue,
    AVG(revenue_eur) AS arpu_this_month
  FROM revenue_events
  GROUP BY cohort_month, months_since_fm
),

cohort_sizes AS (
  SELECT cohort_month, COUNT(DISTINCT user_id) AS cohort_size
  FROM `bit2me_lifecycle.cohort_fm_base`
  GROUP BY cohort_month
)

SELECT
  r.cohort_month,
  cs.cohort_size,
  r.months_since_fm,
  r.arpu_this_month,
  -- Cumulative LTV per cohort user (including users who went silent)
  SUM(r.total_revenue) OVER (
    PARTITION BY r.cohort_month
    ORDER BY r.months_since_fm
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) / cs.cohort_size AS cumulative_ltv_per_user
FROM monthly_cohort_revenue r
JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.months_since_fm;
```

### 4.4 FM Cohort Retention (Bit2Me M1 Retention Query)

This is the canonical query for the M1 Retention crisis metric.

```sql
-- M1 Retention: % of FM users with a second transaction within 30 days
WITH fm_users AS (
  SELECT
    user_id,
    MIN(event_date) AS fm_date,
    DATE_TRUNC(MIN(event_date), MONTH) AS fm_cohort_month
  FROM `bit2me.gold.monetizable_events`
  WHERE commission_eur > 0.50
    AND product != 'b2m_token'
    AND user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)
  GROUP BY user_id
),

second_tx AS (
  SELECT DISTINCT
    me.user_id
  FROM `bit2me.gold.monetizable_events` me
  INNER JOIN fm_users fm ON me.user_id = fm.user_id
  WHERE me.event_date > fm.fm_date               -- strictly after FM
    AND me.event_date <= DATE_ADD(fm.fm_date, INTERVAL 30 DAY)
    AND me.commission_eur > 0.50
    AND me.product != 'b2m_token'
)

SELECT
  fm.fm_cohort_month,
  COUNT(DISTINCT fm.user_id) AS cohort_size,
  COUNT(DISTINCT s.user_id) AS retained_users,
  ROUND(COUNT(DISTINCT s.user_id) / COUNT(DISTINCT fm.user_id) * 100, 2) AS m1_retention_pct
FROM fm_users fm
LEFT JOIN second_tx s ON fm.user_id = s.user_id
GROUP BY fm.fm_cohort_month
ORDER BY fm.fm_cohort_month;
```

Expected result (as of Mar 2026): m1_retention_pct ≈ 0.12%. Target: 25%.

### 4.5 Cohort Heatmap Output (Pivot-Ready)

```sql
-- Produces rows suitable for pivot in Sheets or Qlik
-- weeks_since_fm becomes column headers after pivot
SELECT
  cohort_week,
  cohort_size,
  MAX(IF(weeks_since_fm = 0,  retention_pct, NULL)) AS w0,
  MAX(IF(weeks_since_fm = 1,  retention_pct, NULL)) AS w1,
  MAX(IF(weeks_since_fm = 2,  retention_pct, NULL)) AS w2,
  MAX(IF(weeks_since_fm = 4,  retention_pct, NULL)) AS w4,
  MAX(IF(weeks_since_fm = 8,  retention_pct, NULL)) AS w8,
  MAX(IF(weeks_since_fm = 12, retention_pct, NULL)) AS w12
FROM (
  -- insert Step 2 cohort_activity query here as subquery
  SELECT * FROM cohort_retention_view  -- or inline the CTE
)
GROUP BY cohort_week, cohort_size
ORDER BY cohort_week;
```

---

## 5. Interpretation

### 5.1 What a Healthy Retention Curve Looks Like

A healthy retention curve:
1. Starts at 100% at W0 (by definition)
2. Drops sharply in W1–W2 (some churn is always immediate)
3. **Flattens and stabilizes** above zero by W4–W8
4. The stable floor = your "engaged core" — users who will stay

The floor level is the key indicator:
- > 20% floor = strong product-market fit (Coinbase, Binance range)
- 10–20% floor = reasonable, optimize top of funnel and early journey
- < 5% floor = product-market fit problem or severe onboarding failure
- ≈ 0% floor = death curve (Bit2Me current state at M1 scale)

### 5.2 What a Death Curve Looks Like

A death curve continues declining monotonically toward 0 with no stabilization. Every time period, you lose more of whoever was left. This means:
- No users are finding enduring value
- Reactivation is the only revenue lever (no compounding retention)
- LTV is bounded by a single initial burst

Bit2Me context: The current M1 Retention of 0.12% is effectively a death curve for the first 30-day window. The strategic implication is that the 96% Retention Revenue Pool is almost entirely dependent on pre-existing habitual users (the surviving tail of older cohorts), not new cohort compounding.

### 5.3 Identifying the "Aha Moment" from Cohort Data

The "aha moment" is the experience that separates users who stay from users who leave. You can identify it by:

1. Split your FM cohort into "retained at W4" vs "not retained at W4"
2. Look at what the retained group did in W0 that the churned group did not
3. The differentiating action = your aha moment candidate

Common crypto aha moment candidates:
- Second trade within 7 days (repetition creates habit)
- Using price alert feature
- Setting up DCA (Bit2Me: DCA users churn 60-70% less — this IS the aha moment)
- Earning first yield (Earn product lock-in)
- Reaching Space Center Tier 2+

**SQL approach to find aha moment:**
```sql
-- Compare W4-retained vs churned on W0 actions
WITH retained AS (
  SELECT user_id FROM cohort_retention_view
  WHERE weeks_since_fm = 4 AND retention_pct > 0
),
churned AS (
  SELECT DISTINCT cb.user_id
  FROM cohort_fm_base cb
  WHERE cb.user_id NOT IN (SELECT user_id FROM retained)
)
-- Then join both groups against early action tables
-- and compare action rates using a simple proportion test
```

### 5.4 Smiling Curves: Bimodal Activity in Crypto

Crypto users often show a "smiling curve" retention pattern — high activity at FM (initial excitement), a trough in weeks 2-8 (post-excitement dropout), then a secondary peak when the market moves or a new product launches.

This is structurally different from SaaS retention. It means:
- Week 4 retention understates true LTV (some users are dormant, not churned)
- Re-engagement campaigns targeting W2–W8 dormant users (not fully churned) can recover significant value
- Standard 30-day churn definition overstates churn for crypto (use 90-day definition for balance-holding dormants)

Bit2Me model: Dormant-with-balance users (72.4k, €19.5M AUC) are the "smile trough" population. They are not permanently churned — they are waiting for a trigger. The FOMO Agent is designed to provide that trigger.

---

## 6. Connecting to the Growth Model

### 6.1 NURR (New User Retention Rate)

NURR = % of new FM users who make a second transaction within the defined retention window (typically 30 days = W1–W4 range).

**From cohort data:**
```
NURR = M1 Retention rate for the most recent rolling 3-month FM cohort
```

Current NURR input for Markov calculator: 0.12% (crisis state).
Target NURR: 25% (aligned to Coinbase M1 benchmark).

### 6.2 CURR (Current User Retention Rate)

CURR = % of currently active users who remain active in the next period. Measured on the existing base, not new cohorts.

**From cohort data:**
```
CURR = (Active users in week N who were also active in week N-1) / (Active users in week N-1)
```

This is a diagonal read of the cohort heatmap. For the Markov model, use a rolling 8-week average CURR to smooth volatility.

```sql
-- CURR calculation from weekly active cohorts
WITH weekly_active AS (
  SELECT
    DATE_TRUNC(event_date, WEEK(MONDAY)) AS activity_week,
    user_id
  FROM `bit2me.gold.monetizable_events`
  WHERE commission_eur > 0.50
    AND product != 'b2m_token'
    AND user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)
  GROUP BY activity_week, user_id
)
SELECT
  w1.activity_week AS week,
  COUNT(DISTINCT w1.user_id) AS active_this_week,
  COUNT(DISTINCT w2.user_id) AS also_active_next_week,
  ROUND(COUNT(DISTINCT w2.user_id) / COUNT(DISTINCT w1.user_id) * 100, 2) AS curr_pct
FROM weekly_active w1
LEFT JOIN weekly_active w2
  ON w1.user_id = w2.user_id
  AND w2.activity_week = DATE_ADD(w1.activity_week, INTERVAL 7 DAY)
GROUP BY w1.activity_week
ORDER BY w1.activity_week;
```

### 6.3 Feeding Cohort Data into the Markov Calculator

The Markov lifecycle model needs these inputs from cohort analysis:

| Markov Input | Cohort Source | Query Section |
|-------------|--------------|---------------|
| NURR | M1 Retention (W4 cohort) | Section 4.4 |
| CURR | Week-over-week active retention | Section 6.2 SQL |
| Reactivation rate | Dormant → Active cohort flip rate | Segment cohort join |
| LTV at M3/M6/M12 | Cumulative LTV query | Section 4.3 |
| Churn rate by segment | 1 - CURR per segment | Segment-filtered CURR |

Run all inputs on the same time period (last rolling 90 days) for Markov consistency. Do not mix a NURR from Q1 with a CURR from Q4.

---

## 7. Common Mistakes

### 7.1 Mixing Acquisition Cohorts with Behavioral Cohorts

**Mistake:** Using registration date as the cohort start point when computing M1 Retention.

**Why it matters:** A user who registered in Jan-2025 and FM'd in Apr-2025 will look like they have "0% W1 retention" relative to their registration cohort, but actually have normal retention relative to their FM cohort. Mixing the two inflates apparent churn.

**Fix:** Always define which event anchors the cohort. For LC metrics, anchor on FM date. For funnel metrics (registration → FM conversion), anchor on registration date. Never mix them in the same analysis.

### 7.2 Not Accounting for Survivorship Bias

**Mistake:** Comparing old cohorts (Jan-2021 bull market) to recent cohorts and concluding the product has improved.

**Why it matters:** Old cohorts have been filtered by time — only the most engaged users survive. A 2021 cohort showing 30% retention at W52 is not comparable to a 2024 cohort at W4. You are comparing survivors to the full population.

**Fix:** Always compare cohorts at the same age (same weeks_since_fm), never at the same calendar date. The heatmap diagonal (same age, different cohort birth) is the correct comparison axis.

### 7.3 Comparing Cohorts of Different Sizes Without Normalization

**Mistake:** Saying "the Feb cohort retained 500 users vs the Jan cohort's 300 users — Feb is better."

**Why it matters:** If Feb had 5,000 FM users and Jan had 1,500, Feb's retention rate is 10% vs Jan's 20%. Volume comparisons without normalization always mislead.

**Fix:** Always use retention_pct (retained / cohort_size × 100), never raw retained user counts, in any comparative statement. Show cohort_size alongside all cohort metrics so the reader can verify.

### 7.4 Ignoring Market Cycle Contamination (Bit2Me-Specific)

**Mistake:** Averaging retention across bull and bear market cohorts.

**Why it matters:** Users who FM'd during a BTC bull run behave completely differently from those who FM'd during a bear market. Bull cohorts have higher initial activity but faster churn (FOMO traders). Bear cohorts are smaller but contain more dedicated users with higher CURR.

**Fix:** Annotate all cohort charts with BTC price regime (Bull / Bear / Neutral) and run separate averages per regime before combining.

### 7.5 Using the Wrong Time Window for M1 Retention

**Mistake:** Calling it "M1 Retention" but measuring 7-day or 14-day windows.

**Why it matters:** Crypto trading is lumpy. A 7-day window will show near-zero retention even for healthy users who trade monthly. The Coinbase M1 benchmark of 25% uses a 30-day window.

**Fix:** Always use 30-day (calendar month) as the M1 window for Bit2Me. For weekly operational tracking, use "W4 retention" as the label, not M1.

### 7.6 Not Separating DCA Users

**Mistake:** Including DCA-configured users in the general cohort retention curve.

**Why it matters:** DCA users churn 60-70% less. Including them inflates apparent cohort retention, making the product look healthier than it is for non-DCA users, and obscuring the true retention gap you need to close.

**Fix:** Always produce two retention curves — DCA-on vs DCA-off — and report the DCA-off curve as the baseline product retention. The gap between the two curves quantifies the value of DCA adoption as a retention lever.

---

## 8. Quick Reference: Cohort Analysis Checklist

Before publishing any cohort analysis:

- [ ] Cohort anchor event is clearly defined (registration vs FM vs deposit)
- [ ] C8 whales excluded from all counts
- [ ] B2M token events excluded from monetizable events
- [ ] `status = 'enabled'` and `is_banned = false` filters applied
- [ ] Cohort size shown alongside retention % in every table/chart
- [ ] DCA users separated or flagged
- [ ] Market regime (Bull/Bear/Neutral) annotated on time-series charts
- [ ] Time axis labeled as "weeks/months since [anchor event]" not calendar dates
- [ ] At least 3 months of data (2-week windows are insufficient for lifecycle patterns)
- [ ] Spain filter applied if Spain-specific analysis (89.8% of revenue, ~20% of users)

---

## 9. Output Formats

| Use Case | Output Format | Destination |
|----------|--------------|-------------|
| Stakeholder overview | Retention curve PNG + 3-line summary | Lark / Notion |
| Detailed analysis | Cohort heatmap (Google Sheets, conditional formatted) | Marta / Pablo T |
| Markov model inputs | CSV with NURR, CURR, LTV columns | Daniel / growth model |
| Weekly ops | M1 Retention single number + WoW delta | Flash Report |
| Journey ROI | LTV curve before/after journey launch | LC review meeting |
