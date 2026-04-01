# CleverTap Skill — Bit2Me CRM Execution

**Platform:** CleverTap (CRM / Engagement)
**Owner:** Katy Gildemeister (execution), Daniel Ferraro (strategy)
**Updated:** 2026-03-25

---

## WHO USES THIS SKILL

- **Katy** — CRM execution: builds journeys, campaigns, segments in CleverTap UI
- **Daniel** — strategy design: defines logic, audiences, conversion goals, A/B hypotheses
- **Álvaro / David Sales** — data infra: BigQuery → CleverTap sync, event stream

---

## PART 1 — CLEVERTAP CORE CONCEPTS

### 1.1 The Three Data Objects

| Object | What it is | Examples at Bit2Me |
|--------|-----------|-------------------|
| **Event** | Action a user performed (timestamped) | `trade_completed`, `kyc_approved`, `deposit_made`, `app_open`, `push_clicked` |
| **User Property** | Attribute of the user profile (current state) | `lifecycle_stage`, `cluster_id`, `balance_eur`, `last_trade_date`, `country`, `kyc_status` |
| **Campaign** | A message sent to a segment (one-off or recurring) | Weekly newsletter, FOMO push, reactivation email |

**Key distinction:** Events are immutable historical records. User properties are the current state of the user — they get overwritten. Segments can be built from both.

### 1.2 Segment Types

| Type | Description | When to use |
|------|-------------|-------------|
| **Live segment** | Re-evaluated in real time — membership changes as users qualify/disqualify | Entry triggers for journeys, real-time targeting |
| **Static segment** | Snapshot in time — fixed list at time of creation | One-off campaigns, A/B tests requiring stable control groups, legal/compliance sends |

**Rule at Bit2Me:** Use **live segments** for all journeys. Use **static segments** for A/B tests and compliance-gated sends (Diego must approve before static segments go live).

### 1.3 Journeys vs Campaigns

| Feature | Journey | Campaign |
|---------|---------|---------|
| Trigger | Event, property change, or schedule | Manual launch or schedule |
| Duration | Multi-step, runs over days/weeks | One-off or recurring single message |
| Channels | Mix of push, email, in-app, SMS in one flow | Single channel per campaign |
| Logic | Branching, wait steps, exit conditions | Send to segment, done |
| Best for | Onboarding, reactivation, nurture sequences | Announcements, flash promotions, weekly digest |

### 1.4 A/B Testing Modes

CleverTap supports A/B at two levels:

1. **Campaign-level A/B**: Send variant A to X% of audience, variant B to remaining. CleverTap auto-picks winner after N hours based on selected metric (opens, clicks, conversions).
2. **Journey-level split**: Add a "Random Split" node in a journey to route users to different branch paths. Each branch is a treatment. Measure conversion event downstream.

---

## PART 2 — SEGMENT BUILDING PATTERNS

### 2.1 User Property Segments

Use "User Properties" filter in segment builder. Most common at Bit2Me:

```
lifecycle_stage = "DORMANT_BAL"         → dormant users with balance
cluster_id IN ["c6", "c7"]              → FOMO Agent targets
balance_eur > 0                         → has assets
kyc_status = "APPROVED"                 → KYC-cleared users
country = "ES"                          → Spain cohort
last_trade_date < 90 days ago           → near-dormant threshold
b2b_flag = false                        → B2C only (exclude B2B from retail journeys)
```

**Always exclude:**
- `cluster_id = "c8"` — Whale suppression. NEVER include C8 in mass campaigns.
- Users in UK Compliance Group 3 — must be excluded from all CRM sends.
- `is_banned = true` / `status != "enabled"` — confirmed via profile sync from BigQuery.

### 2.2 Behavioral (Event-Based) Segments

Use "Did/Did not do" event filter:

```
Did event: trade_completed → In last 30 days         → active traders
Did NOT event: trade_completed → In last 60 days     → at-risk / pre-dormant
Did event: app_open → In last 7 days                 → app-engaged (not trading)
Did event: kyc_approved → In last 3 days             → recent converters (onboarding entry)
Did NOT event: deposit_made → Ever                   → never deposited
Did event: push_clicked → campaign: "FOMO_W10"       → FOMO responders
```

### 2.3 Translating the 37-Segment Model to CleverTap

