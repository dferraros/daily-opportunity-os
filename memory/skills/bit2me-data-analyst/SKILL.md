# Bit2Me Data Analyst Skill

**Warehouse:** Google BigQuery
**Dialect:** BigQuery Standard SQL
**Owner:** Daniel Ferraro, Head of Growth / LC Lead
**Updated:** 2026-02-26

---

## Entity Disambiguation

When someone says "user" at Bit2Me, clarify:

| Term | Meaning |
|------|---------|
| **user** | Any registered account (B2C retail or B2B) |
| **B2C user** | Individual retail crypto user (default assumption) |
| **B2B user** | Business client — ARPU ~€1,582 vs B2C ~€222 |
| **TAU** | Transacting Active User: ≥1 monetizable transaction in rolling 28 days |
| **FM user** | User who has completed a First Monetizable event (EMA) |
| **LC user** | Lifecycle segment: FM + ≥1 return in 30d (Candidate) OR ≥2 transactions (Confirmed) |
| **C8** | Whale cluster — top Brokerage users. NEVER include in mass analysis/pushes. |
| **Smart Holders** | Cluster c6/c7 — app-active but not trading. ~8,800 users. |

**Primary ID:** `user_id` (internal UUID). Some tables use `external_id` (business key). Always clarify which when joining.

---

## Standard Filters — ALWAYS APPLY

```sql
-- ALWAYS exclude banned/disabled accounts
WHERE status = 'enabled'
  AND is_banned = false

-- ALWAYS exclude C8 whales from mass analysis
AND user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)

-- ALWAYS exclude UK Compliance group 3 from CRM analysis
AND user_id NOT IN (SELECT user_id FROM `bit2me.compliance.compliance_uk3`)

-- ALWAYS exclude internal/test accounts
AND is_internal = false
AND is_test = false
```

---

## Key Terminology

| Term | Definition |
|------|-----------|
| **FM / First Monetizable** | First Economically Meaningful Action (EMA). EXCLUDES deposits/funding. |
| **EMA** | Economically Meaningful Action = commission > €0.50 (Brokerage), any executed trade (Pro), first loan request (Loan), etc. See full SQL in references/metrics.md |
| **B2M Token** | Internal token. NOT counted as FM. Explicitly excluded. |
| **M1 Retention** | % of FM users who make a second transaction within 30 days. Current: 0.12% (crisis metric). |
| **Trazabilidad** | Data traceability. Brokerage: 80%, ERN: 50%, Loan: 60%, Funding: 40%. |
| **Gold Layer** | BigQuery source of truth for transactions. 136 classified transaction types. |
| **L0–L5** | Spain-specific lifecycle segments (see lifecycle.md) |
| **DEPOSITED_ONLY** | User who deposited fiat/crypto but has no FM event. Highest-ROI nudge target. |

---

## Key Metrics (Quick Reference)

| Metric | Formula | Source |
|--------|---------|--------|
| **FM Rate** | FM users / KYC users | Gold Layer / users table |
| **M1 Retention** | Users with 2nd transaction ≤30d after FM / FM users | Gold Layer |
| **TAU** | Distinct users with ≥1 monetizable tx in rolling 28d | Gold Layer |
| **LTV** | (1 / weekly_churn) × ARPU_weekly | Calculated |
| **ARPU** | Revenue / TAU (for given period) | Gold Layer |
| **ROAS Blended** | Total revenue / Total marketing spend | Revenue + spend tables |
| **mROAS** | ΔRevenue / ΔSpend (incremental) | Requires holdout groups |
| **K (Viral Coef)** | Avg invitations × referral→FM conversion rate | Referral tables |
| **Ghost Conv Rate** | Existing users / Total attributed paid conversions | Paid + user tables |
| **MMU** | Monthly Monetizable Users — operated monetizable volume in last 30d | Gold Layer / users table |
| **Dormant-with-balance** | Users >90d inactive with balance > €0 | users_base / lifecycle segments |

**CRITICAL:** ROAS total = 1,004% vs ROAS new users only = 62%. ~93% of paid attribution = existing users (ghost conversions). Always filter to new user cohorts for paid analysis.

**CONFIRMED (Feb 25, 2026 — Salvia analysis, 1.8M base):**
- MMU (30d): **23k** (1.3% of total base)
- Dormant-with-balance: **72.4k** globally (HIGHEST reactivation value)
- Excluidos (banned + disabled): **~600k** (32%) — NOT addressable
- Active 365d: **~83k**

---

## Knowledge Base Navigation

| Topic | File |
|-------|------|
| Entity definitions | references/entities.md |
| KPI calculations + SQL | references/metrics.md |
| Lifecycle segments + global user base | references/lifecycle.md |
| Inactive fee system + BigQuery query | references/inactivity.md |
| Qlik dashboards catalog | references/qlik-dashboards.md |
| Transaction / Gold Layer | references/tables/gold-layer.md |
| User table | references/tables/users.md |
| Product LTV / churn | references/tables/products.md |
| Activation / funnel data | references/tables/activation.md |
| A/B tests + segments | references/ab-tests.md |
| Data exploration (file profiles) | references/data-exploration.md |

---

## Common Gotchas

1. **FM ≠ deposit.** Deposits are NOT monetizable events. FM requires a transaction that generates revenue (commission/spread).
2. **B2M Token transactions = excluded.** The internal B2M Token is explicitly NOT counted as FM.
3. **C8 suppression is mandatory.** C8 = whales. 90.91% of Loan revenue comes from C8. Mass-including them distorts ALL metrics.
4. **Spain vs Global.** España = 89.8% of global revenue but ~20% of users. Default to España filters unless global is explicit.
5. **Loan traceability = 60%.** Do NOT run Loan analysis as if it's complete. 40% of Loan events are not tracked.
6. **KYC drop-off (corrected).** Drop is NOT at phone step (~1-2%). The 50-90% drop happens at KYC identity verification. Fix = KYC flow, not phone. CO drops 90% at KYC.
7. **Time periods:** Use ≥3 months for reliable analysis. 2-week windows are insufficient for lifecycle patterns.
8. **M1 Retention crisis.** Current 0.12% vs 5% target. If your retention numbers look high, check your definition.
9. **Market cycle contamination.** FM timing is confounded by Bitcoin price cycles. Isolate cohorts by market condition (Bull/Bear/Neutral) for clean analysis.
10. **DCA users.** Users with DCA configured churn 60-70% less. Separate them in retention analysis.
