## 9. Compliance Framework Per Trigger Type

> **Purpose:** This section defines the per-trigger compliance classification system, Diego review workflow, investment advice bright-line test, market abuse prevention protocol, and a fill-in compliance checklist template. Every trigger defined in Phase 2's taxonomy and tabulated in Phase 3's Master Trigger Table references this section for its compliance obligations.
>
> **Owners:** Diego (legal review and approval gate), Katy (template creation and campaign compliance), Daniel (escalation and policy decisions)
>
> **Regulatory scope:** MiCA (EU 2023/1114), GDPR (EU 2016/679), ePrivacy Directive (2002/58/EC), CNMV supervisory authority (Spain)

---

### 9.1 Compliance Classification System

Every trigger must be classified into exactly one of four compliance classes. This classification determines the Diego review level, MiCA obligations, risk warning requirements, and audit trail needs.

#### 9.1.1 Four-Class Compliance Table

| Compliance Class | Definition | Diego Review Level | MiCA Art. 66 Applicability | Risk Warning Required | GDPR Lawful Basis | Examples |
|------------------|-----------|-------------------|---------------------------|----------------------|-------------------|---------|
| **TRANSACTIONAL** | Confirms a user-initiated action or protects account security. No commercial intent. | NOT_REQUIRED | Not applicable (contractual necessity) | No | Art. 6(1)(b) -- contract performance | Trade filled, withdrawal confirmed, login from new device, 2FA code, failed payment |
| **INFORMATIONAL** | States a verifiable fact about market or portfolio state without suggesting any action. | TEMPLATE_PRE_APPROVED (one-time Tier 1) | Applies -- must be fair, clear, not misleading | Link to risk page required | Art. 6(1)(b) for user-configured; Art. 6(1)(f) for proactive | "BTC crossed $70,000", "Your BTC holding is up 12% this week", "ETH Earn APY is currently 3.2%" |
| **MARKETING** | Promotes a Bit2Me product, encourages a commercial action, or targets users for re-engagement. | REQUIRED per template (Tier 1) + per campaign (Tier 2) | Full compliance -- identifiable as marketing, disclaimers, risk warnings mandatory | Yes -- inline or linked | Art. 6(1)(a) -- explicit consent | Cross-sell ("Discover Earn"), reactivation campaigns, new listing promotions, product upsell, promotional offers |
| **ADVISORY_RISK** | Could be construed as suggesting an investment action. HIGH regulatory risk. | REQUIRED per individual message + dedicated legal review | Full compliance + possible MiCA Art. 81 suitability concerns | Yes -- mandatory inline, cannot be link-only | Art. 6(1)(a) -- explicit consent + enhanced review | "Great entry point", "Earn beats savings accounts", "Don't miss this opportunity". **DO NOT USE without explicit legal clearance from Diego. Reserve for V3 or later.** |

#### 9.1.2 Classification Decision Tree

To classify any trigger, answer these four questions in order:

```
QUESTION 1: Does this notification confirm a user-initiated action or protect account security?
  YES --> TRANSACTIONAL (done)
  NO  --> continue

QUESTION 2: Does this notification ONLY state a verifiable fact without suggesting any action?
  YES --> INFORMATIONAL (done)
  NO  --> continue

QUESTION 3: Does this notification suggest, imply, or could reasonably be construed as recommending
            a specific investment action (buy, sell, hold, move assets)?
  YES --> ADVISORY_RISK (done -- flag for Diego legal review)
  NO  --> MARKETING (done)
```

**Tie-breaking rule:** When in doubt between INFORMATIONAL and MARKETING, classify as MARKETING. When in doubt between MARKETING and ADVISORY_RISK, classify as ADVISORY_RISK. It is always safer to over-classify than under-classify. The cost of over-classification is a Diego review; the cost of under-classification is a MiCA violation (up to EUR 5M or 10% annual turnover).

#### 9.1.3 Mapping to Trigger Families

