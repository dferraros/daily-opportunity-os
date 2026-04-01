# Qlik Audit — [GRW] ACTIVATION MAIN v4
## Date: 2026-03-11

## App Structure
- 3 sheets: ACTIVATION | FIRST MOVEMENTS | LIFE CYCLE
- Global filter: REGISTER DATE (date range)
- Last reload: 11/03/2026 8:25:36 AM

---

## Sheet 1: ACTIVATION
**Type:** Straight table by country (RESID)

**Columns / Metrics:**
- USERS
- EMAIL, % EMAIL
- PHONE, % PHONE
- VERI (KYC verified), % VERI
- N° FIRST MOVE, % FIRST MOVE
- N° FIRST MON (first monetary), % FIRST MON
- AVG VOL FIRST (avg volume first transaction)
- N° FIRST PURC (first purchase), % FIRST PURC
- AVG VOL FIRST PURC (avg volume first purchase)
- N° FIRST BLOC (first blockchain?), % FIRST BLOC
- N° ADD CARD, % ADD CARD
- N° CARD PURC (card purchase), % CARD PURC
- N° BANK DEPO (bank deposit), % BANK DEPO
- VOLUME LAST 365 DAYS
- MON VOLUME LAST 365 DAYS
- REVENUE LAST 365 DAYS
- N° CANC ORDERS (cancelled orders)

**Totals:**
- Volume 365d: €6,578,839,848
- Mon Volume: €2,573,126,855
- Revenue: €12,557,011
- Cancelled orders: 564

**Spain (ES) — top country:**
- 372,681 users → 49.48% KYC → 45.85% first move → 43.02% first purchase
- Revenue: €11,284,433

---

## Sheet 2: FIRST MOVEMENTS
**Filters:** DATE, TYPE FIRST MOVE

**Table 1: Breakdown of first movements by type (monthly)**
Movement types:
- funding (dominant ~50-60%)
- purchase (second)
- receive, sell, swap, trading, transfer (small)
- affiliates, automatic-funding, automatic-send, inactive-fee (near zero)
- launchpad-purchase, manual-send, manual-transfer, migration, social-pay, vesting (rare)

Peak: Jan 2025 = 11,235 first movements
Mar 2026 (partial): 660 (413 funding + 186 purchase)

**Table 2: FIRST MONETIZABLE CURRENCY**
- Total: 233,412 movements | €131,852,453 volume
- Has Table + Pie chart toggle
- Top by count: PEPE(1734), SHIB(1697), LUNA(1533), SC(1518), BNB(1332), XLM(1065)
- Top by volume: GFAL(€508K), MATIC(€346K), LUNA(€250K), XLM(€227K), LINK(€220K)
- Meme coins dominate count, high-cap coins dominate volume

---

## Sheet 3: LIFE CYCLE
**Filters (top bar):**
- REGISTER DATE
- num users: 1.87M
- is_crypto_api
- risk_name
- status_panel_referent
- account_type ← B2C / B2B filter
- account_status

**5 Charts:**
- User status by status field (enabled-not-v: 831k dominant)
- Account status: banned 22.8k | disabled 567.7k | enabled 1.28M
- last_mon_mov_group: >365 ~1.64M dominant, no mon large, 30d 148k
- has_balance: false 1.77M | true 99.7k
- last_login_group: >365 526.6k dominant, no login 13.25k

**User-level table columns:**
user_id | account_created_date | country | verification | has first mon |
mon vol last 365 days | last_mon_mov_group | has balance (>10€) |
balance | recent login | last_login_group | churn_cluster

**Totals:**
- Mon vol 365d: €2,588,190,745
- Total balance: €415,362,399

**churn_cluster values:** activos | churn | (empty)

---

## Gap Analysis vs LC-OS Dashboard

### ✅ In both Qlik and LC-OS:
- Total users, KYC verified count/rate
- First purchase count/rate
- Revenue total
- B2C/B2B filter (account_type)
- Has balance
- Country filter (geography)

### ❌ In Qlik but MISSING from LC-OS:
**Activation sheet:**
- AVG VOL FIRST (avg first transaction volume)
- AVG VOL FIRST PURC (avg first purchase volume)
- N° FIRST BLOC / % FIRST BLOC
- N° ADD CARD / % ADD CARD
- N° CARD PURC / % CARD PURC
- N° BANK DEPO / % BANK DEPO
- CANCELLED ORDERS count
- Full country breakdown (Qlik has 25+ countries; LC-OS only ES vs PT)

