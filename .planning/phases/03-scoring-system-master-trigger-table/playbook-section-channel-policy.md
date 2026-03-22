## 13. Channel Policy Matrix

> **Purpose:** This section defines the complete channel routing policy for Bit2Me's trigger-based notification system. It covers four areas: (1) the channel decision algorithm that determines which channel delivers each notification, (2) the deep link architecture that connects every notification to an actionable screen, (3) quiet hours by region that prevent overnight sends, and (4) conflict resolution rules when triggers compete with active CleverTap Journeys (J1-J6).
>
> **Owners:**
> - **Katy** -- CleverTap channel configuration, DND settings, campaign channel selection
> - **Engineering** -- Deep link implementation, universal link fallback, SDK event instrumentation
> - **Product** -- Notification preference UX, deep link destination screens
>
> **Cross-references:**
> - Section 2 (Frequency Caps): Global caps per channel, DND hours (Section 2.6 step 4), priority tier override rules
> - Section 6 (Trigger Taxonomy): Family-level channel defaults, consent categories
> - Section 9 (Compliance Framework): MiCA Art. 89 simultaneous send requirement for Family B
> - Section 10 (Scoring Formulas): Send Score used in conflict resolution ranking
> - Section 11 (Master Trigger Table): Per-trigger channel and deep_link values

---

### 13.1 Channel Decision Tree (CHAN-01)

The channel selection algorithm runs for every trigger evaluation. It determines the primary, secondary, and fallback delivery channels based on trigger priority, content requirements, user channel availability, and family-specific rules.

#### 13.1.1 Decision Tree (4-Step Algorithm)

```
STEP 1: Is priority P0 (security/transactional)?
  |
  |-- YES --> Push + Email (dual delivery, no fallback needed)
  |           Rationale: Security alerts must reach user through all available channels.
  |           DND exempt. No channel selection logic -- send on ALL enabled channels.
  |
  |-- NO  --> Continue to Step 2

STEP 2: Is content_depth_required HIGH?
  |
  |-- YES --> Email (primary) + In-App (secondary)
  |           Rationale: Long-form content (cross-sell value prop, reactivation narrative,
  |           risk explanation) cannot fit in push character limits (65 chars iOS, 240 Android).
  |           Email allows full copy + images + CTA buttons.
  |
  |-- NO  --> Continue to Step 3

STEP 3: Is user_push_enabled AND engagement_recency < 7 days?
  |
  |-- YES --> Push (primary)
  |           Rationale: User is reachable and recently engaged. Push has 3-4x higher
  |           conversion rate per message vs email (industry benchmark).
  |
  |-- NO  --> Is user_email_enabled?
  |     |
  |     |-- YES --> Email (fallback)
  |     |           Rationale: User is not push-reachable or has been inactive >7 days.
  |     |           Email is the next-best channel for reaching disengaged users.
  |     |
  |     |-- NO  --> In-App only
  |                 Rationale: User has no push or email channel available.
  |                 In-App notification displays on next app open.
  |                 Note: This is a last resort -- user may not see it for days/weeks.

STEP 4: Is trigger Family B AND requires simultaneous send?
  |
  |-- YES --> Push to ALL eligible users simultaneously
  |           Rationale: MiCA Art. 89 requires that market-triggered notifications
  |           reach all eligible users at the same time to prevent information asymmetry.
  |           No staggered sends. No A/B testing on send timing.
  |           Override: This step supersedes Step 3's individual channel selection.
  |
  |-- NO  --> Use channel selected in Steps 1-3
```

#### 13.1.2 Channel Assignment Matrix by Family

This matrix defines the default channel routing per trigger family. Individual triggers in the Master Trigger Table (Section 11.2) may override these defaults where documented.

