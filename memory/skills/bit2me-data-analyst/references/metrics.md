# Bit2Me Key Metrics — SQL Reference

## FM (First Monetizable) — EMA Definition

The official FM definition is EMA (Economically Meaningful Action). Threshold: commission > €0.50.

```sql
-- EMA: Economically Meaningful Action (official FM definition)
-- Cross-product UNION ALL
WITH ema_events AS (
  -- Brokerage FM: commission > €0.50
  SELECT user_id, transaction_date AS fm_date, 'BROKERAGE' AS product
  FROM `bit2me.gold.brokerage_transactions`
  WHERE transaction_type IN ('SWAP', 'SELL', 'PURCHASE')
    AND commission_eur > 0.50
    AND status = 'completed'

  UNION ALL

  -- Pro/Spot FM: first executed trade (buy or sell)
  SELECT user_id, transaction_date AS fm_date, 'PRO' AS product
  FROM `bit2me.gold.pro_transactions`
  WHERE transaction_type IN ('BUY', 'SELL')
    AND status = 'executed'

  UNION ALL

  -- Earn FM: first Earn activation
  SELECT user_id, activation_date AS fm_date, 'EARN' AS product
  FROM `bit2me.gold.earn_subscriptions`
  WHERE status = 'active'

  UNION ALL

  -- Loan FM: first loan request (even if not approved)
  SELECT user_id, request_date AS fm_date, 'LOAN' AS product
  FROM `bit2me.gold.loan_requests`

  UNION ALL

  -- Card FM: first card purchase (not just add card)
  SELECT user_id, purchase_date AS fm_date, 'CARD' AS product
  FROM `bit2me.gold.card_transactions`
  WHERE transaction_type = 'PURCHASE'
    AND status = 'completed'
  -- NOTE: B2M Token purchases EXCLUDED (not an EMA)
),
first_ema AS (
  SELECT user_id, MIN(fm_date) AS fm_date, product AS first_fm_product
  FROM ema_events
  GROUP BY user_id
  -- Take earliest FM event across all products
)
SELECT * FROM first_ema;
```

---

## M1 Retention (Crisis Metric — Current 0.12%)

```sql
-- M1 Retention: % of FM users with a second EMA within 30 days of FM
WITH fm_users AS (
  -- get first FM date per user
  SELECT user_id, MIN(fm_date) AS fm_date
  FROM ema_events  -- from above
  GROUP BY user_id
),
second_action AS (
  SELECT DISTINCT e.user_id
  FROM ema_events e
  JOIN fm_users f ON e.user_id = f.user_id
  WHERE e.fm_date > f.fm_date  -- after first FM
    AND e.fm_date <= DATE_ADD(f.fm_date, INTERVAL 30 DAY)  -- within 30 days
)
SELECT
  COUNT(second_action.user_id) AS users_with_m1,
  COUNT(fm_users.user_id) AS total_fm_users,
  ROUND(COUNT(second_action.user_id) / COUNT(fm_users.user_id) * 100, 2) AS m1_retention_pct
FROM fm_users
LEFT JOIN second_action USING (user_id)
-- Current result: ~0.12%. Target Q2 2026: >5%.
```

---

## TAU (Transacting Active User)

```sql
-- TAU: users with ≥1 monetizable transaction in rolling 28 days
SELECT
  COUNT(DISTINCT user_id) AS tau
FROM `bit2me.gold.all_transactions`
WHERE transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY)
  AND is_monetizable = true
  AND status = 'completed'
  AND user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)
  AND user_id IN (SELECT user_id FROM `bit2me.users` WHERE status = 'enabled' AND is_banned = false);
```

---

## FM Rate by Country

```sql
SELECT
  residence_country,
  COUNT(DISTINCT u.user_id) AS total_kyc_users,
  COUNT(DISTINCT f.user_id) AS fm_users,
  ROUND(COUNT(DISTINCT f.user_id) / COUNT(DISTINCT u.user_id) * 100, 1) AS fm_rate_pct
FROM `bit2me.users` u
LEFT JOIN first_ema f USING (user_id)
WHERE u.kyc_status = 'approved'
  AND u.status = 'enabled'
  AND u.is_banned = false
GROUP BY residence_country
ORDER BY fm_users DESC;
-- ES: 44.4%, PT: 23.1%, DE: 32.9%, IT: 24.2%, FR: 23.1%
```