**First Movements sheet:**
- First movement TYPE breakdown (funding vs purchase vs receive etc.)
- Monthly trend by movement type
- First monetizable currency (which crypto was first)
- Volume by first currency

**Life Cycle sheet:**
- Individual user-level table
- churn_cluster field (activos/churn)
- last_mon_mov_group (time buckets since last monetary movement)
- last_login_group (time buckets since last login)
- has balance >10€ boolean
- risk_name filter
- is_crypto_api filter
- status_panel_referent filter
- mon vol last 365 days per user

---

## App 2: [RET] RETENTION MAIN v2
### Last reload: 11/03/2026 8:11:52 AM
### 6 sheets: RETENTION KPIs | PRO & CARDS COHORTS | CHURN | CHURN ANALYSIS | TIME BTW MOV. | EXPLORER

---

## Sheet 1: RETENTION KPIs

**Filters:**
- DATE FROM - TO (date range)
- REGISTERED FROM - TO (registration date range — separate from activity date)
- MOV. TYPOLOGY (movement type)
- DOWNLOAD USER... (individual user ID list — searchable)
- CRYPTO API (boolean filter)
- ACCOUNT INFO (multi-option dropdown):
  - RESIDENCE, NATIONALITY, AGE RANGE, GENDER, ACCOUNT TYPE, VERIFIED,
    MARKET MAKER, TIER LEVEL, PANEL REFERENTS STATUS, CLUSTER B2B, CLUSTER B2C

**Temporal Dimensions (4 configurable windows):**
- TD1: DAILY/WEEKLY/MONTHLY/QUARTERLY/ANNUALLY + CUSTOM → default 7d
- TD2: same options + CUSTOM → default 30d
- TD3 / TD4: numeric day inputs (7, 30)

**KPI Cards — User Activity (30d window):**
- MLU (Monthly Logged Users): 54,835 | Δ30d: -6.18%
- DLU (Daily Logged Users): 22,155 | Δ30d: -9.03%
- DLU/MLU ratio: 0.40 | Δ30d: -3.04%
- MTU (Monthly Transacting Users): 21,691 | Δ30d: -22.71%
- MTU/MLU ratio: 0.40 | Δ30d: -17.61%

**KPI Cards — Revenue (7d window):**
- W-REVENUE: €116,035.55 | Δ7d: -37.50%
- W-AVG. TICKET: €518.56 | Δ7d: -1.71%
- M-REVENUE x MTU: €29.64 | Δ30d: -28.12%
- W-TRANSACTIONS x USER: 13.68 | Δ7d: -3.38%

**Summary stat:** REGISTERED USERS: 850.8k

**Chart (right panel — tabbed):**
- Tabs: W-REVENUE | W-AVG. TICKET | MLU | DLU
- Bar chart: weekly trend
- Peak: 08/02/2026 = €443.82k W-revenue


---

## Sheet 2: PRO & CARDS COHORTS

**Structure:** Two sections (USERS + REVENUE €), each with 4 cohort tabs.

**USERS section tabs:**
- WEEK - BCARD - COHORTS
- MONTH - BCARD - COHORTS
- WEEK - PRO - COHORTS
- BCARD MONTHLY COHORTS

**REVENUE (€) section tabs:**
- WEEK - BCARD - COHORTS
- MONTH - BCARD - COHORTS
- WEEK - PRO - COHORTS
- MONTH - PRO - COHORTS

**Cohort table (each tab):**
- Rows: cohort start dates (weekly, from 17/03/2024 onward)
- Columns: weeks 0-47+ since first BCard/Pro transaction
- Filters per table: FIRST BCARD TRA... (date) + WEEKS FROM FIR... (offset)
- Heat map: warm colors = high retention rate, gray = low/null
- Data visible in recent cohorts at weeks 44-47 (users: 8, 6, 4, 3, 2, 7, 10, 10, 7)

**Key insight:** Product-specific cohort analysis — BCard and Pro tracked separately for both user retention and revenue generated post first-use. Weekly + monthly granularity. 47+ week horizon (14+ months of history).

