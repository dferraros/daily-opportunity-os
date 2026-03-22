## 2. Frequency Cap Policy

> **Purpose:** This section defines the exact notification volume limits per channel, priority tier override rules, cooldown escalation logic, fatigue scoring, and the campaign creation checklist that ensures every new campaign is safely configured. These are the guardrails that prevent notification fatigue and protect push permissions.
>
> **Owners:** Katy (CleverTap campaign configuration), Alvaro (BigQuery fatigue score computation + Hightouch sync), Diego (copy approval gate)

---

### 2.1 Why Caps Matter

Notification frequency directly determines whether users keep or revoke push permissions -- and once lost, permissions are nearly impossible to recover:

- **46% of users opt out at 2-5 push messages/week** (Pushwoosh 2025 benchmark). This is the fatigue cliff -- exceeding it causes irreversible damage.
- **iOS push opt-out is PERMANENT** -- the user must manually navigate to Settings > Notifications > Bit2Me > Allow Notifications to re-enable. Virtually no one does this. Every iOS opt-out is a permanently lost push channel.
- **Android FCM auto-unsubscribes tokens inactive >270 days** (FCM policy enforced since May 2024). Dormant Android users silently disappear from the reachable audience.
- **Chrome Safety Check (2025) auto-unsubscribes high-volume/low-engagement senders** -- web push senders who send frequently but receive few interactions are automatically unsubscribed by the browser.

The consequence is asymmetric: one week of over-messaging can destroy months of permission building. Caps are not conservative -- they are protective of the most valuable channel Bit2Me has.

---

### 2.2 Global Channel Caps

These caps apply to **marketing notifications only** (CAT-MKT, CAT-PRD, CAT-PRO from Section 1). Transactional (P0) and user-configured (P1) are exempt via the "Exclude from Global campaign limits" checkbox in CleverTap.

| Channel | Daily Cap | Weekly Cap | Monthly Cap | CleverTap Config Path |
|---------|-----------|------------|-------------|----------------------|
| Push | 2/day | 8/week | 20/month | Settings > Engage > Campaign Limits |
| Email | 1/day | 3/week | 10/month | Settings > Engage > Campaign Limits |
| In-App | 3/day | 10/week | 30/month | Settings > Engage > Campaign Limits |
| SMS | 1/day | 2/week | 5/month | Settings > Engage > Campaign Limits |

**Configuration steps for Katy:**
1. Navigate to CleverTap > Settings > Engage > Campaign Limits
2. Set the daily, weekly, and monthly limits per channel as specified above
3. These limits apply globally to all campaigns unless a campaign is explicitly marked "Exclude from Global campaign limits"

**Key rule:** These caps apply to marketing notifications only. Transactional (P0) and user-configured (P1) are exempt via the "Exclude from Global campaign limits" checkbox. See Section 2.3 for which tiers are exempt.

---

### 2.3 Priority Tier System

Every notification Bit2Me sends is assigned to exactly one priority tier. When a user hits the global daily/weekly cap, lower-priority notifications are suppressed first. P0 and P1 ALWAYS deliver. P2+ are suppressed in reverse priority order (P5 first, then P4, then P3, then P2).

| Priority | Tier Name | Description | Examples | Subject to Global Caps | Campaign-Level Limit | CleverTap Setting |
|----------|-----------|-------------|----------|----------------------|---------------------|-------------------|
| P0 | Transactional / Security | Critical account and security notifications that must always reach the user | Login from new device, withdrawal confirmation, 2FA code, failed payment, password change | NO | None | "Exclude from Global campaign limits" = checked |
| P1 | User-Configured | Notifications the user explicitly requested | Price alerts user created, watchlist notifications, custom threshold alerts | NO | 1 per asset per 4 hours | "Exclude from Global campaign limits" = checked; campaign-level cooldown of 4h per asset |
| P2 | Lifecycle Critical | High-value lifecycle stage transitions that require timely intervention | AT_RISK stage entry, pre-dormancy warning (L3 Near-Dormant), J-Post-FM 48h activation | YES | 1/week per journey | Subject to global caps |
| P3 | Market Triggers | Proactive market notifications not explicitly requested by the user | Proactive price alerts (not user-configured), volatility spikes, trending assets, new listings | YES | 1/day, 3/week | Subject to global caps + campaign limit |
| P4 | Cross-sell / Product | Product adoption and expansion notifications | Earn promotion for brokerage-only users, Pro upsell, Space Center mission available | YES | 1/week, 2/month | Subject to global caps + campaign limit |
| P5 | Re-engagement / Promotional | Generic reactivation and promotional campaigns | Dormant user reactivation, generic promotional blasts, referral incentives | YES | 2/month | Subject to global caps + campaign limit |