The 37-segment model (SEG-01 to SEG-37) is MECE across: Lifecycle Stage × Archetype × Geo × Channel × B2C/B2B × SpaceCenter tier.

**Translation pattern:**

| Dimension | CleverTap filter type | Property name |
|-----------|----------------------|---------------|
| Lifecycle stage (13 stages) | User Property | `lifecycle_stage` |
| Archetype / cluster | User Property | `cluster_id` |
| Geography | User Property | `country` |
| Acquisition channel | User Property | `acquisition_channel` |
| B2C vs B2B | User Property | `b2b_flag` |
| SpaceCenter tier | User Property | `spacecenter_tier` |

**Example — SEG-12 (Dormant B2C Spain with balance, cluster c6/c7):**
```
lifecycle_stage = "DORMANT_BAL"
AND b2b_flag = false
AND country = "ES"
AND cluster_id IN ["c6", "c7"]
AND balance_eur > 0
AND cluster_id != "c8"
```

### 2.4 MECE Enforcement

To ensure users cannot fall into two segments simultaneously:

1. Define segments in **priority order**. CleverTap evaluates in the order you specify in journey entry or campaign targeting.
2. Use **exclusive exit conditions**: once a user qualifies for SEG-X, suppress from SEG-Y using a "Suppression list" or "Did not do" condition.
3. For journeys: set "Users already in journey = Skip" to prevent double-entry.
4. Validate MECE in BigQuery post-sync: run a cross-segment overlap query before launch. Ask Marta or Álvaro to pull a count-distinct across segment membership before Katy activates.

---

## PART 3 — JOURNEY DESIGN PATTERNS

### 3.1 Entry Condition Types

| Type | CleverTap config | Bit2Me use case |
|------|-----------------|-----------------|
| **Event-triggered** | "User performs event X" | J01: entry when `trade_completed` fires for the first time |
| **Property-based** | "User property changes to value Y" | Entry when `lifecycle_stage` changes to "AT_RISK" |
| **Schedule-based** | "Users in segment Z, run daily at HH:MM" | FOMO Agent: daily 10:00 CET run for dormant users |
| **API-triggered** | Webhook hit from external system | BigQuery cron triggers journey for specific cohort |

**Best practice:** Prefer event-triggered entries for onboarding journeys. Use schedule-based + live segment for reactivation. Use property-change for lifecycle transitions.

### 3.2 Wait Steps and Timing

| Wait type | When to use |
|-----------|-------------|
| Fixed delay (e.g., "wait 2 days") | Standard follow-up sequence |
| Wait until event (e.g., "wait until user opens app") | Behavioral gate — don't send next message until user re-engages |
| Wait until time of day | Force sends to optimal window (10:00 or 19:00 CET) |
| Deadline wait | "Wait up to 7 days for conversion, else go to branch B" |

### 3.3 Branching Patterns

**Split by user property:**
```
Node: "Check property: cluster_id"
  Branch A: cluster_id IN ["c1", "c2"] → High-intent message
  Branch B: cluster_id IN ["c5", "c6"] → Education-first message
  Branch C: else → Generic nurture
```

**Split by behavior (did/did not):**
```
Node: "Did user do event: deposit_made in last 3 days?"
  Yes → Send congratulations + next step prompt
  No  → Send urgency reminder
```

**Random split (A/B):**
```
Node: "Random split"
  50% → Variant A (aggressive CTA)
  50% → Variant B (soft CTA)
  (Optional) 10% → Control (no message)
```

### 3.4 Exit Conditions

Always define at least one exit condition per journey:

| Exit type | Config | Use case |
|-----------|--------|---------|
| Conversion event | User performs `trade_completed` | All monetization journeys |
| Property change | `lifecycle_stage` changes away from target | Dynamic lifecycle journeys |
| Time limit | Max N days in journey | Prevent users getting stuck — cap at 30-60 days |
| Opt-out | User unsubscribes or opts out of channel | Mandatory — always include |
| Manual exit | Suppression list or one-time purge | Compliance-driven removal |

**Rule:** Every journey must have a conversion exit AND a time-limit exit. No open-ended journeys.

### 3.5 Control Groups / Holdout Setup

For measuring true journey uplift (not just campaign performance):