| Trigger Family | Default Compliance Class | Rationale | Exceptions |
|---------------|------------------------|-----------|------------|
| **A -- User Configured** | TRANSACTIONAL | User explicitly requested these alerts (contract performance) | Price alerts with editorial commentary would be INFORMATIONAL or ADVISORY_RISK |
| **B -- Market Triggered** | INFORMATIONAL | Proactive market data notifications stating facts | Any notification pairing market data with action suggestion = ADVISORY_RISK |
| **C -- Behavioral** | MARKETING | Targeting based on user behavior to drive commercial actions | Abandoned order reminder could argue TRANSACTIONAL (user initiated) -- classify as MARKETING to be safe |
| **D -- Lifecycle** | MARKETING | Lifecycle nudges encourage product usage and re-engagement | AT_RISK protective alerts could be INFORMATIONAL if purely factual |
| **E -- Cross-sell** | MARKETING | Product promotion by definition | Product comparison with returns (e.g., "Earn 3.2% vs holding") = ADVISORY_RISK |
| **F -- Risk & Protective** | TRANSACTIONAL | Protects user from financial risk (LTV alerts, security) | LTV threshold alerts are protective (contractual); large balance inactivity alerts may be MARKETING if they encourage action |

---

### 9.2 Diego Review Workflow (Four-Eyes Principle)

Diego Barreira is the single legal gate for ALL CRM message copy at Bit2Me. This workflow implements the four-eyes (maker-checker) principle required for MiCA Art. 66 compliance, while mitigating the bottleneck risk of routing 30+ trigger templates through a single reviewer.

#### 9.2.1 Tier 1: Template-Level Approval (One-Time)

**For:** Notification templates with fixed copy (dynamic variables limited to asset name, price, percentage, user name).

**SLA:** 48 hours from submission to decision.

**Process:**

| Step | Action | Owner | Output |
|------|--------|-------|--------|
| 1 | Create notification template with copy, channel, deep link, and compliance class | Katy / Growth | Template draft in Lark/Notion |
| 2 | Run automated keyword blocklist scan (see Section 9.3.2) | Automated (script or manual check) | PASS / FAIL with flagged terms |
| 3 | Submit to Diego with: template text, compliance class, target segment description, channel, MiCA Art. 66 self-assessment | Katy | Submission record in Lark |
| 4 | Diego reviews against MiCA Art. 66 checklist (see Section 9.5) | Diego | Written approval or rejection with required changes |
| 5 | If approved: mark template as PRE_APPROVED in CleverTap template library | Katy | Template status updated |
| 6 | Record approval with timestamp, Diego's name, and template version | Katy | Audit trail entry |

**Re-approval trigger:** Any change to template copy text requires re-submission through Tier 1. Changes to dynamic variable values (e.g., different asset name populating the same template) do NOT require re-approval.

#### 9.2.2 Tier 2: Campaign-Level Approval (Per Launch)

**For:** Campaigns using dynamic copy, new segment targeting, first use of a template, or any MARKETING/ADVISORY_RISK classification.

**SLA:** 24 hours from submission to decision.

**Process:**

| Step | Action | Owner | Output |
|------|--------|-------|--------|
| 1 | Create campaign with template + targeting segment + schedule + channel | Katy | Campaign draft in CleverTap |
| 2 | Send test notification to internal QA segment | Katy | Test delivered and verified |
| 3 | Submit to Diego with: rendered template (with sample dynamic values), targeting criteria, channel, schedule, compliance class | Katy | Submission record |
| 4 | Diego reviews: template (if not yet pre-approved), targeting appropriateness, schedule timing, channel selection | Diego | Written approval or rejection |
| 5 | Campaign activated only after written Diego approval | Katy | Campaign live |

#### 9.2.3 Tier 3: Emergency Override (P0 Only)

**For:** P0 security alerts and regulatory-mandated communications ONLY. No marketing messages may use this tier.

**SLA:** Immediate -- no pre-review required.

**Process:**

| Step | Action | Owner | Output |
|------|--------|-------|--------|
| 1 | Use pre-approved security/transactional template (approved once during Tier 1) | Engineering / Compliance | Alert sent |
| 2 | Post-send notification to Diego within 4 hours | Katy / Engineering | Email or Lark message to Diego |
| 3 | Diego records in audit trail retrospectively | Diego | Audit log updated |

**Restrictions:** Only TRANSACTIONAL compliance class templates may use Tier 3. Any INFORMATIONAL, MARKETING, or ADVISORY_RISK message sent via Tier 3 is a compliance violation and must be escalated immediately.

#### 9.2.4 Bottleneck Mitigation Strategies

Diego currently reviews 7/9 active journeys and is a known SPOF (single point of failure). These strategies reduce review volume without reducing compliance rigor:

| Strategy | How It Works | Expected Impact |
|----------|-------------|----------------|
| **Pre-approved copy library** | Build a library of 20-30 Diego-approved notification templates covering common scenarios per trigger family. New campaigns using these templates skip Tier 2 review. | Reduces Tier 2 reviews by ~60% |
| **Weekly batch reviews** | Bundle 5-10 new templates for Diego review every Monday (instead of ad-hoc submissions). Provides predictable workload. | Reduces context-switching; faster turnaround |
| **Dynamic variable exemption** | Dynamic variables (asset name, price, percentage, user name) inserted into pre-approved templates do NOT trigger re-review. Only copy text changes require re-approval. | Eliminates re-reviews for personalization |
| **Compliance class fast-track** | TRANSACTIONAL and INFORMATIONAL templates get Tier 1 only (no Tier 2 per campaign). MARKETING templates get both Tier 1 and Tier 2. ADVISORY_RISK gets dedicated legal review. | Proportional review effort to risk level |
| **Deputy reviewer** | Train a second person (e.g., Compliance team member) as backup reviewer for Tier 1 template approvals during Diego's absence. Diego retains final authority for Tier 2 and ADVISORY_RISK. | Eliminates single-point-of-failure risk |

---

### 9.3 Investment Advice vs. Informational -- Bright-Line Test

MiCA does NOT provide a formal bright-line test between "informational" and "investment advice" in notifications. ESMA is still developing detailed guidance as of March 2026 (ESMA Knowledge and Competence Guidelines published January 2026; Suitability Guidelines published February 2026). Until formal guidance exists, Bit2Me adopts the following conservative internal classification test.

#### 9.3.1 The Four-Point Bright Line Test

A notification is **INFORMATIONAL** if and only if ALL four conditions are met:

| # | Condition | Test |
|---|-----------|------|
| 1 | **States a verifiable fact** | Can the statement be independently verified using public data? (e.g., "BTC is at $70,000" is verifiable; "BTC is a good investment" is not) |
| 2 | **Does not suggest any action** | Does the notification avoid any language implying the user should buy, sell, hold, move, or compare assets? |
| 3 | **Does not pair facts with value judgments** | Is the fact presented neutrally without editorial commentary? (e.g., "ETH Earn APY is 3.2%" is neutral; "ETH Earn beats savings" is a value judgment) |
| 4 | **Does not create artificial urgency around financial decisions** | Does the notification avoid time pressure language ("last chance", "don't miss", "limited time") when applied to investment products? |

If ANY condition fails, the notification is NOT informational. Classify as MARKETING (if commercial intent) or ADVISORY_RISK (if investment action is suggested).

#### 9.3.2 Safe vs. Dangerous Examples

| # | Safe (INFORMATIONAL) | Dangerous (ADVISORY_RISK) | Why It Crosses the Line |
|---|---------------------|--------------------------|------------------------|
| 1 | "BTC crossed $70,000" | "BTC is at $70,000 -- great entry point" | Value judgment ("great entry point") suggests action |
| 2 | "Your BTC holding is up 12% this week" | "Your portfolio could grow faster with Earn" | Implies comparative advantage and suggests product action |
| 3 | "ETH Earn APY is currently 3.2%" | "ETH Earn beats savings accounts" | Compares crypto returns to non-crypto alternatives |
| 4 | "New asset available: SOL" | "SOL is trending -- start trading now" | Combines market commentary with explicit trade suggestion |
| 5 | "You haven't traded in 30 days" | "You're missing out on market opportunities" | Creates FOMO and implies financial loss from inaction |
| 6 | "Your LTV ratio is 71.4%" | "Deposit more collateral to avoid liquidation before the market drops further" | Pairs factual LTV with market prediction and action suggestion |
| 7 | "BTC volatility reached 8.5% today" | "High volatility = high opportunity. Trade now." | Converts market data into trading recommendation |
| 8 | "Earn rates updated: USDT now 4.1% APY" | "Lock in 4.1% before rates drop" | Creates urgency around yield product decision |
| 9 | "Your referral earned 3 new sign-ups" | "Refer more friends to maximize your rewards" | Crosses from status update to action suggestion (though low regulatory risk) |
| 10 | "Pro trading now available for SOL/EUR" | "Pro traders are already buying SOL -- join them" | Social proof + trading suggestion = advisory territory |

#### 9.3.3 Keyword Blocklist

Automated pre-screening of all notification copy before Diego review. This catches obvious violations before they consume Diego's review time.

