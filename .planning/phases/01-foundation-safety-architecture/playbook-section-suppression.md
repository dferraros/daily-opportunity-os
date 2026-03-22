## 3. Suppression System

### 3.1 Suppression Overview

Suppression prevents high-risk sends: whale accounts receiving generic marketing blasts, users receiving pushes at 3 AM, and opted-out users getting marketing they explicitly refused. Four suppression layers operate in sequence: **Segment Exclusion**, **Quiet Hours (DND)**, **Opt-Out Handling**, and **Escalating Cooldowns**. A notification must pass ALL four layers to be delivered -- suppression is **additive**. If any layer blocks, the notification is suppressed regardless of the other layers' decisions.

---

### 3.2 Segment-Based Suppression

| Segment Name | Source | Users | Refresh Cadence | CleverTap Mechanism |
|---|---|---|---|---|
| **C8_Whale_Suppression** | BigQuery query (high-balance dormant users, definition from Alvaro) | ~TBD (pending Alvaro query) | Weekly (Monday morning) | Custom List segment via CSV upload or Custom List API |
| **Excluded_Users** | BigQuery (`lifecycle_stage = EXCLUDED`) | ~600,000 | Daily | Custom List segment |
| **Active_Support_Tickets** | Backend/CRM system (users with open support tickets) | Variable | Daily | Custom List segment |
| **Legal_Hold** | Diego-flagged users (pending compliance review) | Variable | On-demand | Custom List segment |
| **Notification_Cooldown** | BigQuery (`notification_cooldown = true` from fatigue system) | Variable | Daily via Hightouch sync | User property filter in campaign targeting |

#### C8 Whale Suppression -- Upload Workflow

> **BLOCKER:** C8 suppression CSV is currently NOT uploaded to CleverTap (identified in LC-OS Phase A audit, March 2026). This is a **P0 action item** before ANY marketing campaign launches. High-value dormant users (72.4K users with EUR 19.5M AUC) are currently exposed to generic marketing blasts.

**Step-by-step upload process:**

1. **Generate list:** Alvaro runs BigQuery query to generate C8 user_id list from `bit2me_lifecycle.user_profiles` (exact query definition pending from Alvaro -- high-balance dormant users).

2. **Export as CSV** with the required format:
   ```
   Type,Identity
   i,user_001
   i,user_002
   i,user_003
   ```
   - `Type` must be `i` (identity-based lookup)
   - `Identity` is the user_id used as CleverTap Identity

3. **Upload to CleverTap** via dashboard (< 50MB) or Custom List API (< 5GB):

   **API Step 1:** Request pre-signed URL
   ```
   POST https://api.clevertap.com/1/custom-list/url
   Headers: X-CleverTap-Account-Id: {ACCOUNT_ID}, X-CleverTap-Passcode: {PASSCODE}
   Body: { "name": "C8_Whale_Suppression" }
   Response: { "presignedUrl": "https://..." }
   ```

   **API Step 2:** Upload CSV to pre-signed URL
   ```
   PUT {presignedUrl}
   Content-Type: text/csv
   Body: [CSV file content]
   ```

   **API Step 3:** Notify upload complete
   ```
   POST https://api.clevertap.com/1/custom-list/upload-done
   Headers: X-CleverTap-Account-Id: {ACCOUNT_ID}, X-CleverTap-Passcode: {PASSCODE}
   Body: { "name": "C8_Whale_Suppression" }
   ```

4. **Verify:** Check segment size in CleverTap dashboard (Segments > Custom List) matches BigQuery count. If mismatch > 5%, investigate identity matching issues.

5. **Schedule:** Every Monday morning (Katy uploads manually) or automate via Cloud Function calling Custom List API on a weekly Cloud Scheduler trigger.

**Owner:** Alvaro (BigQuery query) + Katy (CleverTap upload/verification)

---

### 3.3 Quiet Hours (DND)

| Parameter | Value | Notes |
|---|---|---|
| Quiet window | 22:00 - 08:00 user local timezone | 10-hour quiet period covering sleep hours |
| Timezone source | CleverTap device timezone (auto-detected from SDK) | Resolved per-user from device settings |
| Fallback timezone | CET/CEST (Spain) | Applied when user timezone is unknown |
| DND action | **DELAY** delivery (queue until 08:00) | NOT discard -- notifications are held, not dropped |
| Exception | P0 Security notifications (login from new device, withdrawal confirmation, 2FA) | NEVER subject to DND |
| CleverTap config | Per campaign > Settings > When > Delivery Preferences > DND checkbox | Must be set on EVERY campaign |

**DND is configured PER CAMPAIGN in CleverTap, not globally.** Every new campaign must have DND configured. This is item #4 on the Campaign Creation Checklist (see Section 2.6 Frequency Cap Policy). Failure to set DND on a new campaign means users can receive pushes at 3 AM, which is the #1 cited reason for push opt-out in user surveys.

#### Timezone-Specific Quiet Hours

