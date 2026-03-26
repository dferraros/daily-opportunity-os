# Research Summary — Bit2Me @ Paris Blockchain Week 2026

**Synthesized:** 2026-03-26
**Inputs:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md, PROJECT.md
**Consumer:** gsd-roadmapper (phase planning), Daniel (execution decisions)
**Overall confidence:** MEDIUM-HIGH — core claims (PBW facts, Bit2Me positioning, channel benchmarks) verified across 3+ independent sources. Budget estimates and conversion benchmarks are industry proxies, not Bit2Me-specific data.

---

## 1. Event Overview

Paris Blockchain Week 2026 runs **April 15–16 at Carrousel du Louvre, Paris**. It is Europe's most institutionally dense digital assets event: 10,000+ attendees from 100+ countries, 70%+ C-suite, €999–€3,699 ticket prices, 36,000 networking meetings generated in 2025, 450+ journalists. The 2026 theme is "Where Institutions and Digital Assets Finally Meet." Emmanuel Macron is the first sitting G7 head of state to address a digital assets conference — at PBW 2026.

**What this means operationally:** PBW is not a retail acquisition event. The ticket price structurally excludes casual crypto users. The audience is capital-allocating professionals, regulators, and institutional operators. Mass-market tactics that work at Token2049 or ETH Denver generate low-quality leads here. The correct strategy is dual-track from day one: a B2C offer for crypto-native professionals who personally trade, and a B2B track targeting banks, fintechs, and asset managers for partnership conversations.

**Competitive context:** Bybit EU is lead/title sponsor with CEO Ben Zhou on main stage (estimated spend €150k–€300k). Kraken, KuCoin, Crypto.com, Circle, Ripple, Fireblocks, and BitGo are confirmed sponsors. Coinbase sends executive representation. Bit2Me's presence is booth only, no confirmed speaking slot, which means the brand must earn share of voice through differentiation and pre-event campaigns — not main stage visibility.

---

## 2. Bit2Me's Unique Positioning

Bit2Me holds a differentiation stack that no other exchange at PBW can replicate in the European market:

| Asset | Claim | Replicable by Competitors? |
|-------|-------|---------------------------|
| First Spanish CASP under MiCA | CNMV authorized before Bybit EU's Austrian authorization | No — timing-specific |
| MiCA EU passport | Legal operation across all 27 EU member states | Partially — others claim MiCA but not Spain-first |
| Backed by Bankinter, BBVA, Unicaja, Cecabank, Tether | Only exchange at PBW backed by top Spanish banks | No — bank-specific |
| Europol and Interpol seized crypto processing | Handles EU law enforcement seized assets | No — unique institutional trust signal |
| 5.3 billion EUR trading volume (8x growth since 2023) | Verified growth trajectory | No direct equivalent in Spanish market |
| B2B revenue growing to 27% of total | Bank API infrastructure play, not just retail | No other exchange positions this way at PBW |

**The single message that works at PBW:** "Spain's first MiCA-authorized exchange, backed by Bankinter and BBVA, and trusted to process Europol's seized crypto."

This is concrete, verifiable, and impossible for Bybit EU, Kraken, or Coinbase to claim about the Spanish/Southern European market. Bybit EU plays the same MiCA card but from Austrian authorization — Bit2Me's CNMV authorization date is earlier and Spain-specific. The bank backing (Bankinter joining BBVA and Tether in January 2026) resonates immediately with TradFi executives in the room.

---

## 3. Recommended Strategy — Dual B2C/B2B Tracks

Run two fully separate tracks. These are different audiences, different messages, different collateral, different follow-up systems.

### B2C Track — Crypto-native professional who trades personally

**Goal:** New user sign-ups with offer redemption from professionals attending PBW who have not yet used Bit2Me.

Key decisions:
- Lead with the offer, not the brand. "60 days zero fees" converts better than "Europe's leading exchange."
- Dedicated event landing page live by Day 7. Not the homepage. Not the standard sign-up page. Single-purpose page with the offer front and center.
- CleverTap sequence pre-built before the event. B2C follow-up automated, fires within 1h of QR scan. If it is not built before the event, it will not exist when it matters.
- UTMs on every source before a single asset is drafted. BigQuery cohort pre-configured to track PBW sign-ups separately from organic.
- Two existing user emails: D-7 awareness ("we'll be at PBW"), D-2 last call ("here's your exclusive offer"). Segment: Spain + EU, KYC-complete, at least one deposit.

