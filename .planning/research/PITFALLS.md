# Pitfalls Research: Trigger-Based Notifications in Crypto/Fintech (EU/Spain)

**Domain:** Crypto exchange notification systems (Bit2Me — Spain/EU)
**Researched:** 2026-03-22
**Overall Confidence:** MEDIUM-HIGH (legal frameworks verified against primary sources; fatigue/deliverability data from industry benchmarks)

---

## Compliance Hard Constraints

These are not best practices. These are legal requirements with fines attached.

### Pitfall 1: Treating All Notifications as Equal Under GDPR

**What goes wrong:** Team sends price alerts, cross-sell pushes, and security warnings through the same consent bucket. A user opts out of "notifications" and stops receiving fraud alerts. Or worse: marketing messages are sent without explicit consent because "the user opted in to notifications."

**Why it happens:** GDPR distinguishes lawful bases, but most CRM teams think in terms of "opted in" or "opted out" as a single toggle.

**Legal requirement (HARD):**
- **Transactional/service notifications** (trade confirmations, security alerts, regulatory notices): Lawful basis = **Article 6(1)(b) GDPR** (contractual necessity) or **Article 6(1)(f)** (legitimate interest). No marketing consent needed. User cannot meaningfully opt out of these.
- **Marketing communications** (new listings, promotional offers, cross-sell, reactivation): Lawful basis = **Article 6(1)(a) GDPR** (explicit consent) + **ePrivacy Directive Article 13** (prior consent for electronic marketing). Consent must be freely given, specific, informed, and unambiguous (Article 7 GDPR).
- **User-configured alerts** (price alerts the user set up): Lawful basis = **Article 6(1)(b)** (contract performance — user requested the service). Not marketing.

**Prevention:**
1. Maintain separate consent flags per notification family: `consent_transactional` (implicit via TOS), `consent_marketing_push`, `consent_marketing_email`, `consent_marketing_sms`.
2. Never bundle marketing consent into service registration flow — it must be a separate, affirmative action.
3. Tag every notification template with its GDPR lawful basis in the CRM system (CleverTap custom property).
4. Rule: If a notification mentions a product the user does NOT already use, it is marketing. Period.

**Detection:** Audit quarterly — pull all notification templates, verify each has a lawful basis tag. Any untagged template = compliance gap.

**Confidence:** HIGH — verified against GDPR Articles 6, 7 and EDPB Guidelines 1/2024 on legitimate interest.

**Affected trigger families:** All, but especially Cross-sell and Market triggers.

---

### Pitfall 2: OS-Level Push Permission != Marketing Consent

**What goes wrong:** User enables push notifications on iOS/Android. Team assumes this is consent for marketing pushes. It is not.

**Legal requirement (HARD):**
The ePrivacy Directive classifies push notifications as "electronic mail" (confirmed by national implementations, e.g., Ireland S.I. 336/2011). The OS-level permission prompt (iOS/Android) is a technical gate, not a legal consent mechanism for direct marketing. A 2025 academic analysis in JIPITEC Vol. 16 No. 1 confirms this distinction.

**Prevention:**
1. After OS permission grant, show an in-app consent screen: "We'd like to send you [market updates / promotional offers / product news]. You can change this anytime in Settings."
2. Record this in-app consent separately from the OS permission state.
3. Without in-app marketing consent: only send transactional and user-configured notifications via push.

**Detection:** Compare push subscriber count vs. marketing consent count. If push_subscribers >> marketing_consented, you have a gap.

**Confidence:** HIGH — ePrivacy Directive Article 13; JIPITEC 2025 academic analysis; McCann FitzGerald legal analysis.

**Affected trigger families:** All marketing triggers sent via push channel.

---

### Pitfall 3: MiCA "Fair, Clear, Not Misleading" Violations in Notifications

**What goes wrong:** A push notification says "BTC is pumping! Don't miss out!" or "ETH Earn: up to 5% APY" without risk context. This violates MiCA Article 66.

**Legal requirement (HARD):**
- **MiCA Article 66(1):** CASPs must act honestly, fairly, and professionally in the best interests of clients.
- **MiCA Article 66(2):** All client-facing information, including marketing communications, must be "fair, clear and not misleading" and identifiable as marketing.
- **MiCA Article 66(3):** CASPs must warn clients of risks associated with crypto-asset transactions.
- **Sanctions:** Up to EUR 5 million or 10% of annual turnover. Personal liability for executives (ban from industry).