**What this adds vs LC-OS:**
- BCard-specific cohort (users + revenue by week since first card transaction)
- Pro-specific cohort (users + revenue by week since first Pro transaction)
- Revenue cohort tables (€ value per cohort × week, not just user count)
- Weekly cohort granularity with 47-week horizon


---

## Sheet 3: CHURN

**Header KPIs (persistent):**
- CHURN: 39,812
- ACTIVOS: 46,472
- RIESGO: 21,487

**Filters:**
- churn_cluster_date (weekly date picker, from 11/10/2024)
- CLUSTER LABEL BRK B2B
- Balance in € (numeric >=0)

**6 Tabs:**

### Tab 1 — CHURN EVOLUTIVE
- Line chart: weekly trend of churn / no_churn / riesgo user counts
- From 10/10/2024 to present
- End values: no_churn ~26.3k | churn ~13k | riesgo ~6k

### Tab 2 — % VARIATION
- Grouped bar: week-over-week % change per cluster (churn/no_churn/riesgo)
- Shows volatility peaks (21/10 no_churn +14.23%, 28/10 churn -9.73%)

### Tab 3 — EVOLUTION
- (Not fully visible — likely absolute count evolution chart)

### Tab 4 — USERS
- User-level time series: user_id × weekly churn_cluster_date snapshots
- Cell values: churn | no_churn | riesgo | no_activado | null
- 146,713 users total, paginated 15k/page

### Tab 5 — CLUSTER METRICS
| churn_cluster_label | TAU | Avg Vol/User | Avg Ticket | Avg Num Movements |
|---------------------|-----|-------------|-----------|-------------------|
| Totales | 79,784 | €30,356.45 | €319.97 | 94.87 |
| churn | 26,430 | €2,606.85 | €555.89 | 4.80 |
| no_activado | 23,774 | — | €409.95 | — |
| no_churn | 66,639 | €43,589.21 | €318.89 | 138.92 |
| riesgo | 46,731 | €4,426.89 | €551.32 | 7.33 |

### Tab 6 — MONTHLY METRICS (Mar 2025 – Feb 2026)
Columns: churn_cluster_label × Month
Metrics per cluster: TAU | AVG VOL PER USER | AVG TICKET

Sample (Mar 2025): churn 4,628 | no_activado 4,119 | no_churn 17,771 | riesgo 7,941
Peak no_churn: Oct 2025 = 26,967

**What this adds vs LC-OS:**
- churn_cluster evolution over time (weekly time series) — LC-OS only has point-in-time
- Week-over-week % variation by cluster
- no_activado as distinct cluster (separate from churn)
- Per-cluster comparison: TAU, avg vol/user, avg ticket, avg movements
- Monthly breakdown of cluster metrics (TAU + vol + ticket by cluster × month)
- Balance filter (€ threshold)
- Individual user churn journey tracking (146k users, weekly snapshots)


---

## Sheet 4: CHURN ANALYSIS

**Filters (7 dimensions):**
- DATE FROM - TO (date range)
- RESIDENCE (country)
- MONETIZABLE: monetizable | unmonetizable
- PRODUCT TYPE: card | earn | loan | trade | wallet
- TYPE: deposit | trade | transfer | withdrawal
- SUBTYPE: affiliates | automatic-send | bcard | buy-trade | earn | funding | inactive-fee | loan | (more)
- METHOD: alias | apple-pay | bank-transfer | blockchain | card | cvu | email | google-pay | (more)

**Two distribution charts (side by side):**

### Left: TRANSACTED USER DISTRIBUTION (11/03/2025–11/03/2026)
- Bar histogram: X = TU (transaction frequency bucket), Y = N° Users
- Power law decay: TU=1→12.6k | TU=2→10.48k | TU=3→7.11k | TU=4→5.78k | TU=5→4.31k ...TU=28→~500
- Filterable by all 7 dimensions above

### Right: LOGGED-IN USER DISTRIBUTION (01/03/2025–11/03/2026)
- Bar histogram: X = LU (login frequency bucket), Y = N° Users
- LU=1→2.70k | LU=2→1.92k | LU=3→1.83k | LU=4→1.69k ... LU=28→~500

