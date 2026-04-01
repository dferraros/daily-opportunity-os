# Bit2Me Lifecycle Segmentation Reference
**Last confirmed:** Salvia analysis, 2026-02-25 (1.8M base)

## CONFIRMED GLOBAL USER BASE (Feb 25, 2026 — source: Qlik Activation Main v4)

| Category | Total | B2C | B2B | Notes |
|----------|-------|-----|-----|-------|
| Excluidos (Banned + Disabled) | ~600k (32%) | 590k | 541 | NOT addressable |
| Banned | 23k | 22.5k | 121 | Fraud/abuse — do NOT contact |
| Disabled | 568k | 567k | 420 | Various reasons |
| **Activos MMU (30d)** | **~23k (1.3%)** | **22.6k** | **340** | CONFIRMED monthly active |
| Active 90d | ~35k | — | — | Broader active window |
| Active 180d | ~55k | — | — | |
| Active 365d | ~83k | — | — | |
| **Dormidos total** | **1.24M (67%)** | **1.23M** | **8.4k** | >90d no monetizable op |
| Dormidos con saldo | 72.4k | 71.5k | 965 | HIGHEST reactivation value |
| Dormidos sin saldo | 1.17M | 1.16M | 7.4k | Win-back challenge |

**CRITICAL:** Only 23k users operate monthly. This is the true revenue base.
**CRITICAL:** Dormant-with-balance (72.4k) is the highest-priority reactivation pool.

## Spain L0–L5 Segments (Spain-specific, Feb 2026)
| Segment | Definition | Count (Spain) | Revenue Potential | A/B Test |
|---------|-----------|--------------|------------------|---------|
| L0 | No KYC | 213,863 (49.1%) | €0 direct | — |
| L1 | KYC, no FM | 29,010 | High (FM conversion) | T1 |
| L2 | FM, no retention | 36,866 | €26M+ potential | — |
| L3 | Active with value (last 90d) | 50,416 | Core revenue | T2 |
| L4 | Dormant with balance (90d+) | 4,414 (Spain-specific estimate) | €3.1M+ | T3 |
| L5 | Churned >180d, balance=0 | 101,029 | Win-back | — |

Note: L-segments use Spain-only filters + different criteria than global analysis above.

## 11-Stage Global State Machine (Chunk-2 v1.1)
| Stage | Name | Population | Notes |
|-------|------|-----------|-------|
| 0 | EXCLUDED | ~600K | Banned + disabled. NOT in lifecycle. |
| 1 | REGISTERED_ONLY | ~1.1M global / 213,863 ES | No KYC |
| 2 | KYC_COMPLETE | 29,010 ES | Verified, no deposit, no FM |
| 3 | DEPOSITED_ONLY | ~5K-15K global | Deposited, no FM. HIGHEST ROI nudge. |
| 4 | FIRST_MONETIZATION | Part of L2 | FM within last 30 days |
| 5 | ACTIVE | L3 core | is_economically_active=TRUE + >30d post-FM |
| 6 | POWER_USER | Subset of L3 | 2+ products, p75+ revenue |
| 7 | AT_RISK | — | Activity signals dropping |
| 8 | REACTIVATED | Temporary 30d | Returned from dormancy |
| 9 | DORMANT_WITH_BALANCE | **72.4k global** | 90d+ inactive, has balance. CONFIRMED Feb 25. |
| 10 | DORMANT_ZERO | ~1.17M global | 90d+ inactive, no balance |
| 11 | CHURNED | 101,029 ES | >180d, balance=0 |

## Brokerage Clusters (c0–c9)
Source: ML algorithm run weekly by Data team (Juan Fornell provides business variables).
- c6/c7 = Smart Holders: app-active, not trading. 8,800 users. €600K revenue potential. BEST A/B cluster (constant app use).
- c8 = Whales: 90.91% of Loan revenue. NEVER mass push. Personal relationship required.
- Users need activity before classification (c6/c7 only for users with brokerage activity).
- CSV files: c8-suppression-ES-clevertap.csv / c8-suppression-ALL-clevertap.csv

## FM Window Debate (ongoing)
- Old definition: "first 7 days" window
- Daniel's proposed: "Monthly Monetizer" — user generating EMA within a given month
- Pablo's concern: 5-day median FM is confounded by Bitcoin market cycles
- Measure: FM velocity (rate), not fixed windows

## Key Insights from Chunk-2
- DEPOSITED_ONLY: user has money on platform, hasn't acted. P0 trigger: push within 48h.
- DCA users churn 60-70% less (to validate internally).
- Phone verification = biggest global conversion killer (53% drop non-ES vs 32% ES).
- Market cycle modifier: classify period as BULL/BEAR/NEUTRAL before cohort analysis.

## Salvia's Existing Segmentation (CleverTap-based)
- Active users = minimum login in last 3 months
- Her filters: login by 1/3/6/12 months + "ha operado si/no" + B2B/B2C
- Need: 1/3/6 month filter views (only 12-month currently available in CleverTap)
- Her work: "Análisis base de usuarios 1.8M" at https://bit2me.atlassian.net/wiki/spaces/LC/pages/5255692294/
