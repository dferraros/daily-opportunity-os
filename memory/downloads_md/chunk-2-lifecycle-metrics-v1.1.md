# CHUNK 2: Modelo de Ciclo de Vida + Catálogo de Métricas
## Growth Operating System — Bit2Me

**Version:** 1.1 — Chunk 2 of 4 (reviewed + corrected)
**Date:** 2026-02-19
**Author:** Head of Growth (Daniel)
**Reviewed by:** Growth OS co-pilot
**Status:** Draft for validation by Daniel + Salvia
**Dependencies:** Chunk 1 v1.1 (Definitions + User Model) validated

### v1.1 Changes (from v1.0)
- Fixed POWER_USER threshold instability: p75 revenue threshold now evaluated monthly (not daily) to prevent users flipping between POWER_USER and ACTIVE as the percentile shifts.
- Fixed REACTIVATED stage dependency: added state_transition_history table spec and explicit join for previous_status lookup. Without this, the REACTIVATED classifier can't run.
- Fixed stage count: header now says "11 Stages" (was "10 Stages"). Added EXCLUDED as Stage 0 for clarity.
- Added Card-specific metrics (CD1-CD5) to metrics catalog. Card is the biggest product gap (0.26% vs 42-48% industry) but had zero dedicated metrics.
- Added AUC metrics (AUC1-AUC4) for Assets Under Custody. AUC drives recurring revenue and was missing entirely.
- Added time horizon to cross-sell probability matrix (now specifies "within 12 months of Product A activation").
- Added DCA data availability flag as P0 dependency. DCA metrics are defined but the underlying "recurring orders table" is unconfirmed.
- Restructured revenue forecast (4.4) from single range to conditional forecast: separate BULL/NEUTRAL/BEAR projections. €1.3M-€2.9M range was too wide to be actionable.
- Reconciled market modifier thresholds between Chunk 1 and Chunk 2 (was using different BTC return cutoffs).
- Added statistical significance requirements to incrementality section (4.5): minimum 8-week holdout, sample size guidance, minimum detectable effect.
- Added Portugal steady-state tracking to GTM section (PT is past launch phase, should track convergence metrics).
- Added explicit note on ACTIVE + POWER_USER population non-overlap to prevent double-counting.
- Added NRR vs GRR relationship explanation to Council Metric 4.

---

# PHASE 3: LIFECYCLE MODEL (The Architecture)

## Integration with Salvia's Existing Analysis

Salvia's analysis (Q1-26 LC, "Análisis base de usuarios 1.8M") provides the current population baseline. Key findings integrated below:

| Salvia's Segmentation | Population | Our Lifecycle Mapping |
|----------------------|-----------|----------------------|
| Total registered | 1,858,000 | Full base |
| No válidos (Banned + Disabled) | ~600K (545K banned + 45K disabled) | EXCLUDED from lifecycle. Not addressable. |
| Activos (Enabled + login 365d) | ~300K | Spans ACTIVE, AT_RISK, FIRST_MONETIZATION, KYC_COMPLETE, DEPOSITED_ONLY |
| — Con balance | 85K | Subset of ACTIVE + AT_RISK + DORMANT_WITH_BALANCE |
| — Sin balance | 215K | Subset of ACTIVE (behavioral only) + KYC_COMPLETE + REGISTERED_ONLY who logged in |
| Dormidos (Enabled + no login 365d) | ~968K | DORMANT_ZERO + DORMANT_WITH_BALANCE + CHURNED |
| — Con balance | 14K | DORMANT_WITH_BALANCE (long-dormant, high reactivation value) |
| — Sin balance | 953K | CHURNED (vast majority) + DORMANT_ZERO |
| Never completed account (60.6% of 1.8M) | ~1.1M | REGISTERED_ONLY (global, not just Spain) |

**What is NEW vs Salvia's work:**
- Salvia segments by login (365d) + balance (yes/no). This framework adds: monetizable action, revenue generation, product-level activity, market condition, and multi-product density.
- Salvia's requested filters (login by 1/3/6/12 months, "ha operado" yes/no, B2B/B2C) are answered by this lifecycle model. Each filter maps to a specific lifecycle stage or dimension.
- Salvia's Brokerage clusters (C0-C9) remain intact. This framework overlays global lifecycle on top.

**What EXTENDS Salvia's work:**
- AT_RISK stage (did not exist)
- DEPOSITED_ONLY split from KYC_COMPLETE
- Per-product lifecycle overlays
- Archetype classification (from Chunk 1)
- Revenue-based activity definition (MMU vs login-based)

---

## 3.1 Global User Lifecycle — State Machine

### Design Principles

1. **Non-linear.** Users regress, skip, reactivate. This is a state machine, not a funnel.
2. **Revenue-aligned.** Each stage maps to a revenue behavior. Pablo reads revenue, not engagement.
3. **SQL-classifiable.** Computed daily from data. No manual tagging.
4. **Product-agnostic** at global level. Per-product overlays sit on top.
5. **Market-cycle aware.** Churn context flag from Chunk 1 (Section 1.4) applied to every dormancy/churn transition.

### The 11 Stages (+1 EXCLUDED)

Stage 0 (EXCLUDED) filters out ~600K banned + disabled accounts before any classification. The remaining 11 stages form the state machine.

```
                                    ┌─────────────┐
                              ┌────▶│  POWER_USER  │◀─── (2+ products, high revenue)
                              │     └──────┬──────┘
                              │            │ regression
┌──────────┐   ┌───────────┐  │  ┌─────────▼───────┐   ┌──────────┐
│REGISTERED │──▶│KYC_COMPLETE│──▶│ DEPOSITED_ │──▶│  FIRST_   │
│  _ONLY    │   │           │  │  │   ONLY    │   │MONETIZATION│
└──────────┘   └───────────┘  │  └───────────┘   └─────┬──────┘
                              │                         │
                              │                   ┌─────▼──────┐
                              └───────────────────│   ACTIVE    │
                                                  └──┬───┬─────┘
                                                     │   │
                                          ┌──────────▼┐ ┌▼──────────────┐
                                          │  AT_RISK  │ │REACTIVATED    │
                                          └─────┬─────┘ │(temp, 30d)    │
                                                │       └───────────────┘
                                     ┌──────────▼──────────┐       ▲
                                     │                     │       │
                              ┌──────▼──────┐  ┌──────────▼───┐   │
                              │DORMANT_WITH_ │  │DORMANT_ZERO  │   │
                              │  BALANCE     │──┘              │───┘
                              └──────┬───────┘  └──────┬───────┘
                                     │                 │
                                     └────────┬────────┘
                                              │
                                       ┌──────▼──────┐
                                       │   CHURNED    │
                                       └─────────────┘
```

### Stage Specifications

---

#### Stage 1: REGISTERED_ONLY (Solo Registrado)

