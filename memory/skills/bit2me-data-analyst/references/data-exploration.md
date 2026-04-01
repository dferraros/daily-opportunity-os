# Data Exploration — Bit2Me Dataset Profiles

*Generated: Feb 25, 2026 via data:data-exploration skill*

---

## Dataset Inventory

| File | Location | Rows | Key Use |
|------|----------|------|---------|
| ACTIVATION - 22 de febrero de 2026.xlsx | Downloads/ | 231 countries | Global funnel by country (cumulative) |
| ACTIVATION - 29 de enero de 2026.xlsx | Downloads/ | 37 markets | Weekly new-user cohort snapshot (Jan W4) |
| segmentos-tests-w08-feb26.xlsx | Desktop/Bit2me LC/ | 12,772 users across 4 sheets | W08 A/B test segments (ES users only) |
| ab-test-backlog-bank.xlsx | Desktop/Bit2me LC/ | 35 tests backlog | A/B test pipeline W09-W12 |
| c8-suppression-ES-clevertap.csv | Desktop/Bit2me LC/ | 4,494 user_ids | Whale suppression list (Spain) |
| c8-suppression-ALL-clevertap.csv | Desktop/Bit2me LC/ | 4,776 user_ids | Whale suppression list (global) |
| Flash Revenue Report (14).xlsx | Downloads/ | multi-sheet | Most recent flash revenue report |
| Flash Revenue + Lifecycle — Bit2Me.xlsx | Desktop/Bit2me 3/ | 4 sheets | Revenue + LC template (max date: Feb 22) |
| Flash Revenue Matrix (4).xlsx | Downloads/ | 5 sheets | Full revenue matrix with market sentiment |

---

## ACTIVATION Feb 22, 2026 — Full Profile

**Grain:** One row per country of residence. Cumulative LTD data (not weekly).
**Total rows:** 231 countries
**Columns:** 28

### Schema

| Column | Type | Description | Quality |
|--------|------|-------------|---------|
| RESIDENCE | STRING | ISO 2-letter country code | Complete (0 nulls) |
| USERS | NUMBER | Total registered users | Complete |
| EMAIL | NUMBER | Users who completed email step | Complete |
| % EMAIL | DECIMAL | Email completion rate | Complete |
| PHONE | NUMBER | Users who completed phone step | Complete |
| % PHONE | DECIMAL | Phone completion rate | Complete |
| VERIFIED | NUMBER | KYC-verified users | Complete |
| % VERIFIED | DECIMAL | KYC rate | Complete |
| Nº FIRST MOVEMENTS | NUMBER | Users with any first movement | Complete |
| % FIRST MOVEMENTS | DECIMAL | FM (any movement) rate | Complete |
| Nº FIRST MON. MOVEMENTS | NUMBER | Users with first monetizable event | Complete |
| % FIRST MON. MOVEMENTS | DECIMAL | FM (monetizable) rate | Complete |
| AVG VOL FIRST MON. | DECIMAL | Avg volume at first monetization (€) | **91/231 nulls** (39% sparse) |
| Nº FIRST PURCHASE | NUMBER | Users with first purchase | Complete |
| % FIRST PURCHASE | DECIMAL | Purchase rate | Complete |
| AVG VOL FIRST PURCHASE | DECIMAL | Avg purchase volume (€) | Sparse |
| Nº FIRST BLOCKCHAIN | NUMBER | Users with first blockchain tx | Complete |
| % FIRST BLOCKCHAIN | DECIMAL | Blockchain rate | Complete |
| Nº ADD CARD | NUMBER | Users who added card | Complete |
| % ADD CARD | DECIMAL | Card add rate | Complete |
| Nº CARD PURCHASE | NUMBER | Users with card purchase | Complete |
| % CARD PURCHASE | DECIMAL | Card purchase rate | Complete |
| Nº BANK DEPOSIT | NUMBER | Users who made bank deposit | Complete |
| % BANK DEPOSIT | DECIMAL | Bank deposit rate | Complete |
| VOLUME LAST 365 DAYS | DECIMAL | Total trading volume LTD (€) | Complete |
| MON VOLUME LAST 365 DAYS | DECIMAL | Monetizable volume LTD (€) | Complete |
| REVENUE LAST 365 DAYS | DECIMAL | Revenue LTD (€) | Complete (some negatives = refunds) |
| Nº CANCELLED ORDERS | NUMBER | Cancelled orders count | Complete |