| Family | Primary Channel | Secondary Channel | Fallback Channel | Rationale |
|--------|----------------|-------------------|------------------|-----------|
| A (User Configured) | Push | Email | In-App | User expects immediate delivery of alerts they created. Push is fastest channel. |
| B (Market Triggered) | Push | In-App | Email | Time-sensitive market data. MiCA requires simultaneous send to all eligible users (Art. 89). |
| C (Behavioral) | In-App | Push | Email | Lower permission risk. User is likely in-app when behavioral pattern is detected. In-App avoids push fatigue for nudge-type content. |
| D (Lifecycle) | Push | Email | In-App | Re-engagement requires reaching inactive users who may not open the app. Push + email combo maximizes reach for lifecycle transitions. |
| E (Cross-sell) | Email | In-App | Push (last resort) | Content depth needed for value proposition. Cross-sell copy requires explanation, comparison, and CTA -- too long for push. Push used only as last resort to avoid permission risk. |
| F (Risk/Protective) | Push + Email | -- | -- | Dual delivery for all risk alerts. No fallback needed -- if user has neither push nor email, In-App displays on next open. P0 triggers bypass DND. |

#### 13.1.3 Channel Selection Pseudocode

```python
def select_channel(trigger, user):
    """
    Returns the delivery channel(s) for a given trigger and user.

    Args:
        trigger: dict with keys: priority, family, content_depth_required
        user: dict with keys: push_enabled, email_enabled,
              days_since_last_engagement, active_journey

    Returns:
        list of channels to send on (e.g., ['push'], ['email', 'in_app'], ['push', 'email'])
    """

    # STEP 1: P0 security -- dual delivery, always
    if trigger['priority'] == 'P0':
        channels = []
        if user['push_enabled']:
            channels.append('push')
        if user['email_enabled']:
            channels.append('email')
        if not channels:
            channels.append('in_app')  # last resort
        return channels

    # STEP 4 (checked early): Family B simultaneous send
    if trigger['family'] == 'B':
        # MiCA Art. 89: simultaneous send to all eligible users
        # Push is primary for time-sensitivity
        if user['push_enabled']:
            return ['push']
        elif user['email_enabled']:
            return ['email']
        else:
            return ['in_app']

    # STEP 2: High content depth --> email primary
    if trigger.get('content_depth_required') == 'HIGH':
        channels = ['email'] if user['email_enabled'] else []
        channels.append('in_app')  # always add in-app as secondary
        return channels if channels else ['in_app']

    # STEP 3: Standard channel selection
    if user['push_enabled'] and user['days_since_last_engagement'] < 7:
        return ['push']
    elif user['email_enabled']:
        return ['email']
    else:
        return ['in_app']
```

**CleverTap implementation note for Katy:** When creating a campaign, select the primary channel per the family defaults above. Use CleverTap's "Fallback" feature to configure the secondary and fallback channels. For Family F triggers, create a multi-channel campaign (Push + Email) rather than a single-channel campaign with fallback.

---

### 13.2 Deep Link Architecture (CHAN-02)

Deep links are Bit2Me's MVP differentiator. Phase 2 competitive benchmark (Section 8.7, Gap #6) found that no competitor implements alert-to-action deep links well. Every notification that arrives without a deep link to a relevant action screen is a wasted engagement opportunity.

**Rule: Every trigger in the Master Trigger Table MUST have a deep_link value. No trigger ships without a tested deep link.**

#### 13.2.1 Deep Link Table (11 Products)

