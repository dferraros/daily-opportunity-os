# Phase 2: Launch — Research

**Researched:** 2026-03-30
**Domain:** Event GTM execution — landing page, paid ads, email, LinkedIn B2B outreach, Health Score tool, social calendar, side events
**Confidence:** HIGH for critical path + deliverable specs (drawn from Phase 1 verified outputs). MEDIUM for ad specs and LinkedIn benchmarks (WebSearch verified against official sources). LOW for Health Score tool dev estimate (single internal decision, no external verification).

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-02 | Build dedicated landing page with offer, UTM-tagged QR, CleverTap tag | Landing page brief structure (Section 4), CleverTap pbw_lead tag setup (Section 5) |
| REQ-03 | Launch paid campaigns — X/Twitter primary, Google secondary | Ad campaign setup section (Section 5), creative specs table |
| REQ-04 | Email sequences — warm-up wave 1 (B2C awareness) + B2B invite email | CleverTap segment setup (Section 6), subject line options, send checklist |
| REQ-07 | Social content calendar (pre/during/post) | Social calendar section (Section 9), Buffer setup, content types |
| REQ-11 | Crypto Health Score interactive tool — build starts Phase 2 | Health Score MVP spec (Section 8) |
| REQ-14 | PBW side event calendar mapped, 5-8 RSVP candidates identified | Luma research section (Section 10) |
| REQ-15 | B2B outreach wave 1 — connection requests to full 50-100 list, Calendly live | LinkedIn workflow section (Section 7), day-by-day sequence |

</phase_requirements>

---

## Summary

Phase 2 is the execution sprint that makes Bit2Me visible in market before Paris Blockchain Week. It has one immovable upstream dependency — Diego's approval on April 1 — and seven parallel workstreams that launch in sequence from that gate. The phase runs Days 4-10 (March 29 to April 4), but the first three days (March 29-31) are pre-Diego preparation: briefing the landing page, staging ads, drafting the email, and activating LinkedIn outreach on targets who don't need approved copy.

The critical insight from Phase 1 research is that Diego's approval is the single gate that blocks four of seven workstreams: the landing page going live, paid ads launching, the email to existing users sending, and social content with the offer going out. The two workstreams that are NOT blocked by Diego are LinkedIn outreach (connection requests only, no pitch copy) and Luma side event mapping. Health Score build can start immediately as it contains no regulated copy.

The wave structure for Phase 2 planning should reflect this gate: Wave 1 runs before April 1 (preparation, briefing, pre-Diego work), Wave 2 runs on/after April 1 (everything that requires approved copy).