**Known issue:** `AVG VOL FIRST MON.` is null for 91 countries (small markets with no FM events). Do not average this column without filtering nulls first.

**Known issue:** `REVENUE LAST 365 DAYS` contains negative values (e.g., one country = -€12,648). These are likely refund corrections. Filter `> 0` for revenue analysis.

### Key Statistics (Feb 22)

| Metric | Value |
|--------|-------|
| Total global users | 823,446 |
| Total verified | 309,274 (37.6% of registered) |
| Total FM users | 223,012 (27.1% of registered) |
| Total revenue LTD | €13.1M (note: Spain alone = €11.8M) |
| Median avg FM vol (non-null) | €209 |
| Countries with revenue > 0 | ~80 |

### Top 10 by Revenue per User (min 500 users)

| Country | Rev/User | Revenue | FM% | Notes |
|---------|----------|---------|-----|-------|
| LT | €69.29 | €100,471 | 21.6% | Strong EU market — underexplored |
| EE | €20.01 | €18,711 | 22.1% | Estonia — small but quality |
| ES | €31.84 | €11,795,882 | 44.4% | Core market — 90%+ of revenue |
| AD | €17.40 | €33,899 | 21.0% | Andorra — highest avg vol (€2,138) |
| AT | €14.77 | €27,163 | 29.6% | Austria — quality EU |
| NL | €10.93 | €45,292 | 23.4% | Netherlands |
| DE | €19.80 | €268,301 | 32.9% | Germany — highest FM quality after ES |
| CH | €7.87 | €20,424 | 16.2% | Switzerland — high avg vol (€930) |
| GR | €8.93 | €17,584 | 17.4% | Greece — high avg vol (€942) |
| BE | €6.70 | €26,415 | 22.6% | Belgium |

**Hidden gem: LT (Lithuania).** 1,450 users, €69/user revenue. Highest ARPU globally except micro-markets. Zero attention currently.

### Top 5 by User Volume (with quality score)

| Country | Users | FM% | Rev/User | Quality |
|---------|-------|-----|----------|---------|
| ES | 370,496 | 44.4% | €31.84 | ✅ Core |
| BR | 56,559 | 9.1% | €0.42 | ⚠️ Low quality at scale |
| PT | 45,810 | 23.1% | €4.59 | ✅ Growing |
| AR | 35,593 | 11.3% | €1.07 | ⚠️ Low quality |
| MX | 30,530 | 9.2% | €1.12 | ⚠️ Low quality |

### KYC Funnel Drop-off by Country

**Key finding:** The drop is NOT at phone verification — it's at KYC (identity check).

| Country | Email→Phone Drop | Phone→KYC Drop | KYC% |
|---------|-----------------|----------------|------|
| ES | -1.2% | -48.3% | 49.8% |
| CO | -0.5% | **-90.3%** | 6.5% |
| US | -5.0% | -93.1% | 0.0% |
| VE | -6.5% | -91.5% | 0.0% |
| BR | -1.2% | -69.3% | 28.7% |
| IN | -0.8% | -78.2% | 20.6% |
| MX | -2.3% | -58.3% | 38.0% |
| DE | -1.8% | -56.2% | 40.8% |

**Correction to previous memory:** Phone verification is NOT the main drop. ~99% complete email, ~97% complete phone. The 50-70% drop happens at KYC (identity verification). Priority fix = KYC friction reduction, not phone verification.

### Card Penetration Analysis