1. At journey entry, add a **Random Split** node immediately after entry: 85% → journey flow, 15% → holdout branch (no messages, just tracking).
2. Tag holdout users with a property update: `journey_control_JN01 = true` so BigQuery can identify them.
3. Measure: conversion rate in flow group vs control group over same time window.
4. Do NOT use CleverTap's built-in "control group" for journeys — it does not track downstream conversions reliably. Use BigQuery analysis post-export.

### 3.6 Bit2Me Journeys J01–J12 — CleverTap Implementation

| Journey | Name | Entry Trigger | Primary Goal | Exit on |
|---------|------|--------------|-------------|---------|
| **J01** | Second Trade Accelerator | `first_trade_completed` event | `trade_completed` (2nd trade) | 2nd trade OR 30 days |
| **J02A** | Active-Sleeper Activation | Schedule: users with `lifecycle_stage = "AT_RISK"`, daily | `trade_completed` | Trade OR 45 days |
| **J02B** | Pre-Dormancy Rescue | Property change: `lifecycle_stage → "PRE_DORMANCY"` | `trade_completed` | Trade OR 21 days |
| **J03** | Deep Dormant Reactivation | Schedule: `lifecycle_stage = "DORMANT_BAL"`, weekly | `deposit_made` OR `trade_completed` | Reactivation OR 60 days |
| **J04** | Card Activation (PAUSED) | `card_issued` event | `card_first_use` | Use OR 14 days |
| **J05** | B2B Onboarding | `b2b_kyc_approved` event | `first_b2b_transaction` | Transaction OR 30 days |
| **J06** | Multi-product Expand | `trade_completed` count = 5 (milestone) | Second product adoption | 45 days |
| **J07** | Earn Product Intro | Schedule: active users not using Earn | `earn_deposit` | Deposit OR 30 days |
| **J08** | Referral Activation | Schedule: active users, no referral sent | `referral_sent` | Referral OR 21 days |
| **J09** | KYC Completion Nudge | `registration_completed` event | `kyc_approved` | KYC OR 7 days |
| **J10** | Deposit Nudge (Post-KYC) | `kyc_approved` event | `deposit_made` | Deposit OR 14 days |
| **J11** | SpaceCenter Level-Up | `spacecenter_tier_change` event | Next tier activity | 30 days |
| **J12** | Reactivated User Nurture | Property change: `lifecycle_stage → "REACTIVATED"` | `trade_completed` (2nd post-reactivation) | Trade OR 30 days |

**Setup checklist per journey:**
- [ ] Entry segment defined and validated in BigQuery (no duplicates with other active journeys)
- [ ] Diego legal approval for ALL copy before activation
- [ ] Control group split node added (15% holdout)
- [ ] Conversion event mapped
- [ ] Time-limit exit set
- [ ] Opt-out suppression confirmed
- [ ] Frequency cap check: user not receiving >3 pushes/day across all journeys

---

## PART 4 — PUSH NOTIFICATION BEST PRACTICES

### 4.1 Optimal Send Times — Crypto Users

| Window | CET | Rationale |
|--------|-----|-----------|
| **Morning** | 09:00–10:30 | Pre-market check, BTC opens strong |
| **Afternoon peak** | 16:00–18:00 | EU session close, US pre-market |
| **Evening** | 20:00–21:00 | Second device check, high open rates |
| **AVOID** | 00:00–08:00 | Silent hours — triggers opt-outs |
| **AVOID** | Friday 17:00+ | Weekend wind-down, low intent |

**Market-aware sends (FOMO Agent):** Check CoinGecko API for BTC/ETH 24h change before triggering. If market is up >3% in 24h, use urgency messaging. If down >5%, use "accumulate" framing instead.

### 4.2 Deep Link Patterns

Always include a deep link in push notifications. Format:

```
bit2me://trade                    → Opens Trade tab directly
bit2me://deposit                  → Opens deposit flow
bit2me://earn                     → Opens Earn product
bit2me://portfolio                → Opens portfolio view
bit2me://kyc                      → Opens KYC flow (for J09)
bit2me://referral                 → Opens referral screen
bit2me://market/{coin_symbol}     → Opens specific coin page (e.g., BTC)
```

**Rule:** Never send a push without a deep link. Generic app opens reduce conversion.

### 4.3 Personalization Tokens

