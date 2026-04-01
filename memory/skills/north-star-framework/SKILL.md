# SKILL: North Star Framework
**Domain:** Growth Strategy / Lifecycle Metrics
**Owner:** Daniel Ferraro — Head of Growth, Bit2Me
**Last updated:** 2026-03-25

---

## PURPOSE

This skill teaches how to define, validate, and operate around a North Star Metric (NSM) for a crypto/fintech growth team. It is immediately applicable to Bit2Me's lifecycle context: 1.8M registered users, 23k MMU, M1 retention crisis, and a mandate that "el dinero viene del Life Cycle."

---

## 1. WHAT IS A NORTH STAR METRIC

The North Star Metric is the single metric that best captures the core value your product delivers to customers AND is the strongest leading indicator of long-term sustainable revenue.

It is NOT:
- Revenue (that is a lagging output, not a value signal)
- DAU/MAU (activity without value delivered is noise)
- A composite score (composite NSMs hide signal, create accountability gaps)

It IS:
- The moment users get the core value of your product
- Measurable weekly or monthly
- Owned by the team, not just analytics
- The number that, if it goes up consistently, you are confident the business is healthy

**The test:** "If this metric grows 20% and revenue does not follow within 90 days, is this still the right metric?" If yes, it is a vanity metric. If no, it is a real NSM candidate.

**Crypto/fintech translation:** Value is delivered when users successfully move money or grow assets through your platform. Registration is not value. KYC is not value. The first completed transaction is value.

---

## 2. CRITERIA FOR A GOOD NSM

Evaluate each candidate against all five criteria. Reject any metric that fails more than one.

### 2.1 Measures customer value, not company value
The metric should reflect something the user accomplished — not something you extracted from them.

| Measures Customer Value | Measures Company Value (avoid as NSM) |
|------------------------|---------------------------------------|
| First monetization completers | Revenue |
| Assets Under Custody | Fees collected |
| Weekly active traders | Ad impressions |
| Monthly Monetizable Users | ARPU |

Note: MMU sits in a grey zone. "Monetizable" is defined by company criteria (has traded, has balance). It measures potential company value more than delivered customer value. This tension is explored in section 4.

### 2.2 Leading indicator of revenue
Test this with data. The NSM should have a positive correlation with revenue with a lag of 30–90 days. If the correlation only appears with a 180-day lag, it is too slow to be actionable.

For crypto: FM (First Monetization) completers per week typically lead 30-day revenue by 3–5 weeks. AUC leads fee revenue by 1–3 months depending on volatility cycles.

### 2.3 Actionable by the team
The team must have direct levers to move this metric. If moving the metric requires actions outside the team's control (e.g., macroeconomic BTC price), it is a bad NSM.

Test: "Can we run a campaign this week that measurably moves this metric within 14 days?" If yes, it passes.

### 2.4 Understandable by everyone
Any team member — engineer, designer, CRM exec, analyst — should be able to explain the NSM without a glossary. If you need to define 3 terms to explain the metric, it is too complex.

Good: "Number of users who traded at least once this month"
Bad: "NURR-weighted MMU excluding Space Center tier 1-2 users in dormancy windows"

### 2.5 Not gameable
Can the metric increase without real value being delivered?

- "Registered users" is gameable (bot signups, incentivized registrations)
- "KYC completed" is less gameable but still inflatable with low-quality acquisition
- "Completed a trade above €10" is harder to game
- "MMU with at least 2 trades in 30 days" is harder to game than "any trade"

Add a quality floor to any NSM candidate to reduce gameability risk.

---

## 3. NSM SELECTION PROCESS

### Step 1: Map value moments for your product

List every moment in the user lifecycle where value is delivered. For Bit2Me:

| Stage | Value Moment | Candidate Metric |
|-------|-------------|-----------------|
| Onboarding | User completes KYC | KYC completers/week |
| Activation | User makes first trade (FM) | FM completers/week |
| Retention | User trades again within 30 days | M1 retention rate |
| Expansion | User holds balance / grows AUC | AUC growth |
| Engagement | User logs in and checks portfolio | WAU (weekly active users) |
| Monetization | User is fee-generating this month | MMU |