| Country | Add Card % | Purchase % | Conversion Add→Purchase |
|---------|-----------|-----------|------------------------|
| ES | 36.2% | 26.0% | 71.8% |
| SV | 31.3% | 10.6% | 33.9% |
| RO | 30.6% | 16.2% | 52.9% |
| IE | 28.8% | 17.9% | 62.2% |

ES card penetration (36.2% add, 26% purchase) is strong. Add→Purchase conversion gap (71.8%) means ~28% of card adders never make a purchase.

---

## ACTIVATION Jan 29 — Cohort Snapshot

**Grain:** NEW users registered in ~week of Jan 29. Only 37 top markets.
**Key difference from Feb 22:** This is a WEEKLY new-user cohort, not cumulative LTD.

Critically: ES shows 93.9% FM rate for this week's cohort vs 44.4% cumulative.
This is because the Jan 29 export captured a high-intent week (post-market event).
Use for cohort quality analysis, not funnel baseline.

---

## Segmentos W08 — Feb 2026 A/B Test Segments

**Date:** Feb 19, 2026 | **Country:** ES only

### Sheet: RESUMEN (summary)

| Test | Segment | ES Users | A/B Valid | Send Time | Campaign |
|------|---------|---------|-----------|-----------|----------|
| T1 | Riesgo c operaciones previas | 5,523 | YES — 2,761/variant | Tue Feb 24 11:00 | reactivacion_feb26 |
| T2 | Activos sin operar 90 días | 6,681 | YES — 3,340/variant | Wed Feb 25 10:00 | reactivacion_feb26 |
| T3 | L1 Depositado | 566 | NO (too small) | Single send | — |
| T4 (implied) | Churn+Balance | 8,444 | Planned W10 | — | — |

### User-level Schema (T1/T2/T3 sheets)

| Column | Type | Description |
|--------|------|-------------|
| user_id | UUID | Truncated (privacy) — 22 chars shown |
| account_created_date | DATE | Registration date |
| country | STRING | Always 'ES' in these files |
| verification | BOOLEAN | KYC status |
| has first mon | BOOLEAN | Has prior monetizable event |
| mon vol last 365 days | DECIMAL | Monetizable volume LTD (€) |
| last_mon_mov_group | STRING | Recency bucket (30 days / 90 days / no mon) |
| has balance (>10€) | BOOLEAN | Has balance above €10 threshold |
| balance | DECIMAL | Current balance (€) |
| recent login | BOOLEAN | Logged in recently |
| last_login_group | STRING | Login recency (30 days / 90 days) |
| churn_cluster | STRING | ML cluster label |

**churn_cluster values observed:** `riesgo`, `activos`, `no_activados`

### T3 — L1 Depositado (DEPOSITED_ONLY)

566 users who: verified KYC, have balance >€10, but `has first mon = false`.
These map directly to **Stage 3: DEPOSITED_ONLY** in the 11-stage lifecycle model.
Very small segment for A/B (below 3,100 minimum for significance).
Key attribute: `mon vol last 365 days = 0` for all, but `balance > 0`.

---

## A/B Test Backlog — W09 to W12

**File:** ab-test-backlog-bank.xlsx
**Total tests planned:** 35 (AB-001 to AB-035)

### Priority Breakdown

| Priority | Count | Weeks |
|----------|-------|-------|
| 🔴 Alta | 10 | W09-W11 |
| 🟡 Media | 13 | W09-W12 |
| 🟢 Baja | 12 | W09-W12 |

### Segment Sizes in Backlog

| Segment | Users | Min for A/B |
|---------|-------|------------|
| T2 Activos 90d | 6,681 | 3,340/variant ✅ |
| T1 Riesgo | 5,523 | 2,761/variant ✅ |
| Churn+Balance | 8,444 | 4,222/variant ✅ |
| T3 L1 Depositado | 566 | 283/variant ❌ (underpowered) |

**All T3 tests use single send (no A/B)** because 566 < 3,100 minimum.

