# Bit2Me Inactive Fee Reference

**Source:** Confluence Engineering doc — "[Funding] Fee por cuentas inactivas"
**Last confirmed:** 2026-02-26

---

## System Overview

Bit2Me charges a monthly inactivity fee on accounts that have been inactive for an extended period and still hold a balance.

| Parameter | Value |
|-----------|-------|
| Fee amount | €10/month |
| Current inactivity threshold | **3 years** without operation or login |
| Running since | August 2025 (test month) |
| Execution cadence | Monthly |
| Feb 27, 2026 | Next pending execution |

---

## Legal Definition (T&C)

The legal T&C defines inactivity as either:
- **12+ months** with no transactions, OR
- **3 months** without login

**Critical gap:** The current engineering implementation uses a 3-year threshold, which is far more permissive than what the legal T&C permits. This creates an LC opportunity to advocate for threshold reduction.

---

## Exclusions

The following users are EXCLUDED from the inactive fee, even if they meet inactivity criteria:

1. **B2M Token holders** — excluded to avoid forcing selling pressure on the internal token
2. **Earn rewards recipients** — users receiving staking/yield rewards are considered "active" from a product perspective

```sql
-- Exclusion logic (conceptual — verify actual implementation with Álvaro)
WHERE days_since_last_operation >= 1095  -- 3 years
  AND balance_eur > 0
  AND user_id NOT IN (SELECT user_id FROM b2m_token_holders)
  AND user_id NOT IN (SELECT user_id FROM earn_rewards_recipients)
```

---

## BigQuery Query

Source table confirmed in Confluence doc:

```sql
SELECT *
FROM `bit2me-bigquery-ai.funding_inactive_fee_bronze.inactive_fee`
```

Use this table to:
- See which users have been charged the fee historically
- Identify users approaching the inactivity threshold
- Understand execution cadence and amounts collected

---

## Execution History

| Month | Status |
|-------|--------|
| Aug 2025 | First execution (test) |
| Sep–Jan 2026 | Regular monthly execution |
| Feb 27, 2026 | Pending next execution |

---

## LC Opportunity

**If threshold is reduced from 3 years to 1 year:**

- Dormant-with-balance segment (72.4k globally) would be at risk of fee deduction
- Fee threat = reactivation trigger — users with balances will respond to "your funds are at risk" messaging
- LC team can design a reactivation sequence timed 30/60/90 days before fee execution
- This is a high-urgency message with genuine financial stakes for the user

**Owner:** Daniel (LC input) + Engineering (implementation)
**Status:** PENDING — REQ tied to Plan 21 in ROADMAP.md

---

## Related Lifecycle Segments

- **Stage 9 (DORMANT_WITH_BALANCE):** 72.4k users globally — primary target for fee-driven reactivation
- **L4 (Spain):** 4,414 users Spain-specific estimate with balance in dormant state
- **Dormados con saldo:** 72.4k global / 71.5k B2C / 965 B2B

**Key filter for fee-risk users:**
```sql
WHERE days_since_last_fm > 365  -- approaching 1-year threshold (proposed)
  AND balance_eur > 0
  AND is_earn_active = false
  AND has_b2m_token = false
```