### B2B Track — Institutional executive, fintech founder, bank API buyer

**Goal:** 8–12 pre-booked meetings with qualified institutional targets. 2–3 concrete partnership conversations that move to a follow-up call within 2 weeks of the event.

Key decisions:
- Start B2B outreach on Day 1 of the sprint, not Day 10. Calendars at PBW fill 2 weeks in advance.
- Build ICP list of 50–100 targets from PBW directory, sponsor list, and speaker list. Focus: banks with crypto desks, fintechs building on crypto rails, EU asset managers, institutional custody providers (Fireblocks, BitGo's clients).
- Lead message is specific: "We're Spain's first MiCA-authorized CASP. B2B revenue now 27% of total. We're building regulated infrastructure for EU banks. 20 minutes at PBW?"
- Track in a Google Sheet. No new CRM tool. 2-week runway is not enough to configure and test a new system.
- Post-event: manual personalized follow-up from Daniel within 24h for hot leads. Assign this as an on-site task at the end of each event day — not a post-event task.

### Booth Configuration

Two distinct physical zones:
- **B2C zone:** Product demo screen, sign-up QR on signage and lanyard backs, event offer prominently displayed, one device for assisted mobile sign-up
- **B2B zone:** Corner table, appointment-only conversations, printed institutional one-pager (bank logos + MiCA authorization date + API infrastructure facts), NFC card taps

One qualifying question routes every visitor: "Are you here for personal trading or exploring B2B/API integration?" Answer determines which zone and which follow-up track the person enters.

---

## 4. Recommended Offer

**Primary recommendation: 60-day zero trading fees for new accounts opened via the PBW landing page.**

Rationale:
- Fee-waiver offers drive higher first-trade velocity than cash bonuses because the barrier to first action is lower
- "60 days" is more memorable than "30 days" — stronger at PBW's premium positioning
- Zero fees is an institutional-friendly frame: "priority onboarding" not "sign-up bonus"
- Structurally simpler than deposit bonuses for MiCA compliance. No cash or token distribution, just fee suppression.
- Requires Diego review but avoids the more complex MiCA Article 77 bonus promotion rules that apply to cash distributions

**Premium tier variant (for B2B conversations):** Frame as "Priority onboarding + dedicated account access" for institutional sign-ups. Same economics, different positioning. Do not use "discount" language in B2B materials.

**What to avoid:**
- Cash bonuses: MiCA bonus promotion rules add legal complexity that may delay Diego approval
- NFT/POAP drops: tech friction, wrong audience at PBW
- Sweepstakes: attracts prize hunters, not buyers. Post-event conversion from raffle leads is near zero.
- "0% fees" framed as retail promotion: reframe as "institutional-grade access for professionals"

**Diego approval must cover:** Fee-waiver mechanics, "zero fees" claim in MiCA context, landing page copy, ad copy, email subject lines, and all booth claim text. Batch everything in one review package by Day 4–5. Set a hard approval deadline.

---

## 5. Top 3 Differentiators vs Competitors

**1. MiCA Spain-first + bank backing (Bankinter + BBVA + Cecabank)**

No other exchange at PBW was first authorized by Spain's CNMV. Bybit EU's MiCA claim originates from Austrian authorization. Coinbase's EU operations are Ireland-based. Bit2Me's bank investors — Bankinter, BBVA, Unicaja, Cecabank — are household names to every European bank executive attending PBW. A single banner with bank logos next to the Bit2Me logo is a conversation-stopper for institutional visitors. Print the CNMV authorization date on collateral. "Spain's first, since [date]" beats every generic "MiCA-compliant" claim.

**2. Europol and Interpol seized crypto processing**

This is an institutional trust signal no consumer exchange can manufacture. EU law enforcement trusting Bit2Me to handle seized assets reframes "Spanish crypto exchange" as "regulated financial infrastructure." Use it as a conversation opener in every B2B interaction: "We handle seized crypto for Europol and Interpol. Compliance is not a box we check — it is the product." No competitor at PBW can make this claim.

**3. European exchange built for the Spanish-speaking world**

All major competitors position as "global exchange expanding into Europe." Bit2Me is "European exchange built here, for this market." At a conference with 100+ nationalities, Spanish identity is distinctive and memorable, not limiting. No confirmed Spanish-language side event exists at PBW 2025 or 2026. Even a simple Iberoamerican Crypto happy hour for 30–50 people creates a brand moment that Bybit EU's €300k spend cannot replicate because they are a global exchange, not a Spanish-European one.

---

## 6. Critical Path

Nothing starts until the offer is defined. This is not optional — every other deliverable is downstream of it.

```
Day 1–2:  Define the event offer (internal decision only)
    |
Day 3–5:  Batch ALL copy to Diego in one package:
    |      landing page, ads, emails, booth claim text
    |      Set hard approval deadline: "we need approval by Day 7"
    |      (Parallel, no Diego dependency) Start B2B ICP list building
    |
Day 5–7:  Diego approves copy
    |      Landing page live with approved copy + all UTMs pre-wired
    |      B2B LinkedIn outreach wave 1 sends (connection requests, no pitch)
    |      CleverTap pbw_lead tag + journey configured
    |
Day 7–10: Paid ads launch (X/Twitter primary, Google secondary)
    |      Existing user email #1 (awareness — "we'll be at PBW")
    |      Meeting booking page live (Calendly, 20-min PBW slots)
    |
Day 10–14: B2B email outreach to non-LinkedIn-responders
    |       Existing user email #2 (urgency — "here's your exclusive offer")
    |       Booth design brief to print production (5–7 day lead time minimum)
    |       Post-event CleverTap sequences drafted and configured (non-negotiable)
    |       RSVP to 3–5 PBW side events from Luma calendar
    |
Day 14:   Team booth runbook finalized (demo script, qualifying question, lead capture flow)
    |      Meeting confirmations sent to all pre-booked B2B contacts
    |
Apr 15–16: Event execution
    |      EOD each day: all QR/NFC/badge data uploaded to CleverTap (Katy owns this)
    |      EOD each day: hot B2B leads get Daniel personal LinkedIn message same evening
    |
Apr 16 EOD: Final lead data upload
    |
Apr 17 (<24h): B2C email #1 auto-fires from CleverTap (triggered by pbw tags)
               Daniel sends personal emails to all H-temperature B2B leads
               B2B leads logged in tracking sheet with temperature + next action
```

**Hard blockers in dependency order:**
1. Offer definition (Day 1–2) — nothing else can start without it
2. Diego legal review (Day 3–7) — nothing goes external without it
3. Landing page + UTMs live (Day 5–7) — ads need a destination URL
4. CleverTap sequences pre-built (by Day 14) — post-event nurture cannot be built post-event when the team is exhausted

---

## 7. Top 5 Pitfalls to Avoid

**Pitfall 1: Swag trap — booth traffic with zero lead capture**
The booth attracts foot traffic, swag disappears, and the post-event report shows "1,200 visitors" with zero verified pipeline. Prevention: gate premium swag behind a digital capture action (QR scan to landing page, or email entry). Designate one lead capture owner per shift. QR code must point to the event landing page, not the homepage.

**Pitfall 2: No dedicated event landing page**
Paid ads advertising a specific PBW offer that link to the Bit2Me homepage produce message-to-landing mismatch. Conversion drops from 8–15% to below 1%. Hard deadline: landing page live by Day 7. This is also the URL that every ad, email, and QR code points to — it is the single most leveraged asset in the B2C track.

**Pitfall 3: Diego bottleneck killing launch timelines**
All copy submitted to Diego on Day 12 of a 14-day sprint. Landing page goes live Day 13. Ads launch Day 14 (event start). Zero learning phase. Diego is already a known bottleneck across multiple journeys. Prevention: batch everything in one package to Diego by Day 4–5. Set a hard approval deadline in the request. Brief him on the event context so he can pre-approve a framework that accelerates individual asset review.

**Pitfall 4: B2B void — showing up with no pre-booked meetings**
PBW institutional executives arrive with full calendars. Walk-up booth conversations do not produce institutional partnerships. "We'll network at the event" is not a B2B strategy. Prevention: start outreach on Day 1 of the sprint. Goal is 8–12 pre-booked 20-minute meetings before April 15. Five meetings minimum is the floor below which the B2B track has failed.

**Pitfall 5: Post-event follow-up silence**
Leads contacted after 48 hours convert at 60% lower rate than leads contacted within 24h. By Day 6, 300 other exhibitors have already emailed everyone. Prevention: post-event CleverTap sequences must be drafted and configured before the event. B2C auto-fires within 1h of QR scan. B2B manual follow-up is assigned as an on-site task at the end of each event day — it is not a post-event to-do.

---

## 8. Tools Stack

| Function | Tool | Owner | Notes |
|----------|------|-------|-------|
| Email + push automation | CleverTap (existing) | Katy | Pre-configure all PBW sequences before event |
| Landing page | Bit2Me existing web infra | Dev + Design | Dedicated URL (/pbw or /paris), not homepage |
| On-site lead form | Typeform + Zapier + CleverTap | Katy | 3 fields max: email + name + "trading or B2B?" toggle |
| QR generation + tracking | Bitly or UTM.io | Daniel | Branded short links, UTM params pre-wired, one naming convention owner |
| NFC digital card | Popl or Wave Connect | Booth reps | Each rep carries one card. Tap logs rep ID + timestamp. |
| B2B meeting booking | Calendly | Daniel | 20-min "Coffee at PBW" slots, Apr 15–16 |
| B2B lead tracking | Google Sheet | Daniel | Name / Company / Role / Meeting held / Temp (H/M/C) / Next action |
| Audience segmentation | BigQuery (existing) | Alvaro | Pull pre-event segment + configure PBW cohort tracking before event |
| Attribution | BigQuery + UTM params | Daniel | UTM taxonomy doc Day 1 — single owner, no improvised tags |
| Paid ads | X Ads Manager (direct) | Daniel | 10-day burst campaign. X ~60% crypto ad approval vs Meta ~50% |
| Social scheduling | Buffer or native scheduler | — | Pre-schedule event-week content; do not improvise on-site |
| Side event discovery | Luma.com | Daniel | Map calendar by Day 7; RSVP to 5–8 events |
| Badge scanner (if provided) | PBW organizer app | Booth reps | Confirm with organizer pre-event; if available, replaces Typeform on-site |

**Do not introduce:** New CRM tool (2-week runway is insufficient), Eventbrite (irrelevant for exhibitors), Web3 lead capture (POAP, wallet connect — wrong audience for PBW's TradFi attendees), paper business cards as primary capture method.

---

## 9. Budget Range Estimate by Workstream

| Workstream | Low | High | Notes |
|------------|-----|------|-------|
| Landing page (design + dev) | €500 | €2,000 | On existing Bit2Me infra. Cost is design + dev time. |
| Paid ads — X/Twitter + Google | €1,000 | €4,000 | €500–2k X, €500–2k Google. 10-day burst. |
| Booth design + print production | €2,000 | €6,000 | Banners, one-pagers, QR/NFC cards. Excludes booth space fee. |
| Swag (premium, gated) | €1,500 | €4,000 | 200–500 units. Quality over volume — PBW audience is not a T-shirt crowd. |
| NFC cards (Popl or Wave Connect) | €200 | €500 | 3–5 booth reps. Per-rep cards with CRM sync. |
| B2B tools (Calendly Pro) | €20 | €60 | 1 month. |
| Private side event / dinner | €0 | €10,000 | Optional. High ROI per meeting if 15–20 institutional targets confirmed. |
| On-site social content creator | €0 | €2,000 | Only if dedicated person assigned; otherwise ad hoc. |
| Staff travel + hotel Paris | €1,500 | €5,000 | 2–3 people, 2–3 nights. |
| **Total range** | **€6,720** | **€33,560** | Excludes PBW booth space fee (assumed already contracted). |

**Budget recommendation:** Target €12,000–€18,000 total excluding the booth fee. The single highest-ROI action is the 24h post-event follow-up system (zero incremental cost, highest conversion leverage). The single biggest waste risk is over-spending on swag without a corresponding lead capture system.

---

## 10. Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| PBW 2026 event facts (dates, audience, sponsors) | HIGH | Official PBW site + multiple March 2026 news sources |
| Bit2Me positioning claims (MiCA, bank backing, Europol) | HIGH | PR Newswire, CoinDesk, CNMV public records |
| Bybit EU as lead sponsor with dominant share of voice | HIGH | Chainwire March 2026, Finbold, multiple confirmations |
| Offer mechanics (fee-waiver recommendation) | MEDIUM | Industry conversion data + MiCA framework analysis — not Bit2Me-specific |
| Conversion benchmarks (8–15% landing page CVR) | MEDIUM | Multiple marketing sources — event-type variation is real |
| B2B meeting targets (8–12 pre-booked meetings) | MEDIUM | Industry benchmarks for 2-person B2B team at 2-day event |
| Side event ROI (+250% growth in experiential formats) | MEDIUM | Ch3 Agency 2025 report — single source, directionally credible |
| Budget estimates | LOW-MEDIUM | Proxies from comparable crypto event activations — not Bit2Me historical |

**Gaps requiring validation before execution:**
1. **Diego's bandwidth:** He is already the bottleneck across 7+ active journeys. Confirm he can prioritize PBW review by Day 4–5 before the roadmap is built around that assumption.
2. **Google Ads certification status:** Crypto exchange ads on Google require platform certification. Verify Bit2Me's EU eligibility before the ads workstream is scoped into Phase 1.
3. **PBW badge-scan app:** Confirm with PBW organizers whether exhibitors get access to a lead retrieval app. If yes, this changes the on-site capture architecture.
4. **B2B outreach ownership:** Daniel alone cannot own B2B list building + LinkedIn outreach + booth + campaigns simultaneously. Assign a second owner for B2B outreach before the roadmap is finalized.
5. **Offer final decision:** This is the Day 1–2 blocker. If it slips to Day 5–7, the entire downstream timeline compresses and the launch window collapses.

---

## Sources (Aggregated)

- Paris Blockchain Week 2026 official site: https://www.parisblockchainweek.com/
- PBW 2026 bridge institutions announcement: https://chainwire.org/2026/03/03/paris-blockchain-week-2026-returns-to-bridge-institutions-and-digital-assets/
- Bybit EU lead sponsor: https://chainwire.org/2026/03/12/bybit-eu-leads-paris-blockchain-week-2026-as-title-sponsor-ceo-ben-zhou-to-take-the-stage/
- Bit2Me B2B infrastructure pivot: https://www.coindesk.com/business/2026/02/23/tether-backed-crypto-exchange-is-ditching-the-retail-label-to-build-the-secret-plumbing-for-europe-s-biggest-banks
- Bankinter investment in Bit2Me: https://www.coindesk.com/business/2026/01/14/spanish-bank-bankinter-joins-bbva-and-tether-with-stake-in-crypto-exchange-bit2me
- Bit2Me MiCA authorization: https://www.prnewswire.com/news-releases/bit2me-first-spanish-speaking-fintech-authorized-as-a-crypto-asset-service-provider-under-the-mica-regulation-by-the-cnmv-302516225.html
- Tether EUR 30M investment: https://www.coindesk.com/business/2025/08/07/tether-leads-eur30m-investment-round-in-spanish-crypto-exchange-bit2me
- Crypto Event Report 2025 — Ch3 Agency: https://www.ch3.agency/insights/crypto-event-trends-2025/
- Landing page conversion benchmarks: https://unbounce.com/average-conversion-rates-landing-pages/
- LinkedIn B2B outreach performance: https://growleads.io/blog/linkedin-outreach-strategy-what-actually-works-in-2025-expert-guide/
- Post-event follow-up timing: https://www.default.com/post/event-follow-up-email
- NFC/QR lead capture benchmarks: https://www.mobilocard.com/post/exhibition-lead-capture
- PBW side events calendar: https://luma.com/paris-blockchain-week
- B2B event marketing pipeline: https://www.linkedin.com/business/marketing/blog/trends-tips/b2b-event-marketing-pipeline-impact
- Lead generation at events 2025: https://www.leadbeam.ai/blog/lead-generation-at-events
- PBW 2026 attendee analysis: https://vendelux.com/insights/paris-blockchain-week-summit-2026-attendee-list/
