# GDPR Compliance Skill — CRM & Lifecycle Marketing

**Context:** Bit2Me, Spanish crypto exchange operating under EU GDPR (Regulation 2016/679) and Spanish LOPDGDD (Ley Orgánica 3/2018).
**Owner:** Daniel Ferraro, Head of Growth — lifecycle marketing, CRM campaigns, A/B testing
**Legal Gate:** Diego (internal legal) — ALL CRM messages require Diego pre-approval before send
**Updated:** 2026-03-25

---

## 1. GDPR BASICS FOR MARKETING

### The Six Lawful Bases — Which One Applies to You

| Basis | When it applies at Bit2Me | Practical implication |
|-------|--------------------------|----------------------|
| **Consent** | Marketing emails to non-customers; push notifications; cookies for analytics/advertising | User must opt in explicitly. Withdrawable at any time. Cannot be bundled with T&Cs. |
| **Contract** | Processing necessary to deliver a service the user signed up for | Onboarding emails, KYC status updates, transaction confirmations, account security alerts — no consent needed |
| **Legitimate Interest** | Soft opt-in marketing to existing customers; fraud prevention; internal analytics | Must pass three-part test (see below). User can object. |
| **Legal Obligation** | AML/KYC data retention, tax reporting, regulatory requirements | Overrides GDPR deletion requests. You keep data because you must. |
| **Vital Interests** | Rarely applies to marketing | Ignore for CRM purposes |
| **Public Task** | Rarely applies to marketing | Ignore for CRM purposes |

**The Legitimate Interest Three-Part Test (LIA):**
1. **Purpose test:** Is your interest genuine? (e.g., retain existing customers) Yes.
2. **Necessity test:** Is processing necessary to achieve it? Could you achieve it less intrusively?
3. **Balancing test:** Does your interest override the user's rights and expectations? Would they be surprised by this use?

If you fail any part: default to consent.

---

### What Requires Explicit Consent vs What Does Not

**Does NOT require fresh consent (contract or legitimate interest applies):**
- Transaction confirmations, receipts, order status
- Security alerts (password change, login from new device)
- KYC status updates (approved, rejected, documents needed)
- Account closure or suspension notices
- Onboarding flow emails (complete your profile, verify phone)
- Service changes that affect the user's contract
- Regulatory notices (MiCA updates, fee changes)

**DOES require explicit consent (or soft opt-in — see Section 2):**
- Promotional emails (offers, discounts, new products)
- Newsletter / market updates
- Referral program invitations
- Marketing push notifications
- Retargeting / behavioral advertising
- Any communication whose primary purpose is commercial promotion

**Gray zone — route to Diego:**
- "Educational" content that promotes Bit2Me products (e.g., "Learn about Earn" = actually product pitch)
- Reactivation campaigns to users who have been inactive 12+ months
- Cross-selling unrelated products (e.g., emailing Brokerage users about Loans)

---

### Data Minimization

Only collect what is strictly necessary for the stated purpose. For CRM:

- **Allowed:** email, phone, language, lifecycle stage, transaction history, product usage, CleverTap event data
- **Avoid collecting for marketing:** government ID scans stored in CRM (use BigQuery/KYC system), precise location beyond country/region, biometric data, health data, political/religious data
- **Rule of thumb:** if you wouldn't need the field to personalize or send the message, don't pull it into the campaign audience

---

### Purpose Limitation

Data collected for one purpose cannot be used for another incompatible purpose without new consent or a new lawful basis.

| Data collected for | Can be used for | Cannot be used for (without new basis) |
|-------------------|-----------------|----------------------------------------|
| KYC verification | Fraud detection, regulatory compliance | Marketing segmentation |
| Transaction processing | Account statements, tax reporting | Behavioral profiling for ads |
| Customer support tickets | Resolving the issue | Sending product recommendations |
| Onboarding flow events | Completing onboarding journey | Building third-party lookalike audiences |

---

### Retention Limits

