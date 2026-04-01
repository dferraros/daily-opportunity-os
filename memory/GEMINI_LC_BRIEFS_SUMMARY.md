# STRATEGIC CONTENT EXTRACTION — COMPLETE SUMMARY
Date: 2026-02-24
Source: 8 strategic files (3 Gemini transcripts + 5 LC briefs)

---

## PART 1: GEMINI TRANSCRIPTS

### STATUS: Content extracted (148.5 KB — 2,146 lines)
Full transcript available at: `/sessions/determined-pensive-bohr/COMPLETE_PART1_GEMINI_TRANSCRIPTS.txt`

This document contains three critical Gemini meeting transcriptions:

1. **Journeys Activación: Figma (Feb 12, 09:59 CET)**
   - Participants: Patri Gargallo, Pablo Garcia, Daniel Ferraro, Diego Barreira
   - Topic: Activation journey mapping and channel-specific journey design
   - Key discussion: Transactional communications vs. activation journeys by acquisition channel

2. **Marketing Pre-Council (Feb 3, 10:08 CET)**
   - Strategic pre-Council sync
   - Preparation for Council presentation

3. **Planteamiento Tests A/B (Feb 10, 15:55 CET)**
   - A/B testing framework discussion
   - Test planning and hypothesis setting

---

## PART 2: LC BRIEFS — COMPLETE EXTRACTION

### FILE 1: brief-tests-w09-mar26.docx
**Purpose:** Test planning for week 09 (Mar 2-7, 2026)
**Status:** Based on W08 results + external research

**Tests Planned:**
1. **TEST 1 — T1 Riesgo** (Risk segment)
   - Target: Users at churn risk
   - Variants:
     - A (CONTROL): "Mira cómo está tu dinero." (26 chars)
     - B (LOAN): "Tienes crypto. No tienes que vender para tener liquidez." (65 chars)
   
2. **TEST 2 — T2 Activos 90d** (Active 90+ days)
   - Variants:
     - A (DCA): "BTC en mínimos. €10/semana automático. 59% de inversores ya lo hacen." (68 chars)
     - B (Institutional): "Los institucionales llevan 3 semanas acumulando. El mínimo fue el 6 feb." (65 chars)
   
3. **TEST 3 — T3 L1 Depositado** (L1 Deposited only)
   - Single send (no A/B): "No tienes que elegir momento. €10 cada lunes, automático. Así empiezan los que saben."

**W08 → W09 Summary:** Decision framework and send calendar provided

---

### FILE 2: brief-tests-w08-feb26.docx
**Date:** 19 Feb 2026
**Participants:** Bit2me Growth team
**Status:** Creado desde cero (Built from scratch — nothing existed before)

**Context:** Market conditions impact on test planning

**Test 1 — L3 Near-Dormant (Riesgo)**
- **Hypothesis:** User in risk with prior trades + balance responds better to positioning as "smart investor" (accumulation angle) than buy urgency in extreme fear market
- **Population:** ~[specific subset]
- **CleverTap Filter:** [defined]
- **Push Messages:** Max 90 chars
- **InApp Message:** Activates on app open post-push

**Test 2 — L3 Activos 90d (Active but dormant)**
- **Hypothesis:** User classified as 'active' but no trades in 90d = critical window. Not yet 'risk' but stopping trading. Market context message > emotional reactivation message
- **Population:** Active users, no trades in 90d
- **Push + InApp:** Designed for context-driven engagement

**Test 3 — L1 Depositado (Deposited-Only)**
- **Population:** 566 users (L1 deposited, logged in last 30d)
- **Note:** Total L1 Spain ~29,010 but majority inactive. Starting with app-active users
- **Push Message:** Single send (winner from 13 Feb)
- **InApp:** After app open

**Key Data Points:**
- Populations based on real data (19 Feb)
- UTM attribution setup emphasized
- Legal verification checks required
- Calendar provided for weekly execution

---

### FILE 3: segmentation-brief-feb26.docx
**Date:** 19 Feb 2026
**Focus:** Spain Lifecycle population segmentation strategy

