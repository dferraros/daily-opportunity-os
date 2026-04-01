# Gold Layer — BigQuery Source of Truth

## Overview
- **Location:** `bit2me.gold.*` (approximate — confirm with Pablo Talamantes)
- **Description:** Source of truth for all monetizable transactions. 136 transaction types classified.
- **Status:** Target completion < March 2026. Trazabilidad varies by product.
- **Owner:** Pablo Talamantes (BI Lead). Ticket board: https://bit2me.atlassian.net/jira/software/c/projects/BUS/boards/282

## Traceability by Product
| Product | Traceability | Notes |
|---------|-------------|-------|
| Brokerage | 80% | Good but not complete |
| ERN/Earn | 50% | Target: 80% |
| Loan | 60% | **BLOCKS Growth actions** until ≥80% |
| Funding | 40% | Lowest |
| Pro/Spot | Partial | CleverTap has NO traceability for Pro |

**Do NOT run Loan or Earn analysis as if data is complete.**

## Key Tables (approximate paths)
| Table | Contents | Notes |
|-------|---------|-------|
| `bit2me.gold.brokerage_transactions` | Brokerage trades (SWAP/SELL/PURCHASE) | commission_eur > 0.50 = FM |
| `bit2me.gold.pro_transactions` | Pro/Spot trades | BUY/SELL executed |
| `bit2me.gold.earn_subscriptions` | Earn activations | activation_date |
| `bit2me.gold.loan_requests` | Loan requests | First request = FM even if not approved |
| `bit2me.gold.card_transactions` | Card purchases | Not card add — actual purchase |
| `bit2me.gold.revenue_by_product` | Aggregated revenue | Pre-built for reporting |
| `bit2me.gold.movements` | All movements | Reference: https://docs.google.com/spreadsheets/d/1gD75mrkythn2BWg1gpYw9mwkEQ2RqdOo5pGmXjWl8Os/edit |

## Standard Query Pattern
```sql
-- Always apply these filters to Gold Layer queries
SELECT *
FROM `bit2me.gold.brokerage_transactions` t
JOIN `bit2me.users` u USING (user_id)
WHERE u.status = 'enabled'
  AND u.is_banned = false
  AND u.is_internal = false
  AND u.is_test = false
  AND t.status = 'completed'
  AND t.user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)
```

## Balances Data
- Balance data = manual download from Qlik dashboard (NOT in CleverTap)
- Cross-product segments (Brokerage + Loan) = manual via dashboard downloads
- Qlik Balance dashboard: https://bit2me.eu.qlikcloud.com/sense/app/f1834ad1-c032-4ecc-8b73-f5350c9a3c8c/
- Qlik Brokerage activity: https://bit2me.eu.qlikcloud.com/sense/app/2ccb8cdb-99fe-4d0c-ba03-2c14617a0b87/