**What this adds vs LC-OS:**
- Transaction frequency distribution histogram (TU) — entirely absent from LC-OS
- Login frequency distribution histogram (LU) — entirely absent from LC-OS
- MONETIZABLE boolean filter (monetizable vs unmonetizable movement filter)
- Churn analysis sliceable by: product type (card/earn/loan/trade/wallet), movement type, subtype, payment method
- Power-law insight: 1-3 transactions = majority of user base (high churn risk cohort)


---

## Sheet 5: TIME BTW MOV.

**Filters:**
- Date range (calendar)
- APPLY FILTERS TO LAST...: TRUE / FALSE toggle (controls whether date filter applies to "last movement" calc)
- DATE INTERVAL: numeric input (default 30)
- HAS MAIN USER ID / MAIN USER ID

**Two sections (split by whether user transacted in the selected period):**

### Section 1: USERS WITH TRANSACTION IN PERIOD
Tabs: absolute count | % share
Histogram: X = days since last monetizable movement buckets, Y = Num users

Data (filter: 01/03/2026–11/03/2026):
| Bucket | Users | % |
|--------|-------|---|
| new | 604 | 5.54% |
| 0<=x<30 | 8,117 | 74.40% |
| 30<=x<60 | 935 | 8.57% |
| 60<=x<90 | 250 | 2.29% |
| 90<=x<120 | 211 | 1.93% |
| 120<=x<150 | 137 | 1.26% |
| +500 | 226 | 2.07% |

Key: 74.4% of active transactors had last movement <30 days ago (healthy recency)

### Section 2: USERS WITHOUT TRANSACTION IN PERIOD
Histogram: X = days since last monetizable movement, Y = Num users

Data (same filter):
| Bucket | Users | % |
|--------|-------|---|
| 0<=x<30 | 9,184 | 4.12% |
| 30<=x<60 | 12,644 | 5.68% |
| 60<=x<90 | 5,981 | 2.69% |
| 90<=x<120 | 6,886 | 3.09% |
| 120<=x<150 | 6,909 | 3.10% |
| 150<=x<180 | 6,518 | 2.93% |
| 180<=x<210 | 5,602 | 2.52% |
| 210<=x<240 | 5,615 | 2.52% |
| 240<=x<270 | 3,338 | 1.50% |
| +500 | **147,641** | **66.29%** |

Critical: 147,641 users (66.29%) haven't transacted in period AND last mon movement was 420+ days ago.
This is the true dormant/churned universe — same population as FOMO Agent target.

**What this adds vs LC-OS:**
- Time-between-movements histogram (WITH vs WITHOUT transaction, dual view)
- APPLY FILTERS TO LAST toggle — controls recency calc independently from date range
- Quantification of dormant universe by bucket (not just one aggregate number)
- new/near-dormant segments visible: 9,184 users 0-30d without recent transaction = reactivation priority
- DATE INTERVAL parameter — adjustable window for "active" definition


---

## Sheet 6: EXPLORER

**Filters:**

MOV. TYPOLOGY panel:
- PRODUCT TYPE / TYPE / SUBTYPE / METHOD / CURRENCY / MONETIZABLE

ACCOUNT INFO panel:
- STATUS / RESIDENCE / NATIONALITY / AGE RANGE / GENDER / ACCOUNT TYPE / VERIFIED / MARKET MAKER

Additional:
- HAS MAIN USER ID
- BALANCE threshold filter (SET BALANCE >=X / RESET BALANCE)
- VOLUME threshold filter (SET VOLUME >=X / RESET VOLUME)

**DETAILED TABLE columns:**
- USER ID
- ACCOUNT CREATION DATE
- RESIDENCE (country code)
- MAX MON. MOV (date of last monetizable movement)
- MAX MOV (date of last movement, any type)
- MAX ACCESS (date of last login)
- BALANCE TODAY (€)
- VOLUME OPERATION AMOUNT (€ total volume in period)
- (additional columns truncated)

**Totals (filter: 01/03/2026–11/03/2026):**
- BALANCE TODAY total: €236,909,300.33
- VOLUME OPERATION AMOUNT total: €154,155,996.23