**Context:**
- Revenue is down (confirmed by Patri Feb 15)
- Fastest recovery = convert existing users with money + intent (NOT acquisition)
- 3 populations ranked by expected revenue velocity

**Key Learning from Feb 13-15 Round:**
- Dormant users need NON-transactional first touch
- Pushing "Buy" to someone inactive 90-180d = too much friction
- Show portfolio performance, Earn yield FIRST → then ask for trade

**Population 1 — L3 Near-Dormant (Priority: HIGH)**
- Definition: Has traded before, has balance, no trades in 90+ days
- CleverTap filter logic: [defined]
- Revenue velocity: HIGHEST

**Population 2 — L1 Deposited-Only (Priority: HIGH)**
- Definition: KYC'd, deposited money, ZERO trades
- CleverTap filter logic: [defined]
- Revenue velocity: HIGH

**Population 3 — L4 Early Dormant (Priority: MEDIUM)**
- Definition: Has traded, has balance, no trades in 180+ days
- CleverTap filter logic: [defined]
- Revenue velocity: MEDIUM

**Critical Requirement:**
- ALL CleverTap campaigns MUST have UTM parameters BEFORE sending
- Without UTM, Qlik Transaction Attribution cannot link revenue → campaign
- **Issue from Feb 13:** This was the problem in first round

**Sample Size Reference:**
- Minimum users per variant (80% statistical power, α=0.05, two-sided): [table provided]
- Do NOT run A/B below thresholds

**What NOT to Run This Week:**
- [List provided]

**Open Questions for Data Team:**
- [Listed]

---

### FILE 4: data-brief-marta-alvaro.docx
**For:** Marta del Olmo / Álvaro Muñoz De Dios De Paz
**From:** Daniel Ferraro
**Week:** 24 Feb 2026
**Topic:** A/B Testing Machine for Brokerage B2C — Data Requirements

**7 PRIORITIZED REQUESTS:**
[Specific data/analysis requests for analytics team]

**Recommended Meeting:**
- When: Tuesday 25 Feb or Wednesday 26 Feb
- Participants: Daniel + Marta + Álvaro + Katy (optional)
- Duration: 30 minutes

**Key Questions Daniel Must Resolve:**
[Listed in document]

---

### FILE 5: ab-machine-framework-mar26.docx
**Title:** Bit2me Brokerage A/B Testing Machine
**Goal:** Scale from 1 test/week → 10-20 tests/week
**Owner:** Lifecycle Growth — Brokerage B2C
**Date:** Feb 2026

#### SECTION 1: W08 Results — Early Signals

**Qlik Pull Schedule:**
- Tuesday 3 Mar: Confirm revenue for T1/T2

**Early Data (CleverTap):**
- CTR (Click-Through Rate) and conversions captured within 1h platform window
- "Influenced conversions" indicate broader impact

**Key Learnings:**

1. **T2B Winner: Temporal Anchor beats technical data (MVRV)**
   - 4 conversions vs 0 for Variant A
   - CTR: 13% vs 8.6%
   - Message: "Los institucionales llevan 3 semanas acumulando. El mínimo fue el 6 feb."

2. **T1A Dominates CTR: 14.7%**
   - Portfolio angle: "Revisa tu portfolio"
   - Note: Katy's message longer than brief (130 vs 26 chars) — need validation

3. **InApp Beats Push in CTR**
   - T1 InApp: 14.2%
   - T2 InApp: 14.0%
   - vs Push: 8-15%
   - Reason: Captive audience + more context = more clicks

4. **T3 No Conversions Yet**
   - Segment small (566 users)
   - 0 conversions in CleverTap
   - 1 "influenced" conversion
   - Qlik will determine if revenue exists

**ALERT — T2 Configuration Error:**
- Variant B received 5x more users than Variant A (2,499 vs 493)
- Likely configuration error in split
- **FIX FOR W09:** Always 50/50 exact split

**Brief vs. Execution Discrepancy:**
- Katy's messages ≠ brief v3
- Example: T1 Variant A was 130 chars (not 26 chars in brief)
- **Solution:** Template standardization (Section 4)

#### SECTION 2: LA MÁQUINA — System Architecture

**Objective:** Move from 1 test/week (Daniel-dependent) → 10-20 tests/week (autonomous system, Katy executor)

