# PBW 2026 — Landing Page Brief for Dev / Design Handoff

**From:** Daniel Ferraro, Head of Growth
**To:** Dev team + Design team
**Date:** 2026-03-29
**Event:** Paris Blockchain Week, April 15-16, Carrousel du Louvre, Paris
**Deadline:** Page structure ready March 31 — Diego-approved copy drops in April 1 — PAGE LIVE by April 1

---

## Overview

This brief covers everything needed to build `bit2me.com/pbw` from scratch, without waiting for Diego's legal approval. The page structure, form integration, UTM wiring, and CleverTap event spec can all be built before April 1. The approved copy drops in April 1 and replaces the placeholder text — no architectural changes required after Diego approval.

**Do not link paid ads, QR codes, or emails to the homepage or standard sign-up page.** This dedicated URL is the single destination for every asset produced for PBW.

---

## Section 1: URL and Hosting

| Parameter | Value |
|-----------|-------|
| Target URL | bit2me.com/pbw (primary) — if /pbw is taken: bit2me.com/paris |
| Platform | Existing Bit2Me web infrastructure — no new deployment pipeline |
| Mobile-first | QR code scans happen on phones. Page MUST work on 375px viewport with poor venue Wi-Fi |
| Login wall | Page must NOT require login to view or submit the form |
| Page weight | Total page under 2MB (ideally under 1MB). No heavy JS on form submit. |
| Hard deadline | Page structure ready: March 31. Approved copy drops in: April 1. Page LIVE: April 1 |

**Open question for Dev:** Is `/pbw` URL available on the current Bit2Me domain? If not, confirm `/paris` is available before March 29. Let Daniel know immediately — all UTMs, QR codes, and email links depend on the confirmed URL.

---

## Section 2: Page Architecture — 5 Sections (Locked)

Build all 5 sections now. Placeholder text marked `[APPROVED COPY DROPS IN APR 1: "..."]` is replaced with Diego-approved copy on April 1. Do NOT delay building because of placeholder text — the layout and structure are final today.

### Section 2.1 — Hero

**Purpose:** First thing the visitor sees on mobile. Single message, single action.