### Step 2: Identify which metric predicts retention best

For each candidate, run: corr(metric_week_N, retained_at_week_N+4).

The metric with the highest correlation to retention 4 weeks out is your strongest NSM candidate. This step requires BigQuery data. See the SQL template in section 3.5.

**Bit2Me hypothesis (validate with data):**
- FM completers/week likely predicts 30-day revenue with r > 0.7
- WAU likely predicts FM completers with r > 0.5
- MMU is coincident with revenue, not leading

### Step 3: Validate with correlation analysis

Run in BigQuery (adapt to your schema):

```sql
-- NSM candidate correlation analysis
-- Replace metric_a with your candidate, revenue_30d with 30-day forward revenue

WITH weekly_metrics AS (
  SELECT
    DATE_TRUNC(event_date, WEEK) AS week,
    COUNT(DISTINCT CASE WHEN event = 'first_trade' THEN user_id END) AS fm_completers,
    COUNT(DISTINCT CASE WHEN is_monthly_active AND has_traded THEN user_id END) AS mmu,
    COUNT(DISTINCT CASE WHEN last_login_days <= 7 THEN user_id END) AS wau,
    SUM(auc_eur) AS auc_total
  FROM bit2me_lifecycle.user_weekly_snapshot
  GROUP BY 1
),
lagged AS (
  SELECT
    w1.week,
    w1.fm_completers,
    w1.mmu,
    w1.wau,
    w2.revenue_30d  -- join to revenue table with 30-day lag
  FROM weekly_metrics w1
  LEFT JOIN revenue_weekly w2 ON w2.week = DATE_ADD(w1.week, INTERVAL 4 WEEK)
)
SELECT
  CORR(fm_completers, revenue_30d) AS corr_fm_vs_rev,
  CORR(mmu, revenue_30d)           AS corr_mmu_vs_rev,
  CORR(wau, revenue_30d)           AS corr_wau_vs_rev
FROM lagged;
```

### Step 4: Test with leading/lagging analysis

The NSM should be a LEADING indicator. Confirm by testing multiple lag windows (1 week, 2 weeks, 4 weeks, 8 weeks, 12 weeks) and finding the lag where correlation peaks.

| Lag Window | FM Completers vs Revenue | MMU vs Revenue |
|-----------|--------------------------|----------------|
| 1 week    | expected: moderate       | expected: high |
| 4 weeks   | expected: high (peak)    | expected: high |
| 8 weeks   | expected: high           | expected: moderate |
| 12 weeks  | expected: moderate       | expected: low |

If FM completers correlation peaks at 4 weeks and MMU peaks at 1 week, FM is the better NSM (it leads further, giving more time to act).

### Step 5: Select the NSM

Score each candidate 1–3 on each criterion:

| Criterion | FM Completers/Week | MMU | WAU | AUC |
|-----------|-------------------|-----|-----|-----|
| Customer value | 3 | 2 | 2 | 3 |
| Revenue leading | 3 | 2 | 2 | 2 |
| Actionable | 3 | 2 | 3 | 1 |
| Understandable | 3 | 2 | 3 | 2 |
| Not gameable | 2 | 2 | 1 | 3 |
| **Total** | **14** | **10** | **11** | **11** |

This scoring is a starting point. Bit2Me-specific data may change rankings. Validate before committing.

---

## 4. BIT2ME SPECIFIC — NSM ANALYSIS

### 4.1 Candidate overview

**FM Completers/Week (First Monetization)**
- Definition: distinct users completing their first trade (buy/sell) in a given week
- Why it's strong: the moment Bit2Me delivers its core value proposition. Post-FM users generate 96% of revenue (retention pool). Leading indicator by ~4 weeks.
- Why it's weak: only measures new-to-monetization flow. Ignores the 72.4k dormant users with €19.5M AUC who already crossed FM.

**MMU — Monthly Monetizable Users (current team choice)**
- Definition: users who have traded at least once in the last 30 days AND meet platform criteria
- Current level: 23k actual vs 30k target Mar 31
- Why it's the current choice: directly maps to the revenue base. Pablo Campos mandate: "el dinero viene del Life Cycle." MMU is the most legible metric for CEO reporting.
- Why it's not ideal as a pure NSM: it is near-coincident with revenue, not leading. It measures company-defined "monetizable" not a pure customer value moment.
- Best use: primary business health KPI, secondary NSM for executive reporting.