**Sample top users (sorted by volume desc):**
- TR user, created 16/11/2023 | balance €7.67M | vol €35.19M
- ES user, created 01/07/2025 | balance €2,772 | vol €7.83M
- ES user, created 17/04/2022 | balance €575,838 | vol €6.02M

**What this adds vs LC-OS:**
- User-level explorer with 8 account dimensions + 6 movement typology filters simultaneously
- Balance threshold filter (find all users with balance >= €X)
- Volume threshold filter (find all users with volume >= €X in period)
- MAX MON. MOV / MAX MOV / MAX ACCESS dates per user (recency signals at user level)
- Sortable user table — whale hunting tool
- Total balance + total volume for any filtered cohort
- Combined filter: e.g. "ES residents, earn product, balance >= €1000, last access < 30 days"

---

## [RET] RETENTION MAIN v2 — Gap Summary vs LC-OS

### ✅ Already in LC-OS:
- Total users, KYC rate, revenue
- B2C/B2B filter, country filter
- Cohort analysis (generic)
- Life cycle stage distribution

### ❌ Missing from LC-OS (add these):

**From RETENTION KPIs:**
- MLU (Monthly Logged Users) KPI + trend
- DLU (Daily Logged Users) KPI + trend
- DLU/MLU ratio (engagement density)
- MTU (Monthly Transacting Users) + trend
- MTU/MLU ratio
- W-REVENUE (weekly revenue KPI)
- W-AVG. TICKET (weekly avg ticket)
- M-REVENUE x MTU (revenue per transacting user)
- W-TRANSACTIONS x USER (weekly tx per user)
- 4 temporal dimension windows (configurable 7d/30d/custom)
- TIER LEVEL filter / MARKET MAKER filter
- CLUSTER B2B / CLUSTER B2C separate filters

**From PRO & CARDS COHORTS:**
- BCard-specific cohort (users + revenue × week)
- Pro-specific cohort (users + revenue × week)
- Revenue cohort tables (€ by cohort × week, not just user count)
- Weekly cohort granularity with 47-week horizon

**From CHURN sheet:**
- Churn cluster evolution (weekly time series: churn/no_churn/riesgo trends)
- Week-over-week % variation by cluster
- no_activado as distinct 4th cluster state
- Per-cluster metrics: TAU, avg vol/user, avg ticket, avg movements
- Monthly cluster metrics (Mar 2025–Feb 2026)
- 146,713-user weekly churn journey table
- Balance threshold filter (>=€0, configurable)

**From CHURN ANALYSIS:**
- Transaction frequency distribution histogram (TU: 1–28+ transactions)
- Login frequency distribution histogram (LU: 1–28+ logins)
- MONETIZABLE boolean filter
- Churn analysis by PRODUCT TYPE / TYPE / SUBTYPE / METHOD

**From TIME BTW MOV.:**
- Time-since-last-monetizable-movement histogram (WITH transaction in period)
- Same histogram for WITHOUT transaction in period
- 147,641 dormant users quantified by bucket (66.29% at +500 days)
- APPLY FILTERS TO LAST toggle
- Configurable DATE INTERVAL window

**From EXPLORER:**
- User-level table: balance today, volume in period, MAX MON MOV, MAX MOV, MAX ACCESS
- Balance threshold filter (SET BALANCE >=X)
- Volume threshold filter (SET VOLUME >=X)
- 8-dimension account filter + 6-dimension movement filter simultaneously
- Cohort totals: total balance + volume for any filtered set


---

## App 3: [GRW] TRANSACTION ATTRIBUTION v1
### 3 sheets: Brokerage | Earn | Trade

---

## Sheet 1: Brokerage

**PURPOSE: CRM → Revenue attribution. CleverTap campaigns linked to actual transactions.**

**Filters:**
- Transaction Date (date range)
- users, account_type, account_status, account_residence, status_panel_referents, has_main_user_id, cluster, device, is_first_mon

**UTM Filter Panels (3 expandable):**
- REGISTER UTMS: account_mkt_kind, account_utm_source, account_utm_medium, account_utm_campaign, account_utm_content, account_utm_term, account_PRM
- TRANSACTION UTMS: mov_mkt_kind, mov_utm_source, mov_utm_medium, mov_utm_campaign, mov_utm_content, mov_utm_term, mov_PRM
- MOVEMENT TYPES: TYPE, SUBTYPE, METHOD