**PROHIBITED -- Must never appear in any notification copy (any compliance class):**

| Keyword/Phrase | Why Prohibited |
|---------------|---------------|
| "guaranteed" | Implies certainty of returns (MiCA Art. 66 violation) |
| "risk-free" | No crypto-asset is risk-free (MiCA Art. 66(3)) |
| "pump" / "pumping" | Market manipulation language (MiCA Art. 91) |
| "moon" / "to the moon" | Implies guaranteed price appreciation |
| "100x" / "10x" (in promotional context) | Implies guaranteed multiples of return |
| "no risk" | Factually false for crypto-assets |
| "free money" | Misleading (MiCA Art. 66(2)) |

**FLAGGED -- Requires mandatory Diego review (cannot use TEMPLATE_PRE_APPROVED path):**

| Keyword/Phrase | Why Flagged | Possible Safe Use |
|---------------|-------------|-------------------|
| "should" | Implies recommendation | "You should update your password" (security = OK) |
| "opportunity" | Implies investment opportunity | "Opportunity to learn about Earn" (educational = borderline) |
| "don't miss" / "don't miss out" | Creates FOMO around financial decision | "Don't miss our webinar" (non-financial = OK) |
| "good time to" | Implies market timing advice | No safe use in financial context |
| "beats" / "outperforms" | Comparative return claims | No safe use in financial context |
| "recommended" | Implies personal recommendation (MiCA advisory) | No safe use in financial context |
| "consider buying" | Explicit purchase suggestion | No safe use |
| "last chance" | Urgency around financial decision | "Last chance to update your KYC" (compliance = OK) |
| "entry point" | Implies price timing advice | No safe use in financial context |
| "bargain" / "undervalued" | Implies asset mispricing (advisory territory) | No safe use |
| "profit" / "profits" | Implies guaranteed positive outcome | "See your profit/loss in Portfolio" (factual = OK) |

**REQUIRED -- Must appear in or be linked from every MARKETING notification:**

| Required Element | Where | Format |
|-----------------|-------|--------|
| Risk warning | Inline (email, in-app) or linked (push) | "Capital at risk. Not investment advice." |
| MiCA mandatory disclaimer | Inline (email) or linked landing page (push, in-app) | "This crypto-asset marketing communication has not been reviewed or approved by any competent authority in any Member State of the European Union." |
| Marketing identifier | Visible in notification | Clear labeling as promotional/marketing content (not disguised as transactional) |

#### 9.3.4 Cross-Sell Specific Guidance (Family E)

Family E triggers require special attention because they sit on the boundary between MARKETING and ADVISORY_RISK:

| Cross-Sell Approach | Compliance Class | Example | Diego Review |
|--------------------|-----------------|---------|-------------|
| **Product awareness** (what the product is) | MARKETING | "Did you know about Bit2Me Earn? Stake your crypto." | Tier 1 template approval |
| **Product feature** (how it works) | MARKETING | "Earn lets you stake USDT with flexible withdrawal." | Tier 1 template approval |
| **Product comparison with returns** | ADVISORY_RISK | "Your USDT could be earning 3.2% in Earn vs. 0% in Wallet." | Dedicated legal review -- DO NOT USE in V1 |
| **Product comparison with external alternatives** | ADVISORY_RISK | "Earn yields are higher than traditional savings accounts." | Dedicated legal review -- DO NOT USE in V1 |

**V1 rule:** All Family E triggers must use the MARKETING compliance class with product awareness or product feature framing only. Any copy that mentions yields, returns, or comparisons requires ADVISORY_RISK classification and is deferred to V3.

---

### 9.4 Market Abuse Prevention Protocol (Family B Triggers)

MiCA Title VI (Articles 86-92) establishes the EU's first comprehensive market abuse framework for crypto-assets. Family B triggers (price alerts, volatility spikes, volume alerts, trending assets) are the highest-risk notification type for market abuse because they involve platform-originated communications about asset prices and trading activity.

#### 9.4.1 Five Mandatory Rules for Family B Triggers

