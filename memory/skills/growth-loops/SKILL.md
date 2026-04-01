---
name: growth-loops
description: Use this skill when designing, auditing, or optimizing growth loops for a crypto/fintech product. Invoke when the user asks about "growth loop", "viral loop", "retention loop", "referral loop", "engagement loop", "k-factor", "loop coefficient", "loop velocity", "compounding growth", "flywheel", or asks how lifecycle campaigns connect to self-reinforcing growth mechanics.
version: 1.0.0
---

# Growth Loops — Design, Analysis & Optimization

For a Head of Growth designing lifecycle campaigns on a crypto/fintech platform like Bit2Me.

---

## 1. What Is a Growth Loop

A growth loop is a closed system where the output of one cycle becomes the input of the next, producing compounding growth over time.

```
INPUT → ACTION → OUTPUT → REINVESTMENT → (next cycle INPUT, larger)
```

### Loop vs Funnel

| Dimension | Funnel | Loop |
|---|---|---|
| Shape | Linear, one-time | Circular, recurring |
| Output | Converted user | New inputs for next cycle |
| Growth model | Additive (each campaign adds users) | Multiplicative (each cycle amplifies the next) |
| When it ends | When the campaign ends | It does not end — it compounds |
| Lifecycle role | Acquisition and onboarding | Retention, expansion, referral |

**Critical insight:** Funnels answer "how do we get users?". Loops answer "how does getting one user produce more users?". Lifecycle marketing operates almost entirely in loops, not funnels.

### Compound Effect

A loop with coefficient k = 0.7 and 1,000 new users seeded:

```
Cycle 1: 1,000 users
Cycle 2: 700 new from loop
Cycle 3: 490
...
Total reach = 1,000 / (1 - 0.7) = 3,333 users from one seed cohort
```

A loop with k = 0.9 produces 10,000 from the same 1,000 seed. The difference between k = 0.7 and k = 0.9 is not 20% — it is 3x total output. This is why micro-optimizations at each loop step have outsized impact.

---

## 2. Types of Growth Loops

### 2.1 Viral Loops

The action one user takes exposes the product to new potential users.

**Mechanics:**
- Referral: user shares a unique link → friend signs up → both receive reward → user is incentivized to share again
- Social sharing: user posts a trade result, portfolio milestone, or market alert → non-users see it → curiosity/FOMO triggers → sign-up

**Key variable:** branching factor — how many new users does each existing user expose on average per cycle?

**Crypto-specific driver:** price volatility creates natural sharing moments. "BTC just hit X" posts on social are organic viral triggers.

---

### 2.2 Engagement Loops

The product behavior itself drives habitual return. No external sharing required.

**Mechanics:**
- Trigger (notification, market event, habit cue)
- Variable reward (price movement, portfolio change, yield update)
- Investment (user sets alerts, adds funds, completes a trade)
- Commitment (balance now in platform, deeper hooks)

**Crypto-specific driver:** price volatility is the ultimate engagement trigger. Market alerts tied to user portfolio are the highest-CTR notification type in crypto.

---

### 2.3 Retention Loops

Each action a user takes makes it harder to leave, and more rewarding to stay.

**Mechanics:**
- Gamification: streaks, milestones, Space Center tier progression
- Portfolio gravity: deposited balance creates a reason to return and monitor
- Yield accumulation: staking/earn products create daily returns that pull users back
- Sunk cost + switching cost: tax history, transaction records, familiarity

**Key insight:** retention loops are anti-churn mechanisms dressed as engagement. The goal is to increase the switching cost faster than the user's motivation to leave decays.

---

### 2.4 Content Loops (UGC)

Users generate content that attracts new users or re-engages dormant ones.

**Mechanics:**
- User posts trade result → visible to followers or community → new interest
- User writes a review → appears in app stores → improves conversion from organic search
- User participates in a forum → builds community → community retains other users

