# Project: Lifecycle Intelligence Dashboard (bit2me-lifecycle-intel)

**Status:** v3 COMPLETE + TAGGED ✅ — Messari × Binance Growth redesign
**Last Updated:** 2026-03-06
**Path:** `C:\Users\ferra\OneDrive\Desktop\bit2me-lifecycle-intel\`
**URL:** http://localhost:8000 (uvicorn, port 8000)
**STATE.md:** `bit2me-lifecycle-intel/STATE.md` (detailed history here)

---

## What It Is

FastAPI + SQLite + Chart.js dashboard for Bit2Me Lifecycle Intelligence.
16 tabs covering the full LC-OS framework: Executive, Attribution, Funnel, Lifecycle, Retention, Cohorts, Revenue, Reactivation, Products, Trading, Balance, A/B Testing, Segments, Health, Market, Operational.

Built by Claude (Bit2grow AI agent) for Daniel Ferraro. Used for internal analysis + Council presentations.

---

## Current Version: v2

- **16 tabs**, **50+ API routes**, **150+ metrics**, **34+ new visualizations**
- Last commit: `36e1eb2` — fix(reactivation): add missing /dormant-matrix endpoint + smoke test pass
- All v1 functionality preserved (zero deletions)
- Market Context tab: LIVE data from CoinGecko API (BTC price, Fear & Greed, 30d chart)

---

## How to Run

```bash
# From the project directory (Windows):
cd C:\Users\ferra\OneDrive\Desktop\bit2me-lifecycle-intel
uvicorn app.main:app --reload --port 8000

# Or kill stale uvicorn first if needed:
taskkill /F /IM uvicorn.exe
uvicorn app.main:app --reload --port 8000
```

⚠️ **Known gotcha**: Stale uvicorn processes from previous sessions run OLD code. Always kill + restart before testing.

---

## Complete API Endpoint Map (20 routes — from /openapi.json)

All confirmed 200 as of 2026-03-05 smoke test:

```
GET  /api/health
GET  /api/v1/executive/summary          ← NOT /executive/overview
GET  /api/v1/executive/ratios
GET  /api/v1/attribution/channels       ← NOT /acquisition/overview
GET  /api/v1/funnel/activation
GET  /api/v1/lifecycle/stages           ← NOT /lifecycle/overview
GET  /api/v1/retention/overview
GET  /api/v1/revenue/breakdown          ← NOT /revenue/overview
GET  /api/v1/reactivation/overview
GET  /api/v1/reactivation/dormant-matrix  ← added 2026-03-05 fix
GET  /api/v1/products/adoption          ← NOT /products/overview
GET  /api/v1/trading/overview
GET  /api/v1/balance/overview
GET  /api/v1/abtesting/dashboard        ← NOT /experimentation/overview
GET  /api/v1/segments/overview
GET  /api/v1/health/explorer            ← NOT /health-score/overview
GET  /api/v1/market/context             ← NOT /market/overview
GET  /api/v1/operational/health         ← NOT /operations/overview
GET  /api/v1/cohorts/analysis
GET  /api/v1/agent/anomalies
```

**Rule:** Always fetch `/openapi.json` to get canonical route names. Do NOT guess paths.

---

## Tab Navigation (data-tab attribute map)

The dashboard uses `data-tab` attributes on sidebar buttons. JS navigation is most reliable:

```javascript
document.querySelector('[data-tab="X"]').click()
```

| data-tab | Tab Title | Status |
|----------|-----------|--------|
| executive | Executive Summary | ✅ active |
| attribution | Channels & Attribution | ✅ active |
| funnel | Activation Funnel | ✅ active |
| activation | Activation Economics | ⏳ SOON (disabled) |
| lifecycle | Stage Analysis | ✅ active |
| retention | Retention & Churn | ✅ active |
| cohorts | Cohort Analysis | ✅ active |
| revenue | Revenue Engine | ✅ active |
| reactivation | Dormant & FOMO | ✅ active |
| products | Cross-Sell & Density | ✅ active |
| spacecenter | Space Center | ⏳ SOON (disabled) |
| trading | Volume & Trading | ✅ active |
| balance | AUC & Balances | ✅ active |
| abtesting | A/B Testing Machine | ✅ active |
| segments | Segment Intelligence | ✅ active |
| health | Health Score Explorer | ✅ active |
| market | Market Context | ✅ active (LIVE data) |
| operational | Operational Health | ✅ active |

---

## Git Usage (Windows — Critical Pattern)

This repo is on Windows OneDrive path. Git from bash uses Windows git.exe:

```bash
# Correct (Windows path with forward slashes):
git.exe -C 'C:/Users/ferra/OneDrive/Desktop/bit2me-lifecycle-intel' status
git.exe -C 'C:/Users/ferra/OneDrive/Desktop/bit2me-lifecycle-intel' add app/routers/reactivation.py STATE.md
git.exe -C 'C:/Users/ferra/OneDrive/Desktop/bit2me-lifecycle-intel' commit -m "fix(...): description"

