---
name: push-notification-strategy
description: |
  Expert guide for designing high-converting push notification campaigns in crypto/fintech lifecycle marketing.
  Use when: designing push campaigns, writing push copy, building reactivation sequences, setting up FOMO Agent
  logic, configuring CleverTap journeys with push, planning dormant user reactivation, A/B testing push
  notifications, or when user mentions push strategy, FOMO push, CleverTap push, or dormant user outreach.
metadata:
  author: Daniel Ferraro / Bit2Me LC
  version: "1.0.0"
  context: CleverTap + Bit2Me lifecycle model (37 segments, FOMO Agent, 16,116 dormant users)
---

# Push Notification Strategy — Crypto/Fintech Lifecycle

Expert playbook for designing, writing, and executing push notification campaigns for a crypto exchange using CleverTap. Covers strategy (Daniel) and execution (Katy).

---

## When to Apply

Use this skill when:
- Designing push campaigns for any lifecycle stage (activation, retention, reactivation)
- Writing push copy for the FOMO Agent or ad-hoc campaigns
- Configuring CleverTap journeys that include push steps
- Setting timing, frequency caps, and segmentation for push
- A/B testing push notifications
- Diagnosing low push CTR or high opt-out rates
- Planning dormant-user reactivation via push

---

## 1. Push Notification Fundamentals

### Four Types of Push

| Type | Trigger | Goal | Frequency |
|---|---|---|---|
| **Transactional** | User action (trade, deposit, withdrawal) | Confirm, inform | Unlimited (expected) |
| **Promotional** | Campaign calendar | Drive action (trade, deposit) | Max 2/week |
| **Lifecycle** | Stage transition (KYC done, first deposit, dormancy threshold) | Move user to next stage | 1 per trigger |
| **Behavioral** | User behavior pattern (login without trade, 7d inactivity) | Re-engage before dormancy | 1-2/week max |

### Permission Rates by Platform and Industry

- **Android opt-in:** ~90% (permissions granted by default pre-Android 13; required consent from Android 13+)
- **iOS opt-in:** ~50-55% fintech average; crypto skews higher (~60%) due to high intent users
- **Crypto industry benchmark CTR:** 3-6% (vs 1-2% retail average)
- **Bit2Me baseline to beat:** track open rate and conversion rate per segment, not a blended number

### The Permission Moment

The single most important push decision is **when to ask for permission**.

Rules:
1. Never ask on first app open — user has no context for why they should say yes
2. Ask after a **value moment**: after KYC approval, after first successful deposit, after first price alert
3. Frame the ask around benefit: "Get alerts when your assets move" not "Enable notifications"
4. **Soft ask before hard ask:** Show an in-app modal explaining the value BEFORE triggering the OS-level permission dialog. If the user declines the soft ask, do not trigger the OS dialog — save the permission moment for a later session.

**Soft ask template:**
> "Want us to alert you when BTC moves +5%? We'll only send what matters."
> [Yes, alert me] [Maybe later]

Only trigger the OS permission dialog when the user taps "Yes, alert me."

---

## 2. Timing Strategy for Crypto Users

### Market Hours Awareness

Crypto markets are 24/7, but **user attention is not**. Sends during high volatility moments outperform scheduled sends by 2-4x CTR.

Priority triggers (send immediately when these occur):
- BTC/ETH price move >3% in 1h
- User's held asset moves >5% in 24h
- Major market event (halving, macro data, exchange listing)

### Time Zone Handling in CleverTap

- Always segment by user local time zone, not server time
- CleverTap: use "User's local time" setting in campaign delivery
- For Spain-heavy base (Bit2Me): CET/CEST is primary — but validate with Marta if significant LATAM share exists in target segment

### Optimal Send Times by Lifecycle Stage