**Crypto-specific driver:** crypto is inherently social. Gains (and losses) are publicly discussed. This loop is under-exploited in most CEX products but has high potential.

---

### 2.5 Paid Loops (CAC → LTV → Reinvestment)

The economics of paid acquisition feed back into the budget that funds more acquisition.

**Mechanics:**
```
Paid spend → Acquired user → LTV generated → Gross margin → Reinvested in paid spend
```

**Key condition:** the loop only closes if LTV > CAC within the reinvestment window (typically 6-12 months). If the payback period is 18 months, the loop has too much latency to compound efficiently.

**Crypto-specific risk:** Ghost conversions. If 93% of attributed conversions are existing users (Bit2Me data), the paid loop is not actually acquiring new inputs — it is recycling existing ones. This inflates apparent CAC efficiency while the real new-user CAC is much higher. The loop breaks.

**Fix:** W-shaped attribution (First Touch 30% + KYC Assist 20% + Deposit Assist 20% + FM Last Touch 30%) correctly isolates new-user acquisition from re-engagement, so the paid loop is funded accurately.

---

## 3. How to Map a Loop

For any proposed loop, answer these four questions in sequence:

### Step 1: Identify the Trigger
What causes the user to take action? Categories:
- External trigger: push notification, email, market alert, social post
- Internal trigger: habit, emotion (fear of missing out, portfolio anxiety), schedule
- Product trigger: streak expiry, tier upgrade available, yield payout

### Step 2: Identify the Core Action
What is the single behavior the loop depends on? This must be:
- Measurable (an event in your analytics)
- Repeatable (can happen multiple times per user)
- Valuable (correlates with revenue or retention)

Examples: "executed a trade", "deposited funds", "shared referral link", "completed a staking setup"

### Step 3: Identify the Output
What does the action produce that is valuable to the next cycle? Categories:
- A new user (viral loops)
- A stronger habit signal (engagement loops)
- A deeper financial commitment (retention loops)
- Data that improves targeting (any loop)
- Revenue that funds reinvestment (paid loops)

### Step 4: Identify the Reinvestment Mechanism
How does the output become the input of the next cycle?
- New user → seeds their own loop
- Habit signal → used to time the next trigger more precisely
- Financial commitment → generates yield that triggers another trade
- Revenue → funds next paid acquisition cycle

### Loop Map Template

```
LOOP NAME: [name]
LOOP TYPE: [viral / engagement / retention / content / paid]

TRIGGER:       [what starts the cycle]
    ↓
CORE ACTION:   [the measurable behavior]
    ↓
OUTPUT:        [what the action produces]
    ↓
REINVESTMENT:  [how output becomes next cycle's input]
    ↓
(back to TRIGGER, larger)

COEFFICIENT k: [fraction of outputs that successfully reinvest, 0–1]
VELOCITY:      [average days per cycle]
CURRENT STATE: [healthy / leaking / broken — specify where]
```

---

## 4. Bit2Me Specific Loops

### 4.1 Brokerage Loop

```
TRIGGER:       Market alert (price movement on watched asset)
    ↓
CORE ACTION:   User executes a trade
    ↓
OUTPUT:        P&L event + new portfolio position
    ↓
REINVESTMENT:  Profit or position change triggers another alert → next trade
    ↓
(cycle repeats, portfolio grows, trade frequency increases)
```

**k-factor proxy:** % of active traders who execute a second trade within 7 days of first.
**Leak point:** alert fatigue — users disable notifications after irrelevant or excessive alerts. Fix: personalize alerts to portfolio holdings and price sensitivity thresholds.
**Lifecycle campaign hook:** J1 (Brokerage Journey) activates this loop. Step 1 is getting first trade. Step 2 is ensuring second trade happens within 7 days.

---

### 4.2 Referral Loop