# WRONG (wslpath not available in this environment):
git -C "$(wslpath 'C:\Users\...')"   ← fails
```

---

## Smoke Test Results (2026-03-05) — ALL PASS

### API: 20/20 PASS
All routes confirmed via curl against /openapi.json routes.

### Visual Tabs: 16/16 PASS
| Tab | Key Observation |
|-----|----------------|
| executive | Critical alerts, 6 KPI cards, Dormant Wealth €19.5M |
| attribution | 93% ghost conv rate card, 4 chart areas |
| funnel | 6 KPIs, Phone Drop-Off 100% highlighted red |
| lifecycle | FULL DATA — all 13 stages, transitions table |
| retention | CRITICAL M1 alert, 6 KPIs, Gap bar, Waterfall |
| cohorts | 5 KPIs, 4 chart areas |
| revenue | ARPU benchmarks (€32 industry / €45 Coinbase) |
| reactivation | 9 KPIs, dormant-matrix fix confirmed working |
| products | 6 penetration KPIs, radar chart renders |
| trading | 14 KPIs, Buy/Sell 60%/40%, fee rate 1.5% |
| balance | 7 KPIs, Dormant AUC flagged |
| abtesting | 10 KPIs, velocity gauge, Bonferroni α=0.05 |
| segments | "0 of 37" active segments (correct count) |
| health | 3 score bands, AT_RISK highlighted |
| market | LIVE DATA: BTC $71,570, F&G 22, 30d chart |
| operational | Phone Collection Rate flagged, Last Upload: Never |

### Console: 0 app errors
(2 extension-level errors from accessibility tree tool — not app code)

---

## Architecture

```
bit2me-lifecycle-intel/
├── app/
│   ├── main.py            # FastAPI app, static file mount
│   ├── database.py        # SQLite get_db()
│   ├── config.py          # STAGE_COLORS and constants
│   └── routers/           # 1 router file per tab
│       ├── executive.py
│       ├── attribution.py
│       ├── funnel.py
│       ├── lifecycle.py
│       ├── retention.py
│       ├── cohorts.py
│       ├── revenue.py
│       ├── reactivation.py  ← dormant-matrix endpoint added 2026-03-05
│       ├── products.py
│       ├── trading.py
│       ├── balance.py
│       ├── abtesting.py
│       ├── segments.py
│       ├── health.py
│       ├── market.py
│       ├── operational.py
│       └── agent.py
├── static/
│   ├── index.html         # Single-page app, 16 tabs
│   ├── css/               # Sidebar + component styles
│   └── js/
│       ├── main.js        # Tab router
│       ├── sidebar.js     # Navigation
│       └── *-enhance.js   # Per-tab Chart.js code (P1 enhancements)
└── data/
    └── bit2me_lifecycle.db  # SQLite database (simulated data)
```

**Key design principles:**
- Left sidebar (240px, collapsible to 64px) with Bit2grow agent chat panel
- Zero deletions: all v1 functionality preserved
- ACAR framework: Acquisition → Conversion → Activation → Retention

---

## Known Data Status (2026-03-05)

- **All data is SIMULATED** (SQLite synthetic data)
- **BigQuery connection**: pending Álvaro delivering V0a (~Mar 10)
- **Market Context**: LIVE data from CoinGecko API (exception to simulated)
- **37 segments**: "0 of 37 active" = correct (no real data yet)

---

## Bug Fixed (2026-03-05)

**Root cause**: `reactivation-enhance.js` called `/api/v1/reactivation/dormant-matrix` but Python router only had `/overview`. P1 Batch B subagent added JS enhancement without adding the route.

**Also found**: Stale uvicorn process (PID 13328) from previous session was running pre-P1 code, causing `/executive/ratios` to appear as 404.

**Fixes**:
1. Added `@router.get("/dormant-matrix")` to `app/routers/reactivation.py`
2. Kill + restart uvicorn

---

## Next Steps (v3 / Wave 3)

1. **BigQuery connection**: When Álvaro delivers V0a (~Mar 10) — replace SQLite with real data
2. **Wave 3 new tabs**: Activation Economics + Space Center (currently SOON-disabled)
3. **Council enrichment**: B2M 7d volume/ops/ticket, market-B2M correlation, macro calendar, P&L vs plan, LTV by product — when Daniel sends data
4. **UI redesign (Tier 1)**: Use `frontend-design` skill — Daniel requested
5. **P2 backlog (20 items)**: Nested doughnut, small multiples funnels, days-to-churn survival histogram, trader behavioral bubble chart, Test pipeline Kanban, Bayesian posterior density, Multi-touch Sankey, Health violin plots, Segment recommendation cards

---

## Commit History Summary

| Commit | Description |
|--------|-------------|
| `36e1eb2` | fix(reactivation): dormant-matrix + smoke test (2026-03-05) |
| `a668fba` | docs: visual analysis + design plans |
| `09eb8f7` | P1 HTML containers + STATE update |
| `f6e9641` | P1 Batch C: products+AB+attrib+market+health+seg+ops |
| `f90bec8` | P1 Batch B: retention+react+trading+balance |
| `79e3377` | P1 Batch A: exec+lifecycle+funnel+revenue |
| `4c17886` | Wave 2 Batch B+C |
| `3fb9c94` | Wave 2 Batch A |
| `648c970` | Bit2grow FAB button |
| `817fbf5` | P0 visual improvements |
| `60c2ae1` | Fix: 8 P0 data bugs |
| `563eb75` | Wave 1-03: sidebar JS navigation |