**Main chart (weekly stacked bar, 6 metric tabs):**
- REVENUE | TAUs WALLET | NUM TRANSACTIONS | VOLUME | AVG VOL PER USER | AVG VOL PER TRANS
- Broken down by mkt_kind: BRAND | CRM | DIRECT | EXTERNAL_DOM | INTERNAL | PAID | PARTNERS | PRODUCTO | REFERIDOS | OFFLINE | AI | TEST
- Date range: Mar 2025 – Mar 2026

**Revenue mix (pie):** DIRECT 48.1% | CRM 22.2% | OtrosAI 19.9% | PRODUCTO 8.5%

**UTM BREAKDOWN table** (total: 2,871,586 txns | €12,069,379 revenue):
Columns: mov_utm_source | mov_utm_medium | mov_utm_campaign | mov_utm_content | mov_utm_term | mov_PRM | Num transactions | Revenue

Key rows:
- DIRECT/DIRECT: 789,856 txns | €5,808,488
- (null): 1,240,546 txns | €2,399,111
- FIREBASE/NOTIFICATION/SPACECENTER: 72,047 | €283,309
- CLEVERTAP/PUSH/BULLETIN: 32,187 | €167,981
- CLEVERTAP/INAPP/B2MHOLDERMONTH: 15,588 | €84,839
- CLEVERTAP/NATIVE/400MONEDAS: 18,395 | €81,540
- CLEVERTAP/NATIVE/CANJEOB2M: 12,568 | €76,755
- CLEVERTAP/INAPP/400MONEDAS: 16,637 | €75,885
- CLEVERTAP/EMAIL/ONBOARDINGVERIFICACION: 4,508 | €48,752

**MOVEMENT DETAIL table** (totals: 84,916 TAUs | €581.96M volume | avg vol/user €6,853 | avg vol/tx €203):
| mov_type | mov_subtype | mov_method | Num txns | Revenue | TAUs | Volume | Avg/user | Avg/tx |
|----------|-------------|------------|----------|---------|------|--------|----------|--------|
| transfer | purchase | pocket | 1,285,221 | €5,140,894 | 53,943 | €257.36M | €4,771 | €200 |
| transfer | sell | pocket | 807,517 | €3,608,394 | 46,399 | €196.36M | €4,232 | €243 |
| deposit | purchase | card | 361,184 | €1,239,689 | 23,800 | €31.97M | €1,343 | €89 |
| transfer | swap | pocket | 283,479 | €1,560,939 | 22,787 | €83.12M | €3,648 | €293 |
| deposit | purchase | apple-pay | 67,786 | €287,694 | 8,912 | €7.25M | €813 | €107 |
| deposit | purchase | google-pay | 49,904 | €173,624 | 6,876 | €4.31M | €627 | €86 |

**What this adds vs LC-OS:**
- Full UTM attribution at transaction level (register UTMs vs transaction UTMs — both available)
- CleverTap campaign → revenue linkage (CLEVERTAP rows with exact txns + revenue)
- mkt_kind breakdown (DIRECT/CRM/PAID/PRODUCTO/AI/etc.) for all 6 metrics
- avg vol per user AND avg vol per transaction simultaneously
- TAUs WALLET as distinct metric from TAUs
- is_first_mon filter (first monetizable transaction flag)
- mov_PRM field (partner referral manager attribution)
- PAID vs CRM vs DIRECT revenue split — critical for ROI calculation


---

## APP: [BRO] - CLUSTERS - v1

### Sheet: PROFILING B2C

**Filters:**
- REGISTER DATE (date range)
- CLUSTER (numeric 0–9)
- AGE (range)
- GENDER (female / male)
- RESIDENCE COUNTRY
- NUMBER CURRENCIES

**Charts:**
- KNOWLEDGE CRYPTO LEVEL — bar, 4 levels (1=Poco, 2, 3, 4=Mucho)
- GENDER — bar (female ~90k / male ~390k / N/D ~190k)
- SC LEVEL DISTRIBUTION — bar levels 0–7 (0 = ~150k dominant)
- RESIDENCE COUNTRY CODE — bar by ISO2 (ES ~310k dominant, then BR, PT, AR…)
- AGE — histogram 17–57+ (peak at ~29-32)
- TODAY'S BALANCE CURRENCIES — bar by currency (EUR, BTC, USDC dominant, long tail)
- AVG. TICKET VOLUME PER PRODUCT — bar (Trade ~2.5k highest, then Brokerage, then others)
- NUMBER OF USERS PER PRODUCT — bar (Brokerage ~110k dominant, then ~60k, then ~10k)
- FREQUENCY BETWEEN OPS — histogram (0–<10 days ~58k dominant, long tail 300+ days)

