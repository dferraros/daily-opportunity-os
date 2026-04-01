# Dashboard Missing Features — LC-OS Dashboard Gaps
Last updated: 2026-03-05 (full audit from all desktop folders)
Source: `Bit2me Lifecycle 2/lifecycle_OS_dashboard.html` (8 tabs, 93KB) vs. all strategy docs

Dashboard assessed: `lifecycle_OS_dashboard.html`
Current score: 6.5/10 (per README_ASSESSMENT.txt)

---

## Current Dashboard State (What Exists)

The dashboard has 8 tabs with hardcoded data from Council W08:

| Tab | Content |
|-----|---------|
| OVERVIEW | Crisis KPIs, Revenue KPIs, Activation funnel |
| LIFECYCLE | 13 stages table + transition flow + health score donut |
| HEALTH SCORE | 6 components, thresholds, distribution chart |
| BIGQUERY | 11 views, P0/P1/P2 priorities, deadlines |
| ATTRIBUTION | W-shaped model, 4 revenue pools, Council A1-A5, reporting calendar |
| JOURNEYS | J1-J6 cards, cross-sell matrix, Space Center + Referidos integration |
| SEGMENTOS | 37 segments filterable by group/search, 10 grupos |
| SALVIA BRIEF | Printable executive briefing |

2 charts total: Donut (Health Score) + Bar chart.
All data hardcoded. No live BigQuery connection.

---

## P0 Gaps — Critical Missing Features

### GAP-01: EMA Fiat Deposit Inclusion NOT in Dashboard
**Source:** `00_master_rethink.html` Gap 1, `02_bigquery_fixes.sql` FIX-001
**Problem:** Dashboard shows FM without fiat deposit fees. 20-30% of FM events are invisible.
**Fix:** Update user_fm query to include `fiat_deposit_fm` CTE. Adds 1.99% fee on Card/PayPal/Wire deposits.
**Revenue impact:** +€50K-100K/month newly classified as FM.
**SQL ready:** Yes, in `02_bigquery_fixes.sql` (FIX-001).
**Dashboard action:** Update FM count KPI and FM Rate metric after BQ deploy.

### GAP-02: Dormancy Fee Economics Tab MISSING
**Source:** `00_master_rethink.html` Gap 2, `06_dormancy_fee_economics.html`
**Problem:** €10/month inactivity fee is designed and SQL-ready but has NO visibility in dashboard.
**What needs adding:**
- PRE_DORMANCY_FEE stage user count (users in 30d window before fee)
- Fee collection revenue projection
- Reactivation rate from fee sequence (D-30/D-14/D-7)
- DORMANCY_FEE_PAYING and DORMANCY_FEE_WAIVED sub-stages
**SQL ready:** Yes, `bit2me_lifecycle.pre_dormancy_fee_users` and `bit2me_lifecycle.dormancy_fee_economics` views.
**Estimated revenue:** +€10K-20K/month once operationalized.

### GAP-03: 37-Segment Model Not Actionable in Dashboard
**Source:** `00_master_rethink.html` Gap 3, `README_37_SEGMENTS.txt`
**Problem:** SEGMENTOS tab shows the 37 segments listed but has no:
- Segment-level revenue attribution
- CRM action next step per segment
- Live user counts per segment
- Priority queue: which segments to action THIS WEEK
**What needs adding:**
- Revenue column per segment (requires BigQuery V6 revenue_by_stage_product)
- CRM action button/link per segment
- "This week's P0 segments" panel on OVERVIEW tab
- Weekly action scoring: Impact x (1/Effort) x (Segment Size / 10,000)

### GAP-04: Per-Product FM Activation Curves MISSING
**Source:** `00_master_rethink.html` Gap 4, `04_product_journey_curves.html`
**Problem:** No charts showing time-to-FM by product. Dashboard has no activation velocity data.
**What needs adding:**
- Days-to-FM by product (Referrals ~45d, Organic ~10d)
- Per-product FM conversion funnel
- Requires `bit2me_lifecycle.days_to_fm_by_product` view (NEW, in FIX-003)