**WAU — Weekly Active Users**
- Definition: distinct users logging in or taking any platform action in a 7-day window
- Why it might be better as leading indicator: WAU leads MMU by 2–3 weeks. If WAU rises, MMU follows. More sensitive to product changes. Shorter feedback loop for experiments.
- Why it's risky alone: highly gameable (push notification opens count as "active"). AUC correlation is weaker. Does not guarantee monetization.
- Best use: operational leading indicator sitting one level above MMU in the hierarchy.

**AUC — Assets Under Custody**
- Definition: total EUR value of crypto held on Bit2Me across all users
- Current level: €19.5M across 72.4k dormant users with balance
- Why it's interesting: represents latent monetization potential. Rising AUC from dormant users signals FOMO Agent reactivation success.
- Why it fails as NSM: not directly actionable (AUC moves with BTC price, not only with team actions). Long lag to revenue. Hard to decompose into input metrics.
- Best use: secondary health metric, sentinel for dormant-balance segment.

### 4.2 The current recommendation

**Primary NSM: FM Completers per Week**
Measures the moment value is delivered. Leads revenue. Actionable through onboarding optimization, KYC drop-off fixes (32% phone drop), and activation journeys (JN-01-A: Second Trade Accelerator).

**Operational North Star (executive reporting): MMU**
Keep MMU as the number reported to Pablo Campos and leadership. It is legible, maps to Pablo's mandate, and has clear targets (23k → 30k Mar 31).

**Leading Indicator: WAU**
Track WAU as the canary metric. WAU rising 2 weeks before MMU drops is an early warning. WAU rising while MMU is flat signals a conversion problem (active but not trading).

### 4.3 The WAU vs MMU tension

This tension is real and healthy. Do not collapse it.

| Signal | Interpretation | Action |
|--------|---------------|--------|
| WAU up, MMU up | Healthy growth | Continue |
| WAU up, MMU flat | Engagement without monetization | Fix activation (journeys, offers, friction) |
| WAU flat, MMU up | Monetization from a narrow active core | Acquisition gap — grow WAU |
| WAU down, MMU down | Disengagement — lifecycle crisis | Full lifecycle review |

**The M1 retention crisis (0.12% actual vs 25% Coinbase benchmark)** is most visible in the WAU-flat + MMU-flat pattern. Users register, complete FM, then never return. The NSM framework helps diagnose which layer is failing.

---

## 5. INPUT METRICS — THE LEVERS THAT MOVE THE NSM

### 5.1 How to identify input metrics

For each NSM, identify 3–5 metrics that are:
1. Mathematically upstream of the NSM (the NSM is literally a function of them)
2. Independently ownable by a team member or squad
3. Measurable weekly

Avoid input metrics that overlap (this creates double-counting confusion) or that require each other to move (this creates circular accountability).

### 5.2 The NSM equation

The NSM should be expressible as a function of its inputs. This forces mathematical clarity and exposes which levers exist.

**General form:**
```
NSM(t) = f(Activation rate, Retention rate, Reactivation rate, Base size)
```

### 5.3 Bit2Me MMU equation

```
MMU(t) = [New FM completers(t) × NURR]
        + [Active_MMU(t-1) × CURR]
        + [Dormant_with_balance(t) × RURR]
```

Where:
- **NURR** = New User Retention Rate — % of FM completers who trade again within 30 days (currently ~0.12%, target ~10%)
- **CURR** = Current User Retention Rate — % of last month's MMU who remain monetizable (estimated ~60-70%)
- **RURR** = Reactivation Rate — % of dormant users with balance who trade in a given month (FOMO Agent target metric)

This equation tells you exactly where to focus:
- NURR is near-zero (M1 retention crisis) — this is the biggest lever
- CURR is the steady state — protect it, monitor it
- RURR is the dormant opportunity — 72.4k users × even 1% RURR = 724 reactivations/month

