# A/B Testing Framework — Bit2Me

Last updated: 2026-03-09

---

## Structure
- Sprint model: 2-week sprints, 9-day decision cycles
- Tool: CleverTap (push + in-app messages)
- Ownership: Daniel = LC + Brokerage tests; Consuelo = ADQ tests; Juan Luis = B2B tests
- Pablo Campos = observer (added to A/B group)
- Patri Gargallo = new team lead for Retención/Fidelización/Reactivación (channel created Feb 24)
- Marta del Olmo = measurement validation (confirm if test is measurable BEFORE building)

---

## W08-W09 Results Summary (Closed, Mar 2026)

### Data Sources
- CleverTap: send counts, open rates, CTR per campaign/variant
- Qlik: transactions, revenue, TAUs per campaign/variant
- Significancia sheet: z-test p-values, Bonferroni-corrected p_adj, MDE analysis

### Critical Finding: Split Imbalance
- 7 of 8 tests in W08-W09 had 86/14 to 90/10 splits (Var A vs Var B)
- With ~546 users in minority arm: MDE required = 193% (impossible to detect real effects)
- **Rule W10+: 50/50 always. No exceptions.**

### Bonferroni Results (8 simultaneous tests, multiply p × 8)
Only 2 tests survive Bonferroni correction at p_adj < 0.05:

| Campaign | Winner | p_adj | Lift |
|----------|--------|-------|------|
| W08-SEN-DOT-HV Var A | "Movimiento en DOT" | 0.029 | +134% CTR vs Var B |
| W09-SEN3-V3-BTC-HV Var A | "Revisa tu portfolio 📈" | <0.001 | +531% rev/TAU vs Var B |

All Smart Holders (C6+C7) tests: NOT significant. T1-Push appeared significant at p=0.032 but becomes p_adj=0.259 after correction — false positive.

### Winning Pattern: Endowment Effect Frame
"Revisa tu portfolio / Movimiento en [token]" beats "BTC: $66K / sube X%" consistently:
- 3 waves: W08, W09, W09-V3
- 2 assets: DOT, BTC
- Mechanism: Endowment Effect (what you already own) vs Price Data (market info)

### High Value (C9) vs Smart Holders (C6+C7) Performance Gap

| Metric | C9 HV | C6+C7 Smart Holders |
|--------|-------|---------------------|
| Open rate | 58-59% | 37-42% |
| CTR | 6-8% | 2-5% |
| Revenue/TAU | €101-246 | €7-16 |

### Smart Holders Diagnosis
E1-Riesgo (Mar 2, 2026): 3,935 sent, 36.87% open, 8.77% CTR → only 2 Qlik transactions, €5.89 revenue.
Conclusion: C6+C7 has a POST-CLICK UX friction problem, not a copy problem. Users click but don't transact in-app. Do NOT run more copy tests on this segment without diagnosing the funnel drop-off first.

### InApp Attribution Gap
W08 InApp T2 Activos: 13.93% CTR, 78 CT-influenced conversions → €0 Qlik attribution.
Root cause: missing UTM parameters on deeplinks. Revenue was real but invisible.
Fix: append `?utm_source=clevertap&utm_medium=inapp&utm_campaign=[CAMPAIGN_ID]` to all InApp deeplinks.

### Hidden Gem: CAMBIO24H_V2 Var B (W08-SEN2-BTC-SH)
- 10 transactions, €729.92 revenue, €91.24/TAU
- Minority arm (split imbalance = unreliable), but highest TAU revenue in full W08-W09 dataset
- Worth investigating before W11 design

---

## W10 Active Campaigns (launched Mar 2026)

### E1-Riesgo (launched Mar 2, 2026)
- Segment: C6+C7 Smart Holders
- Copy: "Revisa tu cartera ANTES DE QUE SEA TARDE" (FOMO + Endowment hybrid — design flaw)
- Results: 3,935 sent, 1,451 opens (36.87%), 345 clicks (8.77%), 2 transactions, €5.89 revenue
- Status: CLOSED — confirms UX friction diagnosis, no further copy tests on this segment

### W10 Replication Campaigns (status: 2026-03-09)
Files: `W10_Launches_Today_260303.md` (execution brief), `W10_Replication_Logic_260303.md` (clear logic), `W10_AB_Test_Briefs_Formal_260303.md`