### GAP-05: INE Demographic Enrichment MISSING
**Source:** `00_master_rethink.html` Gap 5, `05_INE_integration_spec.html`
**Problem:** No demographic segmentation in dashboard. INE data not integrated.
**What needs adding:**
- Age distribution of FM users vs. churned users
- Geographic heatmap of Spain (province-level)
- Income proxy segmentation
**Status:** Spec document exists (`05_INE_integration_spec.html`). BigQuery connection pending.

---

## P1 Gaps — Important Missing Features

### GAP-06: No Weekly Action Queue / 30-50 Actions Framework
**Source:** `00_master_rethink.html` Gap 6, `crm_playbooks.html`
**Problem:** CRM team runs 30-50 actions/week with no dashboard support for planning.
**What needs adding to dashboard:**
- Weekly action queue tab (Monday planning view)
- Scoring system panel: Impact x Effort x Segment Size
- Campaign calendar (Tue setup, Wed launch, Fri review)
- P0 segment alert: "These segments need action this week"

### GAP-07: David Sales Data Pulls Not Specified in Dashboard
**Source:** `00_master_rethink.html` Gap 7, `david_sales_brief.html`
**Problem:** Manual BigQuery pull requests not tracked. No visibility on data request queue.
**What needs adding:**
- Data request status panel in BIGQUERY tab
- Per-view owner assignment
- Blocker tracking (ISA access transfer, state_transition_history, etc.)

### GAP-08: Health Score Distribution Chart Incomplete
**Source:** `P0_FIXES_SUMMARY.txt`, dashboard fix record
**Problem:** Health score was 95 pts before fix. Now corrected to 100 pts with B2M Holdings component.
**Status:** FIX applied (P0_FIXES_SUMMARY.txt confirms). Dashboard should now show 6 components = 100 pts.
**Verify:** Check dashboard HEALTH SCORE tab shows B2M Holdings row (5 pts) is present.

### GAP-09: Council Report Template Not in Dashboard
**Source:** `00_master_rethink.html` Gap 9, `council_report_template.html`
**Problem:** Weekly Council reporting relies on manual preparation. No auto-generating template.
**What needs adding:**
- Council-ready slide export button from OVERVIEW tab
- Pre-formatted KPI summary for Pablo Campos review
- Delta vs. prior week for each metric
- Decision row (SCALE/HOLD/CUT/REVIEW) auto-populated from ROAS thresholds

### GAP-10: M1 Retention Cohort Chart MISSING from Dashboard
**Source:** `README_ASSESSMENT.txt`, `AUDIT_v8_NORTH_STARS_AND_PRINCIPALES.txt`
**Problem:** M1 retention crisis (0.12% vs 5% target) is the #1 crisis but has no dedicated chart.
**What needs adding to OVERVIEW tab:**
- M1 Retention rate with big red alert (0.12% actual vs 5% target vs 25% Coinbase)
- Monthly cohort table M0-M12 (exists in v8 Excel but not in LC-OS dashboard)
- Trend line showing if retention is improving

### GAP-11: Ghost Conversion / iROAS Panel MISSING
**Source:** `AUDIT_v8_NORTH_STARS_AND_PRINCIPALES.txt`, `QUICK_REFERENCE_METRICS_SUMMARY.txt`
**Problem:** ROAS 1,004% total vs 62% new-users-only = 93% ghost conversions. No dashboard visibility.
**What needs adding to ATTRIBUTION tab:**
- Ghost conversion rate (existing users / total attributed conversions)
- iROAS calculated panel (incremental revenue / paid spend)
- ROAS New Users Only metric (separate from blended ROAS)

### GAP-12: Product Cross-Sell Matrix Needs Data
**Source:** `DASHBOARD_BUILD_SUMMARY.txt`, journey framework
**Problem:** JOURNEYS tab has the cross-sell matrix structure but no actual adoption numbers.
**What needs adding:**
- Real DCA adoption % (current ~0%, target 20-30%)
- Card penetration % (current 0.26%, target 2%+)
- Multi-product user % (2 products = 1.8-2.5x LTV, 3 = 3-4x, 4+ = 4-6x LTV)
- Requires BigQuery V9 (cross_product_adoption view)

