# PBW 2026 — Email Campaign Brief for Katy
## Campaign: pbw_warmup_email_v1_apr01 + pbw_b2b_invite_v1_apr01

**From:** Daniel Ferraro, Head of Growth
**To:** Katy Gildemeister, CRM/CleverTap
**Date:** 2026-03-30
**Action required by:** March 31 (build + pre-stage) — send on April 1 (pending Diego approval)

---

## PURPOSE OF THIS DOCUMENT

This brief gives you everything needed to build both PBW email campaigns in CleverTap during March 29-31. On April 1, when Diego approves, you swap in the confirmed copy variant and hit send — no back-and-forth with Daniel required.

**Hard rule: do NOT send before Diego approval. Subject lines and offer body contain the PBW offer claim, which requires legal sign-off before it goes to users.**

---

# PART A — B2C AWARENESS EMAIL (Email #1)

---

## Section 1: Campaign Overview

| Field | Value |
|-------|-------|
| Campaign name in CleverTap | `pbw_warmup_email_v1_apr01` |
| Type | Awareness / warm-up — NOT a conversion push |
| Purpose | Prime existing users to register friends, share the offer, or plan to attend PBW |
| Segment | `pbw_warmup_v1` (see Section 2) |
| Send date | April 1 (Tuesday) at 10:00 AM Madrid time |
| Fallback send date | April 2 (Wednesday) at 10:00 AM Madrid time — if Diego approval arrives after 5 PM on April 1 |
| Status gate | DO NOT send before Diego-approved confirmation from Daniel |

**What this email is NOT:**
- It is not a hard sell. Do not add urgency language or "last chance" copy.
- It is not a conversion email. No "sign up now or miss out." It is a brand moment — we are at PBW, here is your exclusive.

**Why this email matters:** Email to existing users is the highest-converting channel for PBW (15-30% conversion from email traffic vs 2-5% from paid ads). A warm, personal email on April 1 primes users to pay attention when the offer goes live.

---

## Section 2: Segment Definition

**Segment name:** `pbw_warmup_v1`

Build this segment in CleverTap. Alvaro can validate the count against BigQuery before send.

### Inclusion Criteria — ALL four conditions must be true:

| # | Property | Operator | Value |
|---|----------|----------|-------|
| 1 | `country` | is any of | Spain, France, Germany, Netherlands, Italy, Portugal, Belgium, Austria, Sweden, Denmark, Finland, Poland, Czech Republic, Slovakia, Hungary, Romania, Bulgaria, Greece, Croatia, Slovenia, Estonia, Latvia, Lithuania, Luxembourg, Malta, Cyprus, Ireland (all EU member states) |
| 2 | `kyc_status` | equals | `complete` — verified accounts only, NOT pending or rejected |
| 3 | Lifetime behavior | has performed | at least 1 `deposit` event ever |
| 4 | `email_opt_in` | equals | `true` — GDPR consent is active |

### Exclusion Criteria — Remove user if ANY of the following is true:

| # | Property | Operator | Value |
|---|----------|----------|-------|
| 1 | User tag | contains | `churned_zero` (no balance, no activity 90+ days) |
| 2 | User tag | contains | `excluded` (per Bit2Me lifecycle stage definition — this maps to the EXCLUDED stage in our 13-stage model) |
| 3 | Email channel status | equals | `unsubscribed` |

### Segment Size Validation

Before send, confirm the segment count with Alvaro using this BigQuery query:

```sql
SELECT COUNT(*)
FROM bit2me_lifecycle
WHERE kyc_status = 'complete'
  AND country IN (/* EU country list */)
  AND email_opt_in = true
  AND tag NOT IN ('churned_zero', 'excluded')
```

**Safety control:** In CleverTap campaign settings, set "Don't send if segment exceeds 200,000" — this prevents accidental oversend to the full base if a filter misconfigures. This is a hard guardrail, not optional.

---

## Section 3: Send Timing

| Setting | Value |
|---------|-------|
| Send date | April 1, 2026 (Tuesday) |
| Send time | 10:00 AM Madrid time (Europe/Madrid timezone) |
| Timezone handling | Use CleverTap's "User's local timezone" option — OFF. Use fixed timezone: Europe/Madrid |
| Fallback | If Diego approval arrives after 5 PM on April 1: move send to April 2, 10:00 AM Madrid time |
| Do not send on | Saturday or Sunday — send only Monday through Wednesday |
| Do not send before | Diego-approved subject line and body are confirmed by Daniel in writing |

**Why 10 AM Madrid?** Professional audiences open email at the start of their workday. 10 AM Madrid = 9 AM London = late morning for Central EU — maximizes open rate for our Spain + EU segment.

---

## Section 4: Subject Line Options

**Source:** Diego review package Section 4 — all three variants submitted for Diego's approval.

On April 1, select the **Diego-approved variant** and use it for 100% of sends. If the segment exceeds 10,000 users and Diego has approved more than one variant, run an A/B split in CleverTap (50/50 split, measure open rate after 24 hours, then send remaining 10% winner).

