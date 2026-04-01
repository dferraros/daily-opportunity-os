# A/B Tests — Bit2Me LC Reference

*Source: ab-test-backlog-bank.xlsx, segmentos-tests-w08-feb26.xlsx*
*Updated: Feb 25, 2026*

---

## Active Segments (W08 Feb 2026)

| Test | Segment Name | ES Users | A/B Valid | Churn Cluster |
|------|-------------|---------|-----------|---------------|
| T1 | Riesgo con operaciones previas | 5,523 | YES (2,761/variant) | riesgo |
| T2 | Activos sin operar 90 días | 6,681 | YES (3,340/variant) | activos |
| T3 | L1 Depositado (DEPOSITED_ONLY) | 566 | NO (too small) | no_activados |
| T4 | Churn+Balance (planned W10) | 8,444 | YES (4,222/variant) | mixed |

Minimum for A/B significance: 3,100 users (95% confidence, 80% power, per Calculadora_Muestra).

## Segment Schema (segmentos-tests-w08-feb26.xlsx)

Columns per user row:
- `user_id` (UUID, truncated for privacy in export)
- `account_created_date` (DATE)
- `country` (STRING — all ES in these files)
- `verification` (BOOLEAN)
- `has first mon` (BOOLEAN)
- `mon vol last 365 days` (DECIMAL — monetizable volume €)
- `last_mon_mov_group` (STRING — "30 days" / "90 days" / "no mon")
- `has balance (>10€)` (BOOLEAN)
- `balance` (DECIMAL — current balance €)
- `recent login` (BOOLEAN)
- `last_login_group` (STRING — "30 days" / "90 days")
- `churn_cluster` (STRING — "riesgo" / "activos" / "no_activados")

## W08 Learnings (Aprendizajes_W08 sheet)

| Test | Canal | Variante | CTR | Conversiones | Key Learning | Next Action |
|------|-------|----------|-----|-------------|-------------|------------|
| T1 Push | Push | A — "Revisa tu portfolio 💼" | 14.7% | 0 | Portfolio angle > market news | Re-test short version (26 chars) |
| T1 Push | Push | B — "BTC se mueve 📉" | 11.8% | 0 | Market news angle inferior for churn risk | Discard for T1 |
| T1 InApp | InApp | Single — Portfolio control + buy CTA | 14.2% | 4 (influenciadas) | InApp > Push CTR consistently | Scale InApp to all segments |
| T2 Push | Push | A — "MVRV data" | 8.6% | 0 | Technical data doesn't convert | Remove MVRV from messaging |
| T2 Push | Push | B — "BTC at historical minimum" | 13.0% | 4 (0.16%) | **WINNER. Temporal anchor > technical data** | Re-test clean 50/50 |
| T2 InApp | InApp | Single — Market data + rate info | 14.0% | 11 (influenciadas) | InApp very strong | Optimize CTA |
| T3 Push | Push | Single — First trade nudge | 10.8% | 0 | Segment too small (566), insufficient power | Single send only |
| T3 InApp | InApp | Single — DCA tutorial | 9.3% | 0 | Tutorial message = lowest CTR | Simplify to 1 action |

**Key meta-learnings:**
- InApp > Push CTR across all segments (~14% vs ~13%)
- Temporal anchoring ("historical minimum") > technical metrics (MVRV)
- Portfolio angle works for T1 (churn risk); market context works for T2 (dormant active)
- 0 direct conversions in W08 — "influenciadas" only. M1 retention problem is upstream.

## W08 Send Schedule

- T1 (5,523 users): Sent Tue Feb 24, 11:00 CET — utm_campaign=reactivacion_feb26
- T2 (6,681 users): Sent Wed Feb 25, 10:00 CET — utm_campaign=reactivacion_feb26
- T3 (566 users): Single send (no A/B split)

## Planned Tests W09-W12 (from Backlog)

### W09 (current week)
| ID | Priority | Segment | Canal | Hypothesis | N |
|----|----------|---------|-------|-----------|---|
| AB-001 | 🔴 Alta | T2 Activos 90d | Push | Temporal anchor re-test (50/50 clean) | 6,681 |
| AB-002 | 🔴 Alta | T1 Riesgo | Push | Short msg (26 chars) vs long (130 chars) | 5,523 |
| AB-006 | 🔴 Alta | T2 Activos 90d | Push | (additional T2 test) | 6,681 |
| AB-010 | 🔴 Alta | T1 Riesgo | Push | (additional T1 test) | 5,523 |
| AB-016 | 🟡 Media | T1 Riesgo | Push | (medium priority) | 5,523 |
| AB-020 | 🟡 Media | T1 Riesgo | InApp | InApp angle test | 5,523 |
| AB-024 | 🟢 Baja | Churn+Balance | Push | Loss aversion — win-back | 8,444 |
| AB-028 | 🟢 Baja | T1 Riesgo | InApp | (low priority) | 5,523 |
| AB-032 | 🟢 Baja | T1 Riesgo | Push | (low priority) | 5,523 |

### W10
| ID | Priority | Segment | Canal | Note |
|----|----------|---------|-------|------|
| AB-003 | 🔴 Alta | Churn+Balance | Push | First win-back test for churned users |
| AB-004 | 🔴 Alta | T1 Riesgo | InApp | InApp vs Push for risk segment |
| AB-008 | 🔴 Alta | T2 Activos 90d | Push | |
| AB-011 | 🟡 Media | T1 Riesgo | Push | |
| AB-022 | 🟢 Baja | T3 L1 Depositado | Push | Small segment — first trade nudge |

### W11
| ID | Priority | Segment | Canal | Note |
|----|----------|---------|-------|------|
| AB-005 | 🔴 Alta | T3 L1 Depositado | InApp | DEPOSITED_ONLY — activation |
| AB-007 | 🔴 Alta | T1 Riesgo | Push | |
| AB-013 | 🟡 Media | T2 Activos 90d | InApp | |
| AB-015 | 🟡 Media | T3 L1 Depositado | InApp | |
| AB-018 | 🟡 Media | T1 Riesgo | Push+InApp | First combined channel test |

### W12
| ID | Priority | Segment | Canal | Note |
|----|----------|---------|-------|------|
| AB-009 | 🔴 Alta | T2 Activos 90d | InApp | |
| AB-021 | 🟢 Baja | T2 Activos 90d | WhatsApp | First WhatsApp test (low prio) |

## Psychological Triggers in Use

| Trigger | Tests | Best Result |
|---------|-------|------------|
| Temporal Anchor | AB-001, AB-007 | T2 Push B winner (13% CTR) |
| Friction Reduction | AB-002 | Testing W09 |
| Loss Aversion | AB-003, AB-024 | Win-back — testing W09/W10 |
| Portfolio Control | T1 Push A | 14.7% CTR best in W08 |
