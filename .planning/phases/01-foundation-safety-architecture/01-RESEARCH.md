# Phase 1: Foundation + Safety Architecture - Research

**Researched:** 2026-03-22
**Domain:** CRM notification safety infrastructure (CleverTap + BigQuery + Hightouch)
**Confidence:** HIGH

## Summary

Phase 1 designs and documents the safety rails that must be in place BEFORE any trigger-based notification fires. This is a strategic/design deliverable (a playbook chapter), not code. The five requirements (FOUND-01 through FOUND-05) cover: Preference Center architecture with data model, frequency cap policy with exact numbers and P0-P5 priority tiers, suppression system (C8 whale list, quiet hours, opt-out handling, cooldown escalation), event schema for CleverTap SDK + Backend Upload Events API, and Hightouch Reverse ETL integration design (BigQuery to CleverTap).

The research confirms that CleverTap provides native mechanisms for all five areas -- subscription groups for preference management, per-channel frequency caps with daily/weekly limits, DND (Do Not Disturb) hours, Custom List segments via CSV upload for suppression, and the Upload Events API with a well-defined schema. Hightouch's BigQuery-to-CleverTap connector supports profile upserts and event inserts with incremental change detection. The planner should structure tasks around documenting the configuration of these existing platform capabilities, not designing custom infrastructure.

**Primary recommendation:** Structure the phase as five deliverable documents (one per FOUND requirement), each specifying the exact CleverTap configuration, BigQuery schema, and Hightouch mapping needed. Every document should be executable by Katy (CleverTap) or Alvaro (BigQuery) without ambiguity.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUND-01 | Preference Center -- architecture, consent categories, data model | CleverTap Subscription Groups (50 max), per-channel MSG-* profile properties, Subscribe API, Group Unsubscribe; GDPR/ePrivacy per-channel consent requirements |
| FOUND-02 | Frequency cap policy -- daily/weekly/monthly caps by channel and trigger family | CleverTap native per-channel frequency caps (Settings > Engage > Campaign Limits), campaign-level frequency limits, priority tier system (P0-P5) from PITFALLS.md |
| FOUND-03 | Suppression system -- C8 whale list, quiet hours, opt-out, cooldown escalation | CleverTap Custom List segments (CSV upload, max 50MB dashboard / 5GB API), DND configuration per campaign, MSG-* profile properties for channel-level DND, cooldown via journey re-entry delays |
| FOUND-04 | Event schema -- minimum viable events for CleverTap SDK + Upload Events API | Upload Events API (1000 records/call, 15 concurrent requests, 512 event types max, 256 properties/event), event property constraints, system reserved events, Charged event pattern |
| FOUND-05 | Hightouch Reverse ETL integration design (BigQuery to CleverTap) | Hightouch CleverTap destination (profile upsert + event insert), identifier fields (Identity or GUID), incremental change detection, field mapping, scheduling |
</phase_requirements>

## Standard Stack

### Core (Already Owned -- Configuration Only)
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| CleverTap | Enterprise | Subscription groups, frequency caps, DND, segments, campaign delivery | Already deployed with J1-J6 journeys. All five FOUND requirements map to native CleverTap features. |
| BigQuery | Current | User profile source of truth, suppression lists, fatigue score computation | bit2me_lifecycle schema exists (V0a-V10). Suppression lists and computed attributes live here. |

### New (One-Time Setup)
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| Hightouch | Business ($350-500/mo) | Reverse ETL: BigQuery user profiles to CleverTap | FOUND-05. Sync lifecycle_stage, health_score, suppression_flags, fatigue_score to CleverTap user properties. |

### No Alternatives Needed

This phase uses only existing platform capabilities. There is no build-vs-buy decision. Everything is configure-and-document.

## Architecture Patterns

### Pattern 1: CleverTap Subscription Groups as Preference Center

**What:** CleverTap natively supports up to 50 Subscription Groups per account. Each group has a name, description, and channel binding (currently Email-focused, with Push/SMS via MSG-* profile properties). Users can subscribe/unsubscribe per group. The system raises a "Channel Unsubscribed" event when status changes.

**When to use:** FOUND-01 -- designing the Preference Center data model.

**CleverTap data model for notification preferences:**