**Prevention — mandatory notification copy rules:**
1. Every marketing notification must include or link to a risk warning. For push (character-limited): use a standardized short disclaimer and link to full risk page. Example: "Capital at risk. Not investment advice. [link]"
2. Never use urgency language implying guaranteed returns: "pumping," "guaranteed," "risk-free," "don't miss out" are all prohibited.
3. APY/yield claims must state: (a) the rate is variable, (b) past performance is not indicative, (c) capital is at risk.
4. All promotional notifications must be clearly identifiable as marketing (not disguised as transactional).
5. Diego (legal gate) reviews ALL notification templates before deployment — this is not optional, it is the compliance control.

**Detection:** Keyword blocklist scan on all notification templates before send. Flag: "guaranteed," "risk-free," "pump," "moon," "don't miss," "last chance" (when applied to financial products).

**Confidence:** HIGH — MiCA Article 66 text verified via EUR-Lex and White & Case analysis.

**Affected trigger families:** Market triggers, Cross-sell triggers, Lifecycle reactivation triggers.

---

### Pitfall 4: CNMV Transition Gap — Assuming No Spanish Rules Apply

**What goes wrong:** Team reads that CNMV Circular 1/2022 was repealed (December 28, 2024 via Circular 1/2024) and concludes "no more Spanish advertising rules." Wrong — MiCA rules now apply directly, and the CNMV retains supervisory authority.

**Legal requirement (HARD):**
- CNMV Circular 1/2022 (prior notification for mass campaigns >100K people) is **repealed**.
- MiCA marketing rules now apply directly in Spain.
- The draft "Ley de digitalización del sector financiero" may reintroduce CNMV administrative control over crypto advertising.
- CNMV retains authority to sanction non-compliant campaigns under MiCA.
- All CASPs in Spain must have full MiCA authorization by **July 1, 2026** (maximum transition deadline).

**Prevention:**
1. Do NOT remove disclaimers that were required under Circular 1/2022 — most align with MiCA anyway.
2. Monitor CNMV announcements for the digitalización law (may add new requirements).
3. Maintain an internal register of all advertising campaigns (was required under Circular 1/2022; remains good practice and may be re-required).

**Detection:** Calendar reminder to check CNMV regulatory updates quarterly.

**Confidence:** HIGH — verified via Baker McKenzie analysis and CNMV official publications.

**Affected trigger families:** All marketing triggers targeting Spain (primary market).

---

### Pitfall 5: MiCA Market Abuse — Price Notifications as Insider Signaling

**What goes wrong:** The platform sends price movement notifications to a subset of users before or during significant market events. Even if unintentional, selective timing of price alerts could be construed as facilitating insider dealing (MiCA Article 89) or market manipulation (Article 91).

**Legal requirement (HARD):**
- **MiCA Article 87:** Inside information = non-public, precise information that could significantly influence crypto-asset prices.
- **MiCA Article 88:** Inside information must be disclosed publicly and remain accessible for 5+ years.
- **MiCA Article 89:** Prohibition of insider dealing — using inside information for trading.
- **MiCA Article 91:** Market manipulation — actions giving false/misleading signals or securing prices at abnormal levels.
- **MiCA Article 92(1):** CASPs must have "effective arrangements, systems, and procedures to prevent and detect market abuse."

**Prevention:**
1. Price alerts must be based ONLY on publicly available market data (exchange price feeds, not internal order book data).
2. Never send price alerts timed to internal platform events (new listing announcements, liquidity changes) before public disclosure.
3. All price alert triggers must fire simultaneously for all eligible users — no staggered sends based on user tier/balance that could create information asymmetry.
4. Document the data source for every market trigger (CoinGecko API, public exchange feeds) in the trigger specification.
5. Maintain audit logs of all market-triggered notifications with timestamps — required under Article 92.

**Detection:** Compare notification send timestamps against platform announcements. Any notification sent <1 hour before a listing/delisting announcement is a red flag.

**Confidence:** HIGH — MiCA Title VI (Articles 86-92) verified via EUR-Lex, Cambridge Core academic analysis, and ESMA Final Report on market abuse guidelines (April 2025).

