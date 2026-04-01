# Product Metrics & Activation Data — Bit2Me

## Official LTV / Churn by Product (Marketing Metrics v8)
Source: DELIVERY_SUMMARY.txt + Marketing_Metricas_2026_COMPLETE.xlsx

| Product | Weekly Churn | Lifetime (weeks) | LTV | 2025 Revenue | Active Users | Notes |
|---------|-------------|-----------------|-----|-------------|-------------|-------|
| Brokerage (Spot) | 1.5% | 66.7 | €246 | ~€18.5M | ~92,000 | Core product. Dominant. |
| Pro | 2.0% | 50 | €511 | €530,959 | ~1,000 | High LTV, few users. Spot rename. |
| Earn | 1.0% | 100 | €350 | — | — | LOWEST churn. BEST retention anchor. Locked funds. |
| Loan | 3.5% | 28.6 | €428.57 | — | 939 | Collateral-based. |
| Card | 6.74% | 14.8 | €15.13 | €245,420 | 4,628 | ⚠ HIGHEST churn. NOT retention anchor. |

**LTV Formula (official):** LTV = (1 / weekly_churn_rate) × ARPU_weekly
**Global avg:** 1.96% weekly churn, 50.93 week lifetime, €222.91 ARPU annual

## 2025 Actuals vs 2026 Targets
| Metric | 2025 Actual | 2026 Target | Growth |
|--------|------------|------------|--------|
| Total Revenue | €21,563,333 | €35,382,717 | +64% |
| B2C Revenue | ~€16M | ~€25M | — |
| B2B Revenue | ~€5.56M | ~€10.38M | — |
| TAU | 96,735 | 155,000 | +60% |
| ARPU Annual | €222.91 | €228.28 | +2.4% |
| New Users | 48,368 | — | — |
| Monthly Churn | 8.0% | 7.5% | -0.5pp |
| CAC Paid | €140 | — | — |
| CAC Blended | €56 | — | — |
| Payback Period | 7.5 months | — | — |

Note: España €11.8M = 89.8% of global. But global = €21.6M (incl B2B, all geos, not just B2C retail).

## ACTIVATION Data by Country (Feb 22, 2026 export)
Source: ACTIVATION - 22 de febrero de 2026.xlsx

| Country | Users | FM Rate | Revenue (LTD) | Avg Vol FM | Notes |
|---------|-------|---------|--------------|-----------|-------|
| ES | 370,496 | 44.4% | €11,795,882 | €662 | 89.8% of global revenue |
| BR | 56,559 | 9.1% | €23,497 | €86 | Low FM rate |
| PT | 45,810 | 23.1% | €210,259 | €162 | Priority market |
| AR | 35,593 | 11.3% | €37,959 | €260 | |
| MX | 30,530 | 9.2% | €34,221 | €208 | |
| IT | 24,602 | 24.2% | €91,361 | €281 | |
| DE | 13,553 | 32.9% | €268,301 | €488 | High quality users |
| FR | 18,414 | 23.1% | €78,177 | €298 | |
| PL | 16,228 | 15.4% | €44,593 | €107 | |
| GB | 7,866 | 13.6% | €225 | €572 | Compliance UK3 = blocked |
| RO | 5,931 | 32.2% | €35,347 | €380 | |

## Drop-off by Verification Step (2025 registrations — Salvia's data)
| Country | Reg→Purchase | Drop at Email | Drop at Phone |
|---------|------------|--------------|--------------|
| ES | 45% | 6% | 32% |
| PT | 20% | 12% | 28% |
| DE | 25% | ~10% | ~50% |
| IT | 22% | ~8% | ~50% |
| FR | 22% | ~10% | ~50% |
| Global ex-ES | ~22% | 13% | 53% |

**Phone verification = #1 conversion killer outside Spain.** P0 optimization target.

## Channel Health (YTD Feb 2026)
Source: QUICK_REFERENCE_METRICS_SUMMARY.txt

**GREEN:**
- ASO B2C: 37.4% of registros (4,938 YTD), €160,223 revenue. #1 by volume.
- SEO B2B: €60,220 revenue. 45.7% of B2B mix. #1 B2B channel.
- Referidos B2C: 483 FMs, 59% FM/reg rate (BEST quality ratio).

**YELLOW:**
- Paid B2C: €141,871 revenue. Ghost conversions massive. Need iROAS methodology.
- Partners B2C: €39,000 revenue. Early-stage scaling.
- SEO/GEO B2C: 1,162 registros YTD, 23.3% reg→FM rate.

**RED (ACTION REQUIRED):**
- Referidos B2C: -92% below annual target (€109,577 vs €1,383,434 target).
- Referidos B2B: -95% below annual target (€14,740 vs €276,687 target).
- GEO revenue: €15,560 (1.7% mix), -90% WoW decline.
- Partners B2B: €22 YTD. Completely underdeveloped.

## Ghost Conversions Crisis (Council W08 — Feb 17, 2026)
- ROAS TOTAL (with existing users): 1,004%
- ROAS NEW USERS ONLY (incremental): 62%
- ~93% of attributed paid conversions = EXISTING USERS = budget waste
- **Blocks all paid spend decisions until resolved**
- Action required: David Sales (BI) to implement holdout test / iROAS calculation
- Comparable issue for Referidos attribution

## Metrics Framework (v8 — 202 metrics, 13 channels × 17 sheets)
13 channels tracked: Consolidado, Consolidado B2C, Consolidado B2B, SEO/GEO B2C, SEO/GEO B2B, ASO B2C, ASO B2B, Paid B2C, Paid B2B, Partners B2C, Partners B2B, Referidos B2C, Referidos B2B.

North Stars by channel:
- Consolidado: ROAS Blended + Revenue LC
- SEO/GEO B2C: Registros Orgánicos B2C
- ASO B2C: Registros ASO B2C
- Paid B2C: ROAS Paid B2C
- Referidos B2C: Viral Coefficient K B2C (K>1 = viral self-sustaining)