| Product | Deep Link Pattern | Example | Used By Families | Notes |
|---------|------------------|---------|-----------------|-------|
| Brokerage | `bit2me://brokerage/trade?asset={symbol}` | `bit2me://brokerage/trade?asset=BTC` | A, B, C | Opens trade screen with asset pre-selected. Primary conversion endpoint. |
| Pro | `bit2me://pro/chart?pair={symbol}-EUR` | `bit2me://pro/chart?pair=ETH-EUR` | B, E | Opens Pro chart view with trading pair. Used for market and cross-sell triggers. |
| Earn | `bit2me://earn/stake?asset={symbol}` | `bit2me://earn/stake?asset=USDT` | E | Opens Earn staking screen with asset pre-selected. Cross-sell conversion endpoint. |
| Card | `bit2me://card/activate` | `bit2me://card/activate` | E | Opens Card activation flow. No asset parameter needed. |
| Loan | `bit2me://loan/collateral?loan_id={id}` | `bit2me://loan/collateral?loan_id=123` | A, F | Opens loan collateral management screen. Used for LTV alerts and user-configured loan monitoring. |
| Space Center | `bit2me://space-center/missions` | `bit2me://space-center/missions` | E | Opens Space Center missions view. V2 trigger (E-03 deferred). |
| Wallet | `bit2me://wallet/asset?symbol={symbol}` | `bit2me://wallet/asset?symbol=BTC` | C, D | Opens wallet view for specific asset. Used for behavioral nudges and lifecycle portfolio review. |
| Launchpad | `bit2me://launchpad/event?id={id}` | `bit2me://launchpad/event?id=456` | B | Opens specific Launchpad event. Used for new listing announcements (B-05). |
| Pay | `bit2me://pay/merchants` | `bit2me://pay/merchants` | E | Opens Pay merchants directory. Cross-sell conversion endpoint. |
| Settings | `bit2me://settings/notifications` | `bit2me://settings/notifications` | All | Opens notification preferences. Used as unsubscribe deep link and for notification preference management triggers. |
| Portfolio | `bit2me://portfolio/overview` | `bit2me://portfolio/overview` | D, F | Opens portfolio overview dashboard. Used for lifecycle and risk/protective triggers that reference aggregate portfolio state. |

#### 13.2.2 Deep Link Testing Protocol

Every deep link must pass this 4-step validation before the associated trigger can launch:

| Step | Test | Expected Result | Owner |
|------|------|----------------|-------|
| 1 | **App installed (iOS):** Tap deep link from push notification | App opens to the correct screen with correct parameters (asset pre-selected, loan ID loaded, etc.) | Engineering (QA) |
| 2 | **App installed (Android):** Tap deep link from push notification | Same as iOS. Verify Intent filter handles the `bit2me://` scheme correctly. | Engineering (QA) |
| 3 | **App NOT installed:** Tap deep link from email on device without app | Fallback to web URL: `https://bit2me.com/[product]/[action]?asset={symbol}`. App Store / Play Store redirect if no web equivalent. | Engineering (QA) |
| 4 | **Web email client:** Click deep link from desktop email client | Opens web app at equivalent URL: `https://app.bit2me.com/[product]/[action]?asset={symbol}` | Engineering (QA) |

**Fallback URL mapping:**

| Deep Link | Web Fallback URL |
|-----------|-----------------|
| `bit2me://brokerage/trade?asset={symbol}` | `https://app.bit2me.com/trade/{symbol}` |
| `bit2me://pro/chart?pair={symbol}-EUR` | `https://pro.bit2me.com/chart/{symbol}-EUR` |
| `bit2me://earn/stake?asset={symbol}` | `https://app.bit2me.com/earn/{symbol}` |
| `bit2me://card/activate` | `https://app.bit2me.com/card/activate` |
| `bit2me://loan/collateral?loan_id={id}` | `https://app.bit2me.com/loan/{id}` |
| `bit2me://wallet/asset?symbol={symbol}` | `https://app.bit2me.com/wallet/{symbol}` |
| `bit2me://portfolio/overview` | `https://app.bit2me.com/portfolio` |
| `bit2me://settings/notifications` | `https://app.bit2me.com/settings/notifications` |

**CleverTap configuration for Katy:** When creating a notification template, paste the deep link into the "On Click" action field. For push notifications, CleverTap handles the `bit2me://` scheme natively. For email, use the web fallback URL as the CTA button href.

---

### 13.3 Quiet Hours by Region (CHAN-03)

Quiet hours prevent notifications from reaching users during sleeping hours. The action is DELAY (queue for morning delivery), not DISCARD (permanently suppress). This ensures notifications are not lost, just time-shifted.

#### 13.3.1 Quiet Hours Table

