## 1. Preference Center Architecture

> **Purpose:** This section defines how user consent is structured, stored, and enforced across all notification channels. It is the foundational data model that every trigger definition in subsequent phases references to determine eligibility.
>
> **Owners:** Katy (CleverTap configuration), Alvaro (BigQuery schema + Hightouch sync), Diego (compliance review)

---

### 1.1 Notification Categories

Every notification Bit2Me sends belongs to exactly one of these six categories. Each category has a distinct GDPR lawful basis, which determines whether user consent is required and whether the user can opt out.

| Category ID | Category Name | Description | GDPR Lawful Basis | Default State | User Can Toggle |
|-------------|--------------|-------------|-------------------|---------------|-----------------|
| CAT-SEC | Security and Account | Login alerts from new devices, withdrawal confirmations, password changes, 2FA codes, failed payment warnings | Art. 6(1)(b) -- contractual necessity | Always ON | No |
| CAT-TXN | Transaction Confirmations | Trade filled, deposit received, earn payout credited, order status changes | Art. 6(1)(b) -- contractual necessity | Always ON | No |
| CAT-USR | User-Configured Alerts | Price alerts the user explicitly created, watchlist notifications, custom threshold alerts | Art. 6(1)(b) -- contract performance (user requested the service) | ON when user creates alert | Yes (per alert) |
| CAT-MKT | Market Updates | Trending assets, volatility alerts, new listing announcements, market momentum signals | Art. 6(1)(a) -- explicit consent | OFF | Yes |
| CAT-PRD | Product Updates | New features, Earn rate changes, Space Center missions, platform improvements | Art. 6(1)(a) -- explicit consent | OFF | Yes |
| CAT-PRO | Promotional | Cross-sell campaigns, reactivation pushes, promotional offers, referral incentives | Art. 6(1)(a) -- explicit consent | OFF | Yes |

**Classification rule:** If a notification mentions a product the user does NOT already use, it is marketing (CAT-MKT, CAT-PRD, or CAT-PRO). If it confirms an action the user took, it is transactional (CAT-TXN). If it protects the user's account, it is security (CAT-SEC).

---

### 1.2 Per-Channel Consent Model

Each channel requires its own consent mechanism. Consent for one channel does NOT extend to another (ePrivacy Directive Article 13, GDPR Article 7 -- consent must be specific, not bundled).

| Channel | Consent Mechanism | Legal Basis | Storage Location | Notes |
|---------|-------------------|-------------|------------------|-------|
| Push | OS permission (technical gate) + in-app marketing consent screen (legal gate) | ePrivacy Art. 13 -- push classified as electronic mail; OS permission is NOT marketing consent | `consent_marketing_push` boolean in BigQuery, synced to CleverTap via Hightouch | After OS permission grant, show an in-app consent screen for marketing categories. Without in-app consent, only CAT-SEC, CAT-TXN, and CAT-USR may be sent via push. |
| Email | Explicit opt-in at registration or via Notification Preferences screen | Art. 6(1)(a) GDPR -- explicit consent for marketing emails; "soft opt-in" exception only for similar products to existing purchases | `consent_marketing_email` boolean in BigQuery, synced to CleverTap via Hightouch. CleverTap Subscription Groups handle unsubscribe links natively. | Unsubscribe link mandatory in every marketing email (CAN-SPAM, GDPR Art. 7(3)). |
| In-App | Part of app experience for transactional/service messages. Marketing in-app requires explicit consent. | Art. 6(1)(b) for service messages; Art. 6(1)(a) for promotional in-app | `consent_marketing_inapp` boolean in BigQuery, synced to CleverTap via Hightouch | Promotional in-app messages (e.g., cross-sell banners for products the user does not use) require `consent_marketing_inapp = true`. Service in-app (e.g., KYC reminder) does not. |
| SMS | Not currently available at Bit2Me. Documented as future channel. | Will require separate Art. 6(1)(a) consent + ePrivacy Art. 13 per-channel consent when activated | Future: `consent_marketing_sms` boolean | SMS requires explicit opt-in with separate consent flow. Never bundle with push or email consent. |