### Channel Distribution

| Channel | Tests | Notes |
|---------|-------|-------|
| Push | 22 | Primary channel |
| InApp | 10 | Strong CTR performance |
| Push+InApp | 2 | Combined |
| WhatsApp | 1 | AB-021 (low priority, W12) |

### W08 Learnings (Validated)

| Test | Winner | Metric | Learning |
|------|--------|--------|---------|
| T1 Push A vs B | A (Portfolio angle) | CTR 14.7% vs 11.8% | Portfolio > market news for churn risk |
| T1 InApp | Single (14.2% CTR) | CTR | InApp consistently > Push CTR |
| T2 Push A vs B | B (Temporal anchor) | CTR 13% vs 8.6% | "BTC at historical minimum" > MVRV data |
| T2 InApp | Single (14% CTR) | CTR | InApp strong; optimize CTA |
| T3 Push | Single (10.8% CTR) | CTR | Segment too small, no A/B |
| T3 InApp | Single (9.3% CTR) | CTR | Tutorial message = lowest CTR — simplify |

**Conversion caveat:** ALL tests showed 0 direct conversions in W08. Only "influenciadas" (assisted). M1 retention problem manifests here.

---

## Flash Revenue Report (14) — Most Recent

**Sheets:** Resumen Ejecutivo, 1ª Adq vs Life Cycle, Salud LC, Revenue por Canal, Paid 8 Semanas, Conversión por País, Fuentes de Datos

### KPI Dashboard (Resumen Ejecutivo)

| KPI | Target | Actual | Status |
|-----|--------|--------|--------|
| Paid quality (Rev/Reg) | >€5.00 | €2.76 | PENDIENTE |
| Conv. Reg→1ª Compra | 15.6% | -4.3pp | ALERTA |
| Gasto Semanal W8 | 2.071 | -0.55 | PAUSA (strategic reduction) |
| Tracking Validado | 0.8 | — | PENDIENTE |
| Fuga Inmediata (Churn) | <15% | **31.8%** | 🛑 CRÍTICO |

**Churn 31.8% = 1 in 3 first buyers churns immediately.** This is the primary metric driving M1 retention crisis.

### Revenue by Channel (most recent period)

| Channel | Revenue | % Mix | Registros | Conv% | Rev/Reg |
|---------|---------|-------|-----------|-------|---------|
| ORGANIC | €152,719 | 42.2% | 4,384 | 13.7% | €7.31 |
| DIRECT | €71,891 | 19.9% | 1,639 | 28.1% | €3.56 |
| PAID | €60,684 | 16.8% | 1,466 | 36.2% | €2.76 |
| REFERIDOS | €47,045 | 13.0% | 392 | 62.5% | €1.60 |
| PARTNERS | €16,617 | 4.6% | 271 | 24.4% | €4.11 |
| AI (LLMs) | €12,801 | 3.5% | 62 | 11.3% | €8.86 |

**Key insights:**
- ORGANIC has highest Revenue and highest Rev/Reg (€7.31)
- AI channel has highest Rev/Reg (€8.86) on small volume
- REFERIDOS has highest conversion % (62.5%) but lowest Rev/Reg (€1.60)
- PAID has worst Rev/Reg (€2.76) vs target €5.00

### Life Cycle Health (1ª Adq vs LC sheet)

| Segment | Users | % Total | Volume | Status |
|---------|-------|---------|--------|--------|
| 1ª Adquisición (Leads) | 7,177 | 83.2% | €0 | Acquisition cost with no revenue |
| Life Cycle (First buy) | 1,668 | 16.8% | €3,498,437 | Revenue activators |
| Has Balance | 1,137 | 11.4% | €2,690,487 | Balance holders |

### LC Health Subtypes

| Subtipo | Users | Balance | Riesgo |
|---------|-------|---------|--------|
| LC Core Healthy | 833 | €1,605,752 | Bajo |
| LC Churn (High Value) | 310 | **€872,500** | CRÍTICO |
| LC Riesgo/Dormidos | 525 | €1,137,739 | Medio |