| Region | Quiet Hours (Local Time) | P0 Exempt | Action During Quiet Hours | CleverTap Config |
|--------|------------------------|-----------|--------------------------|-----------------|
| Spain (CET/CEST) | 22:00 - 08:00 | Yes | Delay -- queue for 08:00 next morning | DND settings: Start 22:00, End 08:00, Action = Show Later |
| LatAm (multiple TZ) | 22:00 - 08:00 local | Yes | Delay -- queue for 08:00 next morning | DND settings per timezone (CleverTap uses user profile TZ) |
| EU (CET/EET/WET) | 22:00 - 08:00 local | Yes | Delay -- queue for 08:00 next morning | DND settings per timezone |
| Other | 22:00 - 08:00 local | Yes | Delay -- queue for 08:00 next morning | DND settings per timezone |

#### 13.3.2 Key Rules

1. **Action is DELAY, not DISCARD.** Notifications triggered during quiet hours are queued and delivered at 08:00 local time the next morning. No notification is permanently lost due to quiet hours. This is configured in CleverTap as "Show Later" (not "Suppress").

2. **P0 security notifications have NO DND.** Login from new device, large withdrawal confirmation, 2FA codes, and stablecoin de-peg alerts (F-04, F-05) send immediately regardless of time. A user receiving a "Login from unknown device" alert at 3:00 AM is a feature, not a bug.

3. **CleverTap handles timezone conversion natively.** CleverTap reads the user's timezone from their profile (set via SDK on app install, updated on location change). The DND window is applied per-user based on their local time. No manual timezone calculation needed.

4. **Quiet hours apply to Push and Email only.** In-App notifications are not subject to quiet hours because they only display when the user opens the app (which they would not do while sleeping).

5. **Queue overflow risk:** If a user has 3+ notifications queued overnight, they all deliver at 08:00. This could feel like a notification dump. Mitigation: the global daily cap (2 push/day, 1 email/day from Section 2.2) applies to the 08:00 delivery window. If the cap is exceeded, lower-priority notifications are suppressed per Section 2.3 priority tier rules.

**Implementation reference:** Phase 1 Section 2.6 step 4 defines the DND configuration in the Campaign Creation Checklist. This section extends that specification with regional coverage and queue behavior.

---

### 13.4 Journey vs Alert Conflict Resolution (CHAN-04)

When a user is currently enrolled in an active CleverTap Journey (J1 through J6) AND a trigger fires for that same user simultaneously, the conflict resolution rules below determine which message sends.

#### 13.4.1 Active Journeys at Bit2Me

| Journey ID | Name | Description |
|-----------|------|-------------|
| J1 | Brokerage Onboarding | New user -> first trade flow |
| J2 | Pro Upgrade | Brokerage user -> Pro adoption |
| J3 | Earn Discovery | Active user -> Earn product adoption |
| J4 | Card Activation | PAUSED -- Card journey currently inactive |
| J5 | B2B Onboarding | Business user onboarding flow |
| J6 | Multi-Product | Cross-product adoption journey |

#### 13.4.2 Conflict Resolution Matrix

| Scenario | Resolution | Rationale |
|----------|-----------|-----------|
| User in J1-J6 + Family A trigger fires | **SEND Family A** | User explicitly requested this alert. User-configured alerts always deliver regardless of journey state. |
| User in J1-J6 + Family B trigger fires | **SEND Family B** | Market data is time-sensitive. MiCA Art. 89 requires simultaneous send to prevent information asymmetry. Cannot delay for journey scheduling. |
| User in J1-J6 + Family C trigger fires | **SUPPRESS Family C** | Behavioral nudge can wait. The journey is already engaging the user with a structured flow. Adding a behavioral nudge risks over-messaging and journey disruption. |
| User in J1-J6 + Family D trigger fires | **SUPPRESS Family D** | Lifecycle nudge can wait. If a user is in J1 (onboarding), they do not need a separate lifecycle stage transition notification. The journey itself is the lifecycle intervention. |
| User in J1-J6 + Family E trigger fires | **SUPPRESS Family E** | Cross-sell can wait. The journey (especially J3 Earn Discovery, J6 Multi-Product) may already be cross-selling. Sending an additional cross-sell trigger creates conflicting CTAs. |
| User in J1-J6 + Family F trigger fires | **SEND Family F** | Protective alert overrides all journey logic. A user at LTV liquidation risk or receiving a security alert must be notified immediately regardless of what journey they are in. |
| Two triggers of the SAME family fire in same evaluation window | **Send highest send_score only** | Avoid double-nudging the user with two messages of the same type. The highest-scoring trigger wins. The other is suppressed for this window. |
| Triggers of DIFFERENT families fire in same day (e.g., P2 lifecycle + P3 market) | **Send both** | Different families have independent frequency caps (Section 2.2). A lifecycle notification and a market notification serve different purposes and count against different caps. |