**Affected trigger families:** Market triggers (price alerts, volatility alerts, volume spikes).

---

### Pitfall 6: ePrivacy Consent Per Channel — Not a Single Opt-In

**What goes wrong:** User consents to email marketing. Team assumes this covers push and SMS too. It does not.

**Legal requirement (HARD):**
- ePrivacy Directive Article 13 requires consent for each electronic communication channel separately.
- GDPR Article 7 requires consent to be specific (not bundled).
- "Soft opt-in" (existing customer exception) applies only when: (a) contact details were obtained in the context of a sale, (b) marketing is for similar products/services, (c) customer was given the opportunity to object at collection time, and (d) customer can opt out at any time. This is channel-specific.

**Prevention:**
1. Collect and store consent per channel: `marketing_email_consent`, `marketing_push_consent`, `marketing_sms_consent`, `marketing_inapp_consent`.
2. In-app messages are the grey area — they are generally considered part of the app experience (not electronic mail), but promotional in-app messages promoting products the user doesn't use should still have a consent basis.
3. In CleverTap: use subscription groups per channel, not a single "marketing opt-in" flag.

**Detection:** Query CleverTap/BigQuery for users receiving marketing on channels where they lack channel-specific consent.

**Confidence:** HIGH — ePrivacy Directive Article 13, GDPR Article 7.

**Affected trigger families:** All marketing triggers across all channels.

---

## Push Fatigue Patterns

### Pitfall 7: Exceeding the Fatigue Threshold — The 2-5/Week Cliff

**What goes wrong:** In the excitement of launching trigger-based notifications, multiple trigger families fire simultaneously. A user gets a price alert, a cross-sell push, and a lifecycle nudge on the same day. Within a week, they've received 6+ pushes. 46% of users opt out at 2-5 messages/week. At 6-10/week, 32% opt out. These are industry-wide numbers. For crypto (where users are more skeptical of spam), the threshold is likely lower.

**Consequences:**
- Push opt-out is **permanent** on iOS — user must manually re-enable in Settings (virtually never happens).
- Android auto-unsubscribes inactive tokens after 270 days (FCM policy, enforced since May 2024).
- Chrome Safety Check (late 2025) auto-unsubscribes users from sites with high volume + low engagement.
- Once push permissions are lost, the highest-converting channel is gone. Email and in-app cannot compensate.

**Prevention — Anti-Fatigue Formula:**
```
Daily hard cap: 2 notifications/user/day (across ALL trigger families)
Weekly soft cap: 5 notifications/user/week
Monthly ceiling: 15 notifications/user/month

Priority tiers (when cap is hit, lower tiers are suppressed):
  P0: Security/transactional (never suppressed)
  P1: User-configured alerts (user asked for these)
  P2: Lifecycle critical (at-risk, pre-dormancy)
  P3: Market triggers (price alerts not user-configured)
  P4: Cross-sell / promotional
  P5: Re-engagement / generic

Cooldown between notifications: minimum 4 hours (same channel)
Cooldown after dismissed notification: 24 hours (same trigger family)
```

**Detection — Fatigue Risk Score:**
```
fatigue_risk = (notifications_sent_7d / 5) * 0.4
            + (notifications_dismissed_7d / notifications_sent_7d) * 0.3
            + (days_since_last_open / 7) * 0.3

If fatigue_risk > 0.7: suppress all P3+ notifications for 48 hours
If fatigue_risk > 0.9: suppress all P2+ notifications for 7 days
```

**Confidence:** MEDIUM-HIGH — industry benchmarks from Pushwoosh 2025, MoEngage, Retenshun; fintech-specific thresholds are estimated based on finance app opt-in rates (72.3% average).

**Affected trigger families:** All, but especially when Market + Cross-sell + Lifecycle fire on same user.

---

### Pitfall 8: Notification Timing — The Sleep Hours Killer

**What goes wrong:** 23% of apps send notifications during 11 PM - 7 AM. This is the #1 cited reason for opt-out in user surveys. For crypto (24/7 markets), the temptation to send at any hour is strong.