> **CRITICAL STATEMENT:** OS-level push permission is NOT marketing consent. ePrivacy Directive Article 13 classifies push notifications as electronic mail. After OS permission grant, show an in-app consent screen for marketing categories (CAT-MKT, CAT-PRD, CAT-PRO). Without this second consent step, only transactional (CAT-SEC, CAT-TXN) and user-configured (CAT-USR) notifications may be sent via push.

---

### 1.3 Data Model

Complete field specification for the consent and preference system. All custom fields are stored in BigQuery as the source of truth and synced to CleverTap via Hightouch Reverse ETL.

| Field Name | Type | Source | Synced To | Update Frequency | Purpose |
|------------|------|--------|-----------|------------------|---------|
| `consent_marketing_push` | boolean | BigQuery | CleverTap via Hightouch | On change (next sync cycle, max 30 min lag) | Per-channel marketing consent for push. True = user explicitly opted in via in-app consent screen. |
| `consent_marketing_email` | boolean | BigQuery | CleverTap via Hightouch | On change | Per-channel marketing consent for email. True = user explicitly opted in at registration or preferences screen. |
| `consent_marketing_inapp` | boolean | BigQuery | CleverTap via Hightouch | On change | Per-channel marketing consent for promotional in-app messages. |
| `consent_timestamp_push` | datetime | BigQuery | CleverTap via Hightouch | On change | Audit trail -- exact timestamp when push marketing consent was given or revoked. Required for GDPR Art. 7(1) proof of consent. |
| `consent_timestamp_email` | datetime | BigQuery | CleverTap via Hightouch | On change | Audit trail -- exact timestamp when email marketing consent was given or revoked. |
| `consent_timestamp_inapp` | datetime | BigQuery | CleverTap via Hightouch | On change | Audit trail -- exact timestamp when in-app marketing consent was given or revoked. |
| `gdpr_lawful_basis` | string | BigQuery | CleverTap via Hightouch | On change | Per-user lawful basis: `"consent"` (Art. 6(1)(a)) or `"legitimate_interest"` (Art. 6(1)(f)). Used for audit and compliance reporting. |
| `MSG-push` | boolean | CleverTap system property | N/A (native) | Real-time | Global push DND toggle. When false, CleverTap suppresses ALL push notifications to this user. Set by user via app settings or CleverTap SDK. |
| `MSG-email` | boolean | CleverTap system property | N/A (native) | Real-time | Global email DND toggle. When false, CleverTap suppresses ALL emails. Set via unsubscribe link or CleverTap preference page. |
| `MSG-sms` | boolean | CleverTap system property | N/A (native) | Real-time | Global SMS DND toggle. Reserved for future SMS channel activation. |
| `MSG-whatsapp` | boolean | CleverTap system property | N/A (native) | Real-time | Global WhatsApp DND toggle. Reserved for future WhatsApp channel activation (Phase 4+). |

**Consent hierarchy:** For a marketing push notification to be sent, ALL of the following must be true:
1. `MSG-push = true` (global push not disabled by user)
2. `consent_marketing_push = true` (in-app marketing consent given)
3. User is subscribed to the relevant CleverTap Subscription Group (e.g., "Market Alerts" for CAT-MKT)
4. The notification passes frequency cap and suppression checks (see Section 2)

---

### 1.4 CleverTap Subscription Groups

CleverTap supports up to 50 Subscription Groups per account. Bit2Me uses the following 5 groups to map to notification categories. Groups are configured in CleverTap > Settings > Channel > Subscription Groups.