```
SUBSCRIPTION GROUPS (CleverTap native, max 50):
  - "Market Alerts" (opt-in, default OFF for marketing push)
  - "Product Updates" (opt-in, default OFF)
  - "Transactional" (always on, not user-toggleable)
  - "Security" (always on, not user-toggleable)

PER-USER PROFILE PROPERTIES (CleverTap):
  MSG-push:     true/false   (system property -- global push DND)
  MSG-email:    true/false   (system property -- global email DND)
  MSG-sms:      true/false   (system property -- global SMS DND)
  MSG-whatsapp: true/false   (system property -- global WhatsApp DND)

CUSTOM USER PROPERTIES (synced via Hightouch from BigQuery):
  consent_marketing_push:    boolean   (in-app consent, NOT OS permission)
  consent_marketing_email:   boolean   (explicit GDPR consent)
  consent_marketing_inapp:   boolean   (consent for promotional in-app)
  consent_timestamp_push:    datetime  (when consent was given/revoked)
  consent_timestamp_email:   datetime  (when consent was given/revoked)
  gdpr_lawful_basis:         string    (per-user: "consent" or "legitimate_interest")
```

**Key insight:** CleverTap's Email Preference Center is the most mature (with Custom Preference Center in Private Beta). For push, the preference model relies on MSG-push profile property (global toggle) plus custom user properties for per-category consent. The playbook must define both the CleverTap-native mechanisms AND the custom BigQuery consent fields synced via Hightouch.

**GDPR constraint:** OS-level push permission is NOT marketing consent (ePrivacy Directive Art. 13). The preference center must collect separate in-app consent per category, stored as custom user properties in BigQuery and synced to CleverTap.