**Prevention:**
1. Enforce quiet hours: no push between 22:00 - 08:00 user local time (use device timezone from CleverTap).
2. Exception: P0 security alerts only (login from new device, large withdrawal).
3. Queue notifications that would fire during quiet hours and send at 08:00-09:00 with context: "While you were away: BTC crossed $X."
4. User-configured price alerts: let user explicitly opt into 24/7 delivery in notification preferences.

**Detection:** Monitor send-time distribution. If >5% of pushes fire during quiet hours, investigate.

**Confidence:** HIGH — Pushwoosh 2025 benchmarks, multiple industry sources.

---

### Pitfall 9: The "Relevant to Me" Decay

**What goes wrong:** Notifications start relevant (user holds BTC, gets BTC alerts). Over time, the user sells BTC but still gets BTC alerts because the trigger is based on "ever held" not "currently holds." Relevance decays, fatigue increases, opt-out follows.

**Prevention:**
1. All asset-specific triggers must check **current portfolio state**, not historical.
2. Recalculate eligibility at send time, not at trigger creation time.
3. For market triggers: only fire for assets the user currently holds OR has on a watchlist.
4. For cross-sell triggers: check product eligibility (not all assets are available in Pro, Earn, etc.) — use the asset eligibility matrix from the playbook.

**Detection:** Track click-through rate by trigger over time. If CTR for a trigger family drops >50% over 30 days, the relevance model is stale.

**Confidence:** MEDIUM — based on general CRM best practices applied to crypto context.

---

## Deliverability Risks

### Pitfall 10: Email Reputation Destruction — Crypto's Spam Penalty

**What goes wrong:** Crypto/fintech emails are pre-penalized by spam filters because the domain includes trigger words ("crypto," "invest," "earn," "money"). Combined with a large dormant user base (72.4K with balance at Bit2Me), sending reactivation emails to long-inactive addresses hits spam traps and destroys sender reputation.

**Consequences:**
- One spam trap hit can cut deliverability by 50%.
- Gmail classifies sender reputation as High/Medium/Low/Bad — dropping from High to Low takes weeks to recover from.
- Global average inbox placement is 84% (2025). Crypto senders typically perform worse.

**Prevention:**
1. **Authentication (non-negotiable):** SPF + DKIM + DMARC (at minimum p=none, target p=reject). Verify quarterly.
2. **List hygiene:** Sunset policy — suppress email to users with zero opens in 90 days. Re-engagement campaign before sunset (30-day window).
3. **Spam complaint rate:** Must stay below 0.1% (Google/Yahoo 2024 requirement for bulk senders). Monitor via Google Postmaster Tools.
4. **Warm-up for new campaigns:** When launching trigger-based emails to dormant segments, start with most-engaged subset (opened email in last 30 days), expand 20-30% weekly.
5. **Never send to the full 72.4K dormant-with-balance segment at once.** Segment by last-active-date and warm up over 4 weeks.
6. **Bounce rate:** Must stay below 1.5%. Hard bounces should be suppressed immediately and permanently.
7. **Separate subdomains:** Use `notifications.bit2me.com` for transactional, `marketing.bit2me.com` for promotional. This isolates reputation damage.

**Detection:** Monitor via Google Postmaster Tools (domain reputation), CleverTap delivery reports, and bounce/complaint rates weekly.

**Confidence:** HIGH — Gmail/Yahoo 2024 sender requirements verified; Validity 2025 deliverability benchmark report.

**Affected trigger families:** All email-channel triggers, especially Lifecycle reactivation targeting dormant users.

---

### Pitfall 11: Push Token Decay — The Invisible Audience Shrink

**What goes wrong:** Team reports 100K push subscribers. Actual deliverable audience is 60K because 40% of tokens are stale (app uninstalled, device changed, OS upgraded). Delivery metrics look fine (sent = 100K) but actual reach is 60% and declining.

**Key data:**
- Android FCM: tokens inactive >270 days are rejected (policy since May 2024).
- Android FCM: tokens inactive >30 days signal dormant device.
- iOS APNs: tokens invalidated on uninstall, OS upgrade, device restore.
- Chrome Safety Check (2025-2026): auto-unsubscribes users from high-volume/low-engagement push senders.

