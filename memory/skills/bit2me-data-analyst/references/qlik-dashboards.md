# Bit2Me Qlik Dashboards Catalog

**Source:** Salvia's analysis doc + team knowledge
**Last confirmed:** 2026-02-26
**Access:** Internal Qlik instance (requires Bit2Me SSO)

---

## Primary LC Dashboards

| Dashboard | Name | Used For |
|-----------|------|----------|
| **Activation Main v4** | Qlik Activation Main v4 | Global user base counts, segment totals, B2C/B2B split. **Source of truth for headcount metrics.** |
| **LC Dashboard** | Lifecycle Dashboard | MMU metric, journey performance, A/B results. PENDING V0a BigQuery build. |
| **Churn Analysis** | Churn Analysis | Dormant/churned segment tracking, reactivation rates |
| **Brokerage** | Brokerage Dashboard | Trading volume, cluster analysis, c6/c7/c8 performance |

---

## Activation Main v4 — Key Segments Available

Salvia's Feb 25 analysis confirms these filters work in Qlik Activation Main v4:

- B2C / B2B split
- Active by 1 / 3 / 6 / 12 months (note: only 12-month currently reliable)
- "Ha operado sí/no" flag
- Banned / Disabled / Active status
- Country filter

**Confirmed Feb 25, 2026 counts (Qlik Activation Main v4):**
- Total base: ~1.8M
- Excluidos: ~600k (32%)
- MMU (30d): ~23k (1.3%)
- Dormidos total: 1.24M (67%)
- Dormidos con saldo: 72.4k

---

## Dashboard Gaps (as of Feb 2026)

| Gap | Impact | Fix |
|-----|--------|-----|
| MMU card not in Qlik LC Dashboard | Can't track primary KPI | Blocked by V0a BigQuery — Plan 08 |
| No 1/3/6 month filter (only 12-month) | Can't segment by engagement recency | Salvia to request from Marta |
| No UTM → Revenue linkage | Can't measure campaign attribution | Plan 07 (V0c BigQuery) |
| No product-level MMU breakdown | Can't see MMU by Brokerage/Earn/Loan | Plan 05 (V0a) + Plan 06 (V0b) |

---

## People

| Person | Role | Owns |
|--------|------|------|
| Marta del Olmo | Analytics | Qlik pulls, dashboard creation, A/B analysis |
| Salvia (S. Rut) | LC Ops | Qlik reads for user base analysis |
| Álvaro Muñoz | Data | BigQuery Gold views that feed Qlik |

---

## Qlik → BigQuery Dependency

Current Qlik dashboards pull from existing BigQuery tables. The planned Gold Layer views (V0a–V0c) will unlock new Qlik metrics:

```
V0a users_base → MMU card in Qlik LC Dashboard
V0b product_activity → Product-level MMU breakdown
V0c revenue_attribution → UTM → Revenue linkage in Qlik
```

All Qlik LC improvements are blocked until Álvaro builds V0a. ETA: Mar 10, 2026.

---

## Key Numbers to Validate in Qlik

Before using any segment count in analysis, validate it within 5% tolerance against Qlik Activation Main v4:

| Metric | Expected | Tolerance |
|--------|----------|-----------|
| Total base | ~1.8M | ±5% |
| MMU (30d) | ~23k | ±5% |
| Dormidos con saldo | 72.4k | ±5% |
| Excluidos | ~600k | ±5% |
| Spain active | ~50k (L3) | ±10% |