**Primary recommendation:** Structure Phase 2 plans around the April 1 Diego gate. Three plans pre-gate (landing page brief delivered to dev/design, Health Score brief to engineering, Luma map + LinkedIn wave 1 started), two plans post-gate (landing page live + ads running, email #1 sent + social calendar scheduled).

---

## 1. Critical Path Analysis

### The Gate Model

Everything in Phase 2 flows from one upstream decision. Diego's April 1 approval is not just a nice-to-have — it is a binary gate. The moment it arrives, four workstreams can move simultaneously. Before it arrives, only three workstreams can run.

```
TODAY (Mar 29-31) — Pre-Diego Gate
├── Workstream A: Landing page BRIEF to dev/design (no copy yet — layout, tech, UTMs)
├── Workstream B: Health Score MVP brief to engineering (no regulated copy involved)
├── Workstream C: LinkedIn connection requests sent (no pitch, no copy approval needed)
└── Workstream D: Luma side event calendar mapped (research only)

APRIL 1 — Diego Approval Gate
│
├── Workstream E: Landing page goes LIVE (approved copy drops in)
├── Workstream F: Paid ads launch on X/Twitter (approved ad copy activates)
├── Workstream G: Email #1 sends to existing users (approved subject + body)
└── Workstream H: Social content calendar scheduled in Buffer (offer posts go live)
```

### Dependency Chain

```
[Diego approval Apr 1]
    ↓ unblocks
[Landing page LIVE]
    ↓ unblocks
[Paid ads launch] — needs destination URL
    ↓ unblocks
[Email #1 send] — must include landing page link
    ↓ unblocks
[Social posts with offer] — link to landing page in every post
```

Health Score and LinkedIn outreach run entirely in parallel — they have zero dependency on Diego.

### Hard Deadlines by Workstream

| Workstream | Must start by | Must complete by | Blocked by |
|------------|---------------|------------------|------------|
| Landing page brief to dev | Mar 29 (Day 4) | Mar 31 (brief delivered) | Nothing — start now |
| Health Score brief to eng | Mar 29 (Day 4) | Mar 31 (brief delivered) | Nothing — start now |
| LinkedIn connection requests | Mar 29 (Day 4) | Apr 1 (wave 1 sent) | Nothing — start now |
| Luma side event map | Mar 29 (Day 4) | Apr 1 (map complete) | Nothing — start now |
| Landing page LIVE | Apr 1 (Day 7) | Apr 1 | Diego approval |
| Paid ads running | Apr 1 (Day 7) | Apr 4 | Diego approval + landing page URL |
| Email #1 sent | Apr 1 (Day 7) | Apr 4 | Diego approval + landing page URL |
| Social calendar scheduled | Apr 1 (Day 7) | Apr 4 | Diego approval |

---

## 2. What "Done" Looks Like for Each Success Criterion

Precise done definitions prevent ambiguous completion claims.

### SC-1: Landing Page Live
**Done when:**
- URL bit2me.com/pbw (or /paris) resolves publicly with no login wall
- Hero headline matches Diego-approved copy verbatim
- "Claim Your 60 Free Days" CTA button is visible above the fold on mobile
- Form submits to CleverTap and fires pbw_lead tag (verifiable in CleverTap real-time activity stream)
- QR code on the page resolves to `?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite`
- Legal footer is present below the fold
- Google Analytics / BigQuery UTM tracking confirmed with a test submission

**Not done if:** Page exists but CleverTap tag is not firing, or QR code points to the homepage.

### SC-2: Paid Ads Running
**Done when:**
- At least 2 X/Twitter ad variants are in "Active" status in X Ads Manager
- Daily spend is registering (not zero)
- Destination URL for all ads is the /pbw landing page with correct UTM params
- Google Ads campaign is either active OR a decision has been made to delay/skip based on certification check

**Not done if:** Campaign is in "Pending" or "Under Review" in X Ads Manager.

### SC-3: Email #1 Sent
**Done when:**
- Campaign send is confirmed in CleverTap (status: "Sent" or "Completed")
- Target segment is Spain + EU, KYC-complete (verified by Alvaro pull or CleverTap filter)
- Open rate tracking is live (CleverTap shows delivery + open stats)
- Unsubscribe link is functional

**Not done if:** Campaign is in Draft status, or segment has not been validated against Bit2Me user properties.

### SC-4: LinkedIn Wave 1 Sent + Calendly Live
**Done when:**
- All H-priority and M-priority targets in the Google Sheet have "Outreach Sent" date filled
- Google Sheet shows minimum 50 rows with outreach status
- Calendly page is live with 20-minute slots on April 15 and 16 (minimum 8 slots per day)
- Calendly link is included in LinkedIn message template after connection acceptance

**Not done if:** Calendly is set up but has wrong dates, or LinkedIn outreach is stuck at the H-priority top 20.

### SC-5: Social Calendar + Luma Map
**Done when:**
- Buffer queue shows at least 15 scheduled posts covering March 29 - April 16 (pre-event, event, post-event)
- Posts are spread across X/Twitter and LinkedIn (minimum)
- Luma side event list has at least 5-8 events identified with date, audience type, and invite status
- At least 3 events have RSVP submitted or pending confirmation

**Not done if:** Posts are in Buffer as drafts but not scheduled, or Luma research is a list with no action taken.

---

## 3. Landing Page Brief Structure

The landing page brief is what Daniel delivers to dev and design by March 31. It does NOT need approved copy — it needs enough structure that dev can build the page and design can mock it, and approved copy drops in on April 1 without requiring architectural changes.

### Section 1: URL and Hosting
- **Target URL:** bit2me.com/pbw (or /paris if /pbw is taken)
- **Platform:** Existing Bit2Me web infrastructure — no new deployment pipeline
- **Mobile-first requirement:** QR code scans happen on phones. The form must work on a 375px viewport with poor Wi-Fi. No heavy JS on form submit.
- **Page must NOT require login** to view or access the form

### Section 2: Page Architecture (5 sections, locked)
1. **Hero** — Headline [APPROVED COPY DROPS IN APR 1] + event badge visual + countdown to Apr 15 + single CTA button
2. **Offer block** — What users get [APPROVED COPY] + plain-language terms (start date, end date, eligible trades, no promo code needed)
3. **3 differentiators** — Spain's first MiCA exchange + bank backing logos + Europol signal (3 bullets, no more)
4. **Social proof** — Press logos row (CoinDesk, Chainwire, Bankinter announcement — 1 row, no captions)
5. **CTA repeat + legal footer** — Second button [APPROVED COPY] + mandatory Diego-approved disclaimer

### Section 3: Form Specification
- **Fields:** Email (required) + Name (required) — 2 fields maximum. Country optional. No phone number.
- **Submit action:** POST to CleverTap via existing integration (Katy to confirm endpoint)
- **On submit:** Fire `pbw_lead` CleverTap event tag; redirect to standard Bit2Me registration flow with UTM params preserved in URL
- **Error handling:** Inline validation, not page reload
- **GDPR:** Email opt-in checkbox required (pre-unchecked, required to check before submit)

### Section 4: UTM Tagging Requirements
Every traffic source that lands on this page needs a distinct UTM. The page itself does not generate UTMs — the links pointing TO it do. This is Alvaro's ownership.

| Source | UTM string |
|--------|-----------|
| X/Twitter paid | `?utm_source=twitter&utm_medium=paid&utm_campaign=pbw2026` |
| Google paid | `?utm_source=google&utm_medium=paid&utm_campaign=pbw2026` |
| QR code (booth) | `?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite` |
| Email #1 | `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup` |
| LinkedIn organic | `?utm_source=linkedin&utm_medium=organic&utm_campaign=pbw2026_b2b` |
| QR on lanyards | `?utm_source=booth&utm_medium=lanyard&utm_campaign=pbw2026_onsite` |

### Section 5: CleverTap Integration Spec (for Katy)
- Event name: `pbw_lead` (fires on successful form submit)
- Properties to capture: `{source: utm_source value, campaign: utm_campaign value, name: form name field, email: form email field, gdpr_consent: true/false}`
- Journey trigger: On `pbw_lead` event fire → enroll user in PBW B2C journey (journey must be pre-built by Katy before April 1)
- Tag to apply to user profile: `pbw_2026_lead` (permanent tag for cohort tracking)

### Section 6: QR Code Specification
- **Generator:** Bitly or UTM.io (branded short link)
- **Target URL:** bit2me.com/pbw?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite
- **Format:** SVG preferred (scales without pixelation for print); PNG backup at 2000x2000px minimum
- **Test:** QR must be scannable at the sizes it will appear: A4 printed takeaway card (minimum), A1 banner (maximum)
- **Owner:** Daniel creates; Alvaro validates UTM

---

## 4. X/Twitter Ad Campaign Setup

### Pre-Launch Requirements
Before any ad goes live on X, Bit2Me must hold a valid X crypto exchange advertising certification for the EU market. This is a platform-level requirement that cannot be bypassed.

**Certification check (do this Day 4, March 29):**
1. Log into X Ads Manager → go to Account Settings → Certification status
2. If expired or missing, submit at: business.x.com → Ads → Account certification → Financial Services → Crypto Exchange
3. Expected timeline: 2-7 business days. If submitted March 29, approval arrives by April 3-4 — still within Phase 2 window.
4. Certification needed separately for each category (exchange cert does not cover DeFi or NFT ads)

**Note:** Belgium is an excluded market for X crypto ads. Do not target Belgium in any campaign.

### Campaign Structure

| Setting | Value |
|---------|-------|
| Campaign objective | Website clicks or conversions (not awareness) |
| Daily budget | €100-200/day for a 10-day burst |
| Total budget | €1,000-2,000 for the full Phase 2 window |
| Bidding | Automatic (let X optimize in the learning phase) |
| Ad format | Image ads (primary) + text ads (secondary) |
| Destination URL | bit2me.com/pbw?utm_source=twitter&utm_medium=paid&utm_campaign=pbw2026 |

### Audience Targeting Layers

Build 2 ad sets with distinct targeting — do not combine them:

**Ad Set 1 — Crypto-native professionals (B2C)**
- Interest: Cryptocurrency, Bitcoin, Ethereum, DeFi, blockchain, fintech
- Follower targeting: Users who follow Binance, Coinbase, Kraken, CoinDesk, Decrypt
- Geography: Spain, France, Germany, Netherlands, Italy, Portugal (EU crypto-active markets)
- Language: English + Spanish
- Age: 25-50

**Ad Set 2 — Event intent audience (B2C + B2B)**
- Keyword targeting: "Paris Blockchain Week", "PBW2026", "PBW 2026", "blockchain conference Paris", "Bit2Me"
- Geography: EU-wide + UK (less restrictive — event-intent users search from anywhere)
- No age restriction on this set

### Creative Specifications (X/Twitter 2026 requirements)
- **Image:** JPEG or PNG, max 5MB, 1200x1200px (square, preferred for feed) or 1200x628px (landscape)
- **Ad copy:** 280 characters maximum per ad variant (each link counts as 23 characters)
- **Disclosure:** "Paid Promotion" label required by X 2026 rules — this is automatic when running through Ads Manager
- **Links:** One URL per ad; link must be in the body text, not appended

**4 ad variants to run (pre-drafted in Diego review package):**
- Variant 1: "Trade Free for 60 Days at Paris Blockchain Week — MiCA-authorized, backed by Bankinter and BBVA" + landing page link
- Variants 2-4: from the ad copy section in Diego's review package (Section 3 of 01-diego-review-package.md)

### Google Ads Track
Google requires separate crypto exchange certification. Verify status before scoping. If Bit2Me already holds Google certification for EU: launch search campaign targeting "Paris Blockchain Week", "buy crypto Europe", "crypto exchange Spain". Budget: €500 for Phase 2. If certification is not in place: do not spend time pursuing it during this sprint — X/Twitter is the primary channel and can carry the load alone.

### What NOT to Do on X Ads
- Do not use "guaranteed" or "returns" language — ad will be rejected
- Do not target Belgium (blocked market)
- Do not use celebrity images without explicit rights
- Do not claim CNMV "endorses" the ad or "recommends" Bit2Me

---

## 5. CleverTap Email #1 Setup

Email #1 is the awareness email: "Bit2Me is at Paris Blockchain Week — here's your offer." It goes to existing users, not new leads. It is not a conversion push — it is a warm-up that primes existing users to register friends, share the offer, or attend PBW themselves.

### Segment Definition (for Katy + Alvaro)

**Segment name:** `pbw_warmup_v1`

**Inclusion criteria (all must be true):**
- User property: `country` = Spain OR EU country (any EU member state)
- User property: `kyc_status` = complete (verified, not pending)
- User behavior: at least 1 deposit event in lifetime
- User property: `email_opt_in` = true (GDPR consent active)

**Exclusion criteria (remove if any is true):**
- User tag: `churned_zero` (no balance, no activity 90+ days)
- User tag: `excluded` (per Bit2Me lifecycle stage definition)
- User status: `unsubscribed` from email channel

**Estimated size:** Verify against BigQuery before send. Pull `SELECT COUNT(*) FROM bit2me_lifecycle WHERE kyc_status = 'complete' AND country IN (EU_list) AND email_opt_in = true AND tag NOT IN ('churned_zero', 'excluded')`

**Safety control:** In CleverTap, set "Don't send if segment exceeds" to 200,000 — this prevents accidental oversend to the full base if a filter misconfigures.

### Send Timing
- **Target send date:** April 1-2 (immediately post-Diego approval)
- **Do NOT send before Diego approval** — subject line and body contain the offer claim
- **Send time:** 10:00 AM Madrid time (Europe/Madrid timezone) — peak open rates for professional audiences
- **Do not send on a weekend** — Monday-Wednesday sends perform best for B2B-adjacent audiences

### Subject Line Options (from Diego review package, Section 4 — use Diego-approved variant)

Primary (test against A):
- A: "Bit2Me at Paris Blockchain Week — your exclusive offer inside"
- B: "Trade free for 60 days — we'll be at PBW April 15-16"
- C: "PBW exclusivo: 60 días sin comisiones en Bit2Me" (Spanish-language version for Spain segment)

Use A/B split in CleverTap if segment is large enough (minimum 10,000 per variant for meaningful data). Otherwise send the Diego-approved version to 100%.

### Email Body Structure (approved copy from Diego package, Section 4)
1. Opening line: event context (we're going to PBW)
2. Offer: 60-day zero fee, plain language
3. CTA button: "Claim Your 60 Free Days" → landing page URL with UTM
4. 3 trust signals: MiCA authorization date, bank names, Europol signal
5. Footer: unsubscribe link + legal disclaimer (Diego-approved footer from Section 8)

**Word count target:** Under 150 words in the body. Event emails are scanned, not read.

### Send Checklist
- [ ] Segment `pbw_warmup_v1` saved in CleverTap and estimated reach verified
- [ ] Diego-approved subject line selected
- [ ] Landing page URL confirmed live before send (do not send to a 404)
- [ ] UTM params in CTA link: `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup`
- [ ] Unsubscribe link functional (test click)
- [ ] Legal footer present verbatim from Diego's approved text
- [ ] Test send to internal Bit2Me team email addresses (minimum 3 people confirm render on mobile)
- [ ] CleverTap open rate tracking enabled (not disabled by default)
- [ ] Scheduled send time confirmed (not sent immediately by mistake)
- [ ] Campaign name in CleverTap: `pbw_warmup_email_v1_apr01`

### Expected Performance Benchmarks
- Open rate: 25-35% (warm base, relevant offer)
- Click-to-open rate: 8-12%
- Conversion from email traffic: 15-30% (highest converting channel)

---

## 6. LinkedIn Outreach Workflow — Day by Day

LinkedIn outreach is the only B2B workstream that can start before Diego approval. Connection requests contain no regulated offer copy — only the identity hook. This gives the team a 3-day head start before April 1.

### Pre-Work Required Before Day 1 of Outreach
- Calendly page live with 20-min slots for April 15 + 16 (minimum 4 slots per day, 8 recommended)
- Google Sheet "PBW_B2B_Targets" populated with at least 50 rows (done in Phase 1)
- LinkedIn connection note template personalized for first 15-20 targets (from 01-b2b-icp-list.md)
- Second outreach owner identified (if Daniel is splitting the list)

### Day-by-Day Workflow

**Day 4 (March 29) — Launch connection wave**
- Send LinkedIn connection requests to all H-priority targets (Deutsche Bank, BlackRock, Fidelity, JPM, Invesco, Fireblocks, BitGo, Circle, Ripple)
- Daily limit: 15-20 requests per day (LinkedIn soft limit). Do not exceed 25.
- Use the 192-character connection note from 01-b2b-icp-list.md verbatim
- Update Google Sheet: mark "Outreach Sent" column with date for each
- Do NOT send the full pitch message yet — connection only

**Day 5 (March 30) — Continue connection wave**
- Send to remaining H-priority + top M-priority targets
- Monitor: who accepted from Day 4 batch? If accepted, wait 24h before sending message
- Do NOT message a connection the same day they accept — wait one full day

**Day 6 (March 31) — First messages to Day 4 acceptances**
- For any Day 4 connection request that was accepted: send persona-appropriate message template (Template A, B, or C from 01-b2b-icp-list.md)
- Include Calendly link: "I have 20-minute slots on April 15-16 — happy to find a time that works around your schedule: [calendly link]"
- Continue sending new connection requests to M-priority and expansion targets

**Day 7 (April 1) — Diego approval day + message wave**
- LinkedIn: continue with Day 5 acceptances receiving messages
- Check Google Sheet: any responses/meetings booked from Day 4-5 outreach?
- For non-acceptances from Day 4 (no response to connection request after 5 days): do not resend, move on
- Begin tracking meeting bookings in Google Sheet

**Days 8-10 (April 2-4) — Follow-up + booking confirmation**
- For any connections who received a message but haven't responded: do not follow up yet (too soon). 5-7 days is the correct follow-up gap.
- Any Calendly bookings: send a confirmation email with booth location, PBW badge, and 3-bullet agenda ("What we'll cover: Bit2Me's B2B API infrastructure, MiCA compliance posture for EU banks, 2026 partnership roadmap")
- Track meeting count. Phase 2 target: 5+ meetings booked (full target of 8-12 is Phase 3)

### LinkedIn Benchmarks (verified sources)
- Connection acceptance rate: 30-50% with personalized note (9.36% reply rate vs 5.44% without)
- Meeting conversion from accepted connections: 10-15%
- At 50 connection requests × 40% acceptance = 20 connections × 12% meeting rate = ~2-3 meetings from Phase 2 alone (remaining meetings close in Phase 3)

### Calendly Page Setup
- **Event type:** "20-min Coffee at PBW — Bit2Me B2B"
- **Available dates:** April 15 and April 16 only
- **Time slots:** 9:00, 9:30, 10:00, 10:30, 11:00, 11:30, 14:00, 14:30, 15:00, 15:30 (Paris time)
- **Buffer between meetings:** 10 minutes (do not book back-to-back — you need to close out notes)
- **Location field:** "Bit2Me booth, Carrousel du Louvre, Paris — [booth number when confirmed]"
- **Confirmation email auto-sent by Calendly:** Include Bit2Me institutional one-pager PDF attachment
- **Calendly plan required:** Essentials ($6/month per calendar) or existing paid plan

---

## 7. Health Score MVP Spec

The Crypto Health Score tool is a booth-only interactive experience. Its purpose is to give a B2C visitor a 60-second engagement that (a) generates a personal output they want to see, (b) creates a conversation hook for the booth rep, and (c) embeds Bit2Me's MiCA positioning in the output. It is NOT a financial product. It is a marketing tool that generates a personalized report.

### What It Is
An interactive web tool (mobile-optimized) that asks 5-7 questions about the user's crypto behavior and produces a "Crypto Portfolio Health Score" with a personalized result that embeds Bit2Me branding and the PBW offer.

### Target Specs for the 10-Day Build

**Platform:** Mobile web (not native app). Works on iPhone Safari + Android Chrome. No download required. Hosted on Bit2Me domain (pbw.bit2me.com/health or similar).

**Input questions (5 questions, multiple choice, 1 screen per question):**
1. How long have you been investing in crypto? (<1yr / 1-3yr / 3yr+)
2. What is your portfolio split? (mostly BTC/ETH / mix of altcoins / DeFi/NFT heavy)
3. How often do you rebalance? (never / quarterly / monthly / weekly)
4. Do you hold your assets on an exchange or in self-custody? (exchange / hardware wallet / split)
5. Are you using a MiCA-regulated exchange? (yes / no / don't know)

**Output:** A score between 0-100 displayed as a visual dial or gauge, with 3 personalized text lines:
- Your score: [number] / 100
- Your strength: [generated from answers, e.g., "Long-term holder — strong conviction"]
- Your gap: [generated from answers, e.g., "Consider a regulated EU exchange for MiCA protection"]
- CTA: "Improve your score — trade fee-free for 60 days at Bit2Me" → link to /pbw landing page

**Shareability:** "Share your score" button generates an image or text card for X/Twitter. This is the viral mechanic. Score must be shareable without sharing the user's actual portfolio data.

**No personal data required:** The tool does not require email or login. It is entirely anonymous until the user opts in via the CTA button. If they click the CTA, they go to the landing page and enter the standard CleverTap funnel.

### Brief for Engineering (10-day window)

| Requirement | Detail |
|------------|--------|
| Timeline | Brief delivered March 31 → build starts April 1 → live by April 10 |
| Dev stack | Existing Bit2Me stack preferred (no new infra dependencies) |
| Hosting | Bit2Me domain, mobile-first |
| Design | 5 question screens + 1 results screen. Design brief to Kira/design team |
| Inputs | 5 multiple choice questions, no free text |
| Scoring logic | Simple weighted sum: Daniel defines weights per answer. No ML, no external API. |
| Output | Score (0-100) + 2 text lines (strength + gap) + CTA to /pbw |
| Share | Native share API (Twitter intent URL). Static image share optional if time allows. |
| Analytics | Each completion fires an event to CleverTap: `health_score_completed` with score value |
| No PII | No login, no email required on tool itself |
| Diego review | Check: does the "gap" text recommendation constitute financial advice? Brief Diego on tool concept by March 31 to get early signal before it's built |

**Budget:** ~€3-5K internal dev estimate (per Phase 1 decisions). Not for external agency — internal build only.

**Risk:** If the "gap" recommendation language ("Consider a regulated EU exchange") triggers Diego review for financial advice concerns, the scoring output must be softened to descriptive only, not prescriptive. Build the output as a configurable copy field, not hardcoded strings, so copy can be updated post-Diego review without a code change.

---

## 8. Social Content Calendar

### Platform Priority
1. **X/Twitter** — primary channel for crypto-native audience. Every post goes here.
2. **LinkedIn** — institutional/B2B audience. Adapt X posts, add more context. 3-4 posts per week.
3. **Instagram** — optional, only if there is a designated visual content creator on the team. Do not start Instagram if there is no owner.

### Content Cadence by Phase

**Pre-event (March 29 - April 14) — 2-3 posts per week on X, 2 per week on LinkedIn**

Content pillars for pre-event:
- **Positioning:** "Spain's first MiCA exchange is going to PBW" — 2-3 posts total
- **Offer:** "60-day zero fees, PBW exclusive" — 2-3 posts total (only after Diego approval)
- **Proof:** Bank backing, Europol signal, user growth stats — 2-3 posts
- **Event hype:** "See you in Paris" + Carrousel du Louvre visual — 1-2 posts
- **Thought leadership:** Short takes on MiCA, institutional crypto, European regulation — 1-2 posts per week (can start before Diego approval — no offer copy)

**Event week (April 14-16) — 2 posts per day minimum**

- Day -1 (April 14): "We're in Paris. Dinner tonight. Booth opens tomorrow." [institutional dinner context if shareable]
- Day 1 (April 15): Booth opening + event energy + "Come find us at [booth number]"
- Day 1 afternoon: A moment, a conversation, or a quote from the floor
- Day 2 (April 16): "Last day — find us before the close" + offer reminder
- Day 2 EOD: "That's a wrap. More to come." [lead into post-event sequence]

**Post-event (April 17-24) — Part of Phase 5, but draft content now**
- Gratitude + recap stats (registrations, meetings, moments)
- Offer expiry reminder if registration window is closing

### Buffer Setup
- **Workspace:** Create a Buffer calendar for `bit2me_pbw_2026` tag
- **Channels:** Connect X/Twitter + LinkedIn minimum
- **Schedule posts 1-2 weeks ahead** for pre-event content; leave April 15-16 flexible for real-time content
- **Tags:** Use Buffer's tag feature to label posts by pillar: `positioning`, `offer`, `proof`, `event`, `thought_leadership`
- **Draft all 15+ posts** in Buffer before April 1 so approved copy can be swapped in after Diego without rebuilding

**Critical:** Draft posts with placeholder copy `[OFFER COPY — PENDING DIEGO APPROVAL]` in the Buffer draft. On April 1 when Diego approves, replace placeholders and schedule. This avoids losing the structural work while waiting for approval.

### Content Types That Work for This Audience

| Content Type | Why It Works at PBW | Platform |
|-------------|--------------------|---------||
| Short stat + visual | "€5.3B trading volume. 8x growth since 2023." | X, LinkedIn |
| Bank logo graphic | "Backed by these institutions" + bank logos | LinkedIn (high shares) |
| Europol proof point | "We process Europol's seized crypto. Compliance is the product." | X, LinkedIn |
| Team/booth photos | Authenticity signal. Institutional audiences trust faces. | X, LinkedIn |
| Event moment clips | 15-second vertical video from the floor | X (if bandwidth allows) |
| Offer card | "60 days zero fees — exclusively at PBW" | X |

---

## 9. Luma Side Events — Research and Evaluation

### What Exists on Luma for PBW 2026

Luma has a dedicated PBW 2026 hub at luma.com/paris-blockchain-week. Side events span approximately April 4-16, with the bulk concentrated April 13-16 (around the main event). Some events are invite-only; others are open registration.

**Confirmed events on Luma (as of research date):**

| Event | Date | Audience | Access | Priority for Bit2Me |
|-------|------|----------|--------|---------------------|
| Paris Blockchain Week Side Events Hub | Apr 4-16 | All attendees | Open | Use as discovery index |
| Founders & Investors Brunch | Apr 8, 11am-2pm | Web3 founders, investors | Invite-only | HIGH — VC/fund contacts overlap with B2B targets |
| VCs & LPs Cocktail Hour | Apr 8, 3pm-5pm | VC funds, LPs | Invite-only | HIGH — A16z, Pantera, Animoca confirmed past attendees |
| Crypto Compliance & Legal Drink #2 | TBD (around PBW) | Legal, compliance officers | Open | HIGH — regulatory credibility audience, Bit2Me's MiCA story lands well |
| Start in Block | Apr 16 | Founders, startup ecosystem | Open | MEDIUM — early stage, not institutional |

**Additional discovery sources:**
- cryptonomads.org/ParisBlockchainWeek2026 — aggregates side events not on Luma
- PBW sponsor Slack/Telegram groups (check with PBW organizer contact)
- Twitter search: "PBW side event" + "Paris Blockchain Week party" filtered to April 2026

### How to Evaluate Side Events for Bit2Me

Score each event on 3 dimensions:

| Dimension | Why It Matters | Score |
|-----------|---------------|-------|
| Audience overlap with B2B ICP | Are fund managers, bank execs, compliance officers attending? | 1-3 |
| Access difficulty | Open = easy = less exclusive. Invite-only = harder but more targeted. | 1-3 |
| Timing relative to booth | Events Apr 13-15 (before or during) are better than Apr 16 EOD | 1-3 |

**Target: 5-8 events identified, RSVP submitted to all, 3-4 confirmed before April 10.**

### RSVP Strategy
- For open events: register on Luma with Bit2Me email, mark as "attending"
- For invite-only events: find the host on LinkedIn (usually a VC or sponsor), send a connection request with event context ("I saw you're hosting the VCs & LPs Cocktail Hour — we're Spain's first MiCA exchange, would love to attend")
- Do not wait for invite-only events to invite you — proactively reach out to the host

### The Iberoamerican Crypto Happy Hour Opportunity

From Phase 1 research: no confirmed Spanish-language side event exists at PBW 2026. Bit2Me could host one (30-50 people, light cost, massive differentiation). If this is in scope, it should be initiated in Phase 2 with a venue check — a rented bar or private room in Paris for an evening costs €2,000-5,000 including drinks. This is a Phase 3 decision but the venue inquiry starts in Phase 2.

---

## 10. Wave Structure Recommendation

Phase 2 contains 5-6 plans. The wave structure reflects the Diego gate.

### Wave 1 (March 29-31) — Pre-Diego, fully parallel
All 4 can run simultaneously:

| Plan | Deliverable | Owner |
|------|------------|-------|
| 02-01 | Landing page brief delivered to dev/design; CleverTap pbw_lead tag spec written; UTM taxonomy doc written | Daniel + Katy + Alvaro |
| 02-02 | Health Score MVP brief to engineering; scoring logic defined; question set finalized | Daniel |
| 02-03 | LinkedIn connection requests sent to all H-priority targets; Calendly live | Daniel |
| 02-04 | Luma side event map complete; initial RSVPs submitted; social calendar drafted in Buffer (placeholder copy) | Daniel |

### Wave 2 (April 1-4) — Post-Diego, sequential within stream but parallel across streams
Triggered by Diego approval. All 3 can run simultaneously once the landing page URL is confirmed:

| Plan | Deliverable | Dependencies |
|------|------------|-------------|
| 02-05 | Landing page goes live; X/Twitter ads launch (pending X certification); Google ads decision made | Diego approval + dev/design completing build from 02-01 |
| 02-06 | Email #1 sent to existing users; CleverTap tracking confirmed | Diego approval + landing page URL live |
| 02-07 | Social calendar offer posts scheduled in Buffer; LinkedIn message templates sent to Day 4-5 acceptances | Diego approval (for offer posts); Day 4-5 connection acceptances (for LinkedIn messages) |

**Wave dependency map:**
```
[Wave 1: 02-01, 02-02, 02-03, 02-04 — all parallel, start March 29]
                        ↓
              [Diego approval April 1]
                        ↓
[Wave 2: 02-05, 02-06, 02-07 — all parallel, start April 1]
```

---

## 11. Execution Risks Specific to Phase 2

### Risk 1: X/Twitter Ad Certification Delay
**What breaks:** If Bit2Me's X crypto exchange certification is expired or absent, ads cannot launch. The certification approval process takes 2-7 business days. If this check is not done on Day 4 (March 29), the ads could slip past April 4 — outside the Phase 2 window.
**Mitigation:** Check certification status March 29 (first action of Phase 2). If expired, submit renewal immediately. Do not wait.
**Signal this is happening:** Ads submitted to X Manager but sitting in "Under Review" for 48h+ = certification issue.

### Risk 2: Diego Approval Slips Past April 1
**What breaks:** Landing page, paid ads, and email are all blocked. The entire Phase 2 Wave 2 cannot execute. Phase 3 also compresses.
**Mitigation:** Diego received the complete package on March 26 (Phase 1 output). The 15-minute call offer is on the table. Follow up on March 30 to confirm he is on track. If Diego cannot approve by April 1: negotiate a partial approval — approve the landing page and email first, ads can follow. Any approved copy is better than no approved copy.
**Signal this is happening:** No Diego response or acknowledgment by March 30 = follow-up call required.

### Risk 3: Landing Page Build Not Ready When Copy Arrives
**What breaks:** Diego approves on April 1 but the page structure isn't built. Copy sits in a document while dev builds from scratch. Page goes live April 5 instead of April 1. Ads launch late.
**Mitigation:** The entire purpose of the Wave 1 plan 02-01 is to deliver the brief so the page is structurally ready by March 31. When Diego's approved copy arrives on April 1, it is a copy drop-in, not a page build. If dev is behind, the page can go live with placeholder text initially and the approved copy swapped in within hours.
**Signal this is happening:** No dev ticket opened by March 30.

### Risk 4: CleverTap pbw_lead Tag Not Firing on Submit
**What breaks:** Users fill out the landing page form, but nothing fires in CleverTap. No journey trigger, no tagging, no lead capture. All ad spend generates zero measurable leads.
**Mitigation:** Katy tests the integration before the page goes live. Test with an internal email address. Confirm the `pbw_lead` event appears in CleverTap real-time activity. Do not launch ads until this is confirmed.
**Signal this is happening:** Submit the form yourself on staging. Check CleverTap real-time. If the event doesn't appear within 60 seconds, something is broken.

### Risk 5: LinkedIn Outreach Stalls Due to No Calendly
**What breaks:** LinkedIn connections are accepted but there is no booking link to send them. The window of intent is 24-72 hours after connection acceptance. If Calendly is not live, that window closes.
**Mitigation:** Calendly is the first thing to set up in Phase 2, before the first connection request goes out. It is a 20-minute task.
**Signal this is happening:** Day 5 and Calendly has not been set up.

### Risk 6: Health Score Build Requires Diego Signoff That Wasn't Anticipated
**What breaks:** The output copy ("Consider using a regulated EU exchange") might be interpreted as financial advice or a financial recommendation, which requires different MiCA compliance treatment than promotional copy.
**Mitigation:** Brief Diego on the Health Score concept by March 31 — a one-paragraph description of the tool + a sample output. Get his signal before the build is complete. Build the output text as configurable copy, not hardcoded strings. This allows changes post-Diego review without a code change.
**Signal this is happening:** Engineering builds the tool with hardcoded output strings that Diego then requires to be changed after launch.

### Risk 7: Luma Events Fill Before Bit2Me RSVPs
**What breaks:** Invite-only events close before the team submits an RSVP request. The highest-value side events (VC cocktail hour, Founders brunch) may have limited seats.
**Mitigation:** Map and RSVP to Luma events in Wave 1 (March 29-31), not Wave 2. This is entirely pre-Diego and has no blockers. First-come-first-served applies to most invite-only side events.
**Signal this is happening:** Wave 1 plan 02-04 is not started by March 30.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| UTM tracking | Custom analytics script | BigQuery + UTM params (existing) | Already wired. New script = new bugs + attribution gaps |
| Email delivery | SMTP from Bit2Me servers | CleverTap (existing) | Deliverability, unsubscribe management, GDPR consent tracking all handled |
| B2B CRM | Notion database, Airtable, HubSpot | Google Sheet | 20-day runway. A new tool will not be configured in time. Spreadsheet is ready in 10 minutes. |
| Meeting booking page | Custom form | Calendly | Calendly sends confirmations, handles timezones, blocks double-bookings automatically |
| QR code generation | Custom QR tool | Bitly or UTM.io | Branded short links with click analytics already supported |
| Social scheduling | Manual posting | Buffer | Pre-schedule prevents "forgot to post during the event" failure mode |
| Health Score logic | ML model, external API | Simple weighted sum | 10-day build, booth demo tool. A/B test logic has no place here. |

---

## Architecture Patterns

### UTM Naming Convention (single owner: Alvaro)

One person creates all UTMs. No exceptions. The naming convention is:

```
utm_source: [twitter | google | linkedin | email | booth]
utm_medium: [paid | organic | clevertap | qr | lanyard | nfc]
utm_campaign: [pbw2026 | pbw2026_b2b | pbw2026_warmup | pbw2026_onsite]
utm_content: [optional — for creative variant tracking in ads]
```

All UTM-tagged links go in a Google Sheet named "PBW UTM Master" with columns: Link name / Full URL / Short URL (Bitly) / Owner / Date created. This is the attribution source of truth.

### CleverTap Event Taxonomy

New CleverTap events for this project:
- `pbw_lead` — fires on landing page form submit (B2C capture)
- `health_score_completed` — fires on Health Score tool completion
- `pbw_email_clicked` — auto-tracked via CleverTap campaign analytics

User tags:
- `pbw_2026_lead` — applied to any user who submits the landing page form
- `pbw_2026_email_warmup` — applied to users in the email #1 campaign

Journey name: `pbw_2026_b2c_journey` (Katy builds and owns)

---

## Common Pitfalls (Phase 2 Specific)

### Pitfall: Ads go live before landing page is ready
The ad destination URL must resolve and the CleverTap tag must be firing before a single ad impression is purchased. Run the test submission flow before activating campaigns in X Ads Manager. Budget wasted on traffic to a 404 or untracked page is unrecoverable.

### Pitfall: Email send triggers before landing page is live
If the email goes out and the landing page link 404s, the email cannot be resent. Users click, see a dead link, and the trust signal is damaged. Send order must be: landing page live → CleverTap integration tested → email sends.

### Pitfall: LinkedIn messages sent too soon after connection
Sending the pitch message within hours of connection acceptance is a conversion killer. A 24-hour gap is the minimum. The workflow must enforce this via the Google Sheet tracking column — only send a message when "Connection Accepted Date" shows the day before.

### Pitfall: Health Score tool uses hardcoded copy
If the output text is hardcoded in the UI component, any Diego revision requires a code deploy. Build it as a configurable content layer (JSON config file or CMS field). This is a 2-hour architecture decision that prevents a potential 2-day blocker.

### Pitfall: Buffer posts published before Diego approval
Social posts containing the offer ("60 days zero fees") are regulated copy. If they are posted before Diego approves, Bit2Me is in violation. Draft posts with placeholder copy in Buffer. Do not schedule — keep as drafts. Only schedule once Diego's approval is in hand.

---

## Sources

### Primary (HIGH confidence)
- Phase 1 output files (offer brief, Diego package, B2B ICP list) — locked decisions from Daniel
- STATE.md / ROADMAP.md — hard deadlines and team ownership
- X Ads policies — business.x.com/en/help/ads-policies/ads-content-policies/financial-services
- CleverTap documentation — docs.clevertap.com (segments, email campaigns, event tracking)
- Luma PBW 2026 side events hub — luma.com/paris-blockchain-week

### Secondary (MEDIUM confidence)
- X ad creative specs 2026 — veuno.com/x-formerly-twitter-ad-specs-your-guide-for-2026/ (verified against X Ads Manager documentation)
- LinkedIn connection request benchmarks — phantombuster.com/blog/social-selling/linkedin-connection-request-limit/ + belkins.io/blog/linkedin-outreach (multiple sources converge on 30-50% acceptance rate for personalized notes)
- LinkedIn outreach workflow — salescaptain.io/blog/cold-linkedin-outreach, clevenio.com/ultimate-guide-to-linkedin-outreach/
- CleverTap segment setup — docs.clevertap.com/docs/create-segments
- Buffer social calendar setup — buffer.com/resources/social-media-calendar/

### Tertiary (LOW confidence)
- Health Score dev estimate (€3-5K, 10 days) — internal decision from STATE.md, not externally verified
- Google Ads crypto certification timeline — based on general knowledge, not a confirmed Bit2Me certification status

---

## Metadata

**Confidence breakdown:**
- Critical path analysis: HIGH — drawn from verified Phase 1 decisions and hard deadlines
- Landing page brief: HIGH — based on prior research + existing toolstack decisions
- X/Twitter ad setup: MEDIUM-HIGH — X policy page verified, creative specs verified against 2026 sources
- CleverTap email setup: MEDIUM — official CleverTap docs confirm segment mechanics; Bit2Me-specific segment criteria require Alvaro validation
- LinkedIn workflow: MEDIUM — multiple converging sources on timing and benchmarks
- Health Score spec: MEDIUM — MVP spec drawn from project decisions; Diego compliance risk is unverified
- Social calendar: HIGH — Buffer mechanics are straightforward; content recommendations are pattern-based
- Luma side events: MEDIUM — specific events confirmed via search; completeness of side event list cannot be guaranteed until April

**Research date:** 2026-03-30
**Valid until:** 2026-04-10 (event-specific research; irrelevant after April 15)