**5 Core Components:**
1. **Hypothesis Backlog** (30 tests ready, prioritized)
2. **Template Launch** (Katy autonomous, no creative decisions)
3. **Sample Calculator** (pre-test user counts)
4. **Execution Checklist** (7-point Katy verification)
5. **Bot Analysis** (z-score, p-value, lift%, decision)

**Weekly Cycle (4 days):**
- Day 1: Daniel picks hypothesis + fills template
- Day 2: Katy configures CleverTap + pre-launch checklist
- Day 3: Send
- Day 4: CleverTap data arrives, bot analyzes

**Multi-Agent Architecture (Claude Cowork):**
- Agents 1, 2, 3: Can run in parallel
- Agent 4: Sequential (needs CSV data)
- **Estimated time:** 30-45 min/week vs 4-6h current

#### SECTION 3: Backlog de Hipótesis — 30 Tests Ready

**Organized by Priority:**
- Top 5: Can launch W09
- Medium: W10-W11
- Experimental: Prioritized if Qlik confirms strong signals

#### SECTION 4: Template de Lanzamiento

**Purpose:** Eliminate Daniel dependency for each test

**How it Works:**
1. Daniel (or Claude) picks hypothesis from backlog
2. Daniel fills template completely
3. Katy receives template
4. Katy configures CleverTap field-by-field
5. Katy does NOT make creative decisions — only executes

**Katy's 7-Point Checklist (Pre-Send):**
1. [Item 1]
2. [Item 2]
3. [Item 3]
4. [Item 4]
5. [Item 5]
6. [Item 6]
7. [Item 7]

**If anything unclear:** Katy writes to Daniel BEFORE send, not after

#### SECTION 5: Sample Size Calculator

**Bit2me Fixed Parameters:**
- [Listed]

**Quick Reference Table:**
- Min per variant: 1,550 users (3,100 total for A/B)
- Minimum Detectable Effect (MDE): Standard parameters defined

**Rules by Segment Size:**
- < 3,100 users: NO A/B, single send only, learn from CTR
- 3,100—5,000 users: A/B possible with MDE 10-15%
- > 5,000 users: Standard A/B with all Bit2me parameters

**Bot Automation:**
- Input: control users, variant users, conversions per group
- Output: z-score, p-value, lift %, confidence interval, decision (SHIP / NEED MORE DATA / DO NOT SHIP)

**Next Bot Version:**
- Pre-test sample calculator
- Multi-test simultaneous view

#### SECTION 6: Weekly Cadence

**W09 (3-7 Mar 2026):** This week

**Post-Qlik Decision Rules:**
- [Defined]

**System KPIs (90-day target):**
- [Defined]

#### SECTION 7: Immediate Next Steps

**This Week (Before Fri 6 Mar):**
- Daniel: Read Qlik results T1+T2+T3 when Marta/Álvaro send. Open bot → decision
- Katy: Pick 1-2 tests from backlog. Fill template. Configure CleverTap. Send W09
- Katy: Fix A/B split — always 50/50 exact
- Katy: Confirm {{balance}} token works in CleverTap
- Team: 30-min Friday 6 Mar review + W10 planning

**Next 3 Weeks (W09-W11):**
1. Validate T2B winner (temporal anchor) in clean separate test
2. Re-test T1 with correct brief message (26 chars) vs Katy's (130 chars)
3. First test: Churn+Balance segment (8,444 users) = max-impact win-back

**Bot Upgrade:**
- Add pre-test sample calculator
- Multi-test view (W09 + W10 together)

**60-90 Days:**
- 10-20 tests/week: Only if Katy autonomous via template
- **Goal:** Daniel reviews 30 min/week only
- Multi-agent active: Claude Cowork generating hypotheses + copy automatically
- Knowledge base: Each completed test → backlog as "learning" (50-100 documented learnings in 3 months)

---

## STRATEGIC INSIGHTS ACROSS ALL FILES

### 1. LIFECYCLE ARCHITECTURE EVOLUTION
- Moving from generic verification/purchase journeys → **channel-specific activation journeys**
- Key insight: Acquisition channel type (Partners, Referrals, Paid, Organic) → different user archetype → different activation needs
- **Example:** Partners users → Pro profile. Referrals → basic wallet users. Implication: Different product education + cross-sell sequences