---

## LTV Calculation (Official Formula)

```sql
-- LTV by product (use pre-calculated churn rates from ALGORITMOS tab)
-- Formula: LTV = (1 / weekly_churn_rate) × ARPU_weekly

WITH product_arpu AS (
  SELECT
    product,
    COUNT(DISTINCT user_id) AS tau,
    SUM(revenue_eur) AS total_revenue,
    SUM(revenue_eur) / COUNT(DISTINCT user_id) AS arpu_annual,
    SUM(revenue_eur) / COUNT(DISTINCT user_id) / 52 AS arpu_weekly
  FROM `bit2me.gold.revenue_by_product`
  WHERE transaction_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY) AND CURRENT_DATE()
  GROUP BY product
)
SELECT
  product,
  tau,
  arpu_annual,
  arpu_weekly,
  -- Apply known churn rates:
  CASE product
    WHEN 'BROKERAGE' THEN (1/0.015) * arpu_weekly  -- LTV ~€246
    WHEN 'PRO' THEN (1/0.020) * arpu_weekly         -- LTV ~€511
    WHEN 'EARN' THEN (1/0.010) * arpu_weekly         -- LTV ~€350 (BEST)
    WHEN 'LOAN' THEN (1/0.035) * arpu_weekly         -- LTV ~€428
    WHEN 'CARD' THEN (1/0.0674) * arpu_weekly        -- LTV ~€15 (WARNING: highest churn)
  END AS ltv
FROM product_arpu;
```

---

## Ghost Conversions — iROAS Calculation

```sql
-- iROAS: revenue attributable to paid only (new users)
-- Critical: distinguish new users from existing users clicking paid ads

WITH paid_clicks AS (
  SELECT user_id, click_date, campaign_id, channel
  FROM `bit2me.paid.ad_clicks`
  WHERE channel IN ('META', 'GOOGLE', 'TIKTOK', 'DSP')
),
new_vs_existing AS (
  SELECT
    c.user_id,
    c.campaign_id,
    c.channel,
    -- Is this user new (registered after seeing the ad)?
    CASE
      WHEN u.registration_date >= DATE_SUB(c.click_date, INTERVAL 7 DAY) THEN 'new_user'
      ELSE 'existing_user'  -- ghost conversion
    END AS user_type
  FROM paid_clicks c
  JOIN `bit2me.users` u USING (user_id)
)
SELECT
  channel,
  COUNT(CASE WHEN user_type = 'new_user' THEN 1 END) AS new_user_conversions,
  COUNT(CASE WHEN user_type = 'existing_user' THEN 1 END) AS ghost_conversions,
  ROUND(COUNT(CASE WHEN user_type = 'existing_user' THEN 1 END) /
        COUNT(*) * 100, 1) AS ghost_conversion_pct
  -- Expected: ~93% ghost conversions (per Council W08, Feb 17, 2026)
FROM new_vs_existing
GROUP BY channel;
```

---

## Lifecycle Segmentation (L0–L5 — Spain)

```sql
SELECT
  CASE
    WHEN kyc_status != 'approved' THEN 'L0_NO_KYC'
    WHEN fm_date IS NULL THEN 'L1_KYC_NO_FM'
    WHEN fm_date IS NOT NULL AND second_action_date IS NULL THEN 'L2_FM_NO_RETENTION'
    WHEN last_active_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) THEN 'L3_ACTIVE_WITH_VALUE'
    WHEN last_active_date < DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
         AND total_balance > 0 THEN 'L4_DORMANT_WITH_BALANCE'
    WHEN last_active_date < DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
         AND total_balance = 0 THEN 'L5_CHURNED'
    ELSE 'OTHER'
  END AS lifecycle_segment,
  COUNT(*) AS user_count
FROM `bit2me.users` u
LEFT JOIN first_ema USING (user_id)
LEFT JOIN user_balances USING (user_id)
WHERE u.residence_country = 'ES'
  AND u.status = 'enabled'
  AND u.is_banned = false
GROUP BY lifecycle_segment
ORDER BY lifecycle_segment;
-- Expected: L0=213,863, L1=29,010, L2=36,866, L3=50,416, L4=4,414, L5=101,029
```