| Data type | Maximum retention | Basis |
|-----------|------------------|-------|
| KYC documents (passport, ID) | 5 years after end of business relationship (Spain AML law) | Legal obligation |
| Transaction records | 5 years (AML Directive 5AMLD) | Legal obligation — overrides GDPR erasure |
| Marketing consent records | Until withdrawal + 3 years for evidence | Legitimate interest / legal defense |
| Behavioral/event data (CleverTap) | 13 months rolling (AEPD guidance) | Minimize and configure retention settings |
| Email campaign engagement (opens, clicks) | 13 months rolling | Minimize |
| Support tickets | 3 years after close | Legitimate interest |
| Web/app analytics (cookies) | 13 months maximum (AEPD) | Consent |
| Inactive accounts with no transactions | 3 years after last activity (then anonymize or delete) | Review with Diego |

**Practical rule:** If a user hasn't logged in or transacted in 3 years AND holds no balance AND has no pending regulatory obligation — schedule deletion or anonymization. Flag for Diego review before executing.

---

## 2. CRM AND LIFECYCLE MARKETING SPECIFICS

### Email Marketing: Consent vs Soft Opt-In

**Soft opt-in rule (Article 13 LSSI-CE / ePrivacy Directive Art. 13.2):**
You can email an existing customer about similar products/services WITHOUT fresh consent IF:
1. They purchased from you recently (active customer — no hard cutoff, but 12 months is safe practice)
2. The email is about similar products/services to what they already use
3. You gave them a clear opt-out at purchase (in T&Cs/registration)
4. Every subsequent email has a one-click unsubscribe

**Soft opt-in applies at Bit2Me:**
- Emailing Brokerage users about Pro features
- Emailing active users about new crypto listings
- Lifecycle nurture sequences (JN-01 through JN-11) for users who have completed FM

**Soft opt-in does NOT apply:**
- Emailing dormant users who haven't interacted in 12+ months — recheck consent status
- Cross-selling radically different products (e.g., emailing crypto users about mortgages if Bit2Me expands)
- Any user who has explicitly unsubscribed — FULL STOP, no exceptions

**Explicit consent required:**
- Users who registered but never purchased (REGISTERED, KYC stages) — they are prospects, not customers
- Any new marketing purpose not covered at registration
- Third-party email acquisition (e.g., co-marketing lists from partners)

---

### Push Notifications: Consent Requirements

Push notifications = require explicit, informed consent before the first push.

**How consent should be obtained:**
- In-app permission prompt (iOS/Android system dialog) — this IS the consent event
- Must be preceded by a pre-permission screen explaining what notifications will contain
- Cannot send marketing pushes before user has seen and accepted the system prompt

**What consent covers:** whatever is described in the permission prompt. Keep it specific.

**When consent expires or needs refresh:**
- If user disables push at OS level — they have withdrawn consent. Do not attempt to re-enable silently.
- If user has not opened the app in 12+ months — treat as lapsed. Do not send reactivation push without refreshed consent flow (use email first).

**FOMO Agent / dormant user pushes (c6/c7):**
- Check CleverTap push opt-in status BEFORE scheduling. Suppression list must be applied.
- Users who are push-enabled but dormant = can receive push under soft opt-in IF they are existing customers with valid consent on record.
- NEVER send push to users who opted out of notifications at OS level. CleverTap will suppress them, but verify suppression is active.

---

### Behavioral Tracking: What You Can Track Without Additional Consent

**No additional consent needed (legitimate interest / contract):**
- Page views and navigation within the authenticated app (logged-in users)
- Transaction events (trade executed, deposit received, withdrawal sent)
- Feature usage (opened Pro chart, used card, viewed Earn yield)
- Login/logout, session duration, device type
- Support ticket creation and resolution

**Requires consent (cookie/tracking consent):**
- Web analytics cookies on public pages (unauthenticated)
- Cross-site tracking (e.g., Facebook Pixel, Google Analytics 4 in advertising mode)
- Heatmaps or session recordings of unauthenticated pages
- Retargeting pixels

**In BigQuery:** tracking authenticated user events = legitimate interest basis is defensible. Document the LIA.

---

### Segmentation and Profiling: When You Need a DPIA

A Data Protection Impact Assessment (DPIA) is required when profiling creates:
- Significant or systematic evaluation of personal aspects
- Automated decision-making that produces legal or similarly significant effects on users
- Large-scale processing of sensitive data