**Override rule:** When a user hits the global daily/weekly cap, lower-priority notifications are suppressed first. P0 and P1 ALWAYS deliver. P2+ are suppressed in reverse priority order (P5 first, then P4, then P3, then P2). This means:
- A user who has received 2 marketing pushes today will NOT receive a P5 promotional push, but WILL receive a P0 security alert.
- A user who has received 8 marketing pushes this week will NOT receive any P3-P5 pushes for the remainder of the week, but P0, P1, and (if critical) P2 still deliver.

**Mapping to consent categories:**
- P0 maps to CAT-SEC and CAT-TXN (Art. 6(1)(b) -- no marketing consent needed)
- P1 maps to CAT-USR (Art. 6(1)(b) -- contract performance)
- P2-P5 map to CAT-MKT, CAT-PRD, CAT-PRO (Art. 6(1)(a) -- require marketing consent)

---

### 2.4 Cooldown Rules

Cooldowns prevent notification fatigue by enforcing minimum time gaps between sends and escalating suppression when users signal disengagement through dismissals.

| Condition | Cooldown | Scope | Mechanism |
|-----------|----------|-------|-----------|
| Between any two notifications (same channel) | 4 hours minimum | Per user, per channel | CleverTap campaign frequency limit: "Minimum time between messages = 4 hours" |
| After dismissed notification | 24 hours for that trigger family | Per user, per trigger family | BigQuery tracks dismissals per trigger family. CleverTap user property `last_dismissed_[family]` updated via Hightouch. Campaign targeting excludes users where `last_dismissed_[family] < 24h ago`. |
| After 3 consecutive dismissals (same family) | 7-day family cooldown | Per user, per trigger family | BigQuery computes consecutive dismissal count per family. When count >= 3, sets `cooldown_[family] = true` with expiry timestamp. Synced to CleverTap via Hightouch. Campaign targeting excludes users where `cooldown_[family] = true`. |
| After 5 consecutive dismissals (any family) | Reduce to P0-P1 only for 14 days | Per user (all families) | BigQuery computes total consecutive dismissals across families. When count >= 5, sets `notification_cooldown = true` with 14-day expiry. Synced to CleverTap as exclusion filter on all P2-P5 campaigns. |
| After user re-engages (opens or clicks any notification) | Reset cooldown immediately | Per user | BigQuery recalculates on next sync cycle. Consecutive dismissal counters reset to 0. `notification_cooldown` and `cooldown_[family]` flags cleared. User becomes eligible for all tiers again. |

**Implementation note for Alvaro:** The dismissal tracking requires a BigQuery scheduled query that reads notification engagement data (from CleverTap export or Hightouch reverse sync) and computes:
- `consecutive_dismissals_[family]`: count of consecutive dismissed notifications per trigger family (reset on any open/click)
- `consecutive_dismissals_total`: count of consecutive dismissed notifications across all families
- `notification_cooldown`: boolean flag (true when total >= 5, expires after 14 days)

---

### 2.5 Fatigue Risk Score Formula

The fatigue risk score is a per-user metric that quantifies how likely the user is to opt out if sent another notification. It combines three signals: send volume, dismissal rate, and engagement recency.

```
fatigue_risk = (notifications_sent_7d / 5) * 0.4
             + (notifications_dismissed_7d / max(notifications_sent_7d, 1)) * 0.3
             + (days_since_last_open / 7) * 0.3

Thresholds:
  fatigue_risk < 0.3:  GREEN    -- all tiers can send
  fatigue_risk 0.3-0.7: AMBER  -- suppress P5 notifications
  fatigue_risk 0.7-0.9: RED    -- suppress P3+ (only P0, P1, P2 can send) for 48 hours
  fatigue_risk > 0.9:  CRITICAL -- suppress P2+ (only P0, P1 can send) for 7 days
```

**Component breakdown:**
- **Send volume (weight 0.4):** `notifications_sent_7d / 5` -- normalized against 5 sends/week (the safe ceiling from Section 2.2). A user who received 5 pushes this week scores 0.4 on this component; 10 pushes scores 0.8.
- **Dismissal rate (weight 0.3):** `notifications_dismissed_7d / max(notifications_sent_7d, 1)` -- fraction of notifications dismissed (swiped away without opening). A user who dismissed 3 of 5 notifications scores 0.18 on this component.
- **Engagement recency (weight 0.3):** `days_since_last_open / 7` -- how many days since the user last opened any notification, normalized against 7 days. A user who last opened a notification 7 days ago scores 0.3 on this component.

**Where this runs:** Computed daily in BigQuery as a scheduled query. Stored in `bit2me_lifecycle.user_profiles` as `notification_fatigue_score` (float, 0-1). Synced to CleverTap via Hightouch every 30 minutes. Used as targeting filter in P3-P5 campaigns: include only where `fatigue_risk < threshold` for that tier.

**Campaign targeting rules by fatigue level:**