| Region | Quiet Start | Quiet End | Timezone |
|---|---|---|---|
| Spain | 22:00 | 08:00 | CET (UTC+1) / CEST (UTC+2) |
| LatAm (general) | 22:00 | 08:00 | User local timezone |
| Central Europe | 22:00 | 08:00 | CET/CEST |

**Note:** CleverTap resolves per-user timezone automatically from device. These are the expected quiet hour ranges for verification purposes. If a user's device reports an unexpected timezone, CleverTap will apply DND based on the reported timezone, not these region defaults.

---

### 3.4 Opt-Out Handling

| Channel | Opt-Out Mechanism | System Response | Reversibility | CleverTap Property |
|---|---|---|---|---|
| **Push** | User disables in iOS Settings / Android app settings | `MSG-push` set to `false`, removed from ALL push campaigns | Requires user to manually re-enable in device settings (effectively permanent on iOS) | `MSG-push` |
| **Push (granular)** | User turns off a category in in-app preference center | `consent_marketing_push` or specific category flag set to `false` in BigQuery, synced to CleverTap via Hightouch | Reversible via preference center | Custom user property (e.g., `consent_marketing_push`) |
| **Email** | User clicks unsubscribe link in email | CleverTap Subscription Group unsubscribed, "Channel Unsubscribed" event fired | Reversible via re-subscribe or preference center | Subscription Group status |
| **Email (global)** | User clicks "Unsubscribe from all" | `MSG-email` set to `false` | Reversible via preference center | `MSG-email` |
| **In-App** | User closes/dismisses | No permanent opt-out for in-app (channel does not have a permission model) | N/A | Dismissed count tracked for fatigue scoring |

**Audit requirement:** All opt-out events must be logged in BigQuery (`bit2me_lifecycle.notification_log`) with timestamp, channel, category, and reason. **GDPR Article 7(3):** withdrawing consent must be as easy as giving it. The preference center must provide one-tap opt-out per category, and the system must process the opt-out within 24 hours (immediate for push/email via CleverTap; daily sync for BigQuery audit trail).

**Owner:** Katy (CleverTap configuration) + Engineering (BigQuery logging)

---

### 3.5 Escalating Dismissal Cooldowns

| Level | Trigger Condition | Cooldown Applied | Scope | Duration | Reset Condition |
|---|---|---|---|---|---|
| **Level 0** | Normal -- no dismissals | No cooldown | -- | -- | -- |
| **Level 1** | 1 dismissal of a notification | 24-hour cooldown for that trigger family | Per user per family | 24 hours | Auto-expires after 24h |
| **Level 2** | 3 consecutive dismissals of same trigger family | 7-day cooldown for that family | Per user per family | 7 days | Auto-expires OR user clicks a notification from that family |
| **Level 3** | 5 consecutive dismissals across ANY trigger families | Reduce to P0-P1 only | Per user (all families) | 14 days | User opens/clicks any notification |
| **Level 4** | 10+ dismissals in 30 days | Flag for manual review, consider permanent suppression from P3+ | Per user | Until manual review | Katy reviews and decides |

**Implementation:** Escalation levels are computed daily in BigQuery from `bit2me_lifecycle.notification_log` (dismissal events). Level 3+ sets `notification_cooldown = true` in `user_profiles`, synced to CleverTap via Hightouch (see Section 5 -- Hightouch Reverse ETL). All P3-P5 campaigns must include targeting filter: `notification_cooldown != true`.

**Why escalating (not flat):** A single dismissal may be accidental or contextual. Three consecutive dismissals of the same family indicate low relevance for that trigger type. Five dismissals across families indicate general notification fatigue. This progressive approach avoids over-suppressing after one bad notification while protecting users who are clearly disengaged.

**Owner:** Alvaro (BigQuery computation) + Katy (CleverTap campaign targeting filters)

---

### 3.6 Campaign Launch Suppression Checklist

Every campaign must pass ALL items before activation. **All items must be YES before campaign activation. Katy owns this checklist. Any NO = campaign blocked until resolved.**

| # | Check | YES/NO |
|---|---|---|
| 1 | C8_Whale_Suppression segment added to exclusion? | YES / NO |
| 2 | Excluded_Users segment added to exclusion? | YES / NO |
| 3 | Active_Support_Tickets segment added to exclusion? | YES / NO |
| 4 | DND configured (22:00-08:00, delay, all days)? | YES / NO |
| 5 | `notification_cooldown != true` in targeting? | YES / NO |
| 6 | `fatigue_risk < threshold` for this tier? (see Section 2.5) | YES / NO |
| 7 | Diego copy approval obtained? | YES / NO |
| 8 | If targeting dormant users: warm-up schedule defined? | YES / NO |

**Process:** Katy completes this checklist for every new campaign before clicking "Activate" in CleverTap. Screenshot of the completed checklist is saved to the campaign documentation folder. Diego's copy approval (item 7) is a hard gate -- no campaign launches without it, per the compliance control established in Section 2.6.

**Cross-references:**
- Section 2.5: Fatigue Risk Score formula and thresholds
- Section 2.6: Frequency Cap Policy and Campaign Creation Checklist
- Section 5: Hightouch Reverse ETL (how suppression_flags and notification_cooldown reach CleverTap)