**DPIA required at Bit2Me:**
- Any automated system that decides which users get worse terms, higher fees, or reduced service
- Scoring that affects credit (Arranca loan scoring based on behavioral data)
- Systematic profiling of all 1.8M users for any purpose (the 37-segment model = document with DPIA)

**DPIA NOT required:**
- Manual segmentation for email campaigns (human decides, sends to segment)
- Standard A/B testing of messaging
- Lifecycle stage assignment based on transaction history (contract basis)

**Action:** Work with Diego to ensure the 37-segment model and Health Score algorithm have a documented DPIA. This is already at scale (>72k dormant users, 1.8M total).

---

### The Soft Opt-In Decision Tree (Use This Before Every Campaign)

```
Is the user an EXISTING CUSTOMER (has made at least one purchase/transaction)?
  YES →
    Has the user explicitly unsubscribed from marketing?
      YES → STOP. Do not contact. No exceptions.
      NO →
        Is this about similar products/services to what they use?
          YES → Soft opt-in applies. Include unsubscribe. Proceed.
          NO → Need explicit consent. Check consent record or route to Diego.
  NO (prospect/registered only) →
    Do you have explicit marketing consent on file?
      YES → Verify consent scope covers this message. Proceed if yes.
      NO → Cannot send marketing. Can send onboarding/contract messages only.
```

---

## 3. CRYPTO-SPECIFIC GDPR

### Blockchain Immutability vs Right to Erasure

This is the fundamental tension in crypto GDPR. The right to erasure (Article 17) conflicts with blockchain's immutability.

**The AEPD / EDPB position:** transaction data recorded on public blockchain is pseudonymous but likely identifiable. Bit2Me cannot delete blockchain records it doesn't control. However:

**What Bit2Me CAN and MUST delete:**
- Internal records linking blockchain addresses to user identity (the bridge data)
- KYC data (after retention period expires)
- Email, phone, name, and other PII from internal databases
- CleverTap user profiles
- BigQuery user tables

**What Bit2Me CANNOT delete (and is not required to):**
- Transaction hashes on public blockchains (Ethereum, Bitcoin, etc.)
- These are considered anonymous/pseudonymous once the linking data is deleted

**Practical approach for erasure requests:**
1. Delete PII from all internal systems (BigQuery, CleverTap, CRM, support)
2. Sever the link between blockchain address and identity
3. Document that on-chain data cannot be deleted and why
4. Confirm to user that all linkable data has been destroyed

---

### KYC Data Retention Requirements (AML vs GDPR)

Spain's AML law (Ley 10/2010 de Prevención del Blanqueo de Capitales) and EU's 5AMLD require:

- KYC documents must be retained for **5 years** after the end of the business relationship
- Transaction records must be retained for **5 years**
- This is a **legal obligation** that overrides GDPR erasure rights

**When a user requests deletion:**
- You CANNOT delete KYC data during the active relationship OR within 5 years of account closure
- You MUST tell the user this, citing the legal obligation
- You CAN delete all non-regulated data (preferences, behavioral data, marketing history)

**After the 5-year period:**
- Schedule active deletion of KYC data
- Anonymize transaction records (remove direct identifiers, keep aggregate stats)
- Confirm in writing to user if they submitted an erasure request earlier

---

### Transaction Data: How Long to Keep, When to Delete

| Data | Keep for | Then |
|------|----------|------|
| Trade history (crypto buy/sell) | 5 years after account closure | Anonymize or delete |
| Deposit/withdrawal records | 5 years after account closure | Anonymize or delete |
| Tax-relevant transaction data | 4 years (Spanish statute of limitations) — often overlaps with AML 5yr | Coordinate with finance |
| Card transactions | 5 years | Anonymize or delete |
| Internal transfer logs | 5 years | Anonymize or delete |
| Session/login logs | 13 months (security) | Delete |
| Marketing event logs (CleverTap) | 13 months | Auto-purge (configure in CleverTap settings) |

**Note:** "Anonymized" means it cannot be re-linked to an individual even with additional data. Pseudonymized (still has user_id) is NOT anonymized.

---

### Cross-Border Data Transfers

Bit2Me operates in Spain (EU). Key rules:

**Within EU/EEA:** Free flow. No restrictions. Standard.

**To third parties outside EU/EEA (e.g., US-based SaaS tools):**
- Must have adequate protection: Standard Contractual Clauses (SCCs), adequacy decision, or Binding Corporate Rules
- CleverTap: Verify DPA (Data Processing Agreement) is in place with current SCCs
- Google BigQuery: Google Cloud has SCCs and EU data residency options — verify your project is configured for EU region
- Any analytics or marketing tool receiving EU user data = must have valid DPA + transfer mechanism

**Action items:**
- Audit all tools receiving Bit2Me user data: CleverTap, BigQuery, any email ESP, Qlik, support tools
- Confirm DPA exists for each
- Confirm SCCs or adequacy decision covers the transfer
- Document in a Record of Processing Activities (RoPA) — legal requirement under Art. 30

---

## 4. PRE-SEND CHECKLIST (Diego Review)

### Standard Pre-Send Checklist — Every Campaign

Before submitting ANY campaign to Diego for approval:

- [ ] **Audience defined:** Who exactly is in this audience? (Lifecycle stage, segment, count of users)
- [ ] **Lawful basis identified:** Consent / Soft opt-in / Contract / Legitimate Interest — and why
- [ ] **Consent status verified:** Have opted-out users been suppressed in CleverTap? (Run suppression list check)
- [ ] **Data used is proportionate:** What user data is used to determine inclusion in this audience? Is it necessary?
- [ ] **Message purpose matches data basis:** Is the message content consistent with why you have the data?
- [ ] **Unsubscribe mechanism present:** One-click unsubscribe in every email. Push opt-out path exists.
- [ ] **No sensitive data used:** No data on health, religion, political views, precise location used for targeting
- [ ] **Retention check:** Are any users in this audience in a "should be deleted" state? (3yr inactive, no balance)
- [ ] **Third-party data:** Is any external/purchased data used? (Almost certainly requires consent — flag)

### What Diego Needs From You

Submit a campaign brief with:

1. **Campaign name and objective:** What is this trying to achieve?
2. **Audience:** How was the list built? What criteria? Approximate size.
3. **Lawful basis:** Which of the six bases applies, and your rationale.
4. **Data fields used:** List every user attribute used for targeting or personalization.
5. **Message content:** Draft copy (subject line, body, CTA).
6. **Opt-out mechanism:** How can users unsubscribe / opt out?
7. **Frequency:** How often will this message be sent to the same user?
8. **Expiry:** When does this campaign end or when will the audience be refreshed?

### Campaign Types: Standard vs Requires Explicit Diego Review

**Standard (pre-approved category — Diego spot-check only):**
- Onboarding sequences to KYC/DEPOSITED users (contract basis)
- Transactional notifications (confirmations, alerts)
- Journey emails (JN-01 to JN-11) to active customers under soft opt-in — already reviewed
- A/B tests on approved journeys (same audience, different copy)

**Requires explicit Diego review before each send:**
- Any new audience not previously approved
- Reactivation campaigns to users dormant 12+ months
- Any campaign using new data signals not previously used (e.g., adding Health Score as a filter for the first time)
- Campaigns involving third-party data or co-marketing lists
- Any automated trigger that runs without human review (FOMO Agent, drip sequences)
- Any message touching on financial advice, investment returns, or regulatory-sensitive content
- Cross-sell to users who signed up for a different product category

---

## 5. TECHNICAL IMPLEMENTATION

### Consent Management in CleverTap

**Suppression lists — maintain and sync:**
- `global_unsubscribe` — users who clicked unsubscribe in any email. Never market to these.
- `push_opt_out` — users who disabled push at OS level or explicitly opted out in-app
- `c8_suppression` — whales (C8 cluster) — never include in mass sends (also a GDPR proportionality issue — high-value users warrant careful handling)
- `compliance_uk3` — UK compliance group 3 — separate regime, do not contact with EU-basis campaigns

**CleverTap suppression sync process:**
1. Unsubscribe events in CleverTap → auto-add to suppression list (verify this is configured)
2. BigQuery erasure requests → manual removal from CleverTap via API or manual delete
3. Weekly audit: pull CleverTap suppression list, cross-check against BigQuery opt-out table