```
TRIGGER:       Post-deposit reward moment (user just made money, emotional peak)
    ↓
CORE ACTION:   User shares referral link with a friend
    ↓
OUTPUT:        Referred friend registers + KYC + deposits
    ↓
REINVESTMENT:  Both user and friend receive reward → user's incentive to refer again increases
    ↓
(user refers more friends; referred friend enters their own loop)
```

**k-factor:** (avg referrals sent per active user) × (conversion rate of referral to depositing user). At k = 1.0 the loop is self-sustaining without paid input.
**Leak points:**
1. Low share rate: user never sends the link (fix: timing — ask at emotional high, not randomly)
2. Low conversion of referral: friend clicks but does not KYC (fix: referral landing page must reduce friction, pre-fill promo code)
3. Reward not salient enough: user forgets or does not value the reward (fix: instant reward visibility, show progress toward reward)

---

### 4.3 Space Center Loop

```
TRIGGER:       User trades → B2M tokens earned as fee rebate / reward
    ↓
CORE ACTION:   User accumulates B2M → advances Space Center tier
    ↓
OUTPUT:        Tier upgrade → better trading rates, higher yield, exclusive features
    ↓
REINVESTMENT:  Better rates make trading more profitable → user trades more to maintain/advance tier
    ↓
(trade volume increases; B2M holdings grow; tier lock-in increases switching cost)
```

**k-factor proxy:** % of users who increase trade volume in the 30 days after a tier upgrade.
**Leak points:**
1. Users do not know their tier status or progress (fix: in-app progress bar, proactive push "you are 3 trades from Silver")
2. Tier benefits are not felt immediately (fix: show fee savings per trade, cumulative savings dashboard)
3. B2M holding vs trading tension: users hold B2M to advance tier but this reduces trading activity (fix: separate B2M holding tier from trading activity tier, or reward both independently)
**Lifecycle campaign hook:** Space Center progress notifications are a high-value engagement trigger for AT_RISK and PRE_DORMANCY segments.

---

### 4.4 Earn Loop

```
TRIGGER:       User has idle capital (deposited balance not deployed)
    ↓
CORE ACTION:   User sets up staking / Earn product
    ↓
OUTPUT:        Daily yield accumulates in account
    ↓
REINVESTMENT:  Yield creates new investable capital → user stakes more → compound interest effect
    ↓
(balance grows; daily return notification re-engages user; larger balance increases switching cost)
```

**k-factor proxy:** % of Earn users who increase their staked amount within 60 days of first stake.
**Leak points:**
1. Activation gap: user deposits but never discovers Earn (fix: onboarding flow must surface Earn to DEPOSITED segment within 24h)
2. Yield too low to feel meaningful at small balances (fix: show annualized % prominently, not absolute daily amount)
3. Lock-up anxiety: user fears losing access to capital (fix: offer flexible staking with instant unstake, even at slightly lower APY)
**Lifecycle campaign hook:** J3 (Earn Journey) drives this loop. Key metric is time-to-first-stake after deposit.

---

## 5. Loop Metrics

### 5.1 Loop Coefficient (k)

The fraction of one cycle's output that successfully seeds the next cycle.

```
k = (outputs produced per cycle) × (reinvestment rate)
```

For a referral loop:
```
k = (avg referrals sent per user) × (referral-to-depositing-user conversion rate)
```

| k value | Loop behavior |
|---|---|
| k < 0 | Loop is shrinking — active churn exceeds reinvestment |
| k = 0 | No reinvestment — loop does not compound |
| 0 < k < 1 | Loop is growing but needs ongoing seed input |
| k = 1 | Loop is self-sustaining — zero seed input needed to maintain |
| k > 1 | Viral / exponential growth |

**Practical target for lifecycle loops:** k > 0.5. At k = 0.5, one seed cohort of 1,000 users produces 2,000 total engagements. At k = 0.8, it produces 5,000.

---

### 5.2 Loop Velocity

How long does one full cycle take?

```
Loop Velocity = avg days from trigger to reinvestment
```