**€872K in balance from 310 high-value users at churn risk.** This is the highest-ROI retention target.

### Paid Performance — 8 Weeks

| Week | Dates | Gasto | Revenue | ROAS | Trend |
|------|-------|-------|---------|------|-------|
| W1 | 01-07 Dic | €4,353 | €17,775 | 4.08x | — |
| W2 | 08-14 Dic | €4,382 | €16,408 | 3.74x | ↘ |
| W3 | 15-21 Dic | €3,564 | €11,633 | 3.26x | ↘ |
| W4 | 22-28 Dic | €4,619 | €11,490 | 2.49x | ⚠️ Festivos |
| W5 | 29 Dic-04 Ene | €4,963 | €12,727 | 2.56x | ↗ |
| W6 | 05-11 Ene | €4,892 | €14,674 | 3.00x | ↗ |

**ROAS trend:** Declining Dec (4.08x→2.49x) then recovering Jan (3.00x+). Note: these are gross ROAS. Ghost conversion issue means effective new-user ROAS ≈ 62%.

---

## C8 Suppression Lists

| File | Rows | Notes |
|------|------|-------|
| c8-suppression-ES-clevertap.csv | 4,494 | Spain whales only |
| c8-suppression-ALL-clevertap.csv | 4,776 | All markets |

Difference: 282 non-ES whales. These are CleverTap-formatted lists (single `user_id` column).
Always JOIN with suppression before any mass communication query.

---

## Data Quality Flags

| Dataset | Issue | Impact |
|---------|-------|--------|
| ACTIVATION | `AVG VOL FIRST MON` null for 91/231 countries | Filter nulls before averaging |
| ACTIVATION | Negative revenue in some countries | Filter `> 0` for revenue KPIs |
| ACTIVATION Jan 29 | Weekly cohort, not cumulative | Do not compare FM% directly to Feb 22 |
| Flash Revenue | Paid ROAS includes ghost conversions | Use iROAS (new users only) for paid decisions |
| Segmentos W08 | user_id truncated to 22 chars | Cannot join directly to BigQuery without full UUID |
| T3 Depositado | 566 users = underpowered for A/B | Single send only, no statistical significance |

---

## Recommended Queries (BigQuery)

### 1. Identify DEPOSITED_ONLY users (T3 equivalent)

```sql
-- Users who verified KYC + have balance > €10 but no FM event
SELECT u.user_id, u.country, b.balance_eur
FROM `bit2me.users` u
LEFT JOIN `bit2me.gold.user_balances` b USING (user_id)
LEFT JOIN `bit2me.gold.brokerage_transactions` t
  ON t.user_id = u.user_id AND t.commission_eur > 0.50 AND t.status = 'completed'
WHERE u.status = 'enabled'
  AND u.is_banned = false
  AND u.is_internal = false
  AND u.is_test = false
  AND u.kyc_verified = true
  AND b.balance_eur > 10
  AND t.user_id IS NULL  -- no FM event
  AND u.user_id NOT IN (SELECT user_id FROM `bit2me.suppression.c8_suppression_all`)
```

### 2. LT (Lithuania) deep dive — why is ARPU so high?

```sql
SELECT
  DATE_TRUNC(t.created_at, MONTH) as month,
  COUNT(DISTINCT t.user_id) as transacting_users,
  SUM(t.commission_eur) as revenue,
  AVG(t.commission_eur) as avg_commission,
  AVG(t.volume_eur) as avg_volume
FROM `bit2me.gold.brokerage_transactions` t
JOIN `bit2me.users` u USING (user_id)
WHERE u.country = 'LT'
  AND u.status = 'enabled'
  AND u.is_banned = false
  AND u.is_internal = false
  AND t.status = 'completed'
  AND t.commission_eur > 0.50
GROUP BY 1 ORDER BY 1
```
