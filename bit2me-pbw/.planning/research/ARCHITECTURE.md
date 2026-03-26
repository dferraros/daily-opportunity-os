# Architecture Patterns — Event Campaign

**Project:** Bit2Me @ Paris Blockchain Week 2026
**Researched:** 2026-03-26
**Domain:** Crypto exchange event marketing (B2C acquisition + B2B pipeline)

---

## Full Funnel Diagram

```
AWARENESS
    │
    ├── Paid ads (X/Twitter, Google Display)
    ├── Existing user email warm-up (CleverTap)
    ├── Organic social (pre-event content calendar)
    └── PR / media outreach (press release + journalist list)
         │
         ▼
CAPTURE
    │
    ├── B2C: Dedicated event landing page (pbw.bit2me.com or /pbw)
    │        └── Lead magnet: exclusive offer (fee discount, bonus, early access)
    │        └── Form: email + country + "interested in" toggle
    │        └── Confirmation: email auto-responder via CleverTap
    │
    └── B2B: Meeting booking page (Calendly or similar)
             └── ICP target list built from PBW attendee directory
             └── LinkedIn + email outreach sequence (2 weeks pre-event)
         │
         ▼
ENGAGE (during event — Apr 15-16)
    │
    ├── B2C: Booth QR → mobile sign-up → instant CleverTap tag
    │        └── Demo flow: live account opening, first trade
    │        └── On-site offer: "open today, fee waived"
    │
    └── B2B: Pre-booked 1:1 meetings (20 min each)
             └── Real-time lead notes in shared spreadsheet (no CRM yet)
             └── Business card + NFC card tap → contact record
         │
         ▼
CONVERT
    │
    ├── B2C: Post-event email sequence Day 0-7 (CleverTap)
    │        └── D+0: "Great meeting you" + offer reminder
    │        └── D+1: KYC completion prompt (if not finished on-site)
    │        └── D+3: Social proof (number of users, regulatory compliance)
    │        └── D+7: Last call on event offer (expiry)
    │
    └── B2B: Human follow-up within 24h by Daniel or BD owner
             └── Personalized email referencing conversation
             └── Shared deck / one-pager attachment
             └── Next step: 30-min call booked
         │
         ▼
RETAIN / NURTURE (post-event, Week 2-4)
    │
    ├── B2C: Onboarded users enter standard lifecycle journeys (CleverTap)
    │        └── LC-OS journey triggers: FM → second trade → active
    │
    └── B2B: Monthly check-in sequence (3 touches over 6 weeks)
             └── Content: relevant regulation news, Bit2Me product update
             └── Goal: discovery call → partnership scoping
```

---

## Phase Breakdown with Timeline

### Phase 0 — Foundation (Days 1-3, before anything launches)

This phase is a hard blocker for everything else. Nothing can be built until these are resolved.

| Deliverable | Why It Blocks | Owner |
|-------------|--------------|-------|
| Define the event offer | Landing page headline, ad copy, booth pitch all depend on this | Daniel |
| Confirm B2B target segments | Determines which ICP list to build and which outreach angle to use | Daniel |
| Diego legal review of offer + key claims | Required before any copy goes live | Diego |
| Bit2Me brand asset pack confirmed | Landing page and booth materials need logo, colors, approved claims | Design |

**Output:** Approved offer brief + ICP definition + legal green light on core claims.

---

### Phase 1 — Pre-Event Week 1 (Days 4-10)

Build and launch the capture infrastructure. Target: live by Day 7.

**B2C track:**