CleverTap tokens (Mustache syntax):

```
{{first_name}}                    → User's first name ("Hola, {{first_name}}")
{{balance_eur}}                   → Current EUR balance
{{last_coin_traded}}              → Most recent traded asset
{{days_since_last_trade}}         → Recency signal
{{lifecycle_stage}}               → Current stage (use for conditional content)
{{spacecenter_tier}}              → Gamification tier
{{btc_price_change_24h}}          → Real-time market data (via FOMO Agent enrichment)
```

**Fallbacks are mandatory:** Always set a fallback for every token. If `first_name` is blank, fallback = "Trader". If `balance_eur` is null, do not show balance personalization.

### 4.4 Frequency Capping and Opt-Out Prevention

**Global caps (enforced in CleverTap settings):**
- Max 2 push notifications per user per day (across all journeys + campaigns)
- Max 1 email per user per day
- Min 4-hour gap between any two messages to same user

**Opt-out prevention rules:**
- Never send more than 3 push notifications in any 7-day window to dormant users (they are already disengaged — over-pushing causes permanent opt-out)
- Always include unsubscribe link in emails
- Suppress users who have not opened any push in 60 days from push campaigns (re-permission flow only)
- FOMO Agent: cap at 1 push/day per user, skip weekends if no major market move

**Suppression lists:**
- `suppression_c8`: C8 whales — never mass-push
- `suppression_uk3`: UK compliance group 3
- `suppression_unsubscribed_email`: global email unsubscribers
- `suppression_push_opted_out`: push permission revoked

### 4.5 FOMO Agent Integration

FOMO Agent runs daily at 10:00 CET. Integration with CleverTap:

1. FOMO Agent (Python cron) pulls BTC/ETH price change from CoinGecko API
2. Selects message variant based on FOMO Score (urgency × social proof × timing)
3. Enriches CleverTap user profiles with `fomo_score_today` property via CleverTap API upload
4. Triggers CleverTap campaign (pre-built as "Triggered" campaign, fires when `fomo_score_today` property is updated)
5. Campaign targets: `cluster_id IN ["c6", "c7"]` + `lifecycle_stage IN ["DORMANT_BAL", "DORMANT_ZERO"]`
6. Total target pool: ~16,116 users

**CleverTap setup for FOMO Agent:**
- Campaign type: API-triggered (not scheduled)
- Trigger: User property update on `fomo_score_today`
- Throttle: 1 send per user per 24h
- Deep link: `bit2me://trade` or `bit2me://market/BTC` based on score variant

---

## PART 5 — A/B TESTING IN CLEVERTAP

### 5.1 Setting Up a Proper A/B Test

**Pre-launch checklist:**
1. Define hypothesis: "Changing CTA from X to Y will increase [metric] by Z%"
2. Calculate required sample size (use external calculator — see Part 5.3)
3. Define primary metric and secondary metrics before launch
4. Set test duration: minimum 7 days, never stop early based on early results
5. Diego approval on all copy variants

**CleverTap campaign A/B setup:**
```
Campaign type: Push / Email / In-App
A/B split: Define % per variant (e.g., 45% A / 45% B / 10% Control)
Winner selection: Manual (do NOT use auto-winner — use BigQuery for final call)
Primary metric in CleverTap: Conversions (map to correct event)
```

**Journey A/B setup:**
```
Add Random Split node at branch point
Set percentages per path
Name each path clearly: "Variant_A_AggressiveCTA", "Variant_B_SoftCTA", "Control_NoMsg"
Tag users in each branch with a property update for BigQuery tracking:
  ab_test_id = "JN01_W10_CTA"
  ab_variant = "A" / "B" / "control"
```

### 5.2 Metrics Hierarchy

| Metric type | What to track | Primary or secondary |
|-------------|--------------|---------------------|
| **Revenue** | EUR traded, EUR deposited | Primary (always) |
| **Conversion** | `trade_completed`, `deposit_made` | Primary |
| **Engagement** | Push open rate, email CTR | Secondary (proxy) |
| **Retention** | 7-day and 30-day return rate | Secondary |
| **Opt-out rate** | Unsubscribes, push opt-outs | Secondary (guardrail) |

**Rule:** Never optimize for engagement metrics (opens/clicks) alone. A message that drives 30% opens but 0% trades is a failure.

