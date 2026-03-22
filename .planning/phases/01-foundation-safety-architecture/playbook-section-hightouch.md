## 5. Hightouch Reverse ETL Integration Design

### 5.1 Why Reverse ETL

BigQuery is the source of truth for user lifecycle stage, Health Score, fatigue score, segment membership, suppression flags, and product eligibility. CleverTap needs these attributes as user properties to target campaigns (e.g., "Enter journey when `health_score < 40 AND lifecycle_stage = AT_RISK`"). Hightouch syncs BigQuery-computed attributes to CleverTap user profiles with **incremental change detection** -- only changed rows are pushed, reducing API calls and cost.

Alternative approaches (custom ETL scripts, direct API calls from Cloud Functions) are fragile and lack error handling, alerting, visual field mapping, and change detection. Hightouch provides all of these out of the box with a native BigQuery-to-CleverTap connector.

---

### 5.2 Setup Requirements

| Requirement | Value | Owner | Notes |
|---|---|---|---|
| CleverTap Account ID | From CleverTap Project Settings | Katy | Required for Hightouch destination config |
| CleverTap Passcode | From CleverTap Project Settings | Katy | API authentication token |
| CleverTap Region | **EU** (`eu1.clevertap.com`) | Katy | Bit2Me is EU-hosted |
| BigQuery Service Account | Read access to `bit2me_lifecycle` schema | Alvaro | JSON key file for Hightouch source config |
| Hightouch Account | Business tier ($350-500/month) | Growth team (budget approval) | Needed for scheduled syncs and multiple models |

---

### 5.3 BigQuery Source View

Alvaro creates this view. Hightouch references it as the sync model.

```sql
CREATE OR REPLACE VIEW `bit2me_lifecycle.user_profiles_for_clevertap` AS
SELECT
  user_id,
  lifecycle_stage,
  health_score,
  segment_id,
  total_balance_eur,
  DATE_DIFF(CURRENT_DATE(), last_activity_date, DAY) AS days_since_last_activity,
  DATE_DIFF(CURRENT_DATE(), last_deposit_date, DAY) AS days_since_last_deposit,
  ARRAY_TO_STRING(products_active, ',') AS products_active,
  notification_fatigue_score,
  ARRAY_TO_STRING(suppression_flags, ',') AS suppression_flags,
  consent_marketing_push,
  consent_marketing_email,
  consent_marketing_inapp,
  country,
  preferred_language,
  space_center_tier,
  CASE WHEN notification_cooldown = TRUE THEN 'true' ELSE 'false' END AS notification_cooldown
FROM `bit2me_lifecycle.user_profiles`
WHERE lifecycle_stage != 'EXCLUDED'
```

**This view excludes EXCLUDED users (~600K) to reduce sync volume.** Excluded users should never receive any notification and are handled by the Excluded_Users suppression segment (see Section 3.2). Excluding them from the Hightouch sync reduces the profile count from ~1.2M to ~600K, halving API calls and sync time.

---

### 5.4 Field Mapping Table

| BigQuery Column | CleverTap Property | Type | Description | Used By | Critical |
|---|---|---|---|---|---|
| `user_id` | Identity (CleverTap primary key) | string | Primary identifier | All campaigns | YES |
| `lifecycle_stage` | `lifecycle_stage` | string | REGISTERED, KYC, DEPOSITED, FM, ACTIVE, POWER, AT_RISK, PRE_DORMANCY, DORMANT_BAL, DORMANT_ZERO, REACTIVATED, CHURNED | Lifecycle journey entry/exit | YES |
| `health_score` | `health_score` | integer (0-100) | Health Score composite metric | AT_RISK detection, fatigue gating | YES |
| `segment_id` | `segment_id` | string (SEG-01 to SEG-37) | MECE segment membership | Segment-specific campaigns | YES |
| `total_balance_eur` | `total_balance_eur` | float | Total balance in EUR | Whale detection, cross-sell eligibility | YES |
| `days_since_last_activity` | `days_since_last_activity` | integer | Days since last app/trade activity | Dormancy triggers | YES |
| `days_since_last_deposit` | `days_since_last_deposit` | integer | Days since last deposit | Funding nudge triggers | NO |
| `products_active` | `products_active` | string (comma-separated) | Active product list (brokerage, pro, earn, card) | Cross-sell eligibility | YES |
| `notification_fatigue_score` | `notification_fatigue_score` | float (0-1) | Fatigue Risk Score from Section 2.5 | P3-P5 campaign targeting filter | YES |
| `suppression_flags` | `suppression_flags` | string (comma-separated) | Active suppression reasons (C8, SUPPORT, LEGAL_HOLD) | Campaign exclusion (Section 3.2) | YES |
| `consent_marketing_push` | `consent_marketing_push` | boolean | Push marketing consent (in-app, not OS permission) | Push campaign targeting | YES |
| `consent_marketing_email` | `consent_marketing_email` | boolean | Email marketing consent (explicit GDPR consent) | Email campaign targeting | YES |
| `consent_marketing_inapp` | `consent_marketing_inapp` | boolean | In-app marketing consent | In-app campaign targeting | NO |
| `country` | `country` | string | User country (ES, VE, CO, etc.) | Geo targeting, compliance rules | NO |
| `preferred_language` | `preferred_language` | string | User language (es, en, pt) | Template localization | NO |
| `space_center_tier` | `space_center_tier` | integer (1-7) | Space Center gamification tier | Gamification triggers | NO |
| `notification_cooldown` | `notification_cooldown` | string ("true"/"false") | Active cooldown from escalating dismissals (Section 3.5) | P3+ campaign exclusion filter | YES |