| Option | Subject Line |
|--------|-------------|
| A | "Bit2Me is at Paris Blockchain Week — here's your exclusive" |
| B | "PBW 2026: Trade free for 60 days" |
| C | "We're in Paris April 15. You should be too." |

**How to select:** Wait for Daniel to confirm which variant Diego approved. If Daniel confirms "Diego-approved Subject A," use Option A for all sends. Do not self-select without confirmation.

**A/B test setup in CleverTap (if segment > 10,000 and Diego approves 2 variants):**
- Split: 45% to A / 45% to B / 10% holdout (winner-send after 24h)
- Winner metric: Open rate (not CTR — we optimize for open rate on email #1)
- Auto-send winner after 24h with minimum 5% open rate lift to declare a winner

---

## Section 5: Email Body Structure

**Word count target: under 150 words in the body.** Event emails are scanned, not read. Do not add more copy.

Build the email with these 5 elements in order:

**1. Opening line (1 sentence):**
> "We're heading to Paris Blockchain Week, April 15-16 at the Carrousel du Louvre — and we're bringing an exclusive offer for you."

**2. Offer block (2-3 sentences max):**
> "Open a Bit2Me account and trade fee-free for 60 days. No promo code. It's automatic."

**3. CTA button (above fold on mobile):**
- Button text: `Claim Your 60 Free Days`
- Destination URL: `https://bit2me.com/pbw?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup`
- Button color: Bit2Me brand primary (use existing brand spec)
- Placement: centered, full-width on mobile, minimum 44px tap target

**4. Three trust signals (below CTA, 3 bullet points):**
- Spain's first MiCA-authorized exchange (CNMV-regulated since [CNMV authorization date — Daniel to confirm])
- Backed by Bankinter, BBVA, Cecabank, and Tether
- Trusted by Europol and Interpol for seized crypto asset processing

**5. Footer (mandatory — verbatim from Diego review package Section 8):**

> Crypto-assets are highly volatile and unregulated in most EU countries. No consumer protection. Tax on profits may apply. Bit2Me is authorized as a Crypto-Asset Service Provider (CASP) under MiCA Regulation (EU) 2023/1114 by Spain's Comisión Nacional del Mercado de Valores (CNMV). Trading crypto-assets involves risk of loss. Past performance is not indicative of future results.

Plus: standard Bit2Me unsubscribe link and physical address (required for CAN-SPAM / GDPR compliance).

**Important:** Do not alter the legal disclaimer wording. It must appear verbatim as written above. This is the Diego-approved text.

---

## Section 6: Expected Performance Benchmarks

| Metric | Target | Notes |
|--------|--------|-------|
| Open rate | 25-35% | Warm base, relevant offer, strong sender reputation |
| Click-to-open rate (CTOR) | 8-12% | Single CTA, clear offer |
| Conversion from email traffic | 15-30% | Highest converting channel for PBW |
| Unsubscribes | <0.5% | Warm base should be low; monitor post-send |

Flag to Daniel immediately if open rate is below 10% after 4 hours — this may indicate a deliverability issue or segment misconfiguration.

---

# PART B — B2B INVITE EMAIL

---

## Section 7: B2B Email Overview

| Field | Value |
|-------|-------|
| Campaign name | `pbw_b2b_invite_v1_apr01` |
| Type | Meeting request — direct, personal, 1:1 tone |
| Send method | Manual send by Daniel (if list < 30 contacts) OR CleverTap (if Katy manages the list) |
| Send date | April 1-2, in parallel with Email #1 |
| Recipients | B2B ICP list contacts who accepted LinkedIn connection but have NOT yet booked a meeting |
| Source list | Google Sheet "PBW_B2B_Targets" — filter: connection_accepted = YES, meeting_booked = NO |

**Note for Katy:** This email may bypass CleverTap entirely if Daniel is managing the B2B list manually. If the B2B list grows beyond 50 contacts, please build this as a separate campaign in CleverTap using the B2B profile segment (non-consumer contacts). Confirm with Daniel by March 31 whether you will handle this in CleverTap or Daniel sends manually.

---

## Section 8: B2B Subject Line Options

**Source:** Diego review package Section 4 — B2B invite email variants submitted for Diego's approval.

On April 1, use the **Diego-approved B2B subject line**. All three options are approved for review:

| Option | Subject Line |
|--------|-------------|
| A | "20 minutes at PBW? Spain's first MiCA exchange + your [company]" |
| B | "Bit2Me B2B at Paris Blockchain Week — brief meeting request" |
| C | "MiCA-authorized infrastructure for [sector] — PBW meeting" |

**Personalization note:** Option A requires manual personalization — replace [company] with the recipient's company name. Option B and C can be sent as-is without personalization. For the top 20 H-priority targets, use Option A with company name inserted. For M-priority and expansion targets, Option B is acceptable.

---

## Section 9: B2B Email Body Structure

Use the persona-appropriate template from `01-b2b-icp-list.md`:
- **Template A** — For banks with crypto desks (Deutsche Bank, BBVA crypto, Bankinter digital)
- **Template B** — For crypto infrastructure (Fireblocks, BitGo, Circle, Ripple, Chainalysis)
- **Template C** — For fintechs / asset managers building on crypto rails

Append the following to every B2B email body:
1. Calendly booking link: `[calendly link — Daniel to insert]` with text: "I have 20-minute slots on April 15 and 16 — happy to find a time that fits your schedule."
2. Diego-approved legal footer (same text from Section 5 above — required on all external communications per MiCA compliance posture)

**Word count target:** Under 100 words. B2B invite emails should be shorter than B2C. Three sentences maximum in the body before the Calendly link.

---

# PART C — PRE-SEND CHECKLIST

---

## Section 10: Pre-Send Checklist for Katy

This checklist applies to both emails. Complete every item before confirming to Daniel that the email is ready to send. Daniel will give the final green light on April 1.

### B2C Email (`pbw_warmup_email_v1_apr01`)

- [ ] Segment `pbw_warmup_v1` saved in CleverTap and estimated reach verified against BigQuery (Alvaro confirms count)
- [ ] Diego-approved subject line selected and noted in this checklist (record which variant: A / B / C)
- [ ] Landing page URL `bit2me.com/pbw` confirmed LIVE — test by visiting the URL directly. DO NOT send email if the page returns a 404 or redirects to homepage
- [ ] UTM params in CTA link verified exactly as: `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup`
- [ ] Unsubscribe link functional — click it manually in the test send and confirm it unsubscribes the test address
- [ ] Legal footer present verbatim from Diego's approved text (compare against Section 5 of this brief word-for-word)
- [ ] Test send completed to internal Bit2Me team addresses — minimum 3 people confirm correct render on mobile (iPhone + Android)
- [ ] CleverTap open rate tracking enabled — go into campaign settings and confirm tracking is ON (not disabled)
- [ ] Scheduled send time confirmed: April 1 (or April 2 fallback) at 10:00 AM Madrid time — NOT set to "send immediately"
- [ ] "Don't send if segment exceeds 200,000" safety control active in campaign settings
- [ ] Campaign name matches convention: `pbw_warmup_email_v1_apr01`
- [ ] `pbw_lead` tag fires on CTA click through to landing page — verify with Alvaro or test in CleverTap event stream

### B2B Email (`pbw_b2b_invite_v1_apr01` or manual)

- [ ] B2B recipient list exported from Google Sheet (filter: connection_accepted = YES, meeting_booked = NO)
- [ ] Diego-approved B2B subject line selected and noted (record which variant: A / B / C)
- [ ] Calendly link inserted and tested — open it to confirm slots are live for April 15 and April 16
- [ ] [company] and [sector] placeholders replaced for personalized variants (H-priority targets)
- [ ] Legal footer present (same Diego-approved text as B2C)
- [ ] Test send to Daniel's own email address before any external send

---

## Section 11: Contacts and Ownership

| Task | Owner | Deadline |
|------|-------|----------|
| Build `pbw_warmup_v1` segment in CleverTap | Katy | March 31 |
| Validate segment count against BigQuery | Alvaro | March 31 |
| Draft email body in CleverTap (placeholder copy) | Katy | March 31 |
| Confirm Diego-approved subject line to Katy | Daniel | April 1 (post-Diego approval) |
| Swap in Diego-approved copy, schedule send | Katy | April 1 (within 2 hours of Daniel confirmation) |
| Confirm landing page URL is live | Daniel / Dev | April 1 |
| Final send authorization | Daniel | April 1 |
| B2B list export to Katy (or manual send by Daniel) | Daniel | March 31 |

---

## Section 12: UTM Taxonomy Reference

All links in both emails must use the correct UTM parameters. These parameters feed the BigQuery UTM attribution model (Alvaro owns).

| Email | UTM string |
|-------|-----------|
| B2C Email #1 CTA | `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup` |
| B2B invite email CTA | `?utm_source=email&utm_medium=direct&utm_campaign=pbw2026_b2b` |

Do not use shortened links (bit.ly, etc.) in emails — these reduce deliverability. Use the full UTM string on bit2me.com domain.

---

## Section 13: Post-Send Monitoring

After send, check CleverTap every 4 hours for the first 24 hours:

| Time after send | What to check | Alert threshold |
|-----------------|---------------|-----------------|
| 4 hours | Delivery rate | Alert Daniel if < 85% delivered |
| 4 hours | Open rate | Alert Daniel if < 10% (deliverability issue) |
| 24 hours | Open rate | Report to Daniel |
| 24 hours | CTOR (click-to-open rate) | Report to Daniel |
| 48 hours | Unsubscribe count | Alert Daniel if > 0.5% of sent |
| 48 hours | Bounce rate | Alert Daniel if hard bounce > 2% |

Send a Lark message to Daniel with the 24-hour stats using this format:
> "PBW Email #1 — 24h stats: [X] sent / [X]% delivered / [X]% open rate / [X]% CTOR / [X] unsubscribes"

---

*Brief prepared by Daniel Ferraro, Head of Growth — 2026-03-30*
*Source references: 01-diego-review-package.md (Section 4 subject lines, Section 8 legal footer), 02-RESEARCH.md (Section 5 CleverTap Email #1 Setup)*