| # | Group Name | Maps to Category | Opt-In Required | Default Status | User-Toggleable | Channel |
|---|-----------|-----------------|-----------------|----------------|-----------------|---------|
| 1 | Security Alerts | CAT-SEC | No (contractual) | Always subscribed | No -- cannot unsubscribe from security alerts | Push, Email |
| 2 | Transaction Confirmations | CAT-TXN | No (contractual) | Always subscribed | No -- cannot unsubscribe from transaction confirmations | Push, Email |
| 3 | Market Alerts | CAT-MKT | Yes (explicit consent) | Unsubscribed | Yes | Push, Email, In-App |
| 4 | Product Updates | CAT-PRD | Yes (explicit consent) | Unsubscribed | Yes | Push, Email, In-App |
| 5 | Promotions | CAT-PRO | Yes (explicit consent) | Unsubscribed | Yes | Push, Email, In-App |

**Note on CAT-USR (User-Configured Alerts):** These are not managed via Subscription Groups because they are per-alert, not per-category. Each user-configured alert (e.g., "BTC > $70K") is stored as a separate record in BigQuery with its own active/inactive status. The user manages these through the app's price alert UI, not through the Notification Preferences screen.

**Configuration steps for Katy:**
1. Navigate to CleverTap > Settings > Channel > Subscription Groups
2. Create each group with the exact name listed above
3. For "Security Alerts" and "Transaction Confirmations": set as non-unsubscribable (if platform supports) or document as always-on in internal SOPs
4. For "Market Alerts", "Product Updates", "Promotions": set default = unsubscribed, allow user toggle

---

### 1.5 Consent Collection Flow

Step-by-step flow from app download to fully consented user. Each step maps to a technical action and a legal requirement.

1. **User downloads app** -- OS push permission prompt appears (iOS: system dialog; Android: auto-granted on install for Android 12 and below, system dialog for Android 13+). This is a **technical gate only**, not legal marketing consent.

2. **After first login** -- In-app Notification Preferences screen appears with individual toggles per marketing category:
   - Market Alerts (CAT-MKT): "Get notified about trending assets, price movements, and new listings"
   - Product Updates (CAT-PRD): "Learn about new features, Earn rate changes, and Space Center missions"
   - Promotions (CAT-PRO): "Receive personalized offers and campaign promotions"
   - All toggles default = **OFF**
   - **"Skip" button equally prominent as "Enable"** -- no dark patterns (GDPR Recital 42)

3. **User toggles a category ON** -- Backend stores `consent_marketing_[channel] = true` + `consent_timestamp_[channel] = NOW()` in BigQuery. The user's action constitutes freely given, specific, informed, and unambiguous consent (GDPR Art. 7).

4. **BigQuery syncs to CleverTap via Hightouch** -- Next sync cycle (max 30 minutes lag). Consent fields are updated on the CleverTap user profile.

5. **CleverTap Subscription Group status updated** -- User is added to the corresponding Subscription Group(s) based on their consent choices.

6. **User can change preferences anytime** -- via Settings > Notification Preferences in the app. Changes follow the same flow: update BigQuery -> Hightouch sync -> CleverTap profile update.

**Consent gap detection rule:** If `push_subscriber_count >> marketing_consent_count`, the consent flow has a gap. **Target: `marketing_consent_count >= 60% of push_subscriber_count`.** If this ratio falls below 60%, investigate whether the in-app consent screen is being shown, is too easy to skip, or has a UX bug preventing toggling.

---

### 1.6 Compliance Checklist

Every element of the Preference Center must satisfy these compliance requirements. This checklist is reviewed quarterly (owner: Diego).