### 5.3 Statistical Significance — CleverTap vs External

| Scenario | Use CleverTap reporting | Use BigQuery / external |
|----------|------------------------|------------------------|
| Quick directional signal (early days) | Yes | — |
| Final test result and decision | No | Yes — always |
| Revenue impact calculation | No | Yes — always |
| Multi-touch attribution | No | Yes — W-shaped model in BigQuery |

**CleverTap's built-in significance test is unreliable for revenue metrics.** It uses simple z-test on click rates, not on revenue. Always export user-level data to BigQuery and run proper two-sample t-test or Mann-Whitney U for non-normal distributions. See `memory/skills/statistical-analysis/SKILL.md` for methods.

**Minimum sample sizes (reference):**
| Expected uplift | Required n per group |
|----------------|---------------------|
| 20% | ~400 |
| 10% | ~1,600 |
| 5% | ~6,400 |
| 2% | ~40,000 |

---

## PART 6 — REPORTING AND ANALYTICS

### 6.1 Journey Analytics — What to Monitor

In CleverTap Journey Analytics view:

| Metric | What it means | Alert threshold |
|--------|--------------|----------------|
| Entry rate | % of eligible users who entered | <50% = check segment size or entry event frequency |
| Step completion rate | % who reached each node | Drop >40% at any step = fix that message |
| Conversion rate | % who hit the conversion event | Benchmark against control group |
| Exit rate (time-limit) | % who aged out without converting | >80% = journey is not working, revisit |
| Opt-out at step | Push opt-outs triggered by a specific message | Any step >2% opt-out rate = pause and review |

### 6.2 Campaign Performance Benchmarks (Bit2Me internal)

| Channel | Open rate target | CTR target | Conversion target |
|---------|-----------------|-----------|------------------|
| Push notification | >8% | >3% | >1% |
| Email | >20% | >4% | >0.5% |
| In-app | >15% | >8% | >3% |
| SMS | N/A | >5% | >1.5% |

**Note:** These are internal Bit2Me targets. Crypto industry benchmarks are higher than general e-commerce. If a campaign consistently underperforms these thresholds, escalate to Daniel before next send.

### 6.3 Connecting CleverTap to BigQuery

CleverTap events stream to BigQuery via the CleverTap Data Export integration. Key tables:

```sql
-- CleverTap events land in:
`bit2me_lifecycle.ct_events`          -- raw event stream (push_sent, push_opened, trade_completed via CT)
`bit2me_lifecycle.ct_user_profiles`   -- user property snapshots (daily sync)
`bit2me_lifecycle.ct_campaigns`       -- campaign sends and metadata

-- Join pattern: CleverTap user ID = CleverTap identity = mapped to internal user_id via:
`bit2me_lifecycle.ct_identity_map`    -- ct_identity → user_id bridge table
```

**Weekly reporting query pattern:**
```sql
SELECT
  e.campaign_id,
  c.campaign_name,
  COUNT(DISTINCT CASE WHEN e.event_name = 'push_sent' THEN e.user_id END) AS sent,
  COUNT(DISTINCT CASE WHEN e.event_name = 'push_opened' THEN e.user_id END) AS opened,
  COUNT(DISTINCT CASE WHEN e.event_name = 'trade_completed' THEN e.user_id END) AS converted,
  ROUND(COUNT(DISTINCT CASE WHEN e.event_name = 'push_opened' THEN e.user_id END) * 100.0
    / NULLIF(COUNT(DISTINCT CASE WHEN e.event_name = 'push_sent' THEN e.user_id END), 0), 2) AS open_rate_pct
FROM `bit2me_lifecycle.ct_events` e
JOIN `bit2me_lifecycle.ct_campaigns` c USING (campaign_id)
WHERE e.event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1, 2
ORDER BY sent DESC;
```

---

## PART 7 — INTEGRATION PATTERNS

### 7.1 BigQuery → CleverTap User Profile Sync

User properties computed in BigQuery are pushed to CleverTap to keep segments current.

**Sync method:** CleverTap Upload API (POST `/1/upload/profiles`)