---

## P2 Gaps — Nice-to-Have

### GAP-13: A/B Test Results Not in Dashboard
**Source:** Requires BigQuery V7 (ab_test_results view), deadline Mar 31
**What needs adding:**
- Active tests panel (T1/T2/T3 current week)
- Test results feed: CTR, conversion, significance, decision (SHIP/HOLD/ITERATE)
- Link to ab-test-bot.jsx for analysis
- Historical test log with winners/losers

### GAP-14: No Live Data Connection
**Problem:** All 8 tabs use hardcoded Council W08 data (Feb 17, 2026).
**What needs adding:**
- BigQuery to Qlik to Dashboard pipeline (Gold Layer V0a-V10)
- Parameterized date range selector
- Auto-refresh daily after scheduled queries run (06:00-08:00 UTC)
- Required views: V0a (06:00), V1 (06:30), V2 (07:00) as the minimum viable daily refresh

### GAP-15: Competitor Benchmarks Panel MISSING
**Source:** `Análisis Competitivo_ Exchanges Cripto.md`
**What needs adding:**
- Benchmark strip on OVERVIEW: M1 retention (Coinbase 25%), Card penetration (42-48%), Traffic gap
- External reference context for each KPI crisis metric

### GAP-16: Flash Revenue Report NOT in Dashboard
**Source:** `chunk-3-reporting-attribution-testing.md`
**Problem:** Daily Flash Report (Acquisition vs LC split) is a separate SQL document, not integrated.
**What needs adding:**
- Daily revenue panel: FM revenue vs LC revenue split
- Section B KPIs: MMU, Churn, NRR, GRR, LT displayed daily
- Portugal own column (separate from España)
- Decision row: SCALE/HOLD/CUT/REVIEW auto-generated from thresholds

---

## Priority Build Order

Recommended sequence based on business impact:

### Phase 1 — Data foundation (must do first, unlocks everything):
1. Deploy `02_bigquery_fixes.sql` (40 min total) — adds FIX-001/002/003
2. Deploy BigQuery V0a/V0b/V0c/V1/V2/V3 (March 10 deadline)
3. Connect V1 output to dashboard LIFECYCLE tab (replace hardcoded data)

### Phase 2 — Crisis visibility (highest business urgency):
4. Add M1 Retention cohort chart to OVERVIEW (GAP-10)
5. Add PRE_DORMANCY_FEE users + economics to LIFECYCLE tab (GAP-02)
6. Add Ghost Conversion / iROAS panel to ATTRIBUTION tab (GAP-11)

### Phase 3 — Operational support (enables 30-50 actions/week):
7. Add Weekly Action Queue tab (GAP-06) with scoring panel
8. Make segment revenue + CRM action visible in SEGMENTOS tab (GAP-03)
9. Add per-product FM activation curves to LIFECYCLE tab (GAP-04)

### Phase 4 — Completeness:
10. Add A/B test results panel (GAP-13) when V7 is live (Mar 31)
11. Council export button from OVERVIEW (GAP-09)
12. INE demographic enrichment (GAP-05) — requires external data pipeline

---

## BigQuery Views Required Per Gap

| Gap | Requires | Deadline |
|-----|---------|---------|
| GAP-01 FM fiat | FIX-001 in 02_bigquery_fixes.sql | Deploy now |
| GAP-02 Dormancy fee | FIX-002 in 02_bigquery_fixes.sql + V1 update | Deploy now |
| GAP-04 Activation curves | FIX-003 days_to_fm_by_product | Deploy now |
| GAP-10 M1 Cohort | V10 cohort_revenue_curves | Mar 31 |
| GAP-11 Ghost conversion | V7 ab_test_results + iROAS calculation | Mar 31 |
| GAP-12 Cross-sell | V9 cross_product_adoption | Mar 31 |
| GAP-13 A/B tests | V7 ab_test_results | Mar 31 |
| GAP-14 Live data | All V0a-V10 | Mar 10-31 |
| GAP-16 Flash report | V6 revenue_by_stage_product | Mar 24 |