A referral loop might have velocity = 21 days (user sees reward moment, shares, friend registers and deposits over ~3 weeks). A brokerage engagement loop might have velocity = 3 days (alert → trade → new position → next alert).

**Lower velocity = faster compounding.** Reducing loop velocity by 30% has the same compound effect as increasing k by 30%, but is often easier (remove friction from individual steps).

---

### 5.3 Loop Size

How many users are currently active in this loop?

```
Loop Size = active users in the loop at any given time
```

Small loop size with high k is better than large loop size with low k. Prioritize optimizing k before scaling seed inputs.

---

### 5.4 Combined Loop Power Score

A single prioritization metric:

```
Loop Power = Loop Size × k / Loop Velocity (cycles per day)
```

Use this to rank which loops to invest in first.

---

## 6. How to Improve a Loop

### Reduce Friction at Each Step

Map every step between trigger and reinvestment. For each step, measure:
- Drop-off rate (% who do not proceed)
- Time to complete
- Error / confusion rate

Prioritize the step with the highest drop-off × downstream value.

**Common friction sources in crypto:**
- KYC re-verification blocking return deposits
- 2FA friction at login discouraging daily check-in
- Complex staking UI requiring too many taps
- Referral link sharing UX buried in menu

---

### Increase Output Quality

Not all outputs are equal. A referred user who deposits €500 is a higher-quality output than one who registers and never KYCs. Segment your loop outputs by quality:

```
Output Quality Score = P(reaches next stage) × expected LTV
```

Focus triggers and rewards on users most likely to produce high-quality outputs.

---

### Improve Reinvestment Rate

This is the most leveraged intervention. The reinvestment rate is how often an output actually feeds back into the loop as a new input. Common failures:

- User earns a reward but never redeems it (reward loop breaks)
- Referred friend registers but does not deposit (referral loop breaks at monetization)
- Yield accumulates but user does not restake (Earn loop breaks at compounding)

Fix reinvestment failures with:
- Timely notifications at the reinvestment moment ("Your €12 yield is available — stake it now")
- Default auto-reinvestment with opt-out (reduces friction to near zero)
- Progress visualization showing what reinvestment unlocks

---

### Timing Optimization

Loops are not time-invariant. Market volatility creates windows where users are maximally susceptible to triggers. In crypto:
- Price pump: best moment for brokerage loop trigger
- Bear market: best moment for Earn loop trigger (yield is stable, trading feels risky)
- New product launch: best moment for content and referral loops

Match loop activation to market context. This is the FOMO Score logic applied at the loop level.

---

## 7. Loop vs Funnel — When to Think in Which Frame

### Think in Funnels When:
- Optimizing a one-time conversion (registration → KYC → first deposit)
- Running a paid acquisition campaign with a defined start/end
- Analyzing a linear onboarding sequence
- Measuring a single cohort's progression through lifecycle stages

### Think in Loops When:
- Designing retention mechanics (what brings users back)
- Building referral programs
- Designing gamification (Space Center, streaks)
- Planning lifecycle journeys past the first purchase
- Evaluating whether a product mechanic is self-sustaining
- Setting strategy for Dormant segment reactivation (reactivation must loop back to retention)

### The Lifecycle Operating System Is a Loop Stack

The LC-OS is not a funnel. Each stage transition in the 13-stage model is a potential loop:
- ACTIVE → POWER users: engagement loop (higher trade frequency)
- AT_RISK → ACTIVE: retention loop (reduce decay rate)
- DORMANT → REACTIVATED: reactivation loop (external trigger restarts internal loop)
- REACTIVATED → ACTIVE: the reactivation loop must hand off to the retention loop or the user churns again

A lifecycle journey that ends at "user reactivated" has broken the loop. The journey must include the reinvestment step: user reactivated → deposits → enters Earn or Brokerage loop → loop self-sustains.

---