**Prevention:**
1. Implement token validation on every send attempt — log failed deliveries and remove invalid tokens.
2. Track "deliverable push audience" as a distinct metric from "push subscribers."
3. Monthly token hygiene: query tokens with 0 deliveries in 60 days, move to suppressed.
4. Re-permission campaigns: for users with valid tokens but 0 opens in 90 days, send a "Still want to hear from us?" in-app message before continuing pushes.

**Detection:** Track `deliverable_push_rate = successful_deliveries / total_sends`. If <70%, token hygiene is overdue.

**Confidence:** HIGH — FCM documentation, Braze push registration docs, Firebase iOS SDK.

---

## Trust and Permission Destruction Patterns

### Pitfall 12: The Scam-Lookalike Problem

**What goes wrong:** Crypto users are hyper-vigilant about scams. A legitimate notification that says "You have unclaimed rewards — tap to claim" or "Your account requires verification" looks identical to phishing. Users report as spam, block, or lose trust.

**Prevention:**
1. Never use urgency + action patterns that mimic phishing: "verify now," "claim before it expires," "your account will be locked."
2. Always identify the notification as from Bit2Me with consistent branding.
3. Never include links in push notifications that go to login pages. Instead: "Open the Bit2Me app to see your [X]."
4. For email: use the authenticated sending domain with BIMI (Brand Indicators for Message Identification) so the Bit2Me logo appears in inbox.
5. Template review: for every notification, ask "Could a scammer send this exact message?" If yes, redesign.

**Detection:** Monitor spam complaint rates per notification template. Any template with >0.05% complaint rate needs immediate review.

**Confidence:** MEDIUM — based on crypto industry scam patterns and anti-phishing best practices.

---

### Pitfall 13: Dark Pattern Consent — Winning Opt-Ins You'll Lose

**What goes wrong:** To hit opt-in KPIs, team uses dark patterns: pre-checked consent boxes, consent buried in TOS, "Accept all" with no granular options. Short-term: opt-in rate looks great. Medium-term: GDPR violation (consent not freely given). Long-term: users who didn't meaningfully consent have 3-5x higher opt-out rates, destroying deliverability.

**Legal requirement (HARD):**
- GDPR Article 7(2): Consent request must be "clearly distinguishable from other matters, in an intelligible and easily accessible form, using clear and plain language."
- GDPR Article 7(4): Consent is not freely given if bundled with service acceptance.
- GDPR Recital 42: Consent is not valid if the data subject has no genuine free choice.

**Prevention:**
1. Notification preferences screen with individual toggles per category (price alerts, security, promotions, product updates).
2. No pre-checked boxes. Default = off for marketing categories.
3. Explain what each category includes before asking for consent.
4. Make the "Skip" or "No thanks" option equally prominent as "Enable."
5. Measure "quality opt-in rate" (users who remain opted in after 30 days) not just "opt-in rate."

**Detection:** Track 30-day opt-in retention rate. If <80% of users who opt in remain opted in after 30 days, the consent flow is coercive.

**Confidence:** HIGH — GDPR Articles 7, Recital 42.

---

### Pitfall 14: The "Investment Advice" Line — Informational vs. Advisory

**What goes wrong:** A notification says "BTC is down 15% — good time to buy?" or "ETH staking yields are higher than savings accounts." This crosses from informational to investment advice, which requires MiFID II authorization (for financial instruments) or MiCA-compliant advisory services.

**Legal requirement (HARD):**
- **MiCA Article 66:** All information must be fair, clear, not misleading, and in the best interest of clients.
- **MiCA Title V, Chapter 2:** Providing advice on crypto-assets is a regulated service requiring specific authorization.
- Notifications that suggest action ("buy now," "good time to," "you should consider") = advisory.
- Notifications that state facts ("BTC is at $X," "Your portfolio changed by Y%") = informational.

**The bright line test:**
| Safe (Informational) | Dangerous (Advisory) |
|---|---|
| "BTC crossed $70,000" | "BTC is at $70,000 — great entry point" |
| "Your BTC holding is up 12% this week" | "Your portfolio could grow faster with Earn" |
| "ETH Earn APY is currently 3.2%" | "ETH Earn beats savings accounts" |
| "New asset available: SOL" | "SOL is trending — start trading now" |
| "You haven't traded in 30 days" | "You're missing out on market opportunities" |