### 5.4 Bit2Me FM Completers equation

If FM Completers/Week is chosen as the primary NSM:

```
FM_Completers(week) = Registrations(week-3)
                    × KYC_conv_rate        [currently ~60%, phone drop = 32% gap]
                    × Deposit_conv_rate     [% who deposit after KYC]
                    × Trade_conv_rate       [% who trade after first deposit]
```

This immediately surfaces the biggest bottleneck: phone drop-off at KYC (32% of the funnel lost here alone).

### 5.5 Input metric ownership matrix

| Input Metric | Owner | Measurement | Current Level | Target |
|-------------|-------|-------------|--------------|--------|
| FM completers/week | PabloG (journeys) | BigQuery V0a | — | +20% |
| M1 retention (NURR) | Katy (CleverTap) | BigQuery retention | 0.12% | 5%+ |
| KYC conv rate (phone step) | Product | Funnel analytics | ~68% | 85%+ |
| FOMO reactivation rate (RURR) | Daniel (FOMO Agent) | CleverTap campaign | ~0% | 1%+ |
| MMU (composite) | Daniel | Qlik / BigQuery | 23k | 30k |

---

## 6. GOVERNANCE — WEEKLY NSM REVIEW

### 6.1 Weekly NSM ritual (30 minutes, Monday)

Structure:
1. **NSM reading** (5 min): What is the NSM this week vs last week vs 4-week trend?
2. **Input metric review** (15 min): Which inputs moved? Which did not?
3. **Diagnosis** (5 min): Is movement coming from the right input (healthy) or a compensating input (warning sign)?
4. **Actions** (5 min): What changes this week to influence next week's inputs?

This replaces ad hoc metric checks. The goal is a single coherent weekly narrative, not a data dump.

### 6.2 NSM dashboard design principles

A good NSM dashboard has exactly three layers:

**Layer 1 — The number (hero metric)**
Single large number. Current week vs last week. 4-week sparkline. Red/green vs target. No other information on this layer.

**Layer 2 — The inputs (1 row per input metric)**
4–5 rows. Each row: metric name, owner, current value, WoW change, 4-week trend. Color coded.

**Layer 3 — The diagnostic drill (one click)**
Each input metric links to its own breakdown. E.g., NURR links to cohort retention curves by acquisition channel.

**Anti-pattern to avoid:** putting 20 metrics on the NSM dashboard. If every metric is highlighted, nothing is. The NSM dashboard should cause discomfort if the number is wrong — that is its job.

### 6.3 Input metric owners

Each input metric must have exactly one named owner. Not a team. Not "growth." One person who is accountable for explaining the number every Monday.

This is the most important governance rule. Without named owners, input metrics become status indicators instead of accountability tools.

### 6.4 NSM review cadence

| Cadence | Forum | Audience | Depth |
|---------|-------|----------|-------|
| Daily | Slack bot (automated) | Team | NSM number only + WoW delta |
| Weekly | Monday LC sync | LC team + Daniel | Full input metric review |
| Monthly | Growth review | Pablo Campos + leadership | MMU trend + revenue bridge |
| Quarterly | Strategic review | C-suite | NSM target reset, input metric recalibration |

---

## 7. PITFALLS

### 7.1 Vanity metrics disguised as NSMs

**Pattern:** The metric always goes up (or rarely down) regardless of real health.
**Examples:** Total registered users, total KYC completions (cumulative), total revenue (cumulative).
**Test:** If the metric has never been red in the last 6 months, it is almost certainly vanity.
**Fix:** Use period-based (weekly/monthly) metrics, not cumulative.

### 7.2 The multi-NSM trap

**Pattern:** Leadership cannot agree on one number, so 3–5 metrics are declared "equally important."
**Problem:** No single accountability signal. Teams optimize locally. Nobody feels responsible when the business softens.
**Bit2Me risk:** Pressure to report both MMU (for Pablo Campos) and FM completers (for the lifecycle team) and AUC (for the BD team) as three co-equal NSMs.
**Fix:** One NSM. Other metrics are inputs or secondary health metrics. Document the hierarchy explicitly:
```
NSM: FM Completers/Week
  ↑ driven by: KYC conv rate, Deposit conv rate, Trade conv rate
Operational KPI: MMU (executive reporting)
  ↑ driven by: NSM × NURR × CURR × RURR
Health monitor: WAU, AUC (sentinel metrics)
```