| Stage | Optimal Window | Rationale |
|---|---|---|
| **New users (registered <24h)** | Within 2h of registration (daytime only) | Urgency while intent is hot; avoid late-night sends |
| **KYC approved** | Within 30 min of approval | Peak motivation moment |
| **Deposited / no FM** | 10:00–12:00 local time | Morning when markets open; user is checking phone |
| **Active users** | Match their historical activity window | CleverTap "Optimal Time" feature — use it |
| **AT_RISK (14-30d inactive)** | Tuesday–Thursday, 10:00–11:00 | Avoid Monday (overwhelmed) and Friday (weekend mode) |
| **Dormant with balance** | Market event OR Tuesday 10:00 fallback | Event-triggered outperforms scheduled |
| **Dormant zero balance** | Lower priority; use email as primary | Push ROI is low without asset hook |

### Frequency Capping Rules (Non-Negotiable)

| Segment | Max per day | Max per week | After N non-opens |
|---|---|---|---|
| New users (0-7d) | 2 | 5 | Suppress after 5 non-opens |
| Active users | 1 | 3 | Suppress after 7 non-opens |
| AT_RISK | 1 | 2 | Suppress after 4 non-opens |
| Dormant | 1 | 1 | Suppress after 3 non-opens |
| Post-reactivation | 1 | 3 | Standard active rules apply |

**CleverTap implementation:** Set frequency caps at the campaign level AND at the user profile level using Do Not Disturb settings. DND should be 22:00–08:00 local time for all segments.

---

## 3. Copy Framework

### Character Limits

| Field | Hard limit | Target sweet spot |
|---|---|---|
| Title | 65 chars (iOS) / 65 chars (Android) | 40-50 chars |
| Body | 240 chars (Android) / 178 chars (iOS) | 80-120 chars |

Always write to the iOS body limit first. Test on both platforms before send.

### The FOMO Formula

**[Trigger] + [Specific number] + [Consequence/opportunity] + [CTA implied or explicit]**

Examples:
- "BTC subió 4.2% en las últimas 3h. Tu cartera lo notó." *(trigger + number + consequence)*
- "73,000 traders compraron hoy. ¿Y tú?" *(social proof + implicit CTA)*
- "Solo hoy: 0 comisiones en tu primera compra de ETH." *(urgency + offer)*

### Copy Templates by Use Case

**Reactivation (dormant with balance):**
```
Title: [Asset] ha subido X% esta semana
Body:  Tu cartera en Bit2Me tiene saldo esperando. Échale un vistazo.
```

```
Title: Llevas [N] días sin operar
Body:  El mercado no para. Tu [Asset] está a un tap de distancia.
```

**Activation (deposited, no first monetization):**
```
Title: Estás a 1 paso de tu primera operación
Body:  Tienes fondos listos. BTC, ETH, SOL — elige y empieza.
```

```
Title: [Name], tu dinero está esperando
Body:  Tienes saldo pero aún no has operado. ¿Qué te frena?
```

**Retention (active, weekly summary):**
```
Title: Tu resumen de la semana está listo
Body:  [Asset] +X%, tu cartera +Y€. Sigue así.
```

**AT_RISK re-engagement:**
```
Title: Te echamos de menos, [Name]
Body:  Han pasado [N] días. El mercado ha movido mucho. Vuelve a ver qué ha cambiado.
```

### Emoji Usage: When It Helps vs Hurts

**Use emojis when:**
- The send is promotional or lifestyle (not transactional)
- The emoji adds clarity faster than words (📈 for price up, ⏰ for urgency)
- The segment is younger or high-engagement

**Avoid emojis when:**
- Transactional notifications (deposit confirmed, withdrawal sent)
- High-value/institutional segments (B2B, Power users)
- The emoji might render as a box on older Android devices

**A/B test rule:** Always test emoji vs no-emoji. Crypto users often respond better to clean, data-forward copy. Never assume emojis help without testing.

---

## 4. Personalization

### Dynamic Tokens Available in CleverTap

Use these tokens in push templates (verify availability with Katy for each property name):

| Token | Example output | When to use |
|---|---|---|
| `{{first_name}}` | "Carlos" | Any message; highest personalization lift |
| `{{last_asset_traded}}` | "BTC" | Reactivation, AT_RISK |
| `{{portfolio_balance_eur}}` | "€342" | Dormant with balance (high urgency) |
| `{{days_since_last_trade}}` | "23" | AT_RISK, dormant |
| `{{last_product_used}}` | "Earn" | Product upsell, cross-sell |
| `{{kyc_status}}` | "Verificado" | Onboarding stage |