## 8. Connection to Markov Model (State Transition Rates)

The 13-stage Bit2Me lifecycle model is a Markov chain. Growth loops map directly to the transition rate parameters:

### Transition Rate Definitions

| Abbreviation | Transition | Loop Connection |
|---|---|---|
| **NURR** | New User Retention Rate: DEPOSITED → ACTIVE | Engagement loop quality at activation |
| **CURR** | Current User Retention Rate: ACTIVE → ACTIVE (stay active) | Retention loop strength |
| **RURR** | Reactivated User Retention Rate: REACTIVATED → ACTIVE | Whether reactivation loop hands off to retention loop |

### Loop Coefficient Maps to Transition Rate

```
NURR ≈ f(engagement loop k, loop velocity in first 30 days)
CURR ≈ f(retention loop k, Space Center loop k, Earn loop k combined)
RURR ≈ f(reactivation trigger quality × reinvestment into retention loop)
```

A 10-point improvement in engagement loop k (e.g., from k=0.5 to k=0.6 in first-30-day brokerage loop) will appear as a measurable increase in NURR in the Markov model. This connects campaign design decisions to the financial model projections.

### Steady-State Loop Analysis

In a Markov model at steady state, the number of ACTIVE users stabilizes when inflow = outflow:

```
Inflow = new activations + reactivations
Outflow = churn to AT_RISK + dormancy

Steady-state ACTIVE = Inflow / (1 - CURR)
```

Improving CURR from 0.85 to 0.90 increases steady-state active base by 33% — with zero additional acquisition spend. This is the loop compounding effect expressed in Markov terms.

### Intervention Priority Matrix

| Intervention | Loop Type | Affected Metric | Leverage |
|---|---|---|---|
| Improve first-trade experience | Engagement | NURR | Very High |
| Add Space Center progress notifications | Retention | CURR | High |
| Auto-restake yield | Earn / Retention | CURR | High |
| Optimize referral share moment | Viral | New user inflow | Medium-High |
| Reduce referral-to-deposit friction | Viral | k of referral loop | High |
| FOMO push for dormant users | Reactivation | RURR | Medium |
| Better reactivation → retention handoff | Reactivation | RURR | Very High |

---

## 9. Quick-Start Checklist for a New Loop Design

Use this before presenting any loop to stakeholders or building a campaign around it.

- [ ] Trigger is defined: specific, measurable, timed
- [ ] Core action is a single behavior tracked as an analytics event
- [ ] Output is quantified (not just "user engages" — what specifically is produced)
- [ ] Reinvestment mechanism is explicit and has a default path (not opt-in only)
- [ ] k coefficient estimated (even rough: high/med/low with rationale)
- [ ] Loop velocity estimated in days
- [ ] Biggest leak point identified (which step loses the most users)
- [ ] One fix for biggest leak point specified
- [ ] Markov transition rate this loop affects is named
- [ ] Success metric defined (what does a 30-day improvement look like in data)

---

## 10. Reference: Bit2Me Loop Registry

| Loop ID | Name | Type | Primary Segment | Key Metric | Current k Estimate | Priority |
|---|---|---|---|---|---|---|
| BL-01 | Brokerage | Engagement | ACTIVE, POWER | 7-day second trade rate | Unknown — measure first | High |
| BL-02 | Referral | Viral | ACTIVE | Referral k = shares × conversion | Low (est.) | High |
| BL-03 | Space Center | Retention | ACTIVE, POWER | Trade volume post-tier-upgrade | Unknown | High |
| BL-04 | Earn | Retention | DEPOSITED, AT_RISK | Restake rate within 60d | Unknown | Very High |
| BL-05 | Paid CAC→LTV | Paid | New users | Real new-user ROAS | Broken (ghost conversions) | Fix first |
| BL-06 | Reactivation | Reactivation | DORMANT_BAL | RURR after FOMO push | 0.08 (M1 retention crisis) | Critical |