### 7.3 NSM drift

**Pattern:** The NSM is redefined subtly over time, usually to show better numbers.
**Examples:** Changing the "active" definition from "traded" to "logged in." Widening the MMU window from 30 to 60 days.
**Consequence:** Historical comparisons break. Leadership loses trust.
**Fix:** Version the NSM definition. Document the exact SQL definition in BigQuery. Any change requires a documented rationale and a restated historical series.

### 7.4 Confusing correlation with causation in NSM selection

**Pattern:** A metric correlates with revenue but does not cause it.
**Example:** Temperature correlates with ice cream sales. AUC may correlate with revenue because both respond to BTC price, not because AUC drives revenue.
**Fix:** Ask "if we artificially inflated this metric (e.g., bought users who hit this metric but did nothing else), would revenue follow?" If no, the correlation is spurious.

### 7.5 Ignoring lag structure

**Pattern:** Measuring NSM against same-week revenue. Claiming "the NSM is not working" because revenue did not respond immediately.
**Fix:** Build the lag model first (Step 4 in section 3). Know whether your NSM is a 2-week, 4-week, or 8-week leading indicator BEFORE you start managing to it.

### 7.6 Setting an NSM target before understanding the baseline

**Pattern:** "Our NSM target is 30k MMU by March 31." Set without understanding current weekly growth rate, input metric rates, or reachability.
**Bit2Me current state:** 23k MMU target of 30k in ~5 weeks requires +30.4% growth. Given NURR of 0.12%, this target requires either massive new acquisition OR a NURR improvement from nearly zero to 5%+.
**Fix:** Decompose the target through the NSM equation before committing. Show the arithmetic. If the math does not work, renegotiate the target before the deadline arrives.

---

## 8. QUICK REFERENCE — BIT2ME NSM SUMMARY

```
NORTH STAR METRIC:    FM Completers / Week
OPERATIONAL KPI:      MMU (Monthly Monetizable Users) — 23k → 30k target Mar 31
LEADING INDICATOR:    WAU (Weekly Active Users)
HEALTH SENTINEL:      AUC (Assets Under Custody — €19.5M)

NSM EQUATION:
MMU(t) = [FM completers × NURR] + [Active MMU × CURR] + [Dormant × RURR]

CRITICAL INPUT:       NURR = 0.12% actual (crisis level, 25% = benchmark)
BIGGEST FUNNEL GAP:   Phone step at KYC = 32% drop-off
DORMANT OPPORTUNITY:  72.4k users with balance × 1% RURR = 724 reactivations/month

WEEKLY RHYTHM:
Mon — NSM review + input metric check (LC sync)
Thu — FOMO Agent reactivation report (RURR signal)
Fri — Flash Report cross-check (revenue bridge vs MMU)

METRIC OWNERS:
FM completers/week    → PabloG
NURR (M1 retention)  → Katy (CleverTap)
KYC conv rate         → Product
RURR (reactivation)   → Daniel (FOMO Agent)
MMU composite         → Daniel (weekly reporting)
```

---

## 9. HOW TO USE THIS SKILL

**Starting a NSM definition project:**
1. Run the NSM selection process (section 3) with BigQuery data
2. Score the candidates against the five criteria (section 2)
3. Define the NSM equation for your chosen metric (section 5)
4. Assign input metric owners (section 5.5)
5. Set up the weekly governance rhythm (section 6)

**Reviewing an existing NSM:**
1. Check for the seven pitfalls (section 7)
2. Re-run the correlation/lag analysis quarterly
3. Version any definition changes

**Resolving a NSM debate (e.g., MMU vs WAU vs FM completers):**
1. Run the five-criterion scoring (section 2)
2. Run the lag correlation analysis (section 3, step 4)
3. Present the NSM hierarchy (NSM + operational KPI + leading indicator) — this resolves most debates because each stakeholder's preferred metric gets a defined role