**Rule:** If a token has a null/empty value for a user, CleverTap will either blank it or break the message. Always set a **fallback value** for every token. Example: `{{first_name | default: "trader"}}`.

### Segment-Specific Messaging Map (37-Segment Model)

Key segments and push approach:

| Segment | Push persona | Key hook | Avoid |
|---|---|---|---|
| SEG-01 New KYC (no deposit) | Curious beginner | "First trade is the hardest — we made it easy" | Complex product language |
| SEG-04 Deposited / no FM | Ready but stuck | Specific asset + price movement | Generic "start trading" |
| SEG-12 Active Power | Performance-driven | Portfolio analytics, advanced features | Beginner-level copy |
| SEG-20 AT_RISK (14-30d) | Drifting | Social proof, what they're missing | Guilt framing |
| SEG-28 Dormant with balance | Sleeping money | Their specific balance + market gain | Alarming/aggressive tone |
| SEG-35 Reactivated | Second chance | Celebrate return, offer continuity | Treating them like new users |

For full 37-segment copy matrix, cross-reference with `bit2me-journey-os/docs/journeys/`.

### Journey-Based Push Integration

**JN-01-A (Second Trade Accelerator — funded no FM):**
- Push fires at Day 1, Day 3, Day 7 post-deposit
- Day 1: activation hook ("Your funds are ready")
- Day 3: FOMO hook ("Here's what you missed")
- Day 7: last chance ("Don't leave your money idle")

**JN-02A (Active Sleeper — 14-30d inactive with balance):**
- Push is trigger 1 in the sequence (before email)
- Single send: market movement hook with balance reference
- If no open in 48h, escalate to email

**JN-03 (Deep Dormant Reactivation — 90d+ inactive):**
- Push is low-confidence channel; use only if opted-in and FOMO Score >= 60
- Send at market event trigger only, not scheduled
- If no conversion in 7d, move to email + retargeting

---

## 5. Deep Links

### The Rule: Always Deep Link to the Action, Not the Home Screen

Every push tap should land the user 0 clicks from the intended action.

| Campaign type | Deep link target |
|---|---|
| Price movement alert | Asset detail screen for the specific asset |
| Deposit reminder | Deposit flow, pre-filled with last method |
| First trade activation | Trade screen with suggested asset pre-selected |
| Portfolio summary | Portfolio overview screen |
| Earn/staking upsell | Earn product page for the specific asset |
| Reactivation (no specific asset) | Portfolio overview (shows their actual balance) |
| KYC completion | KYC flow, next pending step |

### Deep Link Patterns

Confirm exact URL scheme with Katy/Álvaro for Bit2Me app. General pattern:
```
bit2me://trade?asset=BTC
bit2me://portfolio
bit2me://earn?asset=ETH
bit2me://deposit
bit2me://kyc?step=phone
```

### Handling Expired Deep Links

If a deep link points to a time-limited offer or expired promotion:
1. The app should catch the 404/expired state and redirect to the relevant category (not crash)
2. Include a fallback parameter: `bit2me://trade?asset=BTC&fallback=portfolio`
3. Coordinate with engineering to ensure all push deep links have graceful fallback behavior
4. Never deep link to a promo page without confirming the promo is still live

---

## 6. A/B Testing Push Notifications

### What to Test (Priority Order)

1. **Headline / Title** — highest impact variable; test different hooks (FOMO vs benefit vs curiosity)
2. **Timing** — same message, different send time (e.g., 09:00 vs 18:00)
3. **Personalization** — name/asset token vs generic
4. **Emoji vs no emoji** — especially for crypto segments
5. **Body length** — short (50 chars) vs full body (120 chars)
6. **CTA specificity** — "Ver cartera" vs "Operar ahora" vs no explicit CTA

### Sample Size Requirements for Push