---

### B2C Cluster Taxonomy (10 clusters, total ~81,463 MMU)

**Super-groups:**
| Group | Color | Clusters |
|-------|-------|---------|
| High Value | Green | C8 |
| Smart Holders | Orange | C6, C7 |
| Mass Retail | Blue | C0, C1, C4, C9 |
| Underperform | Red | C2, C3, C5 |

**Cluster detail:**

| C# | Name | Users | % | Group | Tag | ARPU |
|----|------|-------|---|-------|-----|------|
| C0 | Stablecoins holders | 2,677 | 3.27% | Mass Retail | 🎯 ADQUISICIÓN | Good |
| C1 | Maybe baby Whales | 4,890 | 5.99% | Mass Retail | 🎯 ADQUISICIÓN | Good |
| C2 | Dormant / Low Value | 8,096 | 10.71% | Underperform | 🔑 IGNORAR | Bad |
| C3 | Hibernating Users | 13,183 | 16.20% | Underperform | 🔑 IGNORAR | Bad |
| C4 | Active / Low Value | 10,747 | 13.20% | Mass Retail | 🔑 RETENCIÓN | Mid |
| C5 | Dormant / High Holder | 8,316 | 10.22% | Underperform | 🔑 IGNORAR | Bad |
| C6 | Maybe Whales | 8,683 | 10.86% | Smart Holders | 🎯 ADQUISICIÓN | Good |
| C7 | Maybe Pro traders | 5,878 | 7.22% | Smart Holders | 🎯 ADQUISICIÓN | Good |
| C8 | Maybe Active traders | 5,393 | 6.62% | High Value | 🎯 ADQUISICIÓN | Good |
| C9 | Basic Users | 13,600 | 16.72% | Mass Retail | 🔑 RETENCIÓN | Mid |

**Key dimensions per cluster:**
- Navegación: Active / Dormant / -
- Valor: Concentrated / Partial Diversify / Diversify
- Actividad (Ciclo): Hyper-Activity / Middle Activity / Low Activity / Low Value / -
- Frecuencia Op.: 0–10 días (active clusters) / - (dormant)
- Demografía (active clusters only): avg age 39–47, male ~75–90%
- Balance principal: EUR + B2M in all active clusters; C0 unique = USDC, EURC (stablecoin profile)

**Product adoption by cluster (% users using each product):**
| C# | Earn | B2M Holder | Trade | Card | Referents | Loan |
|----|------|-----------|-------|------|-----------|------|
| C0 | 36% | 30% | 21% | 14% | 11% | 3% |
| C1 | 34% | 38% | 8% | 2% | 10% | 0.3% |
| C2 | 41% | 32% | 6% | 5% | 9% | 0.1% |
| C3 | 37% | 34% | 6% | 4% | 11% | 0.1% |
| C4 | 60% | 47% | 17% | 7% | 10% | 0.7% |
| C5 | 47% | 52% | 7% | 6% | 13% | 0.04% |
| C6 | 38% | 33% | 15% | 1% | 8% | 0.8% |
| C7 | 56% | 56% | 23% | 4% | 17% | 3.4% |
| C8 | 82% | 78% | 42% | 29% | 30% | 9% |
| C9 | 62% | 54% | 15% | 9% | 16% | 0.8% |

**C8 is uniquely hyper-engaged:** 82% Earn, 78% B2M Holder, 42% Trade, 29% Card — the only cluster with meaningful Card + Loan adoption.

---

## Post-FM 2nd Purchase Journey Proposal (8 Feb 2026)

**Author:** Daniel → Pablo Campos (COO)
**Gap confirmed:** No journey exists between FM and 2nd purchase. Pablo Campos identified it personally.