**Source:** [CleverTap Group Unsubscribe](https://docs.clevertap.com/docs/group-unsubscribe), [CleverTap Manage Email Preferences](https://docs.clevertap.com/docs/manage-email-preferences), [CleverTap Subscribe API](https://developer.clevertap.com/docs/subscribe-api)

**Confidence:** HIGH

---

### Pattern 2: Multi-Level Frequency Capping with Priority Override

**What:** CleverTap supports frequency caps at two levels: (1) Global Campaign Limits (Settings > Engage > Campaign Limits) set per-channel daily maximums, and (2) Campaign-level frequency limits control per-campaign delivery (e.g., "2x per session, 1x per week, max 10 total"). When a cap is hit, notifications are suppressed. Campaigns can be marked "Exclude from Global campaign limits" to bypass -- this is how P0 transactional messages override marketing caps.

**When to use:** FOUND-02 -- designing the frequency cap policy.

**Implementation architecture:**

```
LAYER 1: CleverTap Global Campaign Limits (per channel)
  Push:   max 2/day, 5/week
  Email:  max 1/day, 3/week
  In-App: max 3/day (global limit via Settings)

LAYER 2: Campaign-Level Frequency Limits
  Each campaign configures its own frequency:
  - Transactional (P0): "Exclude from Global campaign limits" = checked
  - User-configured alerts (P1): "Exclude from Global campaign limits" = checked
  - Lifecycle critical (P2): Subject to global caps
  - Market triggers (P3): Subject to global caps
  - Cross-sell (P4): Subject to global caps, plus campaign limit 1/week
  - Re-engagement (P5): Subject to global caps, plus campaign limit 2/month

LAYER 3: BigQuery Computed Fatigue Score (synced to CleverTap via Hightouch)
  fatigue_risk = (notifications_sent_7d / 5) * 0.4
               + (notifications_dismissed_7d / notifications_sent_7d) * 0.3
               + (days_since_last_open / 7) * 0.3

  Campaigns target: fatigue_risk < 0.7 (for P3+)
                    fatigue_risk < 0.9 (for P2+)
```

**Key insight:** CleverTap's native frequency caps are per-channel, not per-trigger-family. The priority tier system (P0-P5) is implemented by marking P0/P1 campaigns as "Exclude from Global campaign limits" and using BigQuery fatigue score as a targeting filter for P2-P5 campaigns. This is not a single CleverTap setting -- it is a design pattern combining three layers.

**Source:** [CleverTap Messaging Frequency Caps](https://docs.clevertap.com/docs/messaging-frequency-caps), [CleverTap Notification Delivery Options](https://docs.clevertap.com/docs/notification-delivery-options)

**Confidence:** HIGH

---

### Pattern 3: Suppression via Custom List Segments + DND

**What:** CleverTap supports Custom List segments created from CSV upload (max 50MB via dashboard, 5GB via API). These segments can be used as exclusion lists in campaign targeting ("Don't send to segment X"). DND hours are configured per campaign (not globally) -- each campaign specifies its quiet hours and whether to discard or delay.

**When to use:** FOUND-03 -- designing the suppression system.

**Suppression architecture:**

```
SUPPRESSION LAYER 1: Segment-Based Exclusion
  C8 Whale Suppression:
    - BigQuery query generates user_id list of C8 segment
    - Export as CSV (Type: "i", Identity: user_id)
    - Upload to CleverTap as Custom List segment "C8_Whale_Suppression"
    - ALL marketing campaigns add "Exclude C8_Whale_Suppression" to targeting
    - Refresh: weekly (Katy uploads, or automate via Custom List API)

  Excluded Users (600K):
    - Same pattern, separate segment "Excluded_Users"

  Active Support Tickets:
    - Same pattern, segment "Active_Support_Suppression"

SUPPRESSION LAYER 2: DND (Quiet Hours)
  Per campaign: Settings > When > Delivery Preferences > DND checkbox
    - Days: All days
    - Hours: 22:00 - 08:00 (user local timezone)
    - Action: "Delay delivery until after DND" (not discard)
    - Exception: P0 security campaigns do NOT set DND

  Timezone handling: CleverTap uses user's device timezone by default.
  Fallback: account timezone (Spain CET/CEST) if user TZ unknown.

SUPPRESSION LAYER 3: Cooldown via Journey Re-Entry Delays
  CleverTap Journeys support re-entry delay configuration:
    - After 3 dismissals of same family: Journey exit + 7-day re-entry block
    - After 5 dismissals across families: User property "notification_cooldown = true"
      synced from BigQuery, used as campaign exclusion filter

SUPPRESSION LAYER 4: Opt-Out Handling
  - Email: CleverTap handles natively (unsubscribe link, group unsubscribe)
  - Push: MSG-push = false removes from all push campaigns
  - Granular opt-out: User changes category in Preference Center
    -> Update subscription group + custom consent property
    -> Sync to BigQuery via CleverTap export for audit trail
```

**Custom List API workflow (for automated C8 refresh):**
1. `POST /custom-list/url` -- request pre-signed URL (valid 24h)
2. Upload CSV to pre-signed URL
3. `POST /custom-list/upload-done` -- notify CleverTap processing is complete

**Source:** [CleverTap CSV Upload](https://docs.clevertap.com/docs/csv-upload), [CleverTap Custom List API](https://developer.clevertap.com/docs/custom-list-endpoints), [CleverTap DND Configuration](https://docs.clevertap.com/docs/notification-delivery-options)

**Confidence:** HIGH

---

### Pattern 4: Event Schema for CleverTap (SDK + Upload Events API)

**What:** CleverTap supports two event ingestion paths: SDK events (tracked client-side) and Upload Events API (backend server-to-CleverTap). The API accepts up to 1000 records per call with max 15 concurrent requests. There are 512 max event types per account and 256 properties per event. Event names are case-insensitive. Certain names are reserved (Notification Sent, App Launched, etc.).

**When to use:** FOUND-04 -- designing the minimum viable event schema.

**Event schema design:**

```
SDK EVENTS (tracked by CleverTap SDK in the app):
  "Product_Viewed"        {product_name: string, duration_sec: int}
  "Price_Alert_Set"       {asset: string, target_price: float, direction: string}
  "Asset_Added_Watchlist" {asset: string}
  "Preference_Changed"    {category: string, channel: string, new_status: boolean}
  "Push_Permission_Changed" -- auto-tracked by CleverTap SDK

BACKEND UPLOAD EVENTS (via Upload Events API):
  "Charged"               {Amount: float, currency: "EUR", Items: [{name, qty, price}]}
  "Deposit_Completed"     {amount_eur: float, method: string, is_first_deposit: boolean}
  "Withdrawal_Completed"  {amount_eur: float, asset: string}
  "KYC_Step_Completed"    {step_number: int, total_steps: int}
  "Earn_Subscribed"       {asset: string, amount: float, apy: float}
  "Order_Filled"          {asset: string, amount_eur: float, side: string, product: string}

CLOUD FUNCTION EVENTS (via Upload Events API):
  "Market_Trigger_Fired"  {asset: string, change_pct: float, direction: string, trigger_type: string}
  "Price_Alert_Triggered" {asset: string, current_price: float, target_price: float, direction: string}

EVENT PROPERTY CONSTRAINTS:
  - Keys: String only
  - Values: String, Boolean, Integer, Float, or Date
  - Prohibited chars in event names: % > < ! | & . : ; $ ' " \
  - Case-insensitive: "Purchase" and "purchase" are the SAME event
  - Use "Charged" for all purchase events (CleverTap built-in revenue tracking)
  - Test with dryRun=1 parameter before production upload
```

**Key insight:** The "Charged" event is special -- CleverTap uses it for built-in revenue analytics and LTV calculation. All purchase/trade events should use "Charged" with the Items array, not custom event names. This is critical for MEAS-01 measurement requirements in Phase 4.

**Source:** [CleverTap Upload Events API](https://developer.clevertap.com/docs/upload-events-api), [CleverTap Events](https://developer.clevertap.com/docs/events), [CleverTap Schema](https://docs.clevertap.com/docs/schema)

**Confidence:** HIGH

---

### Pattern 5: Hightouch Reverse ETL (BigQuery to CleverTap)

**What:** Hightouch syncs data from BigQuery to CleverTap via a native connector. Supports profile upserts (update existing + create new) and event inserts. Uses incremental change detection between syncs -- only changed rows are pushed. Requires one identifier field (Identity or CleverTap Global Object ID). Field mapping is visual (drag-and-drop). Scheduling ranges from every 1 minute to daily.

**When to use:** FOUND-05 -- designing the Reverse ETL integration.

**Integration design:**

```
SETUP REQUIREMENTS:
  - CleverTap Account ID (from Project settings -- ask Katy)
  - CleverTap Passcode (from Project settings -- ask Katy)
  - CleverTap Region (EU for Bit2Me)
  - BigQuery service account with read access to bit2me_lifecycle schema

SYNC 1: User Profiles (Upsert mode, every 30 minutes)
  Source: BigQuery view `bit2me_lifecycle.user_profiles_for_clevertap`
  Identifier: user_id -> CleverTap Identity

  Fields mapped:
    lifecycle_stage        -> string  (REGISTERED, KYC, DEPOSITED, etc.)
    health_score           -> integer (0-100)
    segment_id             -> string  (SEG-01 to SEG-37)
    total_balance_eur      -> float
    days_since_last_activity -> integer
    products_active        -> string  (comma-separated or JSON array)
    notification_fatigue_score -> float (0-1)
    suppression_flags      -> string  (comma-separated: "C8,EXCLUDED")
    consent_marketing_push -> boolean
    consent_marketing_email -> boolean
    country                -> string
    preferred_language     -> string

SYNC 2: Events (Insert mode, every 15 minutes -- optional for Phase 1)
  Source: BigQuery table `bit2me_lifecycle.trigger_events_for_clevertap`
  Identifier: event_id (truly unique per event)

  Maps to CleverTap event name (dynamic from column) with properties.

SYNC BEHAVIOR:
  - Incremental: Hightouch detects changed rows between syncs
  - New profiles: Created automatically if Identity not found in CleverTap
  - Phone format: Must be E.164 or CleverTap rejects
  - Custom fields: Auto-added to CleverTap schema on first sync
  - Debugging: Use Hightouch Live Debugger to inspect API calls
  - Alerts: Configure Slack notifications for sync failures
```

**Key insight:** Profile syncs should use Upsert mode (the primary mode Hightouch supports for CleverTap). Event syncs are insert-only and require a truly unique primary key (not user_id, which repeats across events). For Phase 1, only the profile sync is required. Event sync can wait for Phase 2-3.

**Source:** [Hightouch CleverTap Destination](https://hightouch.com/docs/destinations/clevertap), [Hightouch BigQuery Source](https://hightouch.com/docs/sources/google-bigquery), [CleverTap Hightouch Docs](https://docs.clevertap.com/docs/hightouch)

**Confidence:** HIGH

---

### Anti-Patterns to Avoid

- **Single marketing consent toggle:** Treating "user opted in" as a single boolean instead of per-channel, per-category consent. Violates GDPR Art. 7 (specificity) and ePrivacy Art. 13 (per-channel).
- **Frequency caps without priority tiers:** Setting a global 2/day cap without P0 exemption means security alerts get suppressed. Mark P0/P1 campaigns as "Exclude from Global campaign limits."
- **Manual C8 CSV upload without refresh schedule:** Uploading once and forgetting. Users enter/exit C8 whale segment. Must refresh weekly minimum -- automate via Custom List API.
- **DND configured globally instead of per-campaign:** CleverTap DND is per-campaign. Every new campaign must have DND configured. Create a campaign template/checklist to prevent forgetting.
- **Syncing all BigQuery fields to CleverTap:** Only sync fields used in campaign targeting. Every extra field increases sync time and CleverTap storage cost. The 12 fields listed in Pattern 5 are the minimum viable set.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Notification preference center | Custom database + API | CleverTap Subscription Groups + custom user properties via Hightouch | CleverTap handles unsubscribe links, preference pages, and group management natively. Custom consent fields in BigQuery handle the GDPR per-channel requirement. |
| Frequency capping engine | Custom counter + rate limiter | CleverTap Global Campaign Limits + campaign-level limits | CleverTap counts across campaigns automatically. Custom would need to track every send across every campaign type. |
| Quiet hours enforcement | Custom timezone logic + queue | CleverTap DND per campaign | CleverTap resolves user timezone from device and delays/discards automatically. |
| Suppression list management | Custom exclusion table + campaign filter | CleverTap Custom List segments + API | Custom List API provides CSV upload with pre-signed URLs. Dashboard shows segment size and reachability. |
| BigQuery-to-CRM data sync | Custom ETL scripts + cron | Hightouch Reverse ETL | Hightouch handles incremental change detection, field mapping, error handling, alerting. Custom ETL is fragile. |

**Key insight:** Phase 1 is entirely a configuration and documentation exercise. Zero custom code is needed. The playbook documents WHAT to configure and HOW, so Katy and Alvaro can execute.

## Common Pitfalls

### Pitfall 1: OS Push Permission Treated as Marketing Consent
**What goes wrong:** User enables push notifications in iOS/Android. Team sends marketing pushes assuming consent exists. ePrivacy Directive classifies push as electronic mail requiring separate marketing consent.
**Why it happens:** CRM teams think in binary (push enabled = send everything).
**How to avoid:** The Preference Center design (FOUND-01) MUST include a separate in-app consent screen shown AFTER OS permission grant. Store consent_marketing_push as a custom user property in BigQuery, synced to CleverTap via Hightouch. Without this flag = true, only transactional/user-configured pushes.
**Warning signs:** push_subscriber_count >> marketing_consent_count.

### Pitfall 2: C8 Whale Suppression Not Uploaded
**What goes wrong:** High-value dormant users (C8 segment, 72.4K users with EUR 19.5M AUC) receive generic marketing blasts. Risk of losing top accounts.
**Why it happens:** CSV was generated but never uploaded to CleverTap (identified in LC-OS audit as open gap).
**How to avoid:** FOUND-03 must specify: (1) who generates the C8 CSV (Alvaro from BigQuery), (2) upload process (dashboard or Custom List API), (3) refresh cadence (weekly), (4) verification step (check segment size in CleverTap matches BigQuery count).
**Warning signs:** No "C8_Whale_Suppression" segment visible in CleverTap dashboard.

### Pitfall 3: Frequency Caps Configured Without Priority Exemptions
**What goes wrong:** Global cap of 2 pushes/day suppresses a security alert (login from new device) because user already received 2 marketing pushes that day.
**Why it happens:** All campaigns treated equally in CleverTap frequency caps.
**How to avoid:** P0 (security) and P1 (user-configured alerts) campaigns MUST be marked "Exclude from Global campaign limits." Document this as a mandatory checkbox in the campaign creation checklist.
**Warning signs:** User complains about missing security alert; check if campaign was subject to global cap.

### Pitfall 4: DND Not Set on Every New Campaign
**What goes wrong:** New campaign launches without DND configuration. User gets push at 3 AM. Opts out permanently (iOS).
**Why it happens:** DND in CleverTap is per-campaign, not global. Easy to forget on new campaigns.
**How to avoid:** FOUND-03 must include a campaign launch checklist. Item: "DND configured? 22:00-08:00, delay delivery, all days." The playbook should specify this as a mandatory step.
**Warning signs:** Any push delivered between 22:00-08:00 user local time.

### Pitfall 5: Event Names Conflicting with CleverTap System Events
**What goes wrong:** Backend sends an event named "Notification Clicked" or "App Launched" via Upload Events API. CleverTap silently drops it because these are reserved system event names.
**Why it happens:** Developer doesn't check reserved names list.
**How to avoid:** FOUND-04 event schema must include the full reserved names list and explicitly state "NEVER use these names for custom events."
**Warning signs:** Events uploaded but not appearing in CleverTap event viewer.

## Code Examples

### CleverTap Upload Events API -- Backend Event Upload

```json
// Source: https://developer.clevertap.com/docs/upload-events-api
// POST https://api.clevertap.com/1/upload
// Headers: X-CleverTap-Account-Id, X-CleverTap-Passcode, Content-Type: application/json

{
  "d": [
    {
      "identity": "user_12345",
      "type": "event",
      "evtName": "Deposit_Completed",
      "evtData": {
        "amount_eur": 500.00,
        "method": "bank_transfer",
        "is_first_deposit": true
      },
      "ts": 1711152000
    },
    {
      "identity": "user_12345",
      "type": "event",
      "evtName": "Charged",
      "evtData": {
        "Amount": 250.00,
        "Items": [
          {
            "name": "BTC",
            "quantity": 1,
            "price": 250.00
          }
        ]
      },
      "ts": 1711152300
    }
  ]
}
```

### CleverTap Custom List API -- C8 Suppression Upload

```
// Source: https://developer.clevertap.com/docs/custom-list-endpoints

// Step 1: Request pre-signed URL
POST https://api.clevertap.com/1/custom-list/url
Body: { "name": "C8_Whale_Suppression" }
Response: { "presignedUrl": "https://..." }

// Step 2: Upload CSV to pre-signed URL (PUT)
// CSV format:
// Type,Identity
// i,user_001
// i,user_002
// ...

// Step 3: Notify upload complete
POST https://api.clevertap.com/1/custom-list/upload-done
Body: { "name": "C8_Whale_Suppression" }
```

### BigQuery View for Hightouch Sync

```sql
-- Source: Project-specific design based on Hightouch docs
-- This view powers the Hightouch profile sync to CleverTap

CREATE OR REPLACE VIEW `bit2me_lifecycle.user_profiles_for_clevertap` AS
SELECT
  user_id,
  lifecycle_stage,
  health_score,
  segment_id,
  total_balance_eur,
  DATE_DIFF(CURRENT_DATE(), last_activity_date, DAY) AS days_since_last_activity,
  ARRAY_TO_STRING(products_active, ',') AS products_active,
  notification_fatigue_score,
  ARRAY_TO_STRING(suppression_flags, ',') AS suppression_flags,
  consent_marketing_push,
  consent_marketing_email,
  country,
  preferred_language
FROM `bit2me_lifecycle.user_profiles`
WHERE lifecycle_stage != 'EXCLUDED'
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single opt-in/opt-out toggle | Per-channel, per-category subscription groups | GDPR enforcement 2018+ | Each notification category needs separate consent |
| Global DND hours | Per-campaign DND with delay/discard option | CleverTap native | Transactional can send 24/7; marketing observes quiet hours |
| Manual CSV upload only | Custom List API (programmatic upload) | CleverTap 2024+ | C8 suppression can be automated via scheduled script |
| Custom ETL scripts for warehouse-to-CRM | Managed Reverse ETL (Hightouch/Census) | 2023-2024 | Incremental sync, visual mapping, alerting out of the box |
| Flat frequency caps | Multi-layer caps + campaign exemptions | CleverTap Enhanced Frequency Caps 2025 | Priority tiers (P0-P5) implementable without custom code |

## Open Questions

1. **CleverTap Subscription Groups -- push channel support**
   - What we know: Group Unsubscribe documentation focuses on Email channel. Push preferences use MSG-push profile property (global toggle) but per-category push preferences may require custom user properties.
   - What's unclear: Can Subscription Groups natively manage push categories, or is push limited to the global MSG-push toggle?
   - Recommendation: Design assumes custom user properties for per-category push consent (consent_marketing_push, consent_market_alerts_push, etc.) synced from BigQuery. Verify with CleverTap CSM whether Subscription Groups support push channel natively.

2. **Custom Preference Center Private Beta access**
   - What we know: CleverTap's Custom Email Preference Center (HTML/CSS/JS customization) is in Private Beta.
   - What's unclear: Is this available on Bit2Me's CleverTap plan? Does it support push preference management or only email?
   - Recommendation: Contact CSM to request access. For MVP, use the standard Email Preference Center + in-app preference screen (built by engineering) for push categories.

3. **C8 Whale segment definition query**
   - What we know: C8 is the suppression list for high-value dormant users. The LC-OS audit identified it as unresolved.
   - What's unclear: What is the exact BigQuery query that defines C8? Is it balance > X EUR and dormant > Y days?
   - Recommendation: Alvaro must provide the C8 segment definition before the playbook documents the suppression workflow. The PLAN should include "get C8 definition from Alvaro" as a prerequisite.

4. **Hightouch scheduling granularity cost impact**
   - What we know: Hightouch supports syncs as frequent as every 1 minute. Business tier costs $350-500/mo.
   - What's unclear: Does sync frequency affect pricing? Is every-30-minute sync within the Business tier, or does it require a higher plan?
   - Recommendation: Start with hourly sync (conservative). Increase to 30 minutes after validating cost with Hightouch pricing.

## Validation Architecture

### Deliverable Verification (Document-Based Phase)

This phase produces playbook sections (design documents), not code. Validation checks whether the documents are complete, internally consistent, and actionable.

### Phase Requirements -- Verification Map

| Req ID | Deliverable | Verification Check | Automated? |
|--------|-------------|-------------------|------------|
| FOUND-01 | Preference Center architecture document | Contains: (1) consent category list, (2) data model with field names and types, (3) CleverTap subscription group mapping, (4) per-channel consent flow, (5) GDPR lawful basis per category | Manual review |
| FOUND-02 | Frequency cap policy document | Contains: (1) exact daily/weekly/monthly numbers per channel, (2) P0-P5 priority tier definitions, (3) which tiers exempt from global caps, (4) fatigue score formula, (5) escalation thresholds | Manual review |
| FOUND-03 | Suppression system document | Contains: (1) C8 upload process with CSV format, (2) quiet hours spec (22:00-08:00), (3) opt-out handling per channel, (4) cooldown escalation rules (3 dismissals -> 7d, 5 -> 14d), (5) suppression segment refresh cadence | Manual review |
| FOUND-04 | Event schema document | Contains: (1) SDK events table with properties, (2) Backend Upload events table with properties, (3) reserved event names list, (4) property type constraints, (5) "Charged" event pattern for purchases | Manual review |
| FOUND-05 | Hightouch integration design document | Contains: (1) credential requirements (Account ID, Passcode, Region), (2) BigQuery source view SQL, (3) field mapping table, (4) sync mode (upsert) and schedule, (5) identifier field choice | Manual review |

### Completeness Checks

```
For each FOUND-XX document, verify:
  [ ] Document exists in the playbook output
  [ ] Contains specific numbers (not "TBD" or "to be determined")
  [ ] References CleverTap configuration paths (Settings > Engage > ...)
  [ ] Specifies owner (Katy, Alvaro, or Diego) for each action item
  [ ] Includes compliance basis (GDPR article, MiCA article, ePrivacy reference)
  [ ] Cross-references other FOUND documents where relevant
```

### Cross-Document Consistency Checks

```
  [ ] FOUND-01 consent categories match FOUND-02 priority tiers
  [ ] FOUND-02 frequency caps reference FOUND-03 suppression as override layer
  [ ] FOUND-03 C8 suppression segment is used in FOUND-05 Hightouch sync (suppression_flags field)
  [ ] FOUND-04 event schema includes events needed for FOUND-02 fatigue score calculation
  [ ] FOUND-05 field mapping includes all user properties referenced in FOUND-01, FOUND-02, FOUND-03
```

### Phase Gate

All five FOUND-XX requirements in REQUIREMENTS.md must be marked Complete before proceeding to Phase 2. The verification step checks:
1. Each FOUND document exists and passes the completeness checks above
2. Cross-document consistency checks pass
3. No open questions remain that would block Phase 2 (trigger taxonomy) from referencing Phase 1 outputs

## Sources

### Primary (HIGH confidence)
- [CleverTap Group Unsubscribe](https://docs.clevertap.com/docs/group-unsubscribe) -- subscription groups, max 50, per-group unsubscribe
- [CleverTap Manage Email Preferences](https://docs.clevertap.com/docs/manage-email-preferences) -- preference center setup
- [CleverTap Subscribe API](https://developer.clevertap.com/docs/subscribe-api) -- programmatic subscribe/unsubscribe
- [CleverTap Messaging Frequency Caps](https://docs.clevertap.com/docs/messaging-frequency-caps) -- per-channel caps, campaign limits, global limits
- [CleverTap Notification Delivery Options](https://docs.clevertap.com/docs/notification-delivery-options) -- DND configuration, delay vs discard
- [CleverTap DND Blog](https://clevertap.com/blog/setting-dnd-cut-off-times-for-campaigns/) -- DND use cases and timezone behavior
- [CleverTap CSV Upload](https://docs.clevertap.com/docs/csv-upload) -- CSV format, 50MB dashboard / 5GB API limit
- [CleverTap Custom List API](https://developer.clevertap.com/docs/custom-list-endpoints) -- programmatic segment creation via pre-signed URL
- [CleverTap Upload Events API](https://developer.clevertap.com/docs/upload-events-api) -- 1000 records/call, 15 concurrent, 512 event types, 256 properties
- [CleverTap Events Schema](https://docs.clevertap.com/docs/schema) -- property types, prohibited characters, reserved names
- [CleverTap Preferred Channel](https://docs.clevertap.com/docs/preferred-channel) -- AI-based channel selection
- [Hightouch CleverTap Destination](https://hightouch.com/docs/destinations/clevertap) -- profile upsert, event insert, identifier fields, field mapping
- [Hightouch BigQuery Source](https://hightouch.com/docs/sources/google-bigquery) -- SQL models, table selection, incremental sync
- [Hightouch Sync Types & Modes](https://hightouch.com/docs/syncs/types-and-modes) -- upsert, insert, mirror, add

### Secondary (MEDIUM confidence)
- [CleverTap Custom Email Preference Center (Private Beta)](https://docs.clevertap.com/docs/manage-custom-email-preference-center-1) -- HTML/CSS/JS customization
- [CleverTap Enhanced Frequency Caps Blog](https://clevertap.com/blog/message-reporting-and-enhanced-frequency-caps/) -- 2025 frequency cap improvements
- [CleverTap Golden Frequency Cap Blog](https://clevertap.com/blog/is-there-a-golden-frequency-cap-for-number-of-messages/) -- frequency optimization philosophy

### From Prior Research (HIGH confidence -- verified in STACK.md, PITFALLS.md, ARCHITECTURE.md)
- GDPR Articles 6, 7 -- lawful basis, consent specificity
- ePrivacy Directive Article 13 -- per-channel consent for electronic marketing
- MiCA Article 66 -- fair, clear, not misleading
- PITFALLS.md fatigue benchmarks -- 46% opt-out at 2-5/week, iOS opt-out permanent
- ARCHITECTURE.md data flow -- dual-engine pattern, four integration patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all components are existing platform features, documented and verified
- Architecture: HIGH -- CleverTap native features confirmed via official docs for all five requirements
- Pitfalls: HIGH -- compliance constraints verified against primary legal sources, fatigue benchmarks from multiple industry sources
- Hightouch integration: HIGH -- connector documentation verified, sync modes confirmed

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days -- stable platform features, unlikely to change)