#### 13.4.3 Implementation

**SQL targeting filter for suppressed families (C, D, E):**

```sql
-- Add this WHERE clause to all Family C, D, E campaign targeting queries
-- This ensures users in active journeys do NOT receive these trigger notifications

WHERE active_journey IS NULL

-- active_journey is a CleverTap user property synced via Hightouch
-- It contains the journey ID (J1-J6) if the user is currently in a journey, or NULL if not
-- Updated by CleverTap Journey webhook -> BigQuery -> Hightouch reverse sync
```

**Bypass for families A, B, F:**

```sql
-- Family A, B, F campaigns do NOT include the active_journey filter
-- These families send regardless of journey state

-- Family A: user-requested, always sends
-- Family B: MiCA simultaneous send requirement
-- Family F: protective/security, always sends
```

#### 13.4.4 Additional Conflict Rules

1. **Same-family same-window:** When multiple triggers of the SAME family fire in the same evaluation window (e.g., two B-family triggers fire because BTC has both a volatility spike and a price breakout), only the trigger with the highest `send_score` sends. The other is suppressed for this evaluation cycle. This prevents double-nudging within the same category.

2. **Cross-family independence:** When triggers of DIFFERENT families fire, they are treated independently. Each family has its own frequency cap (Section 2.2), its own cooldown rules (Section 2.4), and its own fatigue contribution. A user can receive one Family B push AND one Family D email on the same day without conflict.

3. **Family B simultaneous send override:** The MiCA Art. 89 simultaneous send requirement for Family B OVERRIDES all other conflict logic. When a Family B trigger fires, it sends to ALL eligible users at the same time, regardless of:
   - Whether they are in a journey (override: SEND)
   - Whether they received another notification today (override: SEND, different family cap)
   - Whether it is quiet hours for some users (override: Family B is P3, so DND DOES apply -- queue for 08:00)

   Note: Family B is NOT exempt from quiet hours (it is P3, not P0). The simultaneous send requirement means all users receive the notification at the same time within their respective timezone delivery windows.

4. **Journey exit events:** When a user exits a journey (completes or drops off), the `active_journey` property is set to NULL on the next Hightouch sync cycle (30-minute cadence). The user then becomes eligible for Family C, D, E triggers again. There is no additional cooldown after journey exit -- the standard family-level cooldowns (Section 2.4) apply.

---

### 13.5 Cross-References

- **Section 2 (Frequency Caps):** Global channel caps (2 push/day, 1 email/day, 3 in-app/day), DND configuration (Section 2.6 step 4), priority tier override rules (Section 2.3)
- **Section 6 (Trigger Taxonomy):** Family-level channel defaults and consent categories per family
- **Section 9 (Compliance Framework):** MiCA Art. 89 simultaneous send requirement for Family B (Section 9.4), market abuse prevention protocol
- **Section 10 (Scoring Formulas):** Send Score Final (SCORE-08) used for conflict resolution ranking when multiple same-family triggers compete
- **Section 11 (Master Trigger Table):** Per-trigger `channel` and `deep_link` values in the 14-column specification
- **Section 12 (MVP Selection):** 30-day launch plan wave structure depends on channel readiness per family