**Setting event data retention in CleverTap:**
- Go to Settings > Data Retention
- Set event data retention to 13 months (AEPD guidance)
- Profile data: retain only while account is active + retention period

**For new journeys:**
- Tag each journey with the lawful basis used
- Configure suppression lists to apply automatically before each send
- Set up exit criteria: if user unsubscribes mid-journey, they exit immediately (not after current step)

---

### Right to Erasure: Process for BigQuery + CleverTap

When a user submits a deletion request (Article 17):

**Step 1 — Verify identity (within 24h of request):**
- Confirm request comes from authenticated session or verified email
- Log the request with timestamp, user_id, request channel

**Step 2 — Legal hold check (within 72h):**
- Check if user has active balance (cannot delete while funds held)
- Check if within AML 5-year retention window
- Check for pending regulatory investigation or legal hold
- If any hold applies: inform user of the reason and estimated date when deletion will be possible

**Step 3 — Execute deletion (within 30 days):**

BigQuery:
```sql
-- Anonymize user PII in primary user table
UPDATE `bit2me.users.user_profile`
SET email = CONCAT('deleted_', user_id, '@deleted.invalid'),
    phone = NULL,
    first_name = 'Deleted',
    last_name = 'User',
    date_of_birth = NULL,
    address = NULL,
    ip_address = NULL,
    deleted_at = CURRENT_TIMESTAMP(),
    deletion_reason = 'GDPR_ERASURE_REQUEST'
WHERE user_id = '[USER_ID]';

-- Keep transaction records but sever identity link
-- (AML retention obligation — do NOT delete transaction rows)
-- The anonymization above severs the link
```

CleverTap:
- Use CleverTap API: `DELETE /1/targets/user_delete.json` with identity
- Or: Mark user profile as "Do Not Contact" and remove all PII fields
- Verify deletion confirmation in CleverTap audit log

Other systems to check:
- Email service provider (bounce/engagement logs)
- Support ticketing system
- Any analytics tools receiving user-level data

**Step 4 — Confirm to user (within 30 days of request):**
- Written confirmation of what was deleted
- Explanation of any data retained (AML) and why
- Reference number for the request

---

### Data Subject Access Requests (DSAR): 30-Day Response

When a user asks "what data do you hold on me" (Article 15):

**Timeline:** Must respond within 30 days. Can extend to 90 days for complex requests — notify user within 30 days if extending.

**What you must provide:**
- Categories of data held
- Purposes of processing
- Recipients or categories of recipients (third parties)
- Retention periods
- Source of data (if not from the user directly)
- Any automated decision-making logic (if Health Score affects decisions)
- Copy of the actual data (if requested)

**DSAR response package for Bit2Me user:**
1. Account data: profile, KYC status, registration date
2. Transaction history: trades, deposits, withdrawals (within accessible period)
3. Marketing preferences: opt-in/out status, communication history
4. Event logs: key app events in CleverTap (13-month window)
5. Support ticket history
6. Note on what is NOT provided: AML data held for legal obligation (you can describe the category without providing the raw investigation file)

**Process:**
- Route all DSARs to Diego immediately upon receipt
- Daniel's team provides data pull from BigQuery + CleverTap export
- Diego coordinates the formal response letter
- Log every DSAR in the compliance tracker

---

### Cookie Consent for Web/App

**What requires cookie consent (ePrivacy Directive + AEPD guidance):**
- Analytics cookies (Google Analytics, unless fully anonymized)
- Advertising/retargeting cookies (Meta Pixel, Google Ads)
- Social media embeds
- Heatmap / session recording tools (Hotjar, etc.)
- Any third-party cookie

**What does NOT require consent:**
- Strictly necessary cookies (session cookies, authentication, shopping cart equivalent)
- Security cookies (CSRF tokens)
- Load balancing cookies

**AEPD (Spanish DPA) requirements for cookie banner:**
- Must offer genuine "Accept All" / "Reject All" choice at first layer
- Pre-ticked boxes: ILLEGAL
- "Continue browsing = consent": ILLEGAL
- Reject must be as easy to click as Accept (same prominence, same position)
- Must document consent with timestamp and version of banner