**Sync frequency:**
| Property type | Sync frequency |
|--------------|---------------|
| `lifecycle_stage` | Daily (runs at 02:00 CET after BigQuery Gold Layer refresh) |
| `cluster_id` | Daily |
| `balance_eur` | Daily |
| `health_score` | Daily |
| `last_trade_date` | Daily |
| `fomo_score_today` | Real-time (FOMO Agent intraday) |
| `spacecenter_tier` | Daily |

**Owner:** Álvaro Muñoz (data infra). If sync is delayed or failing, alert Álvaro — CleverTap segments will be stale and journeys may fire on incorrect user states.

**Profile update payload structure:**
```json
{
  "identity": "{{user_id}}",
  "lifecycle_stage": "DORMANT_BAL",
  "cluster_id": "c6",
  "balance_eur": 142.50,
  "health_score": 28,
  "last_trade_date": "2025-12-14",
  "b2b_flag": false,
  "spacecenter_tier": 2,
  "country": "ES"
}
```

### 7.2 CleverTap → BigQuery Event Stream

CleverTap sends all engagement events back to BigQuery for attribution and analysis:

| CT event | BigQuery event_name | Use |
|----------|--------------------|----|
| Push sent | `ct_push_sent` | Reach tracking |
| Push opened | `ct_push_opened` | Engagement |
| Push clicked | `ct_push_clicked` | CTR |
| Email sent | `ct_email_sent` | Reach |
| Email opened | `ct_email_opened` | Open rate |
| Email clicked | `ct_email_clicked` | CTR |
| Journey entered | `ct_journey_entered` | Funnel top |
| Journey converted | `ct_journey_converted` | Funnel bottom |
| Unsubscribed | `ct_unsubscribed` | Suppression |

**Latency:** Events typically appear in BigQuery 2–4 hours after they occur in CleverTap. Do not use same-day data for A/B analysis.

### 7.3 Webhook / Real-Time Triggers

For real-time journey entry (not waiting for daily sync):

**Pattern:** BigQuery → Cloud Function → CleverTap API

1. BigQuery scheduled query detects lifecycle transition (e.g., user moved to AT_RISK)
2. Triggers Cloud Function (Álvaro owns this pipeline)
3. Cloud Function calls CleverTap API to update user profile AND trigger journey entry event
4. CleverTap journey fires within minutes

**Use cases for real-time triggers:**
- J09: KYC abandonment detection (user starts KYC, drops off mid-flow)
- J02B: Pre-dormancy rescue (user crosses inactivity threshold intraday)
- FOMO Agent: market move detected → immediate push (no waiting for daily sync)

---

## QUICK REFERENCE — KATY'S DAILY WORKFLOW

### Before Building Any Campaign or Journey
1. Confirm segment logic with Daniel (or check `bit2me-journey-os/docs/journeys/`)
2. Confirm copy has Diego's legal approval
3. Check frequency cap: is this user pool already receiving another active campaign?
4. Set conversion event correctly before launch (cannot change after)
5. Add control group (15% holdout) for all journeys — never skip

### Launch Checklist
- [ ] Segment validated in BigQuery (Marta or Álvaro confirm counts)
- [ ] Copy approved by Diego
- [ ] Deep links tested on iOS and Android
- [ ] Personalization fallbacks set
- [ ] Frequency cap confirmed not exceeded
- [ ] Control group / A/B split configured
- [ ] Conversion event mapped
- [ ] Time-limit exit set
- [ ] C8 suppression applied
- [ ] UK Compliance Group 3 suppressed

### Weekly Reporting (Pablo T pulls from Qlik / Daniel reviews)
- Journey conversion rate vs control
- Active user counts entering and exiting each journey
- Push opt-out rates (alert if any campaign >2%)
- Revenue attributed to CRM vs paid (Flash Report)

---

## RELATED SKILLS AND FILES

| Resource | Path |
|----------|------|
| Bit2Me data context and SQL | `memory/skills/bit2me-data-analyst/SKILL.md` |
| Statistical analysis for A/B | `memory/skills/statistical-analysis/SKILL.md` |
| Journey copy and creatives | `bit2me-journey-os/docs/journeys/` |
| Journey tracker (Katy's working file) | `bit2me-journey-os/LC_Journeys_Tracker_v4.xlsx` |
| FOMO Agent overview | `Desktop/fomo_agent/` |
| Segment model (37 segments) | `memory/projects/lc-os.md` |
| LC glossary | `memory/glossary.md` |