| # | Rule | Regulatory Basis | Implementation |
|---|------|-----------------|----------------|
| 1 | **Public data sources only** | MiCA Art. 87 (inside information = non-public, precise information) | All price/volume data for Family B triggers must come from PUBLIC sources (CoinGecko API, public exchange feeds). NEVER use internal order book data, pending listing announcements, or internal liquidity metrics as trigger inputs. Document the data source for every Family B trigger in the trigger specification. |
| 2 | **Simultaneous send to all eligible users** | MiCA Art. 89 (insider dealing prohibition) + Art. 91 (market manipulation) | When a Family B trigger fires, ALL eligible users must receive the notification simultaneously. No staggered sends based on user tier, balance, or VIP status. No "early access" price alerts. Technical: use CleverTap's "Send at best time" = OFF for Family B; use "Send now" delivery. |
| 3 | **No pre-announcement timing** | MiCA Art. 88 (public disclosure of inside information) + Art. 89 | Never send price/volume alerts timed to coincide with or precede internal platform events (new listing announcements, delisting notices, liquidity changes, partnership announcements). Family B triggers must have NO dependency on Bit2Me's internal event calendar. |
| 4 | **Audit trail for every send** | MiCA Art. 92(1) (obligation to prevent and detect market abuse) | Every Family B notification must be logged with: timestamp (UTC), trigger_id, data source, data value at trigger time, list of recipient user_ids, send method. Logs retained for minimum 5 years (Art. 88 public disclosure retention requirement). Storage: BigQuery `bit2me_lifecycle.notification_audit_log`. |
| 5 | **Quarterly compliance review** | MiCA Art. 92 (ongoing obligation) + ESMA April 2025 Guidelines | Every quarter, review all Family B triggers for: (a) data source integrity (still public?), (b) send timing patterns (any correlation with platform announcements?), (c) recipient selection fairness (any inadvertent filtering?), (d) new ESMA guidance applicable. Document review results. Owner: Diego + Daniel. |

#### 9.4.2 Regulatory Citations

| Article | Title | Relevance to Family B Triggers |
|---------|-------|-------------------------------|
| **Art. 87** (Article 87) | Definition of inside information | Defines what constitutes inside information for crypto-assets. Any non-public, precise information likely to significantly affect price. Bit2Me must ensure NO trigger uses inside information. |
| **Art. 88** | Public disclosure of inside information | Inside information must be disclosed publicly and remain accessible for 5+ years. Relevant: if Bit2Me discovers a trigger inadvertently uses non-public data, must disclose and correct. |
| **Art. 89** | Prohibition of insider dealing | Using inside information to trade or enabling others to trade. Selective price alerts could facilitate this. Mitigation: simultaneous send rule. |
| **Art. 91** | Prohibition of market manipulation | Actions giving false or misleading signals about supply, demand, or price. Relevant: triggering notifications that could influence trading behavior in a coordinated way. |
| **Art. 92** | Prevention and detection of market abuse | CASPs must have "effective arrangements, systems, and procedures" to prevent and detect market abuse. The audit trail and quarterly review satisfy this. |

#### 9.4.3 Detection Patterns to Monitor

| Pattern | What to Look For | Detection Method | Response |
|---------|-----------------|------------------|----------|
| **Pre-announcement correlation** | Family B notification sent < 1 hour before a Bit2Me listing/delisting/partnership announcement | Compare notification_audit_log timestamps against internal announcement calendar | Investigate immediately. If correlation found, suspend trigger and conduct root cause analysis. |
| **Selective recipient patterns** | Family B notification reaching a subset of eligible users due to technical filtering, A/B testing, or segment targeting | Query notification_audit_log for send completeness: `sent_count / eligible_count` should be ~100% | Any send completeness < 95% requires investigation. A/B testing on Family B triggers is PROHIBITED. |
| **Data source integrity drift** | Trigger data source changes from public API to internal data without documentation | Quarterly review of trigger specifications vs. actual data queries | Re-certify data source; update trigger specification. |
| **Volume spike correlation** | Trading volume spike on Bit2Me within 30 minutes after a Family B notification send | Correlate notification_audit_log with trading volume data per asset | Expected (notifications drive trades). Flag only if volume spike is disproportionate or concentrated in few accounts. |

#### 9.4.4 ESMA Guidelines Reference

ESMA published Final Report on MiCA Guidelines for Prevention and Detection of Market Abuse in April 2025 (ESMA75-453128700-1408). Key requirements:
- CASPs must implement surveillance systems for order and transaction monitoring
- Suspicious Transaction and Order Reports (STORs) must be filed with national competent authorities
- Market abuse surveillance must cover ALL communication channels, including push notifications
- ESMA Guidelines on Supervisory Practices (July 2025, ESMA75-453128700-1039) provide additional supervisory expectations