| Field | Value |
|-------|-------|
| **Definition** | Account created, KYC not approved, no trades, no deposits |
| **Entry criteria** | User completes registration (email + password) |
| **Exit criteria (forward)** | KYC approved → KYC_COMPLETE |
| **Exit criteria (skip)** | Impossible to skip to FM without KYC (regulatory gate) |
| **Regression criteria** | N/A (entry stage) |
| **Population (Global)** | ~1.1M (60.6% never completed account per Salvia's data) |
| **Population (Spain)** | ~213,863 (49.1% of Spain base) |
| **Revenue contribution** | €0 |
| **Target interventions** | KYC completion nudge sequences: email D+1, push D+3, SMS D+7. Address phone verification drop (32% ES, 53% global sin ES per Salvia). Reduce friction at phone step. |
| **Key metrics** | Reg→KYC conversion rate, time-to-KYC, drop-off step, drop-off by geo |
| **Salvia sync** | Maps to her "nunca completaron cuenta" segment. Her requested filter "has even been verified: False" identifies this group. |

**Onboarding Drop-off Data (from Salvia's analysis, 2025 registrations):**

| Country | Registrations | Verified | First Purchase | Conv % | Did Not Complete |
|---------|-------------|----------|---------------|--------|-----------------|
| ES | 73,541 | 44,262 | 31,749 | 45% | 29,279 |
| DE | 2,130 | 966 | 527 | 25% | 1,164 |
| PT | 5,248 | 2,056 | 1,066 | 20% | 3,192 |
| IT | 4,787 | 2,185 | 1,068 | 22% | 2,602 |
| FR | 2,704 | 1,211 | 584 | 22% | 1,493 |

**Drop-off by step (Salvia's data):**

| Geo | % Drop at Email | % Drop at Phone |
|-----|----------------|-----------------|
| Global sin ES | 13% | 53% |
| ES | 6% | 32% |
| PT | 12% | 28% |

Phone verification is the single biggest conversion killer outside Spain. P0 optimization target.

---

#### Stage 2: KYC_COMPLETE (Verificado Sin Actividad)

| Field | Value |
|-------|-------|
| **Definition** | KYC approved, no deposits, no FM event |
| **Entry criteria** | KYC approved (all steps: email, phone, documentation, verification) |
| **Exit criteria (forward)** | First deposit → DEPOSITED_ONLY. Or first FM event → FIRST_MONETIZATION (skip deposit tracking if trade happens via crypto deposit + immediate trade). |
| **Regression criteria** | N/A (can't "un-verify"). Can become stale (KYC_COMPLETE for >90 days without action → effectively abandoned, but still KYC_COMPLETE in status). |
| **Population (Spain)** | ~29,010 (6.7%) |
| **Revenue contribution** | €0 |
| **Target interventions** | Deposit incentive (€X bonus for first deposit within 7d). Show "next step" clearly in app. Address deposit friction (payment method availability, processing time). |
| **Key metrics** | KYC→Deposit rate, KYC→FM rate, time-to-deposit, deposit method used |
| **Salvia sync** | Subset of her "Activos sin balance" (215K) who have verified but not deposited. NEW split not in Salvia's current model. |

---

#### Stage 3: DEPOSITED_ONLY (Depósito Sin Compra)

| Field | Value |
|-------|-------|
| **Definition** | Has deposited fiat or crypto, KYC approved, but no FM event |
| **Entry criteria** | First deposit completed (fiat or crypto) while fm_date IS NULL |
| **Exit criteria (forward)** | FM event → FIRST_MONETIZATION |
| **Regression criteria** | Withdrawal of full deposit → KYC_COMPLETE (debatable; keep as DEPOSITED_ONLY with balance=0 flag for 30 days, then revert) |
| **Population** | REQUIRES DATA. Estimated: 5,000-15,000 globally. Maps to P0 computed event "Deposit_No_Purchase" and "Idle_EUR". |
| **Revenue contribution** | €0 direct. Float revenue on EUR deposits (minimal). |
| **Target interventions** | Highest-ROI nudge in the entire lifecycle. User has money on platform and hasn't acted. Push within 48h: "Your €X is ready. Here's how to make your first purchase." P0 event triggers. |
| **Key metrics** | Deposit→FM rate, time deposit-to-FM, idle EUR amount, deposit method |
| **Salvia sync** | NEW stage. Did not exist in Salvia's model. She requested "ha operado si/no" filter; this stage is the "deposited but ha operado = no" population. |

---

#### Stage 4: FIRST_MONETIZATION (Primera Monetización)

| Field | Value |
|-------|-------|
| **Definition** | User had FM event (per Chunk 1 EMA definition) within the last 30 days |
| **Entry criteria** | FM event timestamp is within current_date minus 30 days |
| **Exit criteria (forward)** | Day 31 post-FM AND is_economically_active = TRUE → ACTIVE. Day 31 post-FM AND second action taken → ACTIVE. |
| **Exit criteria (backward)** | Day 31 post-FM AND is_economically_active = FALSE AND no second action → AT_RISK |
| **Population (Spain)** | Part of L2 (~36,866 in L2, but L2 includes users with FM > 30 days ago who haven't retained) |
| **Revenue contribution** | FM Revenue (Chunk 1, Section 1.5). Currently €486K all-time FM vs €11.6M LC. |
| **Target interventions** | "Second action" campaigns. This is the activation window. Goal: get user to take second monetizable action within 14 days. DCA setup nudge. Earn introduction. Cross-sell based on first product. P0 event "First_No_Second" fires here. |
| **Key metrics** | FM→Second action rate (14d), FM→ACTIVE conversion rate (30d), time-to-second-action, second product adoption rate |
| **Salvia sync** | Refines L2. L2 was "first monetization, no retention" without time boundary. This adds the 30-day window. |

---

#### Stage 5: ACTIVE (Activo)

| Field | Value |
|-------|-------|
| **Definition** | Per Chunk 1, Section 1.3: is_economically_active = TRUE AND days_since_fm > 30. Includes both Core Active (behavioral + economic) and Silent Revenue (economic only). |
| **Entry criteria** | From FIRST_MONETIZATION after 30 days with continued economic activity. From REACTIVATED after 30 days of sustained activity. From AT_RISK if activity recovers (health_score > 50 AND new monetizable action). |
| **Exit criteria (forward)** | products_used >= 2 AND (monthly_revenue > p75_revenue OR Space_Center_tier >= 3) → POWER_USER |
| **Exit criteria (backward)** | activity_decline_4w >= 50% OR health_score < 30 OR DCA cancelled → AT_RISK |
| **Population (Spain)** | ~50,416 (11.6%). This is the L3 equivalent. MMU may be higher (see Chunk 1 Section 1.3). |
| **Revenue contribution** | Primary revenue engine. Estimated 70-80% of total LC revenue. |
| **Target interventions** | Cross-sell to increase product density. DCA setup for manual traders. Earn suggestion when balance sits idle. Space Center tier promotion. Card activation nudge. |
| **Key metrics** | MMU, ARPMMU, product density, revenue per user, cross-sell conversion rate, DCA penetration |
| **Salvia sync** | Extends L3. Adds multi-product economic activity (not Brokerage-only). Salvia's Brokerage clusters C6/C7 (Smart Holders), C8 (High Value) sit within this stage. |

**Sub-populations within ACTIVE (diagnostic, not separate stages):**

| Sub-population | Definition | Approx Size | Action |
|---------------|-----------|-------------|--------|
| Core Active | is_economically_active AND is_behaviorally_active | REQUIRES DATA | Standard lifecycle. Cross-sell. |
| Silent Revenue | is_economically_active AND NOT is_behaviorally_active | REQUIRES DATA | Do NOT disturb. Monitor balance. Only contact for product improvements or rate changes. |
| Single-Product Active | is_economically_active AND products_used = 1 | REQUIRES DATA | Priority cross-sell target. 1-product retention = 20-30%. |
| Multi-Product Active | is_economically_active AND products_used >= 2 | REQUIRES DATA | Retention already strong. Nurture toward POWER_USER. |

---

#### Stage 6: POWER_USER (Usuario Potente)

| Field | Value |
|-------|-------|
| **Definition** | Active user with 2+ products AND (monthly revenue in top 25th percentile OR Space Center tier >= 3). Bit2Me's most valuable users. |
| **Entry criteria** | products_used >= 2 AND (monthly_revenue_eur > p75_threshold OR space_center_tier >= 3) |
| **Exit criteria (backward)** | products_used drops to 1 OR revenue drops below p50 for 2 consecutive months → ACTIVE. Activity decline → AT_RISK. |
| **Population** | REQUIRES DATA. Estimated: 5,000-10,000 (top 10-20% of ACTIVE). Includes most Whales. |
| **Revenue contribution** | Estimated 40-60% of total revenue from < 20% of active users. Power law. |
| **Target interventions** | VIP treatment. Early access to features. Feedback solicitation. Referral program emphasis. OTC introduction for qualifying users. Personal account manager for top tier. |
| **Key metrics** | Revenue per POWER_USER, products per POWER_USER, Space Center tier distribution, referral rate, NPS |
| **Salvia sync** | NEW stage. Maps to Brokerage C8 (High Value, 5,393 users) plus multi-product high-revenue users from other clusters. Adds cross-product dimension Salvia's Brokerage-only clustering misses. |

```sql
-- POWER_USER classification
-- CRITICAL: revenue_p75_threshold is calculated MONTHLY (on the 1st of each month)
-- and stored as a static value for the entire month. This prevents users from
-- flipping between POWER_USER and ACTIVE as the percentile shifts daily due to
-- market volatility. The threshold is stored in a config table:
--   monthly_thresholds (month DATE, metric STRING, value FLOAT)

WHEN is_economically_active = TRUE
     AND products_with_fm >= 2
     AND (
         monthly_revenue_eur > (SELECT value FROM monthly_thresholds
                                WHERE month = DATE_TRUNC(CURRENT_DATE(), MONTH)
                                AND metric = 'power_user_revenue_p75')
         OR space_center_tier >= 3
     )
THEN 'POWER_USER'
```

**Threshold stability rule:** Once a user is classified as POWER_USER, they retain the status for at least 30 days even if revenue dips below p75. This prevents monthly oscillation. Demotion to ACTIVE requires revenue below p50 for 2 consecutive months (as stated in exit criteria above). This asymmetry is intentional: it's easier to promote than to demote.

**Hard Design Decision: Why POWER_USER is a stage, not just a flag.**
A flag would work for analytics. But Pablo needs to see POWER_USER population in Council reporting as a growth indicator. Growing POWER_USER count = healthy expansion. The stage also drives differentiated operational treatment (VIP flows, referral prompts, OTC introduction). A flag lacks this operational gravity.

---

#### Stage 7: AT_RISK (En Riesgo)

| Field | Value |
|-------|-------|
| **Definition** | Was economically active, now showing significant decline signals |
| **Entry criteria** | fm_date IS NOT NULL AND days_since_last_activity <= 90 AND (activity_decline_4w_pct >= 50 OR health_score < 30 OR dca_cancelled_recently OR earn_withdrawal_significant) |
| **Exit criteria (forward/recovery)** | New monetizable action AND health_score > 50 → ACTIVE (or POWER_USER if qualifying) |
| **Exit criteria (backward)** | days_since_last_activity > 90 → DORMANT_WITH_BALANCE or DORMANT_ZERO |
| **Population** | REQUIRES DATA. Estimated: 8,000-15,000 (users between ACTIVE and DORMANT). |
| **Revenue contribution** | Declining. Still generating some revenue from trailing positions. |
| **Target interventions** | Retention campaigns: "We noticed you haven't traded in X days. Here's what's happening in the market." DCA restart nudge. Earn promotion. Win-back incentive (fee discount for next trade). This is the last chance before dormancy. |
| **Key metrics** | AT_RISK population size (weekly trend), AT_RISK→ACTIVE recovery rate, AT_RISK→DORMANT conversion rate, median days in AT_RISK, cost per save |
| **Salvia sync** | NEW stage. Did not exist in L0-L5 model. Sits between Salvia's L3 and L4. Her requested filter "login by 1/3/6 months" partially addresses this; the health_score adds granularity. |

**Hard Design Decision: AT_RISK is a STAGE, not a flag.**
Reason: AT_RISK users need different campaigns than ACTIVE users. If AT_RISK is a flag on ACTIVE, CRM tools treat them as ACTIVE with a tag. If AT_RISK is a stage, they get their own journey. Operationally, Patri and team need to build AT_RISK-specific flows in CleverTap. A stage makes this cleaner.

---

#### Stage 8: REACTIVATED (Reactivado)

| Field | Value |
|-------|-------|
| **Definition** | User who was DORMANT or CHURNED and has taken a new monetizable action. Temporary stage (30 days). Different churn expectations than first-time ACTIVE users. |
| **Entry criteria** | Previous status was DORMANT_WITH_BALANCE, DORMANT_ZERO, or CHURNED AND new FM-qualifying action taken |
| **Exit criteria (forward)** | 30 days of sustained economic activity → ACTIVE (or POWER_USER) |
| **Exit criteria (backward)** | No second action within 30 days → AT_RISK. No action within 60 days → back to DORMANT. |
| **Population** | REQUIRES DATA. Estimated: varies heavily by market cycle. Bull market = reactivation wave. |
| **Revenue contribution** | Variable. Reactivated users generate 30-50% of their previous active-period revenue initially. |
| **Target interventions** | "Welcome back" sequence. Highlight what's new since they left. Gentle cross-sell. Do NOT overwhelm. Benchmark: reactivated users have 40-60% D30 retention (vs 35-45% for new FM users). |
| **Key metrics** | Reactivation rate (by dormancy duration, balance, market condition), D30 retention of reactivated, cost per reactivation vs new CAC, revenue per reactivated user |
| **Salvia sync** | NEW stage. Salvia's model doesn't track reactivation separately. Her "con balance + dormido" 14K users are the primary reactivation targets. |

**Hard Design Decision: Reactivated is a TEMPORARY stage (30 days), not a permanent classification.**
After 30 days of sustained activity, the user re-enters ACTIVE. This prevents permanent "reactivated" tagging that would skew ACTIVE cohort analysis. But during those 30 days, the user is tracked separately because their churn probability is different (higher than established ACTIVE, lower than brand-new FM).

**⚠️ DATA DEPENDENCY: State Transition History Table**

The REACTIVATED classifier requires knowing a user's PREVIOUS lifecycle stage. The daily snapshot alone doesn't provide this. A state_transition_history table must exist:

```sql
-- State transition history (append-only, one row per state change)
-- P0 data infrastructure requirement. Without this, REACTIVATED cannot be classified.
CREATE TABLE state_transition_history (
    user_id STRING,
    transition_date DATE,
    from_stage STRING,       -- e.g., 'DORMANT_WITH_BALANCE'
    to_stage STRING,         -- e.g., 'REACTIVATED'
    trigger_event STRING,    -- e.g., 'first_trade_after_dormancy'
    market_condition STRING,
    days_in_previous_stage INT
);

-- Populate daily by comparing today's snapshot to yesterday's:
INSERT INTO state_transition_history
SELECT
    t.user_id,
    CURRENT_DATE(),
    y.lifecycle_stage AS from_stage,
    t.lifecycle_stage AS to_stage,
    NULL AS trigger_event,  -- Enriched in post-processing
    t.market_condition,
    DATE_DIFF(CURRENT_DATE(), y.stage_entry_date, DAY)
FROM user_lifecycle_stage_today t
JOIN user_lifecycle_stage_yesterday y ON t.user_id = y.user_id
WHERE t.lifecycle_stage != y.lifecycle_stage
```

The master lifecycle SQL (below) joins to this table for the REACTIVATED check via `previous_status`.

---

#### Stage 9: DORMANT_WITH_BALANCE (Dormido Con Saldo)

| Field | Value |
|-------|-------|
| **Definition** | No monetizable action in 90+ days, balance > €0 |
| **Entry criteria** | days_since_last_monetizable_action > 90 AND total_balance_eur > 0 |
| **Exit criteria (forward)** | New monetizable action → REACTIVATED |
| **Exit criteria (backward)** | Balance withdrawn to €0 → DORMANT_ZERO. 180+ days AND balance decreasing → approaching CHURNED. |
| **Population (Spain)** | ~4,414 (1.0% of Spain, L4). Globally: 14K with balance among the 968K dormant (per Salvia). |
| **Revenue contribution** | Passive only (Earn yield, Staking rewards if positions still active). Some users in this stage generate meaningful recurring revenue. A "Silent Dormant" with €50K in Earn is generating revenue despite being classified as dormant by login metrics. |
| **Target interventions** | Differentiated by sub-tier (see below). Light-touch reactivation. Market update emails (not "we miss you"). Show portfolio performance. Remind of Earn yield being generated. |
| **Key metrics** | Population with weekly delta, average balance, reactivation rate, balance retention (are they slowly withdrawing?), passive revenue generated |

**Dormant Sub-tiers (diagnostic, not separate stages):**

| Sub-tier | Days Dormant | Reactivation Probability | Action Priority |
|----------|-------------|-------------------------|-----------------|
| Early Dormant | 90-180d | 25-40% | High. Reactivation campaigns P1. |
| Mid Dormant | 180-365d | 10-25% | Medium. Market-triggered campaigns. |
| Deep Dormant | 365d+ | 5-15% (but 14K have balance, per Salvia) | Low frequency. Bull-market triggered only. |

**Hard Design Decision: Dormant is ONE stage with sub-tiers, not multiple stages.**
Reason: Too many stages creates operational complexity for Patri's team. One DORMANT_WITH_BALANCE stage with a `days_dormant` attribute enables tiered campaigns without multiplying lifecycle states. Sub-tiers are filters, not stages.

**Salvia sync:** Salvia's "Dormidos con balance" (14K globally, 4,414 Spain L4) maps directly. Her requested filter "login by 1/3/6/12 months" creates the sub-tier segmentation within this stage.

---

#### Stage 10: DORMANT_ZERO (Dormido Sin Saldo)

| Field | Value |
|-------|-------|
| **Definition** | No monetizable action in 90+ days, zero balance, but hasn't hit 180d threshold for CHURNED or has logged in within 180d |
| **Entry criteria** | days_since_last_monetizable_action > 90 AND total_balance_eur = 0 AND NOT (days_since_activity > 180 AND days_since_login > 180) |
| **Exit criteria (forward)** | New deposit or monetizable action → REACTIVATED |
| **Exit criteria (backward)** | days_since_activity > 180 AND days_since_login > 180 → CHURNED |
| **Population** | REQUIRES DATA for precise. Part of Salvia's 953K dormant sin balance. |
| **Revenue contribution** | €0 |
| **Target interventions** | Low-cost only (email batch, no push/SMS budget). Reactivation offer with incentive (€5-€10 bonus for re-deposit). Market recovery notifications. |
| **Key metrics** | Population trend, reactivation rate, cost per reactivation |

---

#### Stage 11: CHURNED (Perdido)

| Field | Value |
|-------|-------|
| **Definition** | No activity 180+ days, zero balance, no login 180+ days |
| **Entry criteria** | days_since_last_activity > 180 AND total_balance_eur = 0 AND days_since_last_login > 180 |
| **Exit criteria** | Any new action → REACTIVATED (rare but possible; market cycle triggers) |
| **Population (Spain)** | ~101,029 (23.2%). Globally: vast majority of Salvia's 953K dormant sin balance. |
| **Revenue contribution** | €0. Write-off for operational budgeting. |
| **Target interventions** | Quarterly batch email only. No CRM spend. If market enters bull phase, one reactivation campaign. Focus on new acquisition instead. |
| **Key metrics** | Population size (should grow slower than ACTIVE), churn rate feeding this stage |

---

### Master Lifecycle SQL (Daily Snapshot)

```sql
-- Updated classifier incorporating POWER_USER and REACTIVATED
-- Extends Chunk 1 Section 1.2 status classifier
-- Run daily to produce user_lifecycle_stage view

SELECT
    user_id,
    CASE
        -- Exclude invalid accounts
        WHEN account_status IN ('banned', 'disabled') THEN 'EXCLUDED'

        -- CHURNED
        WHEN days_since_last_activity > 180
             AND total_balance_eur = 0
             AND days_since_last_login > 180
        THEN 'CHURNED'

        -- DORMANT_ZERO
        WHEN days_since_last_monetizable_action > 90
             AND total_balance_eur = 0
             AND NOT (days_since_last_activity > 180 AND days_since_last_login > 180)
        THEN 'DORMANT_ZERO'

        -- DORMANT_WITH_BALANCE
        WHEN days_since_last_monetizable_action > 90
             AND total_balance_eur > 0
        THEN 'DORMANT_WITH_BALANCE'

        -- REACTIVATED (temporary 30d stage)
        -- REQUIRES: state_transition_history table (see Stage 8 spec above).
        -- previous_status is derived from the most recent row in state_transition_history
        -- where to_stage != from_stage. If table doesn't exist yet, this clause
        -- falls through and reactivated users land in ACTIVE (acceptable interim behavior).
        WHEN previous_status IN ('DORMANT_WITH_BALANCE','DORMANT_ZERO','CHURNED')
             AND days_since_reactivation_event <= 30
             AND is_economically_active = TRUE
        THEN 'REACTIVATED'

        -- AT_RISK
        WHEN fm_date IS NOT NULL
             AND days_since_last_monetizable_action <= 90
             AND (
                 activity_decline_4w_pct >= 50
                 OR health_score < 30
                 OR dca_cancelled_recently = TRUE
                 OR (earn_withdrawal_30d_pct > 0.5 AND earn_balance_eur > 0)
             )
        THEN 'AT_RISK'

        -- POWER_USER (threshold evaluated monthly, stored in monthly_thresholds table)
        -- See Stage 6 spec for stability rules: 30-day minimum tenure, demotion requires
        -- 2 consecutive months below p50.
        WHEN is_economically_active = TRUE
             AND days_since_fm > 30
             AND products_with_fm >= 2
             AND (monthly_revenue_eur > revenue_p75_threshold OR space_center_tier >= 3)
             -- Stability: if already POWER_USER, retain for 30 days even if revenue dips
             -- (handled by COALESCE with previous_status check)
        THEN 'POWER_USER'

        -- ACTIVE
        WHEN fm_date IS NOT NULL
             AND days_since_fm > 30
             AND is_economically_active = TRUE
        THEN 'ACTIVE'

        -- FIRST_MONETIZATION
        WHEN fm_date IS NOT NULL
             AND days_since_fm <= 30
        THEN 'FIRST_MONETIZATION'

        -- DEPOSITED_ONLY
        WHEN total_deposits > 0
             AND fm_date IS NULL
        THEN 'DEPOSITED_ONLY'

        -- KYC_COMPLETE
        WHEN kyc_status = 'approved'
             AND total_deposits = 0
             AND fm_date IS NULL
        THEN 'KYC_COMPLETE'

        -- REGISTERED_ONLY
        WHEN has_account = TRUE
             AND kyc_status != 'approved'
        THEN 'REGISTERED_ONLY'

        ELSE 'UNCLASSIFIED'
    END AS lifecycle_stage,

    -- Context fields for downstream analysis
    days_since_last_monetizable_action,
    total_balance_eur,
    products_with_fm,
    is_economically_active,
    is_behaviorally_active,
    market_condition,
    space_center_tier,
    CURRENT_DATE() AS snapshot_date

FROM user_master_table
WHERE account_status NOT IN ('banned', 'disabled')  -- Exclude 600K invalid
```

### Population Estimates (Combined Salvia + Known Data)

**⚠️ NON-OVERLAP NOTE:** POWER_USER is evaluated BEFORE ACTIVE in the priority-ordered SQL. A user who qualifies as POWER_USER is NOT counted in ACTIVE. These populations are mutually exclusive. Do NOT add them together when calculating "total active users." Instead: Total economically active users = ACTIVE + POWER_USER + REACTIVATED.

| Stage | Spain Est. | Global Est. | Revenue Est. |
|-------|-----------|-------------|-------------|
| EXCLUDED (banned+disabled) | REQUIRES DATA | ~600K | €0 |
| REGISTERED_ONLY | ~213,863 | ~700K-800K | €0 |
| KYC_COMPLETE | ~29,010 | ~50K-70K | €0 |
| DEPOSITED_ONLY | REQUIRES DATA | REQUIRES DATA | €0 |
| FIRST_MONETIZATION | ~5,000-8,000 (monthly inflow) | REQUIRES DATA | FM Revenue |
| ACTIVE | ~35,000-45,000 | REQUIRES DATA | 60-70% of revenue |
| POWER_USER | ~5,000-10,000 | REQUIRES DATA | 25-40% of revenue |
| AT_RISK | ~8,000-15,000 | REQUIRES DATA | Declining |
| REACTIVATED | Variable (market-dependent) | Variable | 30-50% of prior active |
| DORMANT_WITH_BALANCE | ~4,414 | ~14K (Salvia) | Passive only |
| DORMANT_ZERO | REQUIRES DATA | Part of 953K | €0 |
| CHURNED | ~101,029 | ~800K-900K | €0 |

---

## 3.2 Per-Product Lifecycle Overlays

Each product has its own lifecycle that overlays on top of the global status. A user can be globally ACTIVE but Brokerage CHURNED and Earn ACTIVE.

### Product Lifecycle Stages (Universal Template)

Every product uses the same 6-stage overlay:

| Stage | Definition |
|-------|-----------|
| **UNAWARE** | User has not interacted with this product (no page view, no mention) |
| **AWARE** | User has viewed product page or received product communication |
| **TRIED** | User attempted first action (started flow but may not have completed) |
| **ACTIVATED** | Per Chunk 1, Section 1.6 activation definition met |
| **POWER** | High-frequency or high-value usage of this specific product |
| **PRODUCT_CHURNED** | Per Chunk 1, Section 1.6 dormancy definition met |

### Brokerage Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE → TRIED (first deposit, no trade) → ACTIVATED (1st trade + 2nd trade within 14d) → POWER (20+ trades/month OR volume > €10K/month) → PRODUCT_CHURNED (no trade 21d, no DCA) |
| **Activation** | First trade ≥ threshold + second trade within 14 days |
| **Dormancy** | No trade for 21+ days AND no active DCA |
| **Aha moment** | Seeing portfolio value increase after first buy |
| **Time window** | Daily/weekly cadence expected |
| **Key metric** | Tx/month, Volume/month, Spread revenue |
| **Salvia cluster mapping** | C8 (High Value) → POWER. C6/C7 (Smart Holders) → ACTIVATED. C0/C4/C9/C1 (Mass Retail) → ACTIVATED (lower tier). C2/C3/C5 (Inactivos) → PRODUCT_CHURNED. |

### Pro Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE (visited Pro) → TRIED (first Pro trade) → ACTIVATED (first limit order OR 3+ trades in 7d) → POWER (50+ trades/month, maker volume > 30%) → PRODUCT_CHURNED (no Pro trade 14d) |
| **Activation** | First limit order executed OR 3+ market orders within 7 days |
| **Dormancy** | No Pro trade for 14+ days |
| **Aha moment** | Executing a profitable limit order |
| **Time window** | Daily cadence expected |
| **Key metric** | Volume, Maker %, Fee revenue, Active API keys |
| **Note** | Jan 2025 fee cut (95% reduction) changed economics. Pro revenue per user is much lower. Track volume and maker % as health indicators, not just revenue. |

### Earn Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE (viewed Earn page) → TRIED (started deposit flow) → ACTIVATED (deposit ≥ €50 AND first yield visible) → POWER (AUC > €10K OR multiple yield products) → PRODUCT_CHURNED (no new deposit 60d AND withdrawal initiated) |
| **Activation** | First deposit into yield product ≥ €50 |
| **Dormancy** | No new deposits in 60 days AND partial/full withdrawal initiated. **Gradient signal:** Track weekly balance change. If balance is declining >5%/week for 3+ consecutive weeks without new deposits, flag as PRE_DORMANT even if no explicit withdrawal event. Slow drip withdrawals are harder to detect than a single large exit. |
| **Aha moment** | Seeing first yield accrual in portfolio |
| **Time window** | Monthly review cadence (deposits are episodic, yield is continuous) |
| **Key metric** | AUC (Assets Under Custody), Yield generated, Net deposit flow, Stablecoin % |
| **Note** | 82% BTC, €1.02M stablecoins per known data. Earn is counter-cyclical for stablecoins in bear markets. |

### Card Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE (card page viewed or promo received) → TRIED (card ordered) → ACTIVATED (card activated + 3rd purchase within 30d) → POWER (10+ tx/month, €500+/month spend) → PRODUCT_CHURNED (no card tx 30d) |
| **Activation** | Card activated + 3rd purchase within 30 days |
| **Dormancy** | No card transaction for 30+ days |
| **Aha moment** | Seeing B2M cashback credited after purchase |
| **Time window** | Weekly cadence expected |
| **Key metric** | Tx/month, Monthly spend, Interchange revenue, Cashback distributed |
| **Note** | 0.26% penetration vs 42-48% industry. 29% monthly churn. Massive gap = massive opportunity. Card is the stickiest daily-use product. |

### Loan Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE (loan page viewed) → TRIED (loan simulation started) → ACTIVATED (loan originated) → POWER (2+ loans OR outstanding > €50K) → PRODUCT_CHURNED (loan repaid + no new loan 90d) |
| **Activation** | First loan originated |
| **Dormancy** | Loan fully repaid + no new loan in 90 days |
| **Aha moment** | Receiving EUR in bank without selling crypto |
| **Time window** | Per loan term (months) |
| **Key metric** | Loans outstanding, Total collateral, Interest revenue, Liquidation rate |
| **Note** | 90.91% of Loan Whales from Brokerage C8. Cross-sell from High Value Brokerage users is the primary growth lever. |

### Staking Overlay

| Dimension | Value |
|-----------|-------|
| **Stages** | UNAWARE → AWARE (staking page viewed) → TRIED (researched rates) → ACTIVATED (first stake ≥ €50 + first reward visible) → POWER (staked > €5K OR multiple protocols) → PRODUCT_CHURNED (unstaking initiated + no new stake 60d) |
| **Activation** | First stake ≥ €50 + seeing first reward |
| **Dormancy** | Unstaking initiated + no new stake in 60 days |
| **Aha moment** | Seeing first protocol reward |
| **Time window** | Monthly cadence (rewards are periodic) |
| **Key metric** | Amount staked, Protocols used, Reward revenue, Unbonding activity |

---

## 3.3 Cross-Product Adoption Matrix

### Product Density Impact (from mega-prompt, validated by industry benchmarks)

| Products Used | Est. 12-Month Retention | LTV Multiplier | Implied Bit2Me LTV |
|---|---|---|---|
| 1 product | 20-30% | 1.0x | ~€388 |
| 2 products | 45-55% | 1.8-2.5x | ~€700-€970 |
| 3 products | 65-75% | 3.0-4.0x | ~€1,164-€1,552 |
| 4+ products | 80-90% | 4.0-6.0x | ~€1,552-€2,328 |

### Cross-Sell Probability Matrix

Which product leads to which? Estimated probabilities **within 12 months of Product A activation** (REQUIRES VALIDATION with Bit2Me data):

| From \ To | Earn | Card | Pro | Staking | Loan | DCA |
|-----------|------|------|-----|---------|------|-----|
| **Brokerage** | 25-30% | 8-12% | 10-15% | 8-12% | 3-5% | 15-20% |
| **Earn** | — | 5-8% | 5-8% | 15-20% | 8-12% | 10-15% |
| **Card** | 10-15% | — | 3-5% | 3-5% | 2-3% | 5-8% |
| **Pro** | 15-20% | 3-5% | — | 5-8% | 5-8% | 5-8% |
| **Staking** | 20-25% | 3-5% | 5-8% | — | 3-5% | 5-8% |
| **Loan** | 15-20% | 5-8% | 8-12% | 5-8% | — | 3-5% |

**Time decay note:** Most cross-sell happens within the first 90 days of Product A activation. After 90 days, the probability drops by ~50%. This means cross-sell nudges must fire early (Day 7-30 post-activation on Product A, depending on product cadence). A Brokerage→Earn nudge at Day 60 is already late for most users.

### Golden Paths by Segment

**Path 1: Mass Retail (Curious Novice → Millennial Investor)**
```
Brokerage (manual buy) → DCA setup (D7-14) → Earn (idle balance, D30-60) → Card (D60-90)
```
- Retention improvement: 1-product 25% → 3-product 70% (2.8x)
- Revenue: €388 → €1,164+ LTV
- Key trigger: DCA setup is THE inflection point. Users with active DCA have 2-3x better D90.

**Path 2: Smart Holders (Millennial Investor → Yield Seeker)**
```
Brokerage (regular buys) → Earn (BTC/ETH yield) → Staking (ETH, SOL) → Loan (leverage without selling)
```
- Retention improvement: 2-product 50% → 4-product 85%
- Revenue: €700 → €2,328+ LTV
- Key trigger: Earn deposit suggestion when idle balance > €500 sits for 7+ days.

**Path 3: High Value (Whale → Full Ecosystem)**
```
OTC/Brokerage (large trades) → Earn (yield on holdings) → Loan (borrow against) → Staking → Card
```
- Revenue: €5,000 → €100K+ LTV
- Key trigger: Account manager introduction when balance > €50K.

### DCA as the Retention Bridge

DCA (recurring buy) is the highest-leverage retention mechanism for Mass Retail:

```
Manual Brokerage (volatile, churn-prone)
        │
        ▼ DCA setup nudge (D7-14 post first trade)
        │
    Active DCA (automated, sticky)
        │
        ▼ Accumulated balance triggers Earn suggestion
        │
    Earn deposit (passive revenue begins)
```

**Why DCA matters:**
- Manual trader: active decision every time. Each "should I buy?" is a potential exit point.
- DCA user: set-and-forget. Passive. Every automated execution reinforces commitment (sunk cost, consistency bias).
- DCA cancellation is a STRONGER churn signal than missing a manual trade. It represents a deliberate decision to stop.

**DCA Metrics to Track (P0):**

**⚠️ P0 DATA DEPENDENCY:** All DCA metrics below require a "recurring_orders" table that tracks setup, execution, pause, and cancel events. Confirm with David Sales / Álvaro whether this table exists in BigQuery and whether it captures pause/cancel events (not just executions). If it only tracks executions, DCA Cancellation Rate (the strongest single churn signal for mass retail) cannot be computed. Building this tracking is a P0 data infra task if missing.

| Metric | Formula | Tier |
|--------|---------|------|
| Tasa de Activación DCA | DCA_setups_period / eligible_users_period | B |
| DCA Retention Premium | D90_retention_DCA_users / D90_retention_non_DCA_users | B |
| DCA Cancellation Rate | DCA_cancelled_period / DCA_active_start_period | B (churn signal) |
| DCA Volume | SUM(dca_execution_amount) | C |

### B2M Token Flywheel Mapped to Lifecycle

```
                    ┌─────────────────────────────┐
                    │                             │
                    ▼                             │
            Buy B2M ──── Hold for ────── Stake for
           (fee        Space Center       yield
          discounts)     (tier up)       (Earn APY
              │              │            boost)
              │              │              │
              ▼              ▼              ▼
         Pro fee         Launchpad      Card cashback
         discount        priority       (up to 7%
          (25-50%)      allocation       in B2M)
              │              │              │
              └──────────────┴──────────────┘
                             │
                    Increased switching cost
                    (every B2M staked = harder to leave)
```

**Lifecycle integration points:**

| Lifecycle Stage | B2M Flywheel Entry | Mechanism |
|----------------|-------------------|-----------|
| FIRST_MONETIZATION | "Buy B2M to reduce your trading fees by 25%" | Immediate value proposition |
| ACTIVE (single product) | "Upgrade your Space Center tier to unlock Earn APY boost" | Cross-sell through tier incentive |
| ACTIVE (multi-product) | "Your B2M tier qualifies you for Launchpad priority" | Deepen engagement |
| AT_RISK | "Your B2M is still earning. Don't lose your tier benefits." | Retention through sunk cost |
| POWER_USER | "VIP: exclusive Launchpad allocation for Tier 4+" | Recognition and exclusive access |

---

## 3.4 B2B Lifecycle (Separate Model)

B2B operates on fundamentally different timescales, touchpoints, and metrics.

### B2B Lifecycle Stages

| Stage | Definition | Duration | Key Metric | Owner |
|-------|-----------|----------|-----------|-------|
| **LEAD** | Interest expressed (form, event, referral) | Days-weeks | Lead volume, source | Sales |
| **QUALIFICATION** | Fit assessed (volume needs, regulatory, product match) | 1-2 weeks | Qualification rate | Sales |
| **KYB_IN_PROGRESS** | KYB documentation submitted, under review | 2-8 weeks | KYB processing time, completion rate | Compliance + Sales |
| **KYB_COMPLETE** | KYB approved, account created | — | — | — |
| **INTEGRATION** | API integration, test transactions, sandbox | 2-6 weeks | Integration time, test tx success | Product + Sales |
| **FIRST_TRADE** | First production transaction | — | Time-to-first-trade | Sales |
| **RAMP** | Volume building toward contracted/expected levels | 1-3 months | Volume trajectory, % of target | Sales + Growth |
| **STEADY_STATE** | Operating at expected volume | Ongoing | Monthly volume, revenue, SLA compliance | Account Management |
| **EXPANSION** | Adding products, increasing volume, multi-market | Variable | Products used, volume growth, new markets | Account Management |
| **B2B_AT_RISK** | Volume decline 3 consecutive weeks OR API call decline OR support escalation | — | Volume trend, API health | Account Management (escalate) |
| **B2B_CHURNED** | No API calls 60d AND no transactions 90d | — | Revenue lost | Post-mortem |

### B2B Activation Definition
- **Activation:** First production transaction after integration
- **Full Activation:** Reaching 50% of contracted/expected monthly volume within 60 days of first trade

### B2B Churn Signals (Ranked)
1. API call frequency decline (>30% WoW for 2+ weeks)
2. Volume decline (3 consecutive weeks below 70% of steady-state)
3. Account manager receiving competitor RFP questions
4. Support ticket volume spike (frustration indicator)
5. Contract renewal date approaching without engagement

### B2B Council Integration
B2B feeds into Council as a separate line item:

| Council Metric | B2B Version |
|---------------|-------------|
| MMU | Active B2B accounts (traded in month) |
| Activation Rate | KYB_COMPLETE → FIRST_TRADE rate |
| Churn Rate | B2B accounts lost / B2B accounts start of period |
| NRR | B2B revenue this month / B2B revenue same accounts last month |
| Revenue from Tests | N/A for B2B (relationship-managed, not A/B tested) |

---

## 3.5 Academy-to-Conversion Pipeline

### Pipeline Stages

```
Academy Student (3M+)
    │
    ▼ Content consumption (courses, articles, videos)
Academy Engaged (completes 1+ course)
    │
    ▼ CTA: "Ready to buy your first crypto?"
Registered (on exchange)
    │
    ▼ KYC flow (standard)
KYC Complete
    │
    ▼ First deposit (fiat)
Deposited
    │
    ▼ First trade (guided, simplified)
FM (First Monetization)
    │
    ▼ Standard lifecycle from here
```

### Conversion Benchmarks

| Step | Target Rate | Industry Benchmark | Current Bit2Me |
|------|-----------|-------------------|---------------|
| Academy → Registration | 8-15% | 5-12% (education-to-product) | REQUIRES DATA |
| Registration → KYC | 60-70% | Standard (same as other channels) | REQUIRES DATA |
| KYC → FM | 45-55% (ES), 20-25% (LATAM) | Per geo benchmarks | REQUIRES DATA |
| **Overall Academy → FM** | **3-8%** | 2-5% without Learn & Earn, 8-15% with | REQUIRES DATA |

### Learn & Earn Gap Analysis

| Competitor | Learn & Earn Program | Estimated Impact |
|-----------|---------------------|-----------------|
| Coinbase | Earn crypto by watching videos + quiz | 15-25% of new user activations come through L&E |
| Binance | Binance Academy + Learn & Earn campaigns | Significant user acquisition in emerging markets |
| OKX | OKX Learn + token rewards | Growing program |
| **Bit2Me** | **None** | **Major gap. 3M students, zero L&E monetization.** |

**Learn & Earn ROI Estimate:**
- Cost: €X per user in crypto rewards (typically €3-€10)
- Conversion lift: Academy→FM rate from ~5% to ~12% (2.4x)
- Incremental users: If 100K Academy users/year are eligible, 7,000 incremental FM users
- At average LTV of €200-€388: €1.4M-€2.7M incremental revenue
- CAC for L&E users: €3-€10 (vs €15-€50 Paid)
- ROI: 5-20x ROAS
- Implementation: Medium complexity (reward distribution, quiz system, fraud prevention)

### Academy User Lifecycle Differences

| Dimension | Academy User | Paid User | Organic User |
|-----------|-------------|-----------|-------------|
| Knowledge at FM | Higher (educated) | Variable | Variable |
| Time to FM | Longer (30-90d learning first) | Shorter (7-14d) | Medium (14-30d) |
| D30 Retention | Expected higher (intentional decision) | Lower (impulse) | Medium |
| First asset | More diversified (educated about options) | BTC-heavy (brand recognition) | BTC/ETH |
| Product density | Higher (knows about Earn, Staking from courses) | Lower (Brokerage-only) | Medium |
| CAC | €0 (organic) + L&E cost if implemented | €15-€50 | €0 |

---

## 3.6 GTM Market Expansion Lifecycle

### Portugal Template (Completed, Extract Learnings)

**Known data from Salvia's analysis (PT 2025 registrations):**
- 5,248 registrations → 2,056 verified → 1,066 first purchases = 20% conversion
- Drop at email: 12%, Drop at phone: 28%
- 29,346 enabled users, 1,362 disabled, 95 banned (total 30,806)

**Current phase: STEADY STATE (Month 3+).** Portugal is past Launch Burst and Early Activation. The 20% conversion rate is significantly below Spain's 45%, indicating the market has not yet converged.

**Convergence tracking (P0 for Portugal):**

| Metric | Portugal Current | Spain Benchmark | Convergence Target (80% of ES) | Gap |
|--------|-----------------|-----------------|-------------------------------|-----|
| Reg→FM Rate | 20% | 45% | 36% | 16pp gap |
| Phone verification drop | 28% | 32% | Comparable | OK |
| Email drop | 12% | 6% | 4.8% | 7pp gap |

**Key actions to close the gap:**
1. Portuguese localization audit: verify all emails, push notifications, and app screens are in Portuguese, not Spanish.
2. Email verification drop (12% vs 6% ES): investigate whether email deliverability is lower for Portuguese email providers.
3. FM rate gap (20% vs 45%): analyze DEPOSITED_ONLY population in Portugal specifically. If deposit rate is similar to Spain but FM rate is lower, the problem is the buy flow, not onboarding.

### GTM Lifecycle Phases

| Phase | Duration | Key Activities | Success Metric | Target |
|-------|----------|---------------|----------------|--------|
| **Pre-Launch** | 4-8 weeks before | DB building (email collection, waitlist). Local partnerships. Regulatory prep. Localization QA. | DB size, email opt-in rate | 5K-20K depending on market size |
| **Launch Burst** | Week 1-2 | Heavy paid acquisition. PR push. Influencer campaigns. Launch offers. | Registration velocity | 2K-5K reg/week (scaled by market) |
| **Early Activation** | Week 2-4 | KYC completion campaigns. First deposit nudges. Onboarding optimization for local friction points. | KYC rate, FM rate | KYC 50%+, FM 20%+ |
| **Early Lifecycle** | Week 4-8 | First retention campaigns. DCA setup. Earn introduction. | D30 retention, second action rate | D30 > 25% |
| **Steady State** | Month 3+ | Standard lifecycle campaigns. Transition to BAU metrics. | Convergence with mature market benchmarks | FM rate within 80% of mature market |

### GTM Cohort Tracking Rules

1. Tag all users from GTM market with `is_gtm_cohort = TRUE` for first 90 days
2. Track separately from organic users in same market (who arrive later)
3. Benchmark against Spain cohorts of same vintage (adjusted for lower expected conversion)
4. Transition to BAU when monthly metrics converge within 20% of mature market averages for 2 consecutive months

### GTM Metrics (Weekly during phases 1-4)

| Metric | Formula | Target Phase |
|--------|---------|-------------|
| Velocidad de Registro | registrations / day | Launch Burst |
| Tasa de KYC GTM | kyc_completed / registered (GTM cohort) | Early Activation |
| Tasa de FM GTM | fm_users / registered (GTM cohort) | Early Activation |
| Retención D30 GTM | users_active_d30 / fm_users (GTM cohort) | Early Lifecycle |
| CAC Local | spend_market / fm_users_market | All phases |
| Convergencia | metric_new_market / metric_spain | Steady State |

---

# PHASE 4: METRICS CATALOG (The Numbers)

## 4.1 The 5 Council Numbers (Tier A) — Pablo's Weekly View

---

### Council Metric 1: Usuarios Monetizados Mensuales (MMU)

| Field | Value |
|-------|-------|
| **English name** | Monthly Monetized Users |
| **Formula** | `MMU = COUNT(DISTINCT user_id) WHERE is_economically_active = TRUE` (measured on last day of month or rolling 30d) |
| **SQL** | See Chunk 1, Section 1.3 |
| **Dimensions** | Time, Geography, Segment, Product, Archetype, Market Condition, Space Center Tier |
| **Decision tier** | A |
| **Data source** | Requires BigQuery view (user_lifecycle_stage). Currently partially available via Qlik Activation + LC join. |
| **Frequency** | Weekly (for Council), Daily (for dashboard) |
| **Owner** | Growth (Daniel) |
| **Interpretation** | Growing MMU = more users generating revenue. Report alongside BTC price to contextualize. Separate into MMU_transactional (traded) and MMU_passive (Earn/Staking/Loan) for diagnostics. |

---

### Council Metric 2: Tasa de Activación (Activation Rate)

| Field | Value |
|-------|-------|
| **English name** | Activation Rate |
| **Formula** | `Activation_Rate = FM_Users_period / Verified_Users_period` |
| **SQL** | ```SELECT COUNT(DISTINCT CASE WHEN fm_date BETWEEN @start AND @end THEN user_id END) / NULLIF(COUNT(DISTINCT CASE WHEN kyc_approved_date BETWEEN @start AND @end THEN user_id END), 0)``` |
| **Dimensions** | Time, Geography, Segment, Channel, Sub-channel, Product (first FM product) |
| **Decision tier** | A |
| **Data source** | Available now (Qlik Activation report). Cross-product version requires BigQuery EMA view. |
| **Frequency** | Weekly |
| **Owner** | Growth (Daniel) |
| **Interpretation** | Spain target: 45% (current benchmark from Salvia data). New EU: 20-25%. LATAM: 50-60%. Report with time-to-FM median alongside. |
| **Known values** | ES 45%, DE 25%, PT 20%, IT 22%, FR 22% (from Salvia's 2025 data) |

---

### Council Metric 3: Tasa de Churn Mensual (Monthly Churn Rate)

| Field | Value |
|-------|-------|
| **English name** | Monthly Churn Rate |
| **Formula** | `Churn_Rate_Monthly = Users_entering_DORMANT_or_CHURNED_this_month / MMU_start_of_month` |
| **SQL** | ```SELECT COUNT(DISTINCT CASE WHEN lifecycle_stage_today IN ('DORMANT_ZERO','DORMANT_WITH_BALANCE','CHURNED') AND lifecycle_stage_30d_ago IN ('ACTIVE','POWER_USER','AT_RISK','FIRST_MONETIZATION') THEN user_id END) / NULLIF(mmu_start, 0)``` |
| **Dimensions** | Time, Geography, Segment, Product, Archetype, Market Condition |
| **Decision tier** | A |
| **Data source** | Requires BigQuery (user_daily_snapshot with 30d lookback) |
| **Frequency** | Weekly (rolling 30d), Monthly (calendar) |
| **Owner** | Growth (Daniel) |
| **Interpretation** | Always report with market_condition flag. A 5% monthly churn in BULL is alarming. A 5% monthly churn in BEAR may be normal. Separate DORMANT_WITH_BALANCE (recoverable) from DORMANT_ZERO (likely lost). |

---

### Council Metric 4: Retención Neta de Ingresos (NRR)

| Field | Value |
|-------|-------|
| **English name** | Net Revenue Retention |
| **Formula** | `NRR = Revenue_this_month_from_users_active_last_month / Revenue_last_month_from_same_users` |
| **SQL** | ```WITH cohort AS (SELECT user_id, revenue AS rev_m0 FROM monthly_revenue WHERE month = @last_month AND revenue > 0) SELECT SUM(r.revenue) / NULLIF(SUM(c.rev_m0), 0) FROM cohort c LEFT JOIN monthly_revenue r ON c.user_id = r.user_id AND r.month = @this_month``` |
| **Dimensions** | Time, Geography, Segment, Product, Revenue Type |
| **Decision tier** | A |
| **Data source** | Requires BigQuery (monthly_revenue joined to user tables) |
| **Frequency** | Monthly |
| **Owner** | Growth (Daniel) |
| **Interpretation** | NRR > 100% = expansion (existing users spend more). NRR < 100% = contraction. ALWAYS report alongside BTC price. NRR drops during bear markets are expected; the question is whether Bit2Me's NRR drops less than the market (i.e., is Earn/Staking buffering the transactional decline?). Target: NRR > 95% in neutral, > 110% in bull. |

**NRR vs GRR (U4) relationship:**
NRR measures the SAME cohort of users month-over-month. It captures both contraction (users spending less) and expansion (users spending more). GRR (Gross Revenue Retention, metric U4) excludes expansion and measures only contraction + churn.

```
NRR = (Revenue from same users this month) / (Revenue from same users last month)
GRR = (Revenue retained, excluding upsell) / (Revenue from same users last month)

Always: GRR ≤ NRR
If NRR > 100% but GRR < 80%: Expansion from power users is masking high churn.
If NRR > 100% AND GRR > 90%: Healthy. Low churn AND expansion.
```

Report both to Pablo. NRR alone can hide a leaky bucket if expansion revenue from whales compensates for mass churn.

---

### Council Metric 5: Ingreso Incremental de Tests (Revenue from Tests)

| Field | Value |
|-------|-------|
| **English name** | Incremental Revenue from A/B Tests |
| **Formula** | `Test_Revenue = Σ (treatment_conversion - control_conversion) × treatment_population × revenue_per_conversion` for all shipped tests |
| **SQL** | Per-test calculation. Aggregated in test tracker. |
| **Dimensions** | Time, Test ID, Segment, Product |
| **Decision tier** | A |
| **Data source** | CleverTap test results + manual calculation (automate in Month 2) |
| **Frequency** | Weekly |
| **Owner** | Growth (Daniel), Patri (execution) |
| **Interpretation** | This proves Growth's value to Pablo. Every week, report: "Tests shipped this period generated €X incremental revenue." Start with conservative estimates (only count revenue within 30d of test exposure). |

---

## 4.2 Complete Metric Catalog

### Acquisition Metrics (Tier B-C)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| A1 | Registros | Registrations | COUNT(registrations) by period | Time, Geo, Channel, Sub-ch, Segment | B | Qlik Acquisition (available) | Daily | Growth |
| A2 | Verificados | Verified Users | COUNT(kyc_approved) by period | Time, Geo, Channel, Sub-ch, Segment | B | Qlik Acquisition (available) | Daily | Growth |
| A3 | Usuarios FM | FM Users | COUNT(fm_events) by period | Time, Geo, Channel, Sub-ch, Segment, Product | B | Qlik Activation (Brokerage avail), BigQuery (cross-product TBD) | Daily | Growth |
| A4 | CPL | Cost per Lead | Spend / Registrations | Time, Geo, Channel, Sub-ch | B | Qlik + Paid spend data | Weekly | Consuelo |
| A5 | CPA | Cost per Acquisition (verified) | Spend / Verified | Time, Geo, Channel, Sub-ch | B | Qlik + Paid spend | Weekly | Consuelo |
| A6 | CAC | Customer Acquisition Cost | Spend / FM_Users | Time, Geo, Channel, Sub-ch, Product | B | Qlik + Paid spend + BigQuery FM | Weekly | Growth |
| A7 | CAC Blended | Blended CAC | Total_spend_all_channels / Total_FM_users | Time, Geo | B | Aggregated | Monthly | Growth |
| A8 | ROAS | Return on Ad Spend | Revenue_from_cohort / Spend_for_cohort | Time, Geo, Channel, Cohort | B | Qlik Transaction Attribution + Paid spend | Monthly | Consuelo |
| A9 | Tasa Reg→KYC | Registration to KYC Rate | Verified / Registered | Time, Geo, Channel | B | Qlik Acquisition (available) | Weekly | Growth |
| A10 | Tasa KYC→FM | KYC to FM Rate | FM_Users / Verified | Time, Geo, Channel, Product | B | Qlik Activation (available) | Weekly | Growth |
| A11 | Velocidad de FM | Time to First Monetization | MEDIAN(fm_date - reg_date) in days | Geo, Channel, Product | C | BigQuery | Monthly | Growth |
| A12 | KYC Abandonment | KYC Drop-off Rate by Step | DROP_count_step / START_count_step | Geo, Step, Device | C | Qlik Onboarding (available) | Weekly | Growth |
| A13 | Calidad de Canal | Channel Quality Score | D30_retention × ARPU_30d per channel | Channel, Geo | C | BigQuery | Monthly | Growth |

### Monetization Metrics (Tier B-C)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| M1 | Ingresos Totales | Total Revenue | SUM(revenue) | Time, Geo, Segment, Product, Rev Type, Channel | B | Qlik Revenue per Product (available) | Daily | Growth |
| M2 | Ingresos FM | FM Revenue | SUM(revenue) WHERE fm_date in period | Time, Geo, Channel, Product | B | Qlik Transaction Attribution (available) | Weekly | Growth |
| M3 | Ingresos LC | LC Revenue | SUM(revenue) WHERE fm_date before period | Time, Geo, Product, Stage | B | Qlik Transaction Attribution (available) | Weekly | Growth |
| M4 | ARPMMU | Revenue per Monetized User | Total_Revenue / MMU | Time, Geo, Segment, Product | B | BigQuery | Monthly | Growth |
| M5 | Ticket Medio | Average Transaction Size | SUM(volume) / COUNT(transactions) | Time, Geo, Product | C | Qlik Brokerage (available) | Weekly | Data |
| M6 | Ratio Recurrente | Recurring Revenue Ratio | Recurring_Revenue / Total_Revenue | Time, Geo | B | BigQuery (requires product-type mapping) | Monthly | Growth |
| M7 | Volumen Monetizable | Monetizable Volume | SUM(transaction_volume) | Time, Geo, Product, Segment | C | Qlik Brokerage (available) | Daily | Data |

### Retention Metrics (Tier B-C)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| R1 | Retención Dn | D-n Retention | users_active_day_n / users_fm_cohort | Time, Cohort, Geo, Channel, Product | B | BigQuery (cohort views) | Monthly | Growth |
| R2 | Vida Media | Median Lifetime | MEDIAN(last_active_date - fm_date) for churned users | Cohort, Geo, Channel, Archetype | C | BigQuery | Monthly | Growth |
| R3 | Tasa Reactivación | Reactivation Rate | reactivated_users / dormant_start | Time, Dormancy duration, Balance, Market Condition | B | BigQuery | Monthly | Growth |
| R4 | Coste Reactivación | Cost per Reactivation | Reactivation_spend / Reactivated_users | Time, Channel | C | BigQuery + CRM spend | Monthly | Growth |
| R5 | Calidad Reactivación | Reactivation D30 Retention | D30_active_reactivated / reactivated_total | Cohort, Dormancy duration | C | BigQuery | Monthly | Growth |

### Lifecycle Metrics (Tier B)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| L1 | Población por Etapa | Stage Population | COUNT(users) per lifecycle_stage | Time, Stage, Geo, Segment | B | BigQuery user_lifecycle_stage | Weekly | Growth |
| L2 | Flujo Neto de LC | Net Lifecycle Flow | (entering_ACTIVE) - (leaving_ACTIVE) per week | Time, Geo | B | BigQuery stage_transitions_weekly | Weekly | Growth |
| L3 | Tasa de Transición | Stage Transition Rate | users_transitioning / users_in_origin_stage | Time, Stage pair, Geo | B | BigQuery stage_transitions_weekly | Weekly | Growth |
| L4 | Ingreso por Etapa | Revenue per Stage | SUM(revenue) per lifecycle_stage | Time, Stage, Product | B | BigQuery revenue_by_stage_product | Monthly | Growth |
| L5 | Ratio de Activación | Activation Ratio | ACTIVE / (REGISTERED + KYC + DEPOSITED + ACTIVE) | Time, Geo | B | BigQuery | Weekly | Growth |
| L6 | Tasa de Decaimiento | Decay Rate | (ACTIVE→DORMANT count) / ACTIVE_start | Time, Geo, Market Condition | B | BigQuery | Weekly | Growth |
| L7 | Densidad de Producto | Product Density Distribution | % users with 1, 2, 3, 4+ products | Time, Geo, Archetype | B | BigQuery cross_product_adoption | Monthly | Growth |

### Cross-Product Metrics (Tier B-C)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| X1 | Tasa Cross-Sell | Cross-Sell Rate | users_adopting_product_B / users_active_product_A | Time, Product pair, Geo | B | BigQuery | Monthly | Growth |
| X2 | Tiempo a 2º Producto | Time to Second Product | MEDIAN(second_product_fm - first_product_fm) | Cohort, Geo, Archetype | C | BigQuery | Monthly | Growth |
| X3 | Penetración B2M | B2M Token Penetration | users_holding_B2M / MMU | Time, Geo | B | BigQuery + Space Center | Monthly | Growth |
| X4 | Distribución Tiers | Space Center Tier Distribution | COUNT per tier / MMU | Time, Geo | C | Space Center data | Monthly | Growth |
| X5 | Penetración DCA | DCA Penetration Rate | users_with_active_DCA / MMU | Time, Geo | B | BigQuery | Weekly | Growth |
| X6 | Prima Multi-Producto | Multi-Product Retention Premium | retention_2plus_products / retention_1_product | Cohort | C | BigQuery | Monthly | Growth |

### Unit Economics (Tier B)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| U1 | LTV Cohorte | Cohort-Based LTV | See Section 4.3 below | Cohort, Geo, Channel, Product, Archetype | B | BigQuery (cohort_revenue_curves) | Monthly | Growth |
| U2 | LTV:CAC | LTV to CAC Ratio | LTV / CAC | Channel, Geo, Product | B | Derived | Monthly | Growth |
| U3 | Payback | Payback Period | Months until cumulative_revenue >= CAC | Channel, Geo | B | BigQuery | Monthly | Growth |
| U4 | GRR | Gross Revenue Retention | Revenue_retained / Revenue_start (excl expansion) | Time, Geo, Segment | B | BigQuery | Monthly | Growth |

### Referral Metrics (Tier C)

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| RF1 | Factor K | K-Factor | avg_invites_per_user × conversion_per_invite | Time, Geo | C | BigQuery + Referral system | Monthly | Growth |
| RF2 | % Registros Referidos | Referral Registration % | referred_registrations / total_registrations | Time, Geo | C | Referral system | Monthly | Growth |
| RF3 | Prima LTV Referidos | Referral LTV Premium | LTV_referred / LTV_non_referred | Cohort | C | BigQuery | Monthly | Growth |

### Card Metrics (Tier B-C)

Card is the biggest product gap: 0.26% penetration vs 42-48% industry, 29% monthly churn. These metrics are critical for tracking the Card growth initiative.

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| CD1 | Penetración Card | Card Penetration Rate | card_activated_users / MMU | Time, Geo | B | BigQuery + Card system | Monthly | Growth |
| CD2 | Tasa Activación Card | Card Activation Rate | cards_activated_period / cards_ordered_period | Time, Geo | B | Card system | Weekly | Growth |
| CD3 | Card MAU | Card Monthly Active Users | COUNT(DISTINCT user_id WHERE card_tx_30d > 0) | Time, Geo | B | Card transaction data | Monthly | Growth |
| CD4 | Churn Card Mensual | Card Monthly Churn Rate | users_no_card_tx_30d / card_mau_start | Time, Geo | B | Card transaction data | Monthly | Growth |
| CD5 | Interchange por Usuario | Interchange per Active Card User | SUM(interchange_revenue) / card_mau | Time, Geo | C | Card transaction data | Monthly | Growth |
| CD6 | Ticket Medio Card | Avg Card Transaction Size | SUM(card_tx_volume) / COUNT(card_transactions) | Time, Geo | C | Card transaction data | Monthly | Growth |
| CD7 | Card→Second Product | Card Cross-Sell Rate | card_users_adopting_other_product / card_active_users | Time, Product pair | C | BigQuery | Monthly | Growth |

**Card dashboard requirement:** Card metrics should have their own operational dashboard given the magnitude of the gap. Track CD1 (penetration) and CD4 (churn) as leading indicators. The 29% monthly churn rate means the Card team is replacing nearly 1/3 of active users every month. This is a leaky bucket that must be fixed before scaling Card acquisition.

### AUC Metrics (Assets Under Custody, Tier B)

AUC is the primary driver of recurring revenue (Earn yield spread, Staking commission, Loan interest). Total AUC determines Bit2Me's revenue floor in bear markets. These metrics were missing from v1.0.

| # | Nombre Español | English Name | Formula | Dimensions | Tier | Source | Freq | Owner |
|---|---------------|-------------|---------|-----------|------|--------|------|-------|
| AUC1 | AUC Total | Total Assets Under Custody | SUM(all user balances in EUR equivalent) | Time, Geo, Product, Asset type | B | BigQuery balance snapshots | Daily | Growth / Data |
| AUC2 | AUC por Producto | AUC by Product | SUM(balance) per product (Earn, Staking, Brokerage wallet, Loan collateral) | Time, Geo, Product | B | BigQuery | Weekly | Growth |
| AUC3 | Flujo Neto AUC | Net AUC Flow | SUM(deposits) - SUM(withdrawals) per period | Time, Geo, Product, Segment | B | BigQuery deposit/withdrawal tables | Weekly | Growth |
| AUC4 | AUC por Usuario | AUC per Monetized User | AUC_total / MMU | Time, Geo | B | BigQuery | Monthly | Growth |
| AUC5 | Ratio Stablecoin AUC | Stablecoin AUC Ratio | AUC_stablecoins / AUC_total | Time, Geo | C | BigQuery | Monthly | Growth |

**AUC interpretation:** AUC grows via 3 mechanisms: (1) new deposits, (2) asset price appreciation, (3) yield compounding. In a bear market, mechanism 2 works against you. Track Net AUC Flow (AUC3) to separate "users adding money" from "Bitcoin went up." If Net AUC Flow is negative but AUC is flat, it means price appreciation is masking withdrawals. This is a danger signal.

**Recurring Revenue Ratio connection:** Recurring_Revenue_Ratio (M6 in Monetization Metrics) is driven by AUC. Growing AUC1 while maintaining yield spreads directly improves the recurring revenue floor. Target: AUC growth of 5-10% QoQ independent of asset price movements (measured via Net AUC Flow only).

---

## 4.3 LTV Formula (Cohort-Based, Non-Circular)

### The Problem with the Current Approach

```
WRONG: LTV = (1 / churn_rate) × ARPU = Lifetime × ARPU
```

This is circular because:
1. It assumes constant churn rate (churn varies by month and market condition)
2. It uses average ARPU (ARPU changes as users mature)
3. It produces a single number that hides the decay curve shape

### Correct Formula: Cohort-Based LTV

```
LTV(cohort) = Σ [Revenue_month_t(cohort) × Survival_rate_month_t(cohort)]
              for t = 1 to horizon (typically 24 months)
```

Where:
- `Revenue_month_t(cohort)` = average revenue per surviving user in month t
- `Survival_rate_month_t(cohort)` = % of cohort still active at month t (from retention curve)
- `horizon` = 24 months (or 12 months for conservative estimate)

### SQL Implementation

```sql
-- Cohort-based LTV calculation
WITH cohort_monthly AS (
    SELECT
        fm_cohort_month,  -- YYYY-MM of FM event
        acquisition_channel,
        geography,
        TIMESTAMP_DIFF(r.revenue_month, u.fm_date, MONTH) AS months_since_fm,
        COUNT(DISTINCT r.user_id) AS surviving_users,
        SUM(r.revenue) AS total_revenue,
        SUM(r.revenue) / NULLIF(COUNT(DISTINCT r.user_id), 0) AS arpu_surviving
    FROM user_fm u
    JOIN monthly_revenue r ON u.user_id = r.user_id
    WHERE r.revenue_month >= u.fm_date
    GROUP BY 1, 2, 3, 4
),
cohort_size AS (
    SELECT fm_cohort_month, acquisition_channel, geography,
           COUNT(DISTINCT user_id) AS cohort_size
    FROM user_fm
    GROUP BY 1, 2, 3
)
SELECT
    cm.fm_cohort_month,
    cm.acquisition_channel,
    cm.geography,
    cm.months_since_fm,
    cm.surviving_users,
    cs.cohort_size,
    cm.surviving_users / NULLIF(cs.cohort_size, 0) AS survival_rate,
    cm.arpu_surviving,
    cm.arpu_surviving * (cm.surviving_users / NULLIF(cs.cohort_size, 0)) AS ltv_contribution_month_t,
    SUM(cm.arpu_surviving * (cm.surviving_users / NULLIF(cs.cohort_size, 0)))
        OVER (PARTITION BY cm.fm_cohort_month, cm.acquisition_channel, cm.geography
              ORDER BY cm.months_since_fm) AS cumulative_ltv
FROM cohort_monthly cm
JOIN cohort_size cs ON cm.fm_cohort_month = cs.fm_cohort_month
    AND cm.acquisition_channel = cs.acquisition_channel
    AND cm.geography = cs.geography
ORDER BY cm.fm_cohort_month, cm.months_since_fm
```

### Worked Example (Illustrative, Using Known Bit2Me Data Where Available)

**Cohort:** Spain, Paid channel, January 2025 FM users
**Cohort size:** 500 users (hypothetical)
**Market condition at acquisition:** Neutral

| Month | Surviving Users | Survival Rate | ARPU (Surviving) | LTV Contribution | Cumulative LTV |
|-------|----------------|--------------|-----------------|------------------|---------------|
| M1 | 500 | 100% | €15 | €15.00 | €15.00 |
| M2 | 225 | 45% | €18 | €8.10 | €23.10 |
| M3 | 175 | 35% | €20 | €7.00 | €30.10 |
| M6 | 125 | 25% | €25 | €6.25 | ~€55 |
| M12 | 90 | 18% | €30 | €5.40 | ~€100 |
| M18 | 75 | 15% | €32 | €4.80 | ~€130 |
| M24 | 65 | 13% | €35 | €4.55 | ~€155 |

**Notes:**
- ARPU increases for surviving users (power law: users who stay spend more)
- Survival rate drops steeply in M1-M3, then flattens (the "loyal core" emerges)
- Total LTV at 24 months: ~€155 per user acquired
- If CAC (Paid, Spain) = €40-€50: LTV:CAC = 3.1x-3.9x (healthy)
- Numbers above are ILLUSTRATIVE. Must be populated with actual Bit2Me cohort data. Mark all as REQUIRES VALIDATION.

### Market Condition Modifier

```
LTV_adjusted = LTV_base × market_modifier

WHERE market_modifier =
    CASE
        WHEN market_condition_at_acquisition = 'BULL' THEN 1.4
        -- Bull acquirees: higher initial spend but also higher initial churn
        WHEN market_condition_at_acquisition = 'NEUTRAL' THEN 1.0
        WHEN market_condition_at_acquisition = 'BEAR' THEN 0.7
        -- Bear acquirees: lower spend but better long-term survival
    END
```

Bear market acquirees are paradoxically MORE valuable long-term: lower initial spend but higher 12-month survival (they came for a reason, not FOMO). The modifier reflects initial spend, not lifetime quality. Separate bear-acquired cohort LTV curves to validate.

---

## 4.4 Revenue Forecasting Model (Stage-Based Projection)

### Formula

```
Projected_Monthly_Revenue = Σ [
    Population_stage_i
    × Revenue_per_user_stage_i
    × Expected_transition_rate_i
    × market_modifier
]
```

### Model Structure

**Three conditional forecasts, not one range.** A €1.3M-€2.9M range is too wide for Pablo to plan with. Instead, present three scenarios tied to market condition, which is observable in real-time.

#### BEAR Scenario (BTC 30d return < -15%)

| Stage | Population (Spain) | Rev/User/Mo | Activity Factor | Projected Revenue |
|-------|-------------------|-------------|-----------------|-------------------|
| FIRST_MONETIZATION | ~3,000 (fewer new users) | €10-€15 | 0.35 | €10K-€16K |
| ACTIVE | ~35,000 | €12-€20 (volume drops) | 0.85 | €357K-€595K |
| POWER_USER | ~6,000 | €50-€100 (reduced trading, Earn buffers) | 0.90 | €270K-€540K |
| AT_RISK | ~15,000 (swells in bear) | €3-€8 | 0.25 | €11K-€30K |
| DORMANT_WITH_BALANCE | ~4,414 | €2-€8 (passive only) | 0.10 | €0.9K-€3.5K |
| REACTIVATED | ~300 (few reactivations) | €8-€15 | 0.40 | €1K-€1.8K |
| **TOTAL BEAR** | | | | **€650K-€1.2M/month** |

#### NEUTRAL Scenario (BTC 30d return between -15% and +15%)

| Stage | Population (Spain) | Rev/User/Mo | Activity Factor | Projected Revenue |
|-------|-------------------|-------------|-----------------|-------------------|
| FIRST_MONETIZATION | ~6,000 | €15-€25 | 0.45 | €40K-€68K |
| ACTIVE | ~40,000 | €20-€35 | 0.90 | €720K-€1,260K |
| POWER_USER | ~7,000 | €80-€180 | 0.95 | €532K-€1,197K |
| AT_RISK | ~10,000 | €5-€15 | 0.30 | €15K-€45K |
| DORMANT_WITH_BALANCE | ~4,414 | €2-€10 | 0.10 | €0.9K-€4.4K |
| REACTIVATED | ~1,000 | €10-€25 | 0.50 | €5K-€12.5K |
| **TOTAL NEUTRAL** | | | | **€1.3M-€2.6M/month** |

#### BULL Scenario (BTC 30d return > +15%)

| Stage | Population (Spain) | Rev/User/Mo | Activity Factor | Projected Revenue |
|-------|-------------------|-------------|-----------------|-------------------|
| FIRST_MONETIZATION | ~10,000 (FOMO inflow) | €20-€35 | 0.50 | €100K-€175K |
| ACTIVE | ~45,000 | €35-€55 (volume spikes) | 0.92 | €1,449K-€2,277K |
| POWER_USER | ~9,000 | €150-€300 (peak trading) | 0.95 | €1,283K-€2,565K |
| AT_RISK | ~6,000 (shrinks in bull) | €10-€20 | 0.40 | €24K-€48K |
| DORMANT_WITH_BALANCE | ~4,414 | €3-€12 | 0.15 | €2K-€7.9K |
| REACTIVATED | ~3,000 (reactivation wave) | €15-€30 | 0.55 | €25K-€50K |
| **TOTAL BULL** | | | | **€2.9M-€5.1M/month** |

**How to report to Pablo:** "This month, market condition is [NEUTRAL]. Our base forecast for Spain LC revenue is €1.3M-€2.6M. We're tracking at €X through Week N, which puts us [above/below/on] the base case."

**Notes:**
- REQUIRES VALIDATION: All Rev/User/Mo figures are estimates. P0 data request: revenue per user per lifecycle stage per market condition.
- POWER_USER population estimates are EXCLUSIVE of ACTIVE (priority-ordered classifier).
- The model improves monthly as actual data replaces estimates.

### Market Modifier

Aligned with Chunk 1 v1.1 market_condition definition (btc_30d_return thresholds):

```
-- Maps to Chunk 1 BULL/NEUTRAL/BEAR + adds granularity for forecasting
market_modifier = CASE
    WHEN btc_30d_return > 0.25 THEN 1.5  -- Strong bull (within BULL condition)
    WHEN btc_30d_return > 0.15 THEN 1.3  -- Bull (matches Chunk 1 BULL threshold)
    WHEN btc_30d_return > -0.15 THEN 1.0 -- Neutral (matches Chunk 1 NEUTRAL range)
    WHEN btc_30d_return > -0.25 THEN 0.7 -- Bear (matches Chunk 1 BEAR threshold)
    ELSE 0.5                              -- Deep bear (within BEAR condition)
END
```

**Chunk 1 mapping:** BULL (>0.15) maps to modifiers 1.3-1.5. NEUTRAL (-0.15 to 0.15) maps to 1.0. BEAR (<-0.15) maps to 0.5-0.7. The 5-level modifier adds granularity within each condition for revenue forecasting without conflicting with the 3-level classification used elsewhere.

### How A/B Test Impact Feeds the Forecast

```
IF test_X increases L1→L2 conversion by 5 percentage points:
    Additional FM users/month = KYC_population × 0.05
    Additional revenue = additional_FM_users × ARPU_FM × survival_rate_12m
    Annualized: additional monthly × 12

Example:
    KYC population (Spain) = 29,010
    Monthly flow through KYC ≈ 3,400 (850/week × 4)
    5pp lift = 170 additional FM users/month
    At €155 LTV (24m): 170 × €155 = €26,350 incremental LTV per month of new cohort
```

### Confidence Intervals

Report forecasts as ranges, not point estimates:

```
Forecast = [Conservative, Base, Optimistic]
Conservative = base_projection × 0.7
Base = base_projection
Optimistic = base_projection × 1.3
```

Tell Pablo: "We project €X-€Y this month from lifecycle, with base case €Z." The range narrows as the model gets real data.

---

## 4.5 Incrementality Measurement

### Methodology: Permanent Holdout

```
Total addressable population
    ├── 90% Treatment group (receives CRM campaigns)
    └── 10% Holdout group (receives nothing)

Incrementality = Treatment_conversion - Holdout_conversion
```

### Implementation Rules

1. **Holdout is permanent.** Same 10% of users never receive any CRM treatment. This gives a clean baseline.
2. **Random assignment** at user level, stratified by lifecycle stage and geography.
3. **Measurement:** Compare conversion/revenue metrics between treatment and holdout monthly.
4. **Never break the holdout** for "important campaigns." The moment you break it, you lose the baseline.

### Statistical Significance Requirements

The holdout methodology only produces valid results with sufficient sample size and time.

**Minimum holdout duration:** 8 weeks before drawing any conclusions. CRM effects accumulate; measuring at Week 2 produces noise, not signal.

**Sample size per segment:** For a segment with 10,000 users (10% holdout = 1,000), assuming base conversion of 5%, the minimum detectable effect (MDE) at 80% power and 95% confidence is ~2.5 percentage points. This means you can only detect lifts from 5% to 7.5%+. Smaller lifts are real but invisible at this sample size.

```
Minimum sample per segment for meaningful measurement:
  Base rate 5%:   Need 1,000+ holdout users to detect 2.5pp lift
  Base rate 10%:  Need 600+ holdout users to detect 3pp lift
  Base rate 20%:  Need 400+ holdout users to detect 5pp lift
```

**Segments too small for holdout:** If a segment has <4,000 users (holdout <400), incrementality measurement for that segment alone won't reach significance. Options: (a) combine with similar segments for measurement, (b) use longer measurement window (12+ weeks), (c) accept directional signal without statistical certainty.

**Reporting rule:** Always report incrementality with confidence interval. "CRM generated €120K ± €35K incremental revenue this month" is honest. "CRM generated €120K" without interval implies false precision.

### Incrementality Calculation

```sql
-- Monthly incrementality measurement
SELECT
    campaign_segment,
    COUNT(DISTINCT CASE WHEN group = 'treatment' AND converted = TRUE THEN user_id END)
        / NULLIF(COUNT(DISTINCT CASE WHEN group = 'treatment' THEN user_id END), 0) AS treatment_rate,
    COUNT(DISTINCT CASE WHEN group = 'holdout' AND converted = TRUE THEN user_id END)
        / NULLIF(COUNT(DISTINCT CASE WHEN group = 'holdout' THEN user_id END), 0) AS holdout_rate,
    treatment_rate - holdout_rate AS incremental_lift,
    incremental_lift * treatment_population * revenue_per_conversion AS incremental_revenue
FROM user_experiment_groups
GROUP BY campaign_segment
```

### What This Changes

Current CRM-attributed revenue (YTD): €240K (20% of total).

After incrementality measurement, expect this to drop to €100K-€150K in true incremental revenue. The remainder is revenue that would have happened anyway (organic behavior attributed to CRM because of the 7-day push window).

This is not bad news. It's accurate news. It means:
- CRM budget should be evaluated on €100-150K incremental, not €240K attributed
- Some "CRM" revenue should be reclassified to "Organic/Direct"
- Attribution model needs recalibration (Phase 6, Chunk 3)

---

## Sync with Salvia's Segmentation — Summary

| This Chunk Introduces | Relationship to Salvia's Work |
|----------------------|------------------------------|
| 10 lifecycle stages (vs L0-L5) | EXTENDS. Adds DEPOSITED_ONLY, AT_RISK, POWER_USER, REACTIVATED. Splits L5 into DORMANT_ZERO + CHURNED. |
| Per-product lifecycle overlays | NEW. Overlays on Salvia's per-product clusters. Her clusters define WHO (which cluster), overlays define WHERE (which product lifecycle stage). |
| Cross-product adoption matrix | NEW. Requires unified cluster table she's building. |
| DCA as retention bridge | NEW concept for lifecycle. Requires DCA tracking data. |
| B2M flywheel mapping | EXTENDS Space Center work (Rut's domain). Maps tier progression to lifecycle stages. |
| Revenue forecasting model | NEW. Uses Salvia's population data as input. |
| Incrementality methodology | NEW. Changes how CRM revenue is reported. Requires Patri/Katy/Miguel alignment. |
| GTM lifecycle (Portugal template) | EXTENDS. Uses Salvia's PT conversion data. Adds structured phase framework. |
| Salvia's requested filters | ANSWERED: "Login by 1/3/6/12 months" = dormancy sub-tiers. "Ha operado" = DEPOSITED_ONLY vs FM stages. "B2B/B2C" = Segment dimension. |

**Action items for sync with Salvia:**
1. Share this document for feedback (P0, this week).
2. Validate population estimates for new stages (AT_RISK, POWER_USER, DEPOSITED_ONLY).
3. Align on per-product lifecycle overlay definitions with her cluster owners (Juan Fornell for Brokerage, Álvaro Durán for Earn/Loan).
4. Agree on holdout group implementation with Patri (CRM operational change).
5. Schedule joint session: map this framework's stages to Qlik Activation Main v4 Life Cycle panel fields.

---

*End of Chunk 2. Awaiting validation before proceeding to Chunk 3 (Reporting + Attribution + Testing).*
*Dependencies on Chunk 3: reporting templates use metrics from this catalog; attribution model uses revenue types from Chunk 1; testing framework uses lifecycle stages and archetypes as targeting dimensions.*