Push CTR is lower than email (3-6% vs 15-25%), which means you need larger samples for significance.

| Expected CTR | MDE (relative) | Required n per variant |
|---|---|---|
| 3% | 20% (detect 3% → 3.6%) | ~12,000 |
| 5% | 20% (detect 5% → 6%) | ~7,200 |
| 5% | 10% (detect 5% → 5.5%) | ~28,800 |

**Practical rule for Bit2Me FOMO Agent (16,116 users):**
- Minimum viable test: 2 variants, 8,000 users each
- Only test one variable at a time
- Run for minimum 72h before reading results (avoid day-of-week bias)
- Never call a winner at < 95% statistical confidence

For precise sample size calculations, invoke the `statistical-analysis` skill.

### Control Groups — Always Use a Holdout

- Minimum holdout: 10% of eligible segment (pure control, no push sent)
- Purpose: measure true incremental lift of push vs no-push, not just CTR
- CleverTap: create a "Control" bucket in the campaign split; do not send to this group
- Report: compare 7d conversion rate of push recipients vs holdout

### Primary Metric: Conversion, Not CTR

**Wrong:** "Push A had 6.2% CTR vs Push B's 4.1% — A wins."
**Right:** "Push A converted 1.8% to trade vs Push B's 1.2% — A wins on revenue impact."

Metrics hierarchy for push campaigns:
1. **Primary:** 7-day conversion rate (deposit, first trade, reactivation trade)
2. **Secondary:** Revenue per user (push recipients vs control)
3. **Guardrail:** Opt-out rate (if it spikes, something is wrong)
4. **Diagnostic only:** Open rate, CTR

---

## 7. Opt-Out Prevention

### Suppression After Consecutive Non-Opens

Implement in CleverTap using segment filters:

| Segment | Suppress after | Action |
|---|---|---|
| New users | 5 consecutive non-opens | Move to email-only track |
| Active | 7 consecutive non-opens | 30-day push pause, then re-permission attempt |
| Dormant | 3 consecutive non-opens | Remove from push channel; retain for email/retargeting |

In CleverTap: create a "Push Fatigue" segment using the event filter `Push Notification Received` without subsequent `Push Notification Clicked` for N occurrences. Exclude this segment from all non-transactional push.

### Preference Center

Best practice (implement if engineering bandwidth allows):
- Let users choose: "How often do you want to hear from us?" (Daily / Weekly / Only important alerts / Never)
- Map preferences to CleverTap profile properties and filter campaigns accordingly
- Reduces opt-outs by 20-40% in fintech (users who control frequency stay longer)

Minimum viable version: single toggle "Price alerts only" vs "All updates" in app settings.

### Re-Permission Campaigns

For users who have opted out of push but remain in the app:
1. Wait at least 60 days after opt-out before attempting re-permission
2. Use in-app message (not push) to explain what they're missing
3. Trigger on a positive event (asset they held just moved +10%)
4. Template: "Parece que tienes las notificaciones desactivadas. Te perdiste que BTC subió 8% esta semana. ¿Las activamos?"
5. Deep link to OS notification settings if they accept

Do not attempt re-permission more than once per 90 days.

---

## 8. The FOMO Agent Pattern

### What It Is

The FOMO Agent is a daily automated push campaign targeting **16,116 dormant users** (CleverTap segments c6+c7) using market signal inputs to generate personalized, urgency-driven push notifications.

### Architecture

```
CoinGecko API (price data)
        ↓
FOMO Score Calculator
        ↓
Prioritized user list (top N by score)
        ↓
CleverTap API → Push send
        ↓
Conversion tracking (7d window)
```

### FOMO Score Logic

Score range: 0–100. Users with score >= 60 receive the daily push.

Score components:
| Signal | Weight | Description |
|---|---|---|
| **Price movement** | 35% | 24h % change of assets user holds; BTC/ETH baseline |
| **Recency** | 25% | Days since last login (inverse — more days = higher urgency) |
| **Balance value** | 20% | EUR value of held assets (higher AUC = higher priority) |
| **Market volatility** | 10% | VIX equivalent for crypto (ATR or 30d realized vol) |
| **Timing signal** | 10% | Is today a high-activity day? (Mon/Tue outperform) |