**Elements to build:**
- Headline: `[APPROVED COPY DROPS IN APR 1: "Trade Free for 60 Days. Europe's Most Trusted Exchange."]`
- Sub-headline: `[APPROVED COPY DROPS IN APR 1: "Open your Bit2Me account at Paris Blockchain Week and pay zero trading fees for 60 days. MiCA-authorized. Backed by Bankinter, BBVA, and Tether."]`
- Event badge visual: "Paris Blockchain Week 2026 — April 15-16, Carrousel du Louvre, Paris" (static badge, can use Bit2Me brand colors)
- Countdown timer: Days/hours/minutes countdown to April 15, 2026 (static JS countdown component)
- CTA button (primary): `[APPROVED COPY DROPS IN APR 1: "Claim Your 60 Free Days"]` — button links to the form section below (anchor link #form or inline form on hero)

**Mobile requirement:** Hero headline and CTA button must both be visible above the fold on 375px width without scrolling.

---

### Section 2.2 — Offer Block

**Purpose:** Plain-language terms. What users actually get.

**Elements to build:**
- Offer headline: `[APPROVED COPY DROPS IN APR 1]`
- Offer body: `[APPROVED COPY DROPS IN APR 1: "Register via this page between April 1-30, 2026. Your account pays zero trading fees on all spot trades for 60 calendar days from registration. No promo code needed — it's automatic."]`
- Eligibility summary (plain text list):
  - 60 calendar days from account creation date
  - Registration window: April 1 to April 30, 2026
  - Eligible: all spot trades
  - No promo code required — automatic
  - Not eligible: OTC trades, institutional API trades, non-spot products

---

### Section 2.3 — Three Differentiators

**Purpose:** Institutional-grade trust signals. No competitor at PBW can claim all three.

Build as 3 icon + headline + one-line text blocks:

1. **Spain's First MiCA-Authorized Exchange**
   - `[APPROVED COPY DROPS IN APR 1: "CNMV-regulated since [CNMV authorization date — Diego to confirm]"]`
   - Note for Design: Use CNMV logo or official seal if available

2. **Backed by Spain's Leading Banks**
   - Body: "Bankinter, BBVA, Cecabank, and Tether are investors in Bit2Me"
   - Design: Bank logos row (Bankinter + BBVA + Cecabank + Tether logos) — confirm logo usage rights with Diego
   - Note: Bank logo row on a white/light background is an institutional conversation-stopper for PBW audience

3. **Trusted by Europol and Interpol**
   - Body: `[APPROVED COPY DROPS IN APR 1: "We handle seized crypto for Europol and Interpol. Compliance is the product."]`

---

### Section 2.4 — Social Proof

**Purpose:** Press validation row. Establishes credibility without claims.

**Elements to build:**
- Section header: "As seen in" (or "Coverage" — simple, no claims)
- Press logo row (horizontal, single row): CoinDesk, Chainwire, Bankinter (for the January 2026 investment announcement)
- Format: Greyscale logos on white or light background — consistent treatment
- Do NOT include captions or quotes — logos only

---

### Section 2.5 — CTA Repeat + Legal Footer

**Purpose:** Second conversion opportunity for users who scrolled. Mandatory legal footer.

**Elements to build:**
- CTA button (repeat, identical to hero): `[APPROVED COPY DROPS IN APR 1: "Claim Your 60 Free Days"]` — links to the same form
- Secondary CTA (bottom): `[APPROVED COPY DROPS IN APR 1: "Start Trading Free"]`
- Legal footer (mandatory, below both CTAs):

```
[APPROVED COPY DROPS IN APR 1 — PASTE VERBATIM FROM DIEGO PACKAGE SECTION 8:]

Crypto-assets are highly volatile and unregulated in most EU countries. No consumer protection.
Tax on profits may apply. Bit2Me is authorized as a Crypto-Asset Service Provider (CASP) under
MiCA Regulation (EU) 2023/1114 by Spain's Comisión Nacional del Mercado de Valores (CNMV).
Trading crypto-assets involves risk of loss. Past performance is not indicative of future results.
```

**Design note:** Legal footer must be legible (minimum 12px, not greyed out to invisibility). It is a MiCA requirement.

---

## Section 3: Form Specification

The lead capture form is the most critical element. Build it correctly — every QR scan, ad click, and email click ends here.

### Form Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Name | Text input | Yes | Placeholder: "Your name" |
| Email | Email input | Yes | Placeholder: "your@email.com" — validate email format inline |
| GDPR opt-in | Checkbox | Yes — must be checked before submit | See GDPR section below |

**2 fields maximum (Name + Email).** Do NOT add phone number. Do NOT add country dropdown. Do NOT add any optional fields. Form length is a direct conversion kill — every field added reduces conversion rate.

### Form Behavior

| Behavior | Specification |
|----------|--------------|
| Submit action | POST to CleverTap via existing Bit2Me integration (Katy to confirm endpoint — see Section 5) |
| On successful submit | Fire `pbw_lead` CleverTap event — see Section 5 for full event spec |
| Tag to apply | Add tag `pbw_2026_lead` to user profile in CleverTap |
| Post-submit redirect | Standard Bit2Me registration flow — UTM params must be preserved in the redirect URL |
| Error handling | Inline validation (red border + error message under the field). Do NOT reload the page on error. |
| Duplicate email | If email already exists in Bit2Me: redirect to login with a message "Welcome back — your offer is applied automatically" |
| Loading state | CTA button changes to "Processing..." on click — prevents double-submit |

### GDPR Checkbox

- Label: "I agree to receive Bit2Me marketing communications about this offer and related promotions. I can unsubscribe at any time."
- Pre-checked: NO. User must actively check the box.
- Validation: If user tries to submit without checking, show inline error: "Please confirm you accept to receive marketing communications."
- Store as: `gdpr_consent: true` in CleverTap event property (see Section 5)
- Legal: This is mandatory for EU GDPR compliance. Do not remove or pre-check.

---

## Section 4: UTM Tagging Table

Every traffic source that lands on bit2me.com/pbw needs a distinct UTM string. These UTMs are appended to the links pointing TO this page — the page itself does not generate them. All UTMs must be pre-wired before the page goes live.

**Owner:** Alvaro validates the UTM taxonomy. Daniel creates QR codes. Dev pre-wires UTMs in links where applicable.

| Source | UTM String to append to bit2me.com/pbw |
|--------|----------------------------------------|
| X/Twitter paid ads | `?utm_source=twitter&utm_medium=paid&utm_campaign=pbw2026` |
| Google paid ads | `?utm_source=google&utm_medium=paid&utm_campaign=pbw2026` |
| QR code (booth signage) | `?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite` |
| Email #1 (warmup) | `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup` |
| LinkedIn organic | `?utm_source=linkedin&utm_medium=organic&utm_campaign=pbw2026_b2b` |
| QR code (lanyards) | `?utm_source=booth&utm_medium=lanyard&utm_campaign=pbw2026_onsite` |

**Full URL example for QR booth:** `https://bit2me.com/pbw?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite`

**Important for Dev:** When the form fires the `pbw_lead` CleverTap event, the `utm_source` and `utm_campaign` values from the landing URL must be extracted and passed as event properties. This enables Alvaro to attribute each lead back to its source in BigQuery.

---

## Section 5: CleverTap Integration Spec (for Katy)

Katy owns the CleverTap side. This section specifies what fires on form submit.

### Event Specification

| Parameter | Value |
|-----------|-------|
| Event name | `pbw_lead` |
| Trigger | Successful form submit (after inline validation passes, before redirect) |
| Profile tag | Add `pbw_2026_lead` tag to user profile — permanent, never remove |

### Event Properties (5 properties, all required)

| Property | Source | Type | Notes |
|----------|--------|------|-------|
| `source` | utm_source value from URL | String | e.g., "twitter", "booth", "email" — "direct" if no UTM |
| `campaign` | utm_campaign value from URL | String | e.g., "pbw2026", "pbw2026_onsite" — "direct" if no UTM |
| `name` | Form name field | String | Submitted by user |
| `email` | Form email field | String | Submitted by user |
| `gdpr_consent` | GDPR checkbox | Boolean | `true` if checked (required for submit), `false` otherwise |

### Journey Trigger (Katy action required)

On `pbw_lead` event fire: Enroll user in the **PBW B2C Journey** in CleverTap.

**Critical: This journey must be pre-built by Katy before April 1.** If the journey is not built before the page goes live, every lead that submits the form enters a dead end — no follow-up email fires. This is the single most important dependency for post-event conversion.

### Verification (April 1 test protocol)

Before declaring the page live:
1. Submit a test form with a Bit2Me internal email address
2. Check CleverTap real-time activity stream for the `pbw_lead` event
3. Confirm all 5 properties are present on the event
4. Confirm `pbw_2026_lead` tag appears on the test profile
5. Confirm the PBW B2C Journey enrolled the test user

**Not live until all 5 checks pass.**

---

## Section 6: QR Code Specification

The booth QR code and the lanyard QR code are the primary on-site lead capture mechanisms. They must be ready before April 14 (shipped with booth materials by April 8).

| Parameter | Value |
|-----------|-------|
| Generator tool | Bitly or UTM.io (branded short link preferred) |
| Target URL | `https://bit2me.com/pbw?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite` |
| Format | SVG preferred (scales without pixelation) — PNG backup at 2000x2000px minimum |
| Scalability test | QR must be scannable at minimum A4 print size and maximum A1 banner size |
| Error correction | Level H (30% error correction — handles partial damage on physical prints) |
| Owner | Daniel creates the Bitly/UTM.io link — Alvaro validates UTM string before creation |
| Deliverable | QR file sent to Design by March 31 for inclusion in booth materials |

**Note for Design:** The lanyard QR uses a different UTM (`utm_medium=lanyard`) but the same base URL. Generate two separate QR codes — one for booth signage, one for lanyards.

---

## Section 7: Handoff Checklist

Track each item. Nothing is "done" until the line is checked.

- [ ] Brief sent to dev/design (March 29)
- [ ] Dev confirms `/pbw` URL availability (March 29)
- [ ] Katy confirms CleverTap endpoint and `pbw_lead` event tag setup (March 30)
- [ ] Alvaro confirms UTM taxonomy is finalized — no improvised UTMs after this (March 30)
- [ ] Design mock ready for Daniel review (March 31)
- [ ] Diego-approved copy received (April 1)
- [ ] Copy dropped into page — all `[APPROVED COPY DROPS IN APR 1]` placeholders replaced (April 1)
- [ ] Test form submission fires `pbw_lead` event in CleverTap real-time stream (April 1)
- [ ] All 5 CleverTap event properties confirmed on test submission (April 1)
- [ ] `pbw_2026_lead` tag applied to test profile (April 1)
- [ ] Redirect to registration flow works with UTM params preserved (April 1)
- [ ] GDPR checkbox is pre-unchecked and blocks submit if unchecked (April 1)
- [ ] Page LIVE at bit2me.com/pbw (April 1)

---

## Section 8: Open Questions for Dev (Answers Needed by March 29)

1. **Is `/pbw` available on the Bit2Me domain?** If not, confirm the fallback URL immediately — it unblocks UTM creation, QR code generation, and email link drafts.

2. **What is the deployment pipeline for a new standalone page?** Is this a standard CMS page, a custom Next.js route, or a separate deployment? This determines how quickly approved copy can be dropped in on April 1.

3. **Can the CleverTap form integration reuse an existing endpoint?** Katy needs to confirm the endpoint URL. If dev needs to build a new integration layer, estimate dev hours and flag immediately — this is a blocker for the April 1 go-live.

4. **Estimated dev hours for the full page build?** Planning to have the structure complete by March 31. If hours are insufficient, flag now so we can descope or accelerate.

5. **Does the existing Bit2Me web stack support server-side UTM preservation on redirect?** The form must pass `utm_source` and `utm_campaign` to CleverTap AND preserve them in the post-submit redirect URL for BigQuery attribution.

---

## Appendix: Copy Status by Section

| Page Section | Copy Status | Source When Available |
|--------------|-------------|----------------------|
| Hero headline | [PLACEHOLDER] | Diego approval Apr 1 — from Diego package Section 2 |
| Hero sub-headline | [PLACEHOLDER] | Diego approval Apr 1 — from Diego package Section 2 |
| Hero CTA button | `"Claim Your 60 Free Days"` | Diego package Section 2 — CONFIRMED |
| Offer block | [PLACEHOLDER] | Diego approval Apr 1 — from Diego package Section 2 |
| Differentiator 1 (MiCA) | [PLACEHOLDER — CNMV date TBD] | Diego to confirm exact CNMV authorization date |
| Differentiator 2 (Banks) | "Bankinter, BBVA, Cecabank, and Tether" | CONFIRMED — no Diego dependency |
| Differentiator 3 (Europol) | [PLACEHOLDER] | Diego approval Apr 1 |
| Social proof | Press logo row | CONFIRMED — no copy needed |
| Bottom CTA button | `"Start Trading Free"` | Diego package Section 2 — CONFIRMED |
| Legal footer | Full MiCA disclaimer | Diego package Section 8 — text provided, confirmation pending |

**Diego package Section 8 legal footer (paste verbatim when approved):**

> Crypto-assets are highly volatile and unregulated in most EU countries. No consumer protection. Tax on profits may apply. Bit2Me is authorized as a Crypto-Asset Service Provider (CASP) under MiCA Regulation (EU) 2023/1114 by Spain's Comisión Nacional del Mercado de Valores (CNMV). Trading crypto-assets involves risk of loss. Past performance is not indicative of future results.