**Prevention:**
1. Every notification template must pass the "bright line test" before Diego approval.
2. Keyword blocklist for notification copy: "should," "opportunity," "don't miss," "good time to," "beats," "outperforms," "recommended."
3. Price alerts: state the fact only. Never pair with a CTA that implies a trading action.
4. Cross-sell triggers: describe the product, never compare to non-crypto alternatives (savings accounts, bonds).
5. Include standard disclaimer in or linked from every market notification: "This is not investment advice. Capital at risk."

**Detection:** Automated copy scan against keyword blocklist before send. Manual Diego review for all new templates.

**Confidence:** HIGH — MiCA Article 66, Title V Chapter 2; MiFID II advisory service definitions.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: "Blast and Pray" Reactivation

**What it looks like:** Send the same reactivation push to all 72.4K dormant users simultaneously.
**Why it destroys value:** Hits invalid tokens (deliverability damage), hits disengaged users (spam complaints), no personalization (low conversion).
**Instead:** Segment by dormancy duration. Warm up by engagement recency. Personalize by held assets. Stagger sends over 4 weeks.

### Anti-Pattern 2: Notification Copy-Paste Across Channels

**What it looks like:** Same message text for push, email, and in-app.
**Why it destroys value:** Push has 40-60 character sweet spot. Email needs full context + unsubscribe link. In-app can be richer. Same text = suboptimal on all channels.
**Instead:** Write channel-native copy. Push = headline only. Email = context + CTA + disclaimer. In-app = visual + action.

### Anti-Pattern 3: Volume = Engagement

**What it looks like:** "We need to increase notifications to increase engagement." Team doubles notification frequency.
**Why it destroys value:** 46% of users opt out at 2-5 pushes/week. More volume = fewer permissions = less reach = less engagement. The curve inverts.
**Instead:** Increase relevance, not volume. Personalized notifications convert 202% more than mass messages. One perfectly-timed, relevant notification > five generic ones.

### Anti-Pattern 4: Ignoring Dismissed Notification Signals

**What it looks like:** User dismisses 5 consecutive push notifications. System keeps sending at the same rate.
**Why it destroys value:** Dismissed = "I saw this and chose not to engage." Continuing to send at the same rate signals you don't respect the user's attention. Next step is opt-out.
**Instead:** After 3 consecutive dismissals of the same trigger family, apply a 7-day cooldown for that family. After 5 consecutive dismissals across all families, reduce to P0-P1 only for 14 days.

### Anti-Pattern 5: Testing in Production Without Holdout Groups

**What it looks like:** Launch 30 triggers simultaneously with no control group.
**Why it destroys value:** Cannot measure incremental lift. Cannot isolate which triggers help vs. hurt. Cannot detect if notifications are causing opt-outs faster than conversions.
**Instead:** Always maintain a 10% holdout (no notifications except P0 transactional). Measure incrementality per trigger family weekly.

---

## Phase-Specific Warnings

| Phase/Trigger Family | Likely Pitfall | Mitigation |
|---|---|---|
| MVP (first 30 days) | Launching too many triggers at once, overwhelming users | Start with 5 triggers max. Add 2-3 per sprint after measuring. |
| Market Triggers | Price alerts construed as investment advice | Bright line test + Diego review on every template |
| Market Triggers | Selective timing = insider signaling risk | Public data sources only; simultaneous send to all eligible |
| Cross-sell Triggers | Marketing without consent (push channel) | Verify per-channel marketing consent before send |
| Lifecycle Triggers | Reactivation emails to dormant = spam traps | Warm-up schedule; 90-day sunset policy; engaged-first rollout |
| User-Configured Alerts | Over-delivery when market is volatile (10+ alerts/hour) | Per-alert cooldown: 1 alert per asset per 4 hours minimum |
| Risk/Security Triggers | Scam-lookalike notifications | No login links; no "verify now" language; app-open CTAs only |
| All Triggers (Spain) | CNMV regulatory changes mid-project | Quarterly CNMV review; maintain campaign register |
| All Triggers (EU) | MiCA full enforcement July 2026 | Ensure all templates compliant before June 2026 deadline |

---

## Sources