### Daily Execution Workflow (Katy in CleverTap)

1. FOMO Agent script generates daily prioritized user list and top FOMO message variant
2. Katy receives list + message via automated report (or Slack/Lark notification)
3. Katy creates one-time push campaign in CleverTap:
   - Segment: import FOMO user list (or use pre-built "c6+c7 eligible" segment)
   - Message: use generated copy with dynamic tokens
   - Timing: send at 10:00 CET (default) or immediate if price event triggered
   - Frequency cap: confirm user hasn't received push in last 24h
4. Campaign sent; results checked at 24h and 7d marks

### Success Metrics

| Metric | Target | Notes |
|---|---|---|
| Reactivation rate | >2% per send | Reactivation = trade within 7d of push |
| Revenue per send | >€500/day | Track via Qlik or BigQuery using send cohort |
| Opt-out rate | <0.5% per send | Monitor daily; pause if spike detected |
| Open rate | >5% | Diagnostic only — do not optimize for opens |

**What NOT to optimize for:** raw open rate. A dormant user who opens but doesn't trade is not a win. Focus on the reactivation trade as the terminal conversion event.

### Market Signal Integration

When BTC or ETH moves >3% in 24h:
- Trigger an **unscheduled FOMO send** regardless of the day's scheduled send
- Use the price movement as the headline: "BTC subió 4.1% hoy. Tu cartera nota la diferencia."
- Limit to 1 unscheduled send per day even if multiple signals fire
- Do not send during DND window (22:00–08:00 local)

### Scaling the FOMO Agent

Current state: 16,116 dormant users, daily send.

Expansion path:
1. **AT_RISK segment** (14-30d inactive) — add to FOMO Agent with lighter-touch copy (they are not yet dormant)
2. **Frequency tuning** — currently daily; test 3x/week if opt-out rate climbs above 0.5%
3. **Multi-asset personalization** — if user holds 3+ assets, rotate which asset is featured in the message
4. **Post-reactivation suppression** — immediately remove reactivated users from FOMO Agent list; put them in the active retention track

---

## CleverTap Quick Reference (Katy)

### Campaign Setup Checklist

- [ ] Segment defined and user count confirmed
- [ ] Frequency cap set (check user hasn't received push in 24h)
- [ ] DND enabled (22:00–08:00 local)
- [ ] Dynamic token fallback values configured
- [ ] Deep link tested on iOS and Android
- [ ] A/B split configured (if testing)
- [ ] Holdout group set (minimum 10%)
- [ ] Conversion event defined in campaign goal
- [ ] Diego legal approval on copy (required for all CRM sends)
- [ ] Conversion tracking window set to 7 days

### Common CleverTap Pitfalls

| Pitfall | Fix |
|---|---|
| Tokens showing as `{{first_name}}` in send | Token name mismatch — verify exact property name in CleverTap profile |
| Push sending at wrong time | Check if "User's local time" is enabled; verify time zone mapping |
| Low delivery rate | Check permission status filter — only send to users with `push_token_status = valid` |
| Opt-out spike | Check frequency — likely too many sends in 24h; review cap settings |
| Zero conversions | Verify deep link is functional; check conversion event is correctly mapped |

---

## Strategy Decision Guide (Daniel)

| Situation | Recommended action |
|---|---|
| Dormant user has balance >€100 | FOMO Agent eligible; prioritize in score |
| Dormant user has zero balance | Low push priority; email + retargeting instead |
| User opened push 3x but never converted | Change copy angle; test benefit vs urgency vs social proof |
| Opt-out rate >0.5% on a send | Pause; audit frequency and copy; likely over-sending or wrong audience |
| Market moved >5% in 24h | Trigger unscheduled FOMO send immediately |
| New lifecycle journey needs push | Map push touchpoints to journey stages; 1 push per stage transition max |
| AT_RISK user hasn't responded to push | After 4 non-opens, pause push; escalate to email and in-app |