| Fatigue Level | Score Range | Allowed Tiers | Campaign Filter |
|---------------|-------------|---------------|-----------------|
| GREEN | < 0.3 | P0, P1, P2, P3, P4, P5 | No fatigue filter needed |
| AMBER | 0.3 - 0.7 | P0, P1, P2, P3, P4 | Exclude from P5 campaigns: `notification_fatigue_score < 0.3` |
| RED | 0.7 - 0.9 | P0, P1, P2 | Exclude from P3+ campaigns: `notification_fatigue_score < 0.7` |
| CRITICAL | > 0.9 | P0, P1 only | Exclude from P2+ campaigns: `notification_fatigue_score < 0.9` |

---

### 2.6 Campaign Creation Checklist

Every new campaign Katy creates must follow this 8-step checklist. This is the operational procedure that ensures frequency caps, suppression, and compliance are correctly configured before any notification is sent.

1. **Assign priority tier (P0-P5)** from the Priority Tier table (Section 2.3). Document the tier in the campaign name or description (e.g., "[P3] BTC Volatility Alert").

2. **If P0 or P1:** Check "Exclude from Global campaign limits" in CleverTap campaign settings. This ensures transactional and user-configured notifications are never suppressed by marketing caps.

3. **Set campaign-level frequency limit** per the Priority Tier table:
   - P1: 1 per asset per 4 hours
   - P2: 1/week per journey
   - P3: 1/day, 3/week
   - P4: 1/week, 2/month
   - P5: 2/month

4. **Set DND hours:** 22:00 - 08:00 user local timezone. Action = **Delay** (not discard) -- notifications queued during quiet hours are sent at 08:00 the next morning. **Exception:** P0 security notifications (login from new device, large withdrawal) have NO DND -- they send immediately at any hour.

5. **Add suppression segments:** For ALL marketing campaigns (P2-P5), add these exclusion segments:
   - Exclude `C8_Whale_Suppression` (high-value dormant users requiring white-glove treatment)
   - Exclude `Excluded_Users` (600K excluded users who should receive no communications)

6. **If P3+: Add fatigue risk targeting filter.** Include only users where `notification_fatigue_score < [threshold]`:
   - P3 campaigns: `notification_fatigue_score < 0.7`
   - P4 campaigns: `notification_fatigue_score < 0.7`
   - P5 campaigns: `notification_fatigue_score < 0.3`

7. **Send test notification** to internal QA segment before activation. Verify: correct copy, correct deep link, correct channel, no broken personalization variables.

8. **Get Diego approval on notification copy** (mandatory for all campaigns). Send the notification template text + any linked landing page to Diego for legal review. No campaign activates without Diego's written approval. This is the MiCA Art. 66 compliance gate.

---

### 2.7 Monitoring and Alerting

These KPIs are tracked weekly to detect fatigue, deliverability degradation, or cap misconfiguration before they cause permanent damage.

| KPI | Target | AMBER Threshold | RED Threshold | Data Source | Owner |
|-----|--------|----------------|---------------|-------------|-------|
| Push opt-out rate | < 0.5%/week | > 0.8%/week | > 1%/week = STOP all P3+ campaigns, investigate immediately | CleverTap dashboard > Push > Unsubscribe Rate | Katy (monitor), Daniel (escalation) |
| Push delivery rate | > 85% | < 80% | < 70% = token hygiene needed, check stale tokens | CleverTap delivery reports | Katy |
| Email spam complaint rate | < 0.1% | > 0.08% = AMBER | > 0.1% = RED, pause email campaigns, check Google Postmaster | Google Postmaster Tools (domain reputation) | Katy + Alvaro |
| Notification dismissal rate | < 40% | > 45% | > 50% = review notification relevance and copy | CleverTap engagement reports (per campaign) | Katy |
| Average fatigue_risk score (all active users) | < 0.4 | > 0.5 = AMBER | > 0.6 = reduce P3-P5 frequency | BigQuery scheduled query: `SELECT AVG(notification_fatigue_score) FROM bit2me_lifecycle.user_profiles WHERE lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')` | Alvaro (query), Daniel (review) |
| Push permission rate (iOS) | > 60% | < 50% | < 40% = consent flow UX issue | CleverTap > Users > Push Reachability | Katy + Product |

**Weekly review cadence:**
- Every Monday, Katy pulls the 6 KPIs above from CleverTap and BigQuery
- Any AMBER triggers a Slack notification to Daniel
- Any RED triggers an immediate pause of affected campaigns + escalation to Daniel + Diego

---

### Cross-References

- **Section 1 (Preference Center Architecture):** Priority tiers (P0-P5) map directly to consent categories (CAT-SEC through CAT-PRO). P0-P1 are exempt from marketing consent requirements. P2-P5 require `consent_marketing_[channel] = true`.
- **FOUND-03 (Suppression System):** Frequency caps are Layer 1 of the suppression architecture. Suppression segments (C8 whale, excluded users) are Layer 2. Cooldown escalation (Section 2.4) feeds into Layer 3. All three layers work together.
- **FOUND-05 (Hightouch Reverse ETL):** The `notification_fatigue_score` field must be included in the Hightouch sync configuration so that CleverTap campaigns can use it as a targeting filter.