| Deliverable | Notes |
|-------------|-------|
| Event landing page | Single-purpose page. Offer hero, 3 trust signals, short form, CTA. No nav links out. |
| CleverTap lead capture flow | Form submit → tag "pbw_lead" → confirmation email auto-fires |
| Paid ad creative (X/Twitter + Google) | 2-3 variants per channel. Copy locked by Diego before launch. |
| Existing user email (warm-up #1) | "We'll be at PBW — here's what's coming." No CTA beyond awareness. |
| Social content: announcement post | LinkedIn + X/Twitter. "Bit2Me at PBW 2026" with booth number. |

**B2B track:**

| Deliverable | Notes |
|-------------|-------|
| ICP target list (50-100 contacts) | Sources: PBW attendee list / LinkedIn / Swapcard app. Filter: funds, fintechs, media, institutions. |
| LinkedIn connection wave 1 | Personalized note referencing PBW. No pitch. Goal: connect. |
| Meeting booking page | Calendly link to 20-min "Coffee at PBW" slot. Time options: Apr 15 morning, Apr 16 afternoon. |
| Outreach email #1 | Sent after LinkedIn connection accepted. Propose meeting. 75-100 words max. |

**Build order within Phase 1:**
```
Offer brief approved → landing page copy → Diego review → page live → ad creative → ads live
ICP list built → LinkedIn wave → email #1 → booking page linked in email #2
```

---

### Phase 2 — Pre-Event Week 2 (Days 11-17)

Amplify reach. Warm up engaged leads. Lock down on-site execution.

**B2C track:**

| Deliverable | Notes |
|-------------|-------|
| Existing user email #2 (urgency) | "Event in X days — here's your exclusive offer." Link to landing page. |
| Paid ad optimization | Pause underperforming variants. Scale winners. |
| Social content: 3 pre-event posts | Speaker highlights, team intro, what to expect at the booth. |
| Booth brief finalized | Dimensions, design files, QR placement, swag quantities, demo device setup. |

**B2B track:**

| Deliverable | Notes |
|-------------|-------|
| LinkedIn follow-up message | Sent to connected but non-responding contacts. "Still open to a quick chat at PBW?" |
| Outreach email #2 (non-responders) | 3 days before event. "Schedules fill up fast" urgency framing. |
| Meeting confirmations | Re-confirm all booked meetings 48h before. Include booth location. |
| Lead tracking sheet ready | Columns: Name, Company, Role, Contact info, Meeting notes, Temperature (H/M/C), Next action, Owner. |

---

### Phase 3 — During Event (Apr 15-16, ~2 days)

Capture and qualify. Every interaction gets logged same day.

**B2C on-site flow:**

```
Attendee stops at booth
    → Demo: "Let me show you how to buy your first crypto in 3 minutes"
    → QR code on booth signage → mobile landing page → sign-up form
    → OR: rep scans their badge via lead retrieval app → email collected
    → Tag in CleverTap: "pbw_booth_scan" + rep ID
    → Offer explained verbally: "Sign up today, first X trades fee-free"
    → If signs up on the spot: celebrate + direct to KYC on their phone
    → If not: "We'll follow up tomorrow — here's what you'll get"
```

**B2B on-site flow:**

```
Pre-booked meeting starts
    → Rep opens lead tracking sheet row for this contact
    → 5-min: "Tell me about what you're working on right now"
    → 10-min: Bit2Me positioning + relevant product capability
    → 5-min: Agree on next step (call, intro, POC, partnership brief)
    → End: rep enters notes + temperature + agreed next step immediately
    → NFC card tap or business card collected
```

**Daily close (end of each event day):**
- Team sync: leads reviewed, temperatures agreed, next-day adjustments
- Any hot B2B leads: Daniel sends personal LinkedIn message same evening
- Any B2C signups with incomplete KYC: flag for D+0 automated trigger

---

### Phase 4 — Post-Event (Apr 17-24, Days 1-7 after)

The 72-hour window is the highest-leverage moment. Warm leads go cold by Day 4.

**B2C email sequence (via CleverTap, triggered by pbw tags):**

| Trigger | Timing | Message |
|---------|--------|---------|
| Booth scan, not signed up | D+0 (same evening) | "Great to meet you — here's how to claim your offer" + sign-up link |
| Signed up, KYC incomplete | D+1 | "You're almost there — finish in 3 minutes" + KYC deep link |
| Signed up, KYC done, no deposit | D+3 | Social proof email: "X users trust Bit2Me" + first deposit guide |
| Deposited, no trade | D+5 | "Your first trade is waiting" + explainer |
| Offer expiry reminder | D+7 | "Last 24h on your PBW exclusive offer" |

**B2B follow-up sequence (manual, tracked in spreadsheet):**

| Lead temp | D+1 | D+4 | D+14 | D+30 |
|-----------|-----|-----|------|------|
| Hot (H) | Personal email from Daniel, reference specific conversation, propose call this week | Confirm call or follow-up if not booked | Share relevant content or update | Check-in: "Any progress on X?" |
| Medium (M) | Team email, reference conversation, share one-pager, soft next step | LinkedIn message if no reply | Email with new content angle | Soft re-engage |
| Cold (C) | Add to long-term nurture list | — | 1 email: "Thought this might be useful" | — |

---

## Component Dependencies

The following dependencies define what must be built before what else can start.

```
[1] Offer definition
    └── blocks: landing page copy, ad copy, booth pitch script, email copy

[2] Diego legal approval (on offer + key claims)
    └── blocks: landing page going live, ads launching, email sends

[3] Landing page live
    └── blocks: ad campaigns (need destination URL)
    └── blocks: B2C email #1 (need link to share)

[4] CleverTap pbw_lead tag + journey configured
    └── blocks: post-event email sequences
    └── blocks: on-site QR → tag flow working

[5] ICP target list (B2B)
    └── blocks: LinkedIn outreach wave 1
    └── blocks: meeting booking page being linked

[6] Meeting booking page
    └── blocks: email outreach #1 having a CTA link

[7] On-site lead tracking sheet
    └── blocks: post-event B2B follow-up (need notes to personalize)

[8] Booth design brief
    └── blocks: print production (needs 5-7 day lead time minimum)
```

**Critical path for B2C:**
```
Offer → Diego approval → Landing page → Ads → Email warm-up → On-site QR flow → Post-event sequences
```

**Critical path for B2B:**
```
ICP list → LinkedIn wave → Email outreach → Meeting booking → On-site 1:1s → 24h follow-up → Nurture
```

---

## Recommended Channel Architecture

### B2C — Channel to Goal Mapping

| Goal | Primary Channel | Secondary Channel | Notes |
|------|----------------|-------------------|-------|
| New audience reach | X/Twitter paid ads | Google Display | Crypto ads require Google certification. Verify Bit2Me account status. |
| Warm existing users | CleverTap email | Push notification | Segment: Spain-based, active in last 90 days, not yet at PBW audience |
| Event landing conversions | Landing page SEO + ads | Social posts with link | UTM params on every source for attribution |
| On-site signups | Booth QR code | Rep-assisted mobile | QR should go to mobile-optimized page, not desktop version |
| Post-event nurture (B2C) | CleverTap email sequences | Push (mobile users) | Personalize by completion state, not generic blast |

### B2B — Channel to Goal Mapping

| Goal | Primary Channel | Secondary Channel | Notes |
|------|----------------|-------------------|-------|
| Build target list | PBW attendee directory / Swapcard | LinkedIn Sales Navigator search | Filter: funds, fintechs, fintech media, compliance/legal leaders |
| Initial outreach | LinkedIn connection + message | — | Do not pitch in first message. Only invite to connect. |
| Meeting booking | Email with Calendly link | LinkedIn DM | Short email, 75-100 words, single CTA |
| On-site interaction | In-person meeting | Ad hoc booth conversations | Have 1-page company overview printed (not a product brochure) |
| Post-event follow-up | Personalized email from Daniel | LinkedIn message | Reference specific detail from conversation |
| Long-term nurture | Monthly email (manual) | — | Track in spreadsheet; no CRM tool available |

---

## B2B Pipeline Architecture (Full Detail)

```
WEEK -2 (Apr 1-7)
├── Build ICP list: 50-100 targets from PBW directory + LinkedIn
│    Target roles: CEO/Founder (fintech), CIO (fund), BD (exchange), Editor (crypto media)
│    Target company types: VCs, family offices, fintechs, payment processors, banks with crypto desk
│
├── LinkedIn wave 1: connection requests with event reference
│    Message: "Hi X, noticed you're attending PBW — I'll be there representing Bit2Me.
│    Would love to connect." (under 100 words)
│
└── Set up meeting booking page (Calendly): 20-min "Coffee at PBW" slots

WEEK -1 (Apr 8-14)
├── LinkedIn follow-up: message to connected contacts
│    "Thanks for connecting. Given your work at [Company] on [topic],
│    I think we could have a useful conversation at PBW.
│    Would you be open to a 20-min coffee on Apr 15 or 16?"
│
├── Email outreach to non-LinkedIn-responders
│    Subject: "Meeting at Paris Blockchain Week?"
│    Body: [Company] + [mutual topic] + specific time proposal + Calendly link
│
├── Final follow-up email: 3 days before (Apr 12)
│    "Slots filling up — happy to carve out 15 min if you're there"
│
└── Target: 8-12 meetings pre-booked

APR 15-16 (On-site)
├── Meeting execution: 20-min structured 1:1s
│    Min 0-5: Their situation / what they're focused on
│    Min 5-15: Bit2Me positioning + relevant angle for their context
│    Min 15-20: Agree next step explicitly ("Can we do a call next week?")
│
├── Ad hoc conversations logged same-day (name, company, topic, temperature)
│
└── Hot leads: Daniel sends LinkedIn message same evening

APR 17-18 (48-hour window — highest priority)
├── Hot leads (H): personalized email from Daniel within 24h
│    Reference specific detail from conversation
│    Propose concrete next step (call date/time, intro, deck)
│
├── Medium leads (M): team follow-up email within 48h
│    Reference conversation + attach 1-pager
│    Soft next step
│
└── Cold leads (C): added to monthly nurture list

APR 19 - MAY 15 (nurture)
├── Week 2: share relevant article or Bit2Me update (no ask)
├── Week 4: "Checking in — any progress on X we discussed?"
└── Week 6: last touch before cooling the lead
```

**Benchmarks (MEDIUM confidence, industry sources):**
- 8-12 pre-booked meetings is a realistic target for a 2-person B2B team at a 2-day event
- 60-70% of productive B2B conference meetings come from pre-event outreach, not walk-ins
- Leads followed up within 24h convert at ~3x the rate of Day 7+ follow-ups

---

## Architecture Anti-Patterns to Avoid

### Anti-Pattern 1: Generic "Come Visit Our Booth" Posts
**What goes wrong:** Booth traffic comes from people with no intent, wasting rep time on non-ICP visitors.
**Instead:** Target all pre-event comms at specific audience segments. Tease a specific reason to visit (demo, exclusive offer, limited-time registration bonus).

### Anti-Pattern 2: Shared B2C and B2B Landing Page
**What goes wrong:** Copy tries to speak to both audiences, converts neither. B2C visitor gets confused by "partnership inquiries." B2B prospect sees consumer product pitch.
**Instead:** Separate pages or clearly branched CTAs. "Sign up as a user" vs. "Book a meeting" as distinct paths from the homepage banner or landing page.

### Anti-Pattern 3: Post-Event Generic Blast
**What goes wrong:** One email to all PBW contacts regardless of how warm they are. Cold contacts unsubscribe. Hot contacts feel deprioritized.
**Instead:** Segment by on-site interaction tag. pbw_booth_scan → different sequence than pbw_preregistered → different sequence than pbw_meeting_held.

### Anti-Pattern 4: B2B Outreach Starting Day-of Event
**What goes wrong:** Calendars are full. Serendipitous conversations yield no structured outcome. Most attendees leave without a booked call.
**Instead:** Start outreach 2 weeks before. Pre-book the meetings. Use on-site time to execute, not to prospect cold.

### Anti-Pattern 5: Offer Not Defined Before Assets Are Built
**What goes wrong:** Landing page, ads, and email copy all get built with placeholder offer, then require full rework after offer is approved. 3-5 days of delay in a 2-4 week sprint is critical.
**Instead:** Block Day 1-3 exclusively for offer definition. Nothing else starts until this is confirmed and Diego-approved.

### Anti-Pattern 6: QR Code Points to Homepage
**What goes wrong:** Visitor scans QR at booth, lands on homepage, bounces in 8 seconds. No conversion data.
**Instead:** QR → mobile-optimized event landing page → single CTA → form. UTM params on QR link: `utm_source=pbw_booth&utm_medium=qr&utm_campaign=pbw2026`.

---

## Scalability for 2-4 Week Runway

This architecture is intentionally sized for a lean team (Daniel + Katy + one designer, with Diego as a gate, not a builder).

**Week 1 (Days 1-7):** Offer + legal + landing page + CleverTap flow + B2B list + LinkedIn wave 1. This is the minimum viable launch. Everything else builds on it.

**Week 2 (Days 8-14):** Ads running + email warm-up 2 + B2B email outreach + booth brief to designer.

**Week 3 (Days 15-21):** Booth materials printed + meeting confirmations + final pre-event emails + team briefing on on-site runbook.

**Event + Week after (Days 22-28):** Execute on-site + post-event sequences fire automatically (CleverTap) + B2B human follow-up within 24-48h.

If the runway is only 2 weeks (not 4), the cut order is:
1. Keep: offer, landing page, B2B outreach, on-site QR flow, post-event email sequences
2. Defer: paid ads (launch Day 10 instead of Day 7), booth swag (printed faster)
3. Cut: organic social calendar (do ad hoc posts only), PR/press release (nice to have, not conversion-driving)

---

## Sources

- Paris Blockchain Week 2026 event details: [parisblockchainweek.com](https://www.parisblockchainweek.com/) — HIGH confidence
- B2B Event Marketing Guide 2026: [engineerica.com](https://www.engineerica.com/conferences-and-events/post/b2b-event-marketing/) — MEDIUM confidence
- Conference lead generation framework: [virtuwise.io](https://virtuwise.io/insights/conference-lead-generation-b2b) — MEDIUM confidence
- B2B event marketing pipeline: [linkedin.com/business/marketing](https://www.linkedin.com/business/marketing/blog/trends-tips/b2b-event-marketing-pipeline-impact) — MEDIUM confidence
- LinkedIn outreach sequences 2026: [belkins.io](https://belkins.io/blog/linkedin-outreach) — MEDIUM confidence
- NFC/QR booth lead capture: [mobilocard.com](https://www.mobilocard.com/post/exhibition-lead-capture) — MEDIUM confidence
- Crypto marketing strategies 2026: [blockchain-ads.com](https://www.blockchain-ads.com/post/crypto-marketing) — MEDIUM confidence (WebSearch, not official docs)
- Crypto conference B2B deal flow: [ninjapromo.io](https://ninjapromo.io/best-crypto-conferences) — LOW confidence (WebSearch only)
- Lead retrieval apps 2026: [mapdevents.com](https://mapdevents.com/blog/best-lead-retrieval-apps-for-trade-shows-events) — LOW confidence (WebSearch only)