**Quantified opportunity:**
- ES 2025: 31,749 First Movements (43% Reg→FM conv)
- If 20% make 2nd purchase in 14d @ €150 ticket → ~€950K incremental volume (Spain alone)
- Smart Holders (C6+C7): €600K/month potential revenue not captured

**Journey design (4 segments, A/B sprint):**
| Segment | Clusters | Strategy |
|---------|---------|---------|
| High Value (C8) | Active traders, hyper-freq | Frequency boost + Pro cross-sell |
| Smart Holders (C6+C7) | Whales/Pro, high ticket | Earn/Loan cross-sell + DCA |
| Mass Retail (C0,C1,C4,C9) | Baby whales to basic | Education + DCA automation |
| Underperform (C2,C3,C5) | Dormant, bad ARPU | Minimal 2-3 touch reactivation |

**Journey timing by segment:**
- D+1: Push+Email (all segments — personalized by cluster)
- D+3–5: Push (2nd purchase nudge or Loan/DCA intro)
- D+7: Email (weekly summary or market move trigger)
- D+10–14: Email+InApp (cross-sell or DCA setup)
- D+21–30: Underperform only — final reactivation

**A/B design (Juan Fornell requirement):**
- Control: 20% — no journey (baseline)
- Variant A: 40% — full journey (4 touchpoints per segment)
- Variant B: 40% — reduced journey (D+1 + D+7 only)

**KPIs:**
- 2nd Purchase Rate: +5pp vs control (14d window)
- Time to 2nd Purchase: -2 days vs control
- DCA Setup Rate: +3pp
- Cross-sell Rate: +2pp (C6–C8 only)
- Unsubscribe Rate: <0.5% (guardrail)

**Cross-sell data (Álvaro Durán, 7 Feb):**
- C8 → Loan Whales: 90.91% of Loan Whales come from C8
- C8 → Loan Power Users: 50%
- C7 → Loan Power Users: 17.39%
- C6 → Earn: 82% BTC in Earn, +€5.2M vol

**Quick wins (launchable immediately):**
1. DCA recharge → ~1,200 users with empty DCA
2. Smart Holders market signal → 284 users (€600K/month potential)
3. Volatility alert (C8 first) — competitors send 25x more push than Bit2Me

---

## QLIK AUDIT — GAP ANALYSIS SUMMARY (complete)

### What Qlik has that LC-OS dashboard is missing:

**High priority — add to LC-OS:**
| Metric/Feature | Source App | Gap |
|----------------|-----------|-----|
| MLU / DLU / MTU (Monthly/Daily/Monthly Transacting Users) | RETENTION MAIN v2 | Not in LC-OS at all |
| Churn cluster time series (churn / no_churn / riesgo / no_activado) | RETENTION MAIN v2 | No churn cluster view |
| TU/LU split histogram | RETENTION MAIN v2 | No TU vs LU segmentation |
| TIME BTW MOV histogram (days since last mov, split by TU/non-TU) | RETENTION MAIN v2 | Not present |
| CleverTap → revenue attribution (UTM × campaign × revenue) | TRANSACTION ATTRIBUTION v1 | Not connected |
| Revenue by mkt_kind channel (DIRECT/CRM/PAID/REFERIDOS…) | TRANSACTION ATTRIBUTION v1 | No channel revenue split |
| Cluster profiling view (demographics + product adoption per cluster) | BRO CLUSTERS v1 | No cluster deep-dive tab |
| Frequency between operations histogram | BRO CLUSTERS v1 | Not present |
| AVG ticket volume per product | BRO CLUSTERS v1 | Not present |
| Knowledge crypto level distribution | BRO CLUSTERS v1 | Not present |
| SC Level distribution (0–7) | BRO CLUSTERS v1 | Partial (0–3 only in LC-OS) |
| Post-FM journey funnel (FM → 2nd purchase rate) | Proposal data | Not tracked in LC-OS |
| ARPU by cluster (Good/Mid/Bad tiering) | BRO CLUSTERS v1 | Not visible per-cluster |

**Already in LC-OS (no gap):**
- 13 lifecycle stages, health score, FOMO score
- YTD strip (Revenue, Reg, KYC, FM, TAU)
- Spain vs PT funnel comparison
- Per-chart inline filters (addChartControls)
- Space Center 7-tier view
- Earn AUM, DCA retention

