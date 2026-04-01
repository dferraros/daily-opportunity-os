# BIT2ME MASTER ARCHITECTURE — MEMORY SUMMARY
**Produced:** 2026-03-06 | **Full doc:** Desktop/BIT2ME_MASTER_ARCHITECTURE.md

---

## KEY DECISIONS

### v3 Tag
- `v3.0.0` tagged on commit `62268b1` = Messari × Binance Growth redesign
- v2 = dark theme + 16 tabs | v3 = compact metric-strip, alert-strip, section-headers
- BigQuery swap (SQLite → BQ) will be v4 (March 10-31)

### Metrics Framework (NOT 250 random — 6 strategic domains)
| Domain | Count | Priority | Dashboard Status |
|--------|-------|---------|-----------------|
| Lifecycle Core (13 stages × 6) | 78 | P0 | Partial |
| Journey Machine (9 journeys × 9) | 81 | P0 | MISSING |
| Gaussian Distributions (6 × 10) | 60 | P1 | MISSING |
| Council Intelligence | 30 | P1 | Partial |
| Product Layer (6×6×4) | 144 | P1 | MISSING |
| Blockchain + Market | 30 | P2 | Partial |
| **TOTAL** | **717** | — | **~220 tracked** |

### New Tabs Needed (v4+)
1. **Journeys Performance** (P0) — 9 journeys × metrics heat map
2. **Distribution Lab** (P0) — 6 Gaussian charts (health, days-since-tx, balance, fomo, revenue pareto, time-in-stage)
3. **Council Prep** (P1) — auto-populate Pablo's weekly slide data
4. **Space Center** (P2) — tier distribution + near-level-up
5. **Blockchain & B2M** (P2) — BitQuery integration

### APIs to Integrate
| API | Cost | Priority | Use |
|-----|------|---------|-----|
| CoinGecko | $0-$129/mo | P0 | Already used by FOMO agent |
| Alternative.me | Free | P0 | Fear & Greed |
| CleverTap API | Included | P0 | Journey performance |
| BitQuery GraphQL | $0-$149/mo | P1 | B2M on-chain, DEX data |
| Messari | $24/mo | P2 | Institutional data |
| CoinGlass | Free | P2 | Derivatives |

### Gaussian Distributions — Key Insight
The "Gauss" request = distribution analysis revealing intervention zones:
- Health Score per stage → overlaid bell curves (AT_RISK tail = score 25-45)
- Days-since-FM → cliff at Day 60-90 = where AT_RISK journey must catch users
- Balance → log-normal → identifies Loan (>€100) and Earn (>€50) eligibility tiers
- Revenue per user → power law → top 10% = 60-70% of revenue (protect POWER_USER)

### Journey Landscape (9 Designed)
| Journey | Stage | Target | Est. Revenue/yr |
|---------|-------|--------|----------------|
| Activación | FIRST_MONETIZATION | M1 retention 0.12% → 5% | — |
| Earn/DCA | ACTIVE | DCA setup >12% | €80-100K |
| AT_RISK Prevention | AT_RISK | >20% stage prevention | €315K |
| Loan | ACTIVE/DORMANT | Loan activation | — |
| Reactivación | DORMANT_W_BALANCE | Reactivation >5% | €149K (ES test) |
| Referidos | Post-FM/DCA | K coefficient | — |
| Card | Approved, not used | First transaction | — |
| PRO | 10+ trades | First Pro trade | High (LTV €511) |
| Space Center | Near level-up | Tier advance | — |

### Strategic Insights (Updated)
1. M1 retention fix = Activación journey + DCA Day 7 pitch
2. €19.5M dormant AUC → R-HIGH first → €840K/year potential
3. DCA = retention superpower (85% vs 30% 12M retention)
4. Card = retention anchor (4× retention), NOT revenue (EU interchange cap 0.2%)
5. Space Center near-level-up = cheapest retention intervention
6. Ghost Conversions: 93% paid revenue = existing users (ROAS crisis, need iROAS)

### BitQuery — B2M Contract
- Need to identify B2M contract address on BSC (ask David Sales)
- Key queries: holder count, transfer volume, DEX liquidity, top holders
- Route: `/api/blockchain/b2m` → BigQuery `b2m_on_chain_daily` table

---

## IMPLEMENTATION ORDER

1. **March 10:** BigQuery V0a deploys → swap SQLite in backend
2. **April 1-14:** APIs (CoinGecko, CleverTap, BitQuery)
3. **April 15-30:** New tabs (Journeys, Distribution Lab, Council Prep)
4. **May:** Visualization upgrades (Sankey, Forest Plot, Cohort Heatmap)