**Action item:** Ensure the notification audit trail described in Rule 4 above is accessible to Bit2Me's compliance team for STOR preparation if needed.

---

### 9.5 Per-Trigger Compliance Checklist Template

Every trigger defined in the Master Trigger Table (Phase 3) must have a completed compliance checklist. This is a 7-section fill-in template that Diego reviews during Tier 1 template approval.

```
=================================================================
COMPLIANCE CHECKLIST -- Trigger: [trigger_id] [trigger_name]
=================================================================

SECTION 1: GDPR Lawful Basis
-----------------------------
[ ] Lawful basis identified: ____________________
    (Art. 6(1)(a) consent | Art. 6(1)(b) contract | Art. 6(1)(f) legitimate interest)
[ ] If Art. 6(1)(a): consent collection mechanism documented
[ ] If Art. 6(1)(f): legitimate interest assessment completed
[ ] Data minimization: only necessary personal data used in notification
[ ] Retention period defined for notification engagement data: ______ days

SECTION 2: ePrivacy Per-Channel Consent
-----------------------------------------
[ ] Channel(s) for this trigger: ____________________
[ ] Per-channel marketing consent verified:
    [ ] Push: consent_marketing_push = true (required for MARKETING/ADVISORY_RISK)
    [ ] Email: consent_marketing_email = true (required for MARKETING/ADVISORY_RISK)
    [ ] SMS: consent_marketing_sms = true (required for MARKETING/ADVISORY_RISK)
    [ ] In-App: consent_marketing_inapp = true (recommended for MARKETING)
[ ] If TRANSACTIONAL: channel consent not required (contractual basis)
[ ] Soft opt-in applicable? (existing customer, similar products, opt-out offered): Y/N

SECTION 3: MiCA Art. 66 -- Fair, Clear, Not Misleading
--------------------------------------------------------
[ ] Notification copy is fair (balanced presentation of risks and benefits)
[ ] Notification copy is clear (unambiguous language, no jargon without explanation)
[ ] Notification copy is not misleading (no exaggeration, no omission of material facts)
[ ] If MARKETING: notification is clearly identifiable as marketing communication
[ ] If MARKETING: MiCA mandatory disclaimer present (inline or linked):
    "This crypto-asset marketing communication has not been reviewed or approved
    by any competent authority in any Member State of the European Union."
[ ] Risk warning present (inline for email/in-app; linked for push):
    "Capital at risk. Not investment advice."
[ ] No prohibited keywords (Section 9.3.3 blocklist scan): PASS / FAIL
[ ] No flagged keywords without Diego review: PASS / FAIL / N/A

SECTION 4: MiCA Investment Advice Boundary
--------------------------------------------
[ ] Bright-line test applied (Section 9.3.1):
    [ ] States verifiable fact only? Y/N
    [ ] No action suggestion? Y/N
    [ ] No value judgment paired with fact? Y/N
    [ ] No artificial urgency around financial decision? Y/N
[ ] Classification result: INFORMATIONAL / MARKETING / ADVISORY_RISK
[ ] If ADVISORY_RISK: dedicated legal review completed by Diego: Y/N / N/A
[ ] Cross-sell triggers: uses product awareness framing only (no return comparisons)? Y/N / N/A

SECTION 5: MiCA Art. 87-92 Market Abuse (Family B Only)
---------------------------------------------------------
[ ] N/A (not a Family B trigger) -- skip this section
OR:
[ ] Data source is PUBLIC (documented): ____________________
[ ] Simultaneous send to all eligible users (no staggering): Y/N
[ ] No dependency on internal platform event calendar: Y/N
[ ] Audit trail logging configured (notification_audit_log): Y/N
[ ] Quarterly review scheduled: Y/N
[ ] A/B testing disabled for this trigger: Y/N

SECTION 6: CNMV / Spain-Specific
-----------------------------------
[ ] Campaign register entry created (internal tracking): Y/N
[ ] MiCA marketing rules applied (CNMV Circular 1/2022 repealed Dec 2024,
    MiCA now applies directly): Y/N
[ ] Monitoring CNMV digitalisation law developments: Y/N
[ ] If targeting >100K users in Spain: extra scrutiny applied
    (former Circular 1/2022 threshold, retained as internal best practice): Y/N / N/A

SECTION 7: Diego Approval Gate
--------------------------------
[ ] Compliance class: TRANSACTIONAL / INFORMATIONAL / MARKETING / ADVISORY_RISK
[ ] Diego review tier: NOT_REQUIRED / TIER_1 / TIER_2 / DEDICATED_LEGAL
[ ] Diego approval status: APPROVED / PENDING / REJECTED / NOT_REQUIRED
[ ] Approval date: ____________________
[ ] Approval record location (Lark/Notion link): ____________________
[ ] Template version approved: v____
[ ] Next re-review date (6-month maximum): ____________________

=================================================================
Checklist completed by: ____________________
Date: ____________________
=================================================================
```