#### REP-2 / L1 — Revisa tu portfolio (C9 HV) — STATUS: ACTIVE ✅
- Hypothesis: Direct replication of V3-BTC-HV Var A (p<0.001) → establishes it as control for all future HV tests
- Design: copy invariant, C9 no trans last 30d, 50/50 split
- Campaign: `W10_SEN_BTC_HV_260303`
- Deep link: `bit2me://portfolio?utm_source=clevertap&utm_medium=push&utm_campaign=PUSH_SEN_BTC_HV_260303`
- Segment: C9, sin tx últimos 30d; C8 excluida
- Send: Tue Mar 10 (pending Diego written approval → Katy config)
- Decision: 17 March
- **Pre-send checklist**: Segmento C9 ✓ | Split 50/50 ✓ | Deeplink UTM ✓ | C8 excluida ✓

#### REP-1 / L2 — Movimiento en [TOKEN] (C9 HV) — STATUS: BLOCKED ⛔
- Hypothesis: Extending DOT-HV Endowment frame to top-5 HV portfolio tokens → CTR ≥ 6%, revenue/TAU ≥ €100
- Design: single send per token, C9 holders of that token only, trigger = 24h move ≥ +8%
- **BLOCKER**: Álvaro token-holder filter in BigQuery (table: user_id + primary_token, C9 only). ETA: Thu Mar 12
- Stagger with REP-2: 48h minimum or mutual exclusion in CleverTap
- Decision: 17 March

#### REP-3 / L3 — InApp T2 Activos + UTM fix (C8 Activos 90d) — STATUS: PENDING UTM CONFIRM ⏳
- Hypothesis: With UTM fix, replication reveals real revenue previously invisible (W08: €0 despite 13.93% CTR)
- Design: session trigger, C8, 7d window, UTM mandatory on all deeplinks
- **BLOCKER**: Katy UTM staging test confirmation (Mar 7 target — confirm by Mar 10)
- Attribution check: 10 March | Decision: 10 March

---

## Replication Rules (W10+)
A result qualifies for replication ONLY if:
1. p_bonf < 0.05 (Bonferroni corrected)
2. Pattern confirmed in ≥2 distinct waves

Without both conditions: don't replicate, run new test.

---

## Design Rules (W10+)
- Split: 50/50 always. 86/14 makes tests underpowered.
- UTM: mandatory on ALL deeplinks (push and in-app)
- Control holdout: 10% minimum for incrementality proof
- Conversion window: 14 days for dormant/Smart Holder segments
- Diego approval: ALL CRM messages before send
- Staging test: deeplinks and UTM before CleverTap activation

---

## Checkpoint Protocol (W10)
| Date | Check |
|------|-------|
| 7 March | L3 CTR check (is InApp firing?) |
| 10 March | L3 Qlik attribution (is UTM working?) |
| 17 March | L1 + L2 + L3 final read |

---

## Critical Rules (unchanged)
- **C8 suppression**: ALWAYS exclude from mass tests
  - C8 = whale cluster (90.91% of Loan revenue)
  - Process: Juan Fornell exports CSV → Katy uploads to CleverTap
- **Legal brief gate**: ALL CRM messages must pass Diego Barreira review before launch
  - URL: https://docs.google.com/document/d/1k8IjId5uxtJfAWwyqhkD9AalQLoc-1DhQNJ4NjWwROk/edit?tab=t.0
- **Marta validation gate**: Before building any test, confirm measurement is possible
  - transaction_api: CONFIRMED measurable for Brokerage
- Deep links:
  - appbit2me://bit2me.com/wallet
  - appbit2me://bit2me.com/crypto-currency-price-list
  - Confluence: https://bit2me.atlassian.net/wiki/spaces/MAR/pages/2881585168/Deeplinks+y+Dynamic+Links+Growth

---

## Review Schedule
- Daniel + Juan Fornell: Tuesdays (Katy starts at 12h, so afternoon works)
- Katy's schedule: available from 12h

---

## Data Pipeline
- Tracker: `AB_Testing_Tracker_Bit2Me_v7.xlsx` (4 sheets: Pruebas, Qlik, CleverTap, Significancia)
- Qlik sheet: revenue/TAU per variant
- CleverTap sheet: sends, opens, CTR per variant
- Significancia sheet: z-test p-values, Bonferroni correction, MDE, split analysis