---

## Tab Architecture Recommendation (After Gaps Are Fixed)

Keep existing 8 tabs. Add 2 new tabs:

| Tab | Status | Priority |
|-----|--------|---------|
| OVERVIEW | Exists — add M1 retention chart, ghost conversion alert, P0 segment queue | P0 |
| LIFECYCLE | Exists — add PRE_DORMANCY_FEE stage, activation curves, live user counts | P0 |
| HEALTH SCORE | Exists — verify B2M Holdings 5pt component present | Done |
| BIGQUERY | Exists — add data request tracker, blocker status | P1 |
| ATTRIBUTION | Exists — add ghost conversion panel, iROAS calculation | P1 |
| JOURNEYS | Exists — add DCA %, Card %, multi-product adoption data | P1 |
| SEGMENTOS | Exists — add revenue per segment, weekly P0 queue, CRM action | P0 |
| SALVIA BRIEF | Exists — keep as-is | Done |
| WEEKLY OPS (NEW) | Action queue, scoring, campaign calendar | P1 |
| FLASH REPORT (NEW) | Daily revenue FM vs LC, Section A/B/C, Portugal column | P0 |

---

## Metrics in Strategy Docs But NOT Yet in Dashboard

These metrics exist in the v8 Excel or strategy docs but are absent from the LC-OS dashboard:

| Metric | Where defined | Tab it belongs in |
|--------|--------------|------------------|
| mROAS (Marginal ROAS) | AUDIT_v8 PRINCIPALES PAID | ATTRIBUTION |
| iROAS (Incremental ROAS) | chunk-3, AUDIT_v8 | ATTRIBUTION |
| ROAS New Users Only | AUDIT_v8 PRINCIPALES REFERIDOS | ATTRIBUTION |
| K (Viral Coefficient) | v8 REFERIDOS NS | OVERVIEW |
| NRR (Net Revenue Retention) | DELIVERY_SUMMARY | OVERVIEW |
| GRR (Gross Revenue Retention) | chunk-3 | OVERVIEW |
| MMU target (30K) vs actual (23K) | CLAUDE.md | OVERVIEW |
| AUC (€19.5M, 4,414 users) | lifecycle.md | LIFECYCLE |
| PRE_DORMANCY_FEE user count | 00_master_rethink | LIFECYCLE |
| DCA adoption % | crm_playbooks | JOURNEYS |
| Card penetration % | README_ASSESSMENT | JOURNEYS |
| Days to FM by product | FIX-003 | LIFECYCLE |
| Ghost Conversion Rate | AUDIT_v8 | ATTRIBUTION |
| Product density (2/3/4+ products LTV multiplier) | chunk-2 | JOURNEYS |
| Health Score distribution by stage | chunk-2 | HEALTH SCORE |
| Stage transition rates (L2 to L3 etc.) | chunk-2 | LIFECYCLE |
| M1 retention trend (weekly) | README_ASSESSMENT | OVERVIEW |
| Weekly new users entering L0 (~1,400/week) | lifecycle.md | OVERVIEW |
| CRM actions this week (30-50 target) | crm_playbooks | WEEKLY OPS (NEW) |
| Payback period (7.5mo actual, <60d target) | DELIVERY_SUMMARY | OVERVIEW |
| B2M Holdings component (5 pts) | P0_FIXES_SUMMARY | HEALTH SCORE |
| Fiat deposit FM count | FIX-001 | LIFECYCLE |
| Dormancy fee events today | FIX-002 | LIFECYCLE |
| Finland traffic share (31%, more than Spain 22.66%) | Competitive analysis | OVERVIEW |
| M2 Retention (0.00% actual) | Bit2me 3 CLAUDE.md | OVERVIEW |
| Phone drop-off rate (32%) | CLAUDE.md | OVERVIEW |