### Legal / Regulatory (HIGH confidence)
- [MiCA Regulation Full Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32023R1114) — Articles 66, 86-92
- [MiCA Article 66 Reference](https://www.mica.wtf/mica/title-v-authorisation-and-operating-conditions-for-crypto-asset-service-providers-art.-59-85/chapter-2/article-66)
- [White & Case — MiCA Regulatory Framework](https://www.whitecase.com/insight-alert/mica-regulation-new-regulatory-framework-crypto-assets-issuers-and-crypto-asset) — Article 66 analysis
- [ESMA Final Report on MiCA Market Abuse Guidelines (April 2025)](https://www.esma.europa.eu/sites/default/files/2025-04/ESMA75-453128700-1408_Final_Report_MiCA_Guidelines_on_prevention_and_detection_of_market_abuse.pdf)
- [ESMA MiCA Guidelines on Market Abuse Supervision (July 2025)](https://www.esma.europa.eu/sites/default/files/2025-07/ESMA75-453128700-1039_Guidelines_on_supervisory_practices_to_prevent_and_detect_market_abuse__MiCA_.pdf)
- [Cambridge Core — Crypto-Asset Market Abuse Under EU MiCA](https://www.cambridge.org/core/product/FDC11EC096728B9EF1097A5346F0EF27/core-reader)
- [CNMV Circular 1/2022 (repealed)](https://cnmv.es/DocPortal/Legislacion/Circulares/Circular_1_2022_EN.pdf)
- [Baker McKenzie — Spain Crypto Advertising Flexibility](https://blockchain.bakermckenzie.com/2025/01/22/spain-crypto-exchanges-welcome-more-flexibility-on-spanish-crypto-asset-advertising-rules/)
- [TrustCloud — CNMV Adapts MiCA for Crypto Advertising](https://trustcloud.tech/blog/cnmv-adapts-mica-changes-cryptocurrency-advertising-regulation-spain/)
- [GDPR Article 6 — Lawfulness of Processing](https://gdpr-info.eu/art-6-gdpr/)
- [EDPB Guidelines 1/2024 on Legitimate Interest](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf)
- [ICO — Legitimate Interests Basis](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/legitimate-interests/what-is-the-legitimate-interests-basis/)

### ePrivacy & Push Consent (HIGH confidence)
- [JIPITEC 2025 — Push Notifications under ePrivacy Law](https://www.jipitec.eu/jipitec/article/view/423) — Academic analysis of push as electronic mail
- [McCann FitzGerald — Mobile Push as Direct Marketing](https://www.mccannfitzgerald.com/knowledge/data-privacy-and-cyber-risk/mobile-app-push-notifications-the-next-frontier-in-direct-marketing)
- [Lexology — Push Notifications Frontier in Direct Marketing](https://www.lexology.com/library/detail.aspx?g=271fdffd-2879-4bf0-bfcf-a532d974b7ec)

### Push Fatigue & Benchmarks (MEDIUM-HIGH confidence)
- [Pushwoosh 2025 — Push Notification Benchmarks](https://www.pushwoosh.com/blog/push-notification-benchmarks/)
- [Retenshun — Push Notification Frequency Sweet Spot](https://retenshun.com/blog/push-notification-frequency-sweet-spot)
- [Business of Apps — Push Notification Statistics 2025](https://www.businessofapps.com/marketplace/push-notifications/research/push-notifications-statistics/)
- [MoEngage — Push Notification Metrics](https://www.moengage.com/blog/push-notification-metrics/)

### Deliverability (MEDIUM-HIGH confidence)
- [Pushwoosh 2025 — Email Deliverability and Spam Avoidance](https://www.pushwoosh.com/blog/email-deliverability-spam-avoidance-tips/)
- [Mailmunch — Email Deliverability 2026 Guide](https://www.mailmunch.com/blog/mastering-email-deliverability)
- [1827 Marketing — Email Deliverability 2025](https://1827marketing.com/smart-thinking/email-deliverability-in-2025-new-rules-higher-standards-and-what-b2b-marketers-should-do/)

### Push Token Lifecycle (HIGH confidence)
- [Braze — Push Registration Documentation](https://www.braze.com/docs/user_guide/message_building_by_channel/push/push_registration)
- [Batch — FCM API Updates Affecting Android Push](https://batch.com/blog/posts/android-push-updates-fcm-api)
- [OneSignal — FCM Expired Token FAQ](https://documentation.onesignal.com/docs/en/fcm-expired-token-faq)