---

### 5.5 Sync Configuration

| Parameter | Value | Notes |
|---|---|---|
| Sync Mode | **Upsert** (update existing + create new) | Primary mode Hightouch supports for CleverTap |
| Identifier Field | `user_id` mapped to CleverTap Identity | Must be unique per user |
| Sync Schedule | **Every 30 minutes** | Balance between freshness and API cost. Start with hourly, increase if needed. |
| Change Detection | **Incremental** (Hightouch diff) | Only changed rows are synced -- reduces API calls |
| New Profiles | Auto-created if Identity not found in CleverTap | No manual profile creation needed |
| Error Handling | Hightouch retries failed records 3x, then flags as error | Monitor via Hightouch dashboard |
| Alerting | Slack notification on sync failure | Configure Slack channel for CRM team |

---

### 5.6 Sync Monitoring

| Metric | Target | Alert | Source |
|---|---|---|---|
| Sync success rate | >99% | <95% = RED, investigate immediately | Hightouch dashboard |
| Sync latency (time from BQ update to CT update) | <45 minutes | >60 minutes = AMBER, check sync queue | Hightouch sync logs |
| Records synced per run | Track trend (baseline ~600K initial, then incremental changes) | Sudden spike or drop = investigate | Hightouch dashboard |
| API errors | 0 | Any error = investigate | Hightouch error log |
| Profile match rate | >99% (synced records found in CleverTap) | <95% = identity mismatch issue | Hightouch sync report |

**Monitoring owner:** Katy checks Hightouch dashboard daily during first 2 weeks after launch, then weekly. Slack alerts provide real-time notification of failures.

---

### 5.7 Phase 2+ Event Sync (Future)

Phase 1 syncs **USER PROFILES only** (upsert mode). Future phases may add event sync:

- **Phase 2-3:** Event sync from BigQuery `trigger_events_for_clevertap` table to CleverTap events (insert mode)
- **Primary key:** Event sync requires a truly unique primary key (`event_id`, not `user_id` which repeats across events)
- **Sync mode:** INSERT-only (events are immutable once created)
- **Use case:** Enables BigQuery-computed triggers to fire as CleverTap events without building custom API integrations. For example, a BigQuery scheduled query detects "user moved to AT_RISK" and writes an event row; Hightouch syncs it as a CleverTap event that triggers a Journey entry.

**Decision:** Event sync is deferred to Phase 2-3. For Phase 1, all trigger events reach CleverTap via direct Upload Events API calls (from backend or Cloud Function). Hightouch handles only profile attribute sync.

---

### 5.8 Implementation Checklist

Ordered steps for Alvaro to set up the full BigQuery-to-CleverTap pipeline:

| # | Step | Owner | Dependency |
|---|---|---|---|
| 1 | Create BigQuery view: `bit2me_lifecycle.user_profiles_for_clevertap` (SQL in Section 5.3) | Alvaro | `bit2me_lifecycle.user_profiles` table exists |
| 2 | Create BigQuery service account with read access to `bit2me_lifecycle` | Alvaro | GCP project access |
| 3 | Get CleverTap Account ID and Passcode from Katy | Alvaro + Katy | Katy has CleverTap admin access |
| 4 | Sign up for Hightouch Business tier | Growth team | Budget approval |
| 5 | Connect BigQuery as source (upload service account JSON key) | Alvaro | Steps 2, 4 |
| 6 | Connect CleverTap as destination (Account ID, Passcode, Region: EU) | Alvaro | Steps 3, 4 |
| 7 | Create Model: select the `user_profiles_for_clevertap` view | Alvaro | Steps 1, 5 |
| 8 | Create Sync: map fields per the Field Mapping Table (Section 5.4) | Alvaro | Steps 6, 7 |
| 9 | Set schedule: every 30 minutes | Alvaro | Step 8 |
| 10 | Run initial full sync (expect ~600K profiles after EXCLUDED filter) | Alvaro | Step 9 |
| 11 | Verify: check 10 random users in CleverTap dashboard to confirm properties match BigQuery | Alvaro + Katy | Step 10 |
| 12 | Configure Slack alerting for sync failures | Alvaro | Step 8 |
| 13 | Document Hightouch login credentials in team password manager | Alvaro | Step 4 |

**Estimated timeline:** Steps 1-6 can be completed in one session (~2 hours). Steps 7-13 require ~1 hour. Total: half a day, assuming credentials are available.

**Cross-references:**
- Section 3.2: Suppression segments (suppression_flags field in sync)
- Section 3.5: Escalating cooldowns (notification_cooldown field in sync)
- Section 4: Event schema (events tracked feed into user profile attributes synced here)