---

### 9.6 Compliance by Trigger Family Summary

Summary table mapping each trigger family to its default compliance obligations. Use this as a quick reference -- the per-trigger compliance checklist (Section 9.5) provides the detailed audit trail.

| Family | Default Compliance Class | Diego Review Level | Risk Warning Required | MiCA Disclaimer Required | Market Abuse Protocol | Key Compliance Risk |
|--------|------------------------|-------------------|----------------------|------------------------|--------------------|-------------------|
| **A -- User Configured** | TRANSACTIONAL | NOT_REQUIRED | No | No | No | Low -- user-requested service. Risk only if editorial commentary added to alerts. |
| **B -- Market Triggered** | INFORMATIONAL | TEMPLATE_PRE_APPROVED (Tier 1) | Link to risk page | Yes (if proactive/unsolicited) | **YES -- full protocol (Section 9.4)** | HIGH -- market abuse risk (Art. 87-92). Data source must be public. Simultaneous send mandatory. Audit trail required. |
| **C -- Behavioral** | MARKETING | REQUIRED (Tier 1 + Tier 2) | Yes (inline or linked) | Yes | No | Medium -- requires explicit marketing consent per channel. Behavioral targeting must comply with GDPR data minimization. |
| **D -- Lifecycle** | MARKETING | REQUIRED (Tier 1 + Tier 2) | Yes (inline or linked) | Yes | No | Medium -- reactivation campaigns targeting dormant users risk scam-lookalike appearance. Warm-up schedule required for dormant segments. |
| **E -- Cross-sell** | MARKETING | REQUIRED (Tier 1 + Tier 2) | Yes (inline or linked) | Yes | No | HIGH -- investment advice boundary. V1 must use product awareness framing only. Return comparisons = ADVISORY_RISK (defer to V3). |
| **F -- Risk & Protective** | TRANSACTIONAL | NOT_REQUIRED | No (protective by nature) | No | No | Low -- these protect the user. Risk only if protective alerts are paired with commercial CTAs (e.g., "Your LTV is high -- deposit more via Bit2Me"). |

---

### 9.7 Cross-References

| Reference | Section | Relationship |
|-----------|---------|-------------|
| **Section 1 (Preference Center Architecture)** | Phase 1 | Consent categories (CAT-SEC through CAT-PRO) determine the GDPR lawful basis for each trigger. TRANSACTIONAL triggers use CAT-SEC/CAT-TXN (Art. 6(1)(b)). MARKETING triggers require CAT-MKT/CAT-PRD/CAT-PRO consent (Art. 6(1)(a)). |
| **Section 2 (Frequency Caps)** | Phase 1 | Campaign creation checklist step 8 = Diego approval gate. Priority tiers (P0-P5) align with compliance classes: P0-P1 = TRANSACTIONAL, P2 = INFORMATIONAL/MARKETING, P3-P5 = MARKETING. |
| **Section 3 (Suppression System)** | Phase 1 | Suppression segments (C8 whale, excluded users) apply regardless of compliance class. All compliance classes must pass suppression layers. |
| **Section 6 (Trigger Taxonomy)** | Phase 2 | Each trigger definition includes a `compliance_class` field that references this section. The taxonomy establishes the default class; this section defines what that class requires. |
| **Phase 3 (Master Trigger Table)** | Phase 3 | Every row in the Master Trigger Table includes a completed compliance checklist (Section 9.5). The table's compliance columns reference the classification system (Section 9.1), Diego workflow (Section 9.2), and keyword blocklist (Section 9.3.3). |
| **PITFALLS.md** | Research | Pitfalls 1-6 and 14 directly inform this compliance framework. The bright-line test (Section 9.3) operationalizes Pitfall 14. The keyword blocklist operationalizes Pitfall 3. The market abuse protocol operationalizes Pitfall 5. |