| Requirement | Source | Implementation | Owner |
|-------------|--------|----------------|-------|
| Lawful basis documented per notification category | GDPR Art. 6 | Category table (Section 1.1) maps each CAT-XX to its lawful basis. CAT-SEC/CAT-TXN = Art. 6(1)(b); CAT-MKT/CAT-PRD/CAT-PRO = Art. 6(1)(a). | Diego (review), Katy (CleverTap config) |
| Consent freely given, specific, informed, unambiguous | GDPR Art. 7 | In-app consent screen with individual toggles, default OFF, "Skip" equally prominent. No pre-checked boxes. Consent not bundled with service registration. | Product (UI), Diego (review) |
| Per-channel consent for electronic marketing | ePrivacy Art. 13 | Separate consent flags per channel: `consent_marketing_push`, `consent_marketing_email`, `consent_marketing_inapp`. OS push permission treated as technical gate, not marketing consent. | Alvaro (BigQuery schema), Katy (CleverTap) |
| Marketing identifiable as marketing | MiCA Art. 66(2) | All promotional notifications (CAT-MKT, CAT-PRD, CAT-PRO) clearly labeled. Push notifications from these categories must not be disguised as transactional. Notification templates reviewed by Diego before deployment. | Diego (copy approval), Katy (template config) |
| No pre-checked consent boxes | GDPR Recital 42 | All marketing toggles default to OFF. "Enable all" is not pre-selected. Consent screen shows individual category toggles with descriptions. | Product (UI implementation) |
| Consent proof and audit trail | GDPR Art. 7(1) | `consent_timestamp_[channel]` fields record exact datetime of consent grant/revocation. Stored in BigQuery for minimum 5 years. | Alvaro (BigQuery retention policy) |
| Right to withdraw consent | GDPR Art. 7(3) | User can change preferences anytime via Settings > Notification Preferences. Withdrawal as easy as giving consent. Email unsubscribe links in every marketing email. | Product (UI), Katy (CleverTap unsubscribe) |

---

### 1.7 UI Wireframe Description

Text description of the Notification Preferences screen. No image needed -- this is a specification for the Product/Engineering team to implement.

**Screen: Notification Preferences**
- **Access path:** Settings > Notification Preferences (also shown as onboarding screen after first login)

**Header:**
- Title: "Notification Preferences"
- Subtitle: "Choose what you want to hear about. You can change this anytime."

**Section 1: Essential Notifications (always on)**
- Visual: Light grey background, toggles shown in ON state but greyed out / non-interactive
- Label: "These keep your account safe"
- Row 1: "Security Alerts" -- "Login alerts, withdrawal confirmations, password changes" -- [Always ON toggle, greyed]
- Row 2: "Transaction Confirmations" -- "Trade filled, deposit received, earn payouts" -- [Always ON toggle, greyed]
- Explanatory text: "These notifications are required for your account security and cannot be disabled."

**Section 2: Optional Notifications (user-toggleable)**
- Visual: White background, toggles in OFF state (default), interactive
- Label: "Stay informed (optional)"
- Row 1: "Market Alerts" -- "Trending assets, price movements, new listings" -- [OFF toggle]
- Row 2: "Product Updates" -- "New features, Earn rates, Space Center missions" -- [OFF toggle]
- Row 3: "Promotions" -- "Personalized offers and campaigns" -- [OFF toggle]
- Each row includes a brief description of what the category includes

**Footer:**
- "You can change these preferences anytime in Settings."
- Link: "Read our full Privacy Policy" (links to privacy policy page)

**Action buttons (onboarding variant):**
- Primary: "Save Preferences" (saves whatever the user toggled)
- Secondary (equally prominent): "Skip for now" or "Not now"
- **Design note:** "Skip" and "Not now" must be equally prominent as any "Enable" option. No visual hierarchy that nudges toward enabling. This is a GDPR Recital 42 requirement -- consent must be freely given with genuine free choice.

**Action buttons (settings variant):**
- Primary: "Save Changes"
- No skip needed (user navigated here intentionally)

---

### Cross-References

- **Section 2 (Frequency Cap Policy):** Uses consent categories (CAT-SEC through CAT-PRO) to determine which priority tier (P0-P5) a notification belongs to, and therefore whether it is subject to global frequency caps.
- **FOUND-03 (Suppression System):** Uses `consent_marketing_[channel]` fields as suppression filters -- if consent is false, marketing notifications are suppressed for that channel.
- **FOUND-05 (Hightouch Reverse ETL):** All consent fields listed in Section 1.3 are synced from BigQuery to CleverTap via Hightouch. The field mapping in FOUND-05 must include every field in the Data Model table.