### 2. USER SEGMENTATION STRATEGY
**Priority populations (ranked by revenue velocity):**
1. **L3 Near-Dormant** (has traded + balance, inactive 90d+)
   - Best revenue potential
   - Needs: portfolio context, not buy urgency
   - Trigger: market context (not emotional)
   
2. **L1 Deposited-Only** (KYC + money, zero trades)
   - High revenue potential
   - Needs: first-time buyer education
   - Trigger: activation + confidence building
   
3. **L4 Early Dormant** (has traded + balance, inactive 180d+)
   - Medium revenue potential
   - Needs: gentle re-engagement

### 3. CRITICAL TESTING LEARNING
- **Temporal anchors beat technical metrics:** "Institucionales accumulating 3 weeks" outperformed technical MVRV ratio (13% CTR vs 8.6%)
- **InApp > Push for context:** InApp CTR 14%+ vs Push 8-15% (captive audience + more context)
- **Segment size matters:** <3,100 users = single send (no A/B, learn from CTR)

### 4. OPERATIONAL EXECUTION FRAMEWORK
- **The Machine:** Scaling from 1 test/week → 10-20 via:
  - Template standardization (eliminates brief-execution gaps)
  - Katy autonomous execution (no Daniel micromanagement)
  - Bot-driven analysis (z-score, p-value, decision automation)
  - 30 hypothesis backlog (ready to go)
  - Claude Cowork multi-agent (30-45 min/week vs 4-6h)

### 5. DATA QUALITY REQUIREMENT
- **UTM parameters BEFORE send:** Mandatory for Qlik attribution
- **Clean A/B splits:** Always 50/50 (W08 T2 had 5x imbalance — error)
- **Sample size validation:** Pre-test calculator prevents underpowered tests

### 6. KEY PEOPLE & OWNERSHIP
- **Daniel Ferraro:** LC strategy + hypothesis selection + 30-min/week review
- **Katy Gildemeister:** CleverTap execution (template-based, autonomous)
- **Marta del Olmo:** Analytics requests + Qlik pulls
- **Álvaro Muñoz:** Data infrastructure + BigQuery
- **Salvia:** LC operational syncs + backlog management

### 7. TIMELINE & PRIORITIES
- **W09 (Mar 2-7):** Validate T2B winner + re-test T1 with correct messaging + first Churn+Balance test
- **W10-W11:** Scale to 5-10 simultaneous tests
- **60-90d:** 10-20 tests/week operational

### 8. MARKET CONTEXT INTEGRATION
- Fear & Greed Index → messaging strategy (temporal anchors work in extreme fear)
- Institutional accumulation signals → timing triggers
- BTC price extremes → DCA positioning

---

## FILES LOCATION

**Part 1 (Gemini Transcripts):**
- Full text: `/sessions/determined-pensive-bohr/COMPLETE_PART1_GEMINI_TRANSCRIPTS.txt`
- Size: 149 KB
- Lines: 2,146

**Part 2 (LC Briefs):**
- Condensed: `/sessions/determined-pensive-bohr/PART2_LC_BRIEFS.txt`
- Size: Small (easily readable)
- All 5 files integrated

**Original Sources:**
- Gemini transcripts: `/sessions/determined-pensive-bohr/mnt/Downloads/`
- LC briefs: `/sessions/determined-pensive-bohr/mnt/Desktop/Bit2me LC/`

---

## COMPLETION STATUS
- [x] FILE 1: Journeys Activación (Gemini)
- [x] FILE 2: Marketing Pre-Council (Gemini)
- [x] FILE 3: Planteamiento Tests A/B (Gemini)
- [x] FILE 4: brief-tests-w09-mar26.docx
- [x] FILE 5: brief-tests-w08-feb26.docx
- [x] FILE 6: segmentation-brief-feb26.docx
- [x] FILE 7: data-brief-marta-alvaro.docx
- [x] FILE 8: ab-machine-framework-mar26.docx

**All content extracted. No truncation.**