**Practical:** If the marketing team adds any new analytics or advertising pixel, this requires a cookie banner update AND potentially a consent re-request if the new purpose wasn't covered. Route to Diego before implementation.

---

## 6. COMMON VIOLATIONS TO AVOID

### The Fatal Mistakes — Zero Tolerance

**1. Sending to opted-out users**
- Symptom: unsubscribe list not synced to CleverTap suppression list
- Risk: AEPD fines up to €20M or 4% global turnover. Plus reputational damage.
- Prevention: Automated suppression sync. Weekly audit. Never export audience without running through suppression filter.

**2. Using data for purposes not stated at collection**
- Symptom: using KYC data to build behavioral segments; using support ticket content for product targeting
- Risk: GDPR Art. 5(1)(b) violation
- Prevention: Label every data field in BigQuery with its collection purpose. Before using a data source in a campaign, check the purpose tag.

**3. No unsubscribe mechanism**
- Symptom: transactional email template reused for promotional send without footer update
- Risk: LSSI-CE violation + GDPR Art. 21 violation
- Prevention: Email templates must have unsubscribe footer hard-coded. QA checklist item before send.

**4. Sharing data with third parties without appropriate basis**
- Symptom: exporting user emails to a co-marketing partner; sharing segments with ad platforms without DPA
- Risk: GDPR Art. 44-46 (transfer) violation
- Prevention: Any data leaving Bit2Me systems = Diego review. No exceptions. This includes uploading user lists to Meta Custom Audiences, Google Customer Match, etc. — requires consent AND valid DPA with the platform.

**5. Keeping data longer than necessary**
- Symptom: CleverTap retaining 3 years of event data; BigQuery tables with 2019 user data never audited
- Risk: GDPR Art. 5(1)(e) violation
- Prevention: Set automated retention policies. Annual data audit. CleverTap data retention = 13 months max.

**6. Profiling without informing users**
- Symptom: Health Score or 37-segment model affects what users see or receive, without this being disclosed in privacy policy
- Risk: GDPR Art. 22 (automated decision-making) violation if decisions are solely automated and significant
- Prevention: Update privacy policy to disclose profiling. If decisions are significant and automated, provide opt-out mechanism. DPIA completed.

**7. Re-contacting users who have been fully inactive and never gave explicit consent**
- Symptom: Emailing REGISTERED users who never transacted, years after registration
- Risk: They are prospects with no soft opt-in basis. Without explicit consent = violation.
- Prevention: Audience builder should have a hard rule: REGISTERED + no FM + no explicit marketing consent = excluded from all promotional sends.

---

## QUICK REFERENCE CARD

### Before Building Any Campaign Audience

```
1. Does every user in this list have a valid lawful basis? (Consent OR Soft opt-in OR Contract)
2. Have opted-out users been excluded? (CleverTap suppression list applied)
3. Is the data used proportionate to the purpose?
4. Does Diego need to review? (Check Section 4 decision tree)
5. Is there a one-click unsubscribe in the message?
```

### Retention Cheat Sheet

| What | Keep | Then |
|------|------|------|
| KYC docs | 5yr after account close | Delete |
| Transactions | 5yr after account close | Anonymize |
| Marketing events | 13 months | Auto-delete |
| Consent records | Until withdrawal + 3yr | Keep (legal defense) |
| Inactive users | 3yr after last activity | Anonymize or delete |

### Basis by Campaign Type

| Campaign | Basis |
|----------|-------|
| Onboarding (KYC flow) | Contract |
| Transactional alerts | Contract |
| Journey JN-01 to JN-11 (active customers) | Soft opt-in (Legitimate Interest) |
| Reactivation of 12mo+ dormant | Route to Diego — likely needs consent |
| Prospects (registered, no purchase) | Must have explicit consent |
| FOMO push (dormant, push-enabled) | Verify consent status per user in CleverTap |

---

*For questions, always route to Diego. For data operations (BigQuery deletion, CleverTap audit), coordinate with Álvaro (data infra). GDPR compliance is a shared responsibility — marketing sets the rules, data executes the deletion, legal approves the edge cases.*
