# Technology & Tactics Stack

**Project:** Bit2Me @ Paris Blockchain Week 2026
**Researched:** 2026-03-26
**Mode:** Ecosystem — Event Marketing for Crypto/Fintech Brands at Major Conferences

---

## Summary Verdict

Paris Blockchain Week (April 15–16, 2026, Carrousel du Louvre) skews institutional: 70%+ C-level attendees, 10,000+ from 100 countries. This is not ETH Denver. The audience is TradFi executives, VCs, regulators, and compliance-led operators. Retail crypto-native users are a secondary audience here, not the primary.

**This changes the playbook materially.** Mass lead-capture tactics that work at Consensus or Token2049 convert at lower rates at PBW. The winning strategy blends a premium booth for brand credibility with a targeted pre-event digital campaign that drives retail sign-ups, and a parallel curated outreach track for B2B partnership meetings.

---

## Pre-Event Campaign: Channels and Timing

### Timing (from 2-4 week runway)

| Day | Action |
|-----|--------|
| D0–D3 | Define the offer. Nothing launches without it. |
| D3–D5 | Landing page live, UTM structure set, Diego copy approval |
| D5–D7 | Paid ads on X/Twitter and Google launch |
| D7–D10 | Email campaign to existing Bit2Me base (warm-up + "attend with us") |
| D10–D14 | B2B LinkedIn outreach sequence starts |
| D14 | Event starts. All live campaigns redirect to live booth CTA |
| D+1 | Hot lead follow-up within 24h. Non-negotiable. |
| D+3 | Warm follow-up batch, second email in sequence |
| D+7–D+10 | Final value-add email + meeting request for B2B |

Most conference registrations (54.7%) happen within 7 days of the event. Paid campaigns launched on D5–D7 hit the peak intent window.

### Channel Breakdown

**X/Twitter (Crypto Twitter)** — Primary paid channel for retail acquisition

- X has the highest crypto ad approval rate among major platforms (~60% vs Meta ~50%)
- Use promoted tweets targeting: crypto interest, fintech, Spain/France/EU, users who follow Binance, Coinbase, Kraken
- Layer KOL amplification: 2–3 crypto-native Spanish/European accounts sharing the PBW offer (disclose as #ad per new X rules)
- Format: short video (15s) showing the offer + CTA to landing page. Carousel for product features.
- Budget indicator: €500–€2,000 for a 10-day burst campaign is sufficient for brand awareness + click volume in this vertical

**Google Search** — Capture intent from people searching "Paris Blockchain Week" or "Bit2Me"

- Target branded terms + event terms: "Paris Blockchain Week 2026", "crypto exchange Spain", "buy crypto Europe"
- Not the highest volume channel for this event, but captures the warmest intent
- Use a dedicated event landing page URL, not the homepage

**Email to existing Bit2Me base** — Highest conversion, lowest cost

- Segment: Spain + EU users, KYC-complete, at least one deposit (exclude churned-zero and excluded users)
- Subject line: "We'll be at Paris Blockchain Week — here's your offer"
- Send through CleverTap. Two emails: D7 (awareness) and D12 (last call)
- Expected open rate: 25–35% for warm base; CTR 8–12%

**LinkedIn** — B2B track only, not retail

- Use for partnership meeting requests, not user acquisition
- Personalized connection note > cold DM. Reference PBW specifically.
- Message acceptance rate increases 55–58% with personalized note
- Sequence: connection request → accepted → 24h gap → value-led DM → 48h → meeting ask
- Target: compliance officers at EU fintechs, fund managers, crypto custody providers, exchange BD teams
- Send 20–30 outreach messages/day starting D10. Expect 15–20% acceptance, 10–15% meeting conversion from those

---

## Landing Page

### Core Architecture

One dedicated URL (e.g., bit2me.com/paris or bit2me.com/pbw26). Do NOT use the homepage.

**Structure:**

1. **Hero** — Offer headline + event badge + deadline countdown. One CTA button.
2. **Offer details** — What the user gets, terms in plain language, time limit
3. **Why Bit2Me** — 3 differentiators max. Spain's #1, MiCA-compliant, X assets
4. **Social proof** — Logos of press mentions or awards (1 row)
5. **CTA repeat** — Same button as hero, different copy ("Claim offer" vs "Start now")
6. **Legal footer** — Diego-approved disclaimer. Required before launch.

**Form:** 3 fields maximum. Email + Name + Country. The KYC/full registration happens on-platform after the handoff. Every extra field kills conversion.

### Offer Structure (Options, Ranked by Conversion Potential)

**Option A — Zero trading fees, 30 days** (recommended)
"Trade free for 30 days when you register at PBW." Time-limited, clear, no-deception. Fee-waiver offers drive higher first-trade velocity than bonus cash because the barrier to first action is lower.

**Option B — Deposit bonus** (e.g., "€10 in BTC on first €100 deposit")
Industry standard. Works well but requires legal clarity on MiCA bonus promotion rules. Needs Diego to validate the structure under Spanish/EU regulation.

**Option C — Exclusive access / early feature** (e.g., staking access, Pro tier trial)
Best for brand positioning; lower raw conversion. Use this for B2B landing page variant, not retail.

**Do not offer free NFTs or on-chain drops** — adds technical friction, deters non-native users.

### Conversion Benchmarks

- Well-optimized event landing page: **12–13% conversion rate**
- Crypto-specific sign-up with a strong offer: **8–15% for lead gen, 3–8% for direct registration**
- Email traffic converts at **15–30%** — highest of any channel
- Paid social at **2–8%**
- All pages mobile-first. Form must work offline/slow Wi-Fi (on-site scan scenario).

### UTM Structure

Every traffic source gets a tagged URL:
- `?utm_source=twitter&utm_medium=paid&utm_campaign=pbw2026`
- `?utm_source=linkedin&utm_medium=organic&utm_campaign=pbw2026_b2b`
- `?utm_source=booth&utm_medium=qr&utm_campaign=pbw2026_onsite`
- `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup`

This maps to BigQuery + CleverTap attribution. Daniel can slice conversion by channel in the post-event report.

---

## On-Site Lead Capture

### The Stack (Recommended)

**QR code (primary)** — Universal, zero hardware dependency. Place on:
- Back of all booth rep lanyards (at chest height during conversation)
- Main booth signage (1 large format, eye-level)
- Takeaway card handed to every visitor
- Demo screen idle state

QR target: Mobile landing page variant (shorter form: email only + opt-in). Connects directly to CleverTap or a Typeform → Zapier → CleverTap bridge.

**NFC card (secondary, for 1:1 conversations)** — Premium feel for exec conversations. Each booth rep carries a digital business card (Popl or Wave Connect) that, on tap, adds the rep's contact + landing page URL to the visitor's phone. Every tap is logged with rep ID and timestamp — useful for post-event lead routing.

**Badge scanner (if PBW provides)** — Paris Blockchain Week uses event-native badges. If the organiser provides a badge-scan app (typical for 300-sponsor events), use it for every attendee who visits the booth. This feeds into the official attendee list you can export post-event.

### What NOT to Do

- Do not rely on paper cards. 88% are discarded within a week.
- Do not run a sweepstakes/raffle as the primary capture mechanic — attracts low-intent leads.
- Do not use a tablet form with more than 3 fields standing at a booth. Context: you have ~5 seconds per interaction at a busy booth.

### Lead Qualification at Booth

Ask one question verbally: "Are you more interested in trading, or in partnership/integration?" Routes the lead into B2C (CleverTap nurture) or B2B (spreadsheet + manual follow-up) track immediately. Tag this in the CRM at scan time.

---

## Post-Event Nurture

### Timing Protocol (Non-Negotiable)

| Timing | Action | Channel |
|--------|--------|---------|
| Same day, EOD | Upload all QR/NFC/badge scan data to CleverTap | Data ops (Katy) |
| < 24h after event ends | Email #1 to all captured leads | CleverTap |
| 24–48h | Personalized follow-up to hot leads (verbal commitment, high dwell time) | Manual email or WhatsApp |
| D+3 | Email #2 — value content (not a sales push) | CleverTap |
| D+7 | Email #3 — product highlight / case study | CleverTap |
| D+10 | Final CTA — offer expiry reminder if applicable | CleverTap |

Leads contacted within 24–48h are 60% more likely to convert. This window is the single biggest ROI lever in post-event marketing.

### Email Sequence Content

**Email #1 (< 24h) — "Great to meet you at PBW"**
- Personalize with event context (mention Paris, not a generic greeting)
- Remind of the offer
- One CTA: "Complete your registration"
- Keep under 150 words

**Email #2 (D+3) — Value, not pitch**
- Share something useful: a market insight, a feature explainer, or a relevant piece of content
- Soft CTA: "Explore Bit2Me" not "Register now"
- Goal: stay top of mind, not push for conversion

**Email #3 (D+7) — Social proof**
- One customer story or stat ("X users from Spain trust Bit2Me")
- MiCA-compliance signal — critical at PBW where regulatory credibility matters
- CTA: first deposit / first trade

**Email #4 (D+10) — Urgency close**
- "Your PBW offer expires in 48h"
- One button. No distractions.

### B2B Nurture (Separate Track — Spreadsheet, Not CleverTap)

- No CRM tool for B2B yet. Use a Google Sheet: Name, Company, Role, Meeting held (Y/N), Follow-up owner, Next action, Stage
- B2B Email #1 (< 24h): "Following up from PBW — I'd like to schedule 30 minutes"
- B2B Email #2 (D+3): "Quick note — here's what Bit2Me is doing in [their relevant area]"
- B2B Email #3 (D+7): Final ask for a call
- Non-responders: move to quarterly LinkedIn touch, stop active pursuit

---

## Tools Stack

| Function | Recommended Tool | Why |
|----------|-----------------|-----|
| Email/Push automation | CleverTap (existing) | Already in-stack, Katy owns it |
| Lead form (on-site) | Typeform → Zapier → CleverTap | Quick to deploy, mobile-first, 3-field forms |
| NFC digital card | Popl or Wave Connect | Every tap logs rep ID + timestamp. CRM sync. |
| QR generation + tracking | Bitly or UTM.io | Branded short links with click analytics |
| B2B CRM (minimal) | Google Sheet (manual) | No B2B tool exists. Spreadsheet is faster than onboarding new software in 2-week runway |
| Landing page | Bit2Me existing web infra | Per constraints. Build on existing platform, not a new tool |
| Segmentation | BigQuery (existing) | Pull pre-event audience segments for email campaign |
| Analytics | BigQuery + UTM parameters | Map every channel to CleverTap conversions post-event |
| Social scheduling | Buffer or native X/LinkedIn scheduler | Pre-schedule event-week content in advance |
| Paid ads management | X Ads Manager (direct) | No agency layer needed for a 10-day burst campaign |

### What to Avoid

- Do not introduce a new CRM tool for this event. 2-week runway is not enough to configure and test.
- Do not use Eventbrite — Bit2Me is the sponsor/exhibitor, not an event organiser. It adds no value here.
- Do not use Web3-native lead capture (wallet connect, POAP) — PBW retail audience overlaps with traditional finance; wallet-connect creates friction for non-DeFi users.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Lead form | Typeform | Google Forms | Typeform has better mobile UX, conditional logic, and Zapier native integration |
| NFC card | Popl | HiHello | Popl has better CRM sync options and tap analytics |
| Email channel | CleverTap | Mailchimp | CleverTap is already in-stack with audience segments |
| B2B outreach | LinkedIn (manual) | Apollo.io sequence | Apollo adds cost and setup time. For 20–30 targets, manual is faster. |
| Landing page host | Existing Bit2Me web | Unbounce/Webflow | Tech constraints. Deploying on Bit2Me infra is faster given Diego approval loop. |
| Paid channels | X/Twitter | Meta/Facebook | Meta has stricter crypto ad policy (~50% approval). X is the native crypto channel. |

---

## Sources

- Paris Blockchain Week 2026 official site: https://www.parisblockchainweek.com/
- Paris Blockchain Week 2026 sponsor info: https://chainwire.org/2026/03/03/paris-blockchain-week-2026-returns-to-bridge-institutions-and-digital-assets/
- CH3 Agency Crypto Event Report 2025: https://www.ch3.agency/crypto-event-trends-2025/
- ETH Denver 2025 side events analysis: https://www.thestreet.com/crypto/innovation/ethdenver-2025-ai-everywhere-side-events-take-over
- NFC/QR lead capture benchmarks: https://www.mobilocard.com/post/exhibition-lead-capture
- Lead generation at events 2025: https://www.leadbeam.ai/blog/lead-generation-at-events
- Post-event follow-up timing: https://www.default.com/post/event-follow-up-email
- Trade show follow-up best practices: https://romify.io/blog/follow-up-email-after-trade-show
- Crypto exchange sign-up bonus structures: https://www.finder.com/cryptocurrency/crypto-bonuses
- Landing page conversion benchmarks: https://unbounce.com/average-conversion-rates-landing-pages/
- Event registration landing page CVR: https://getwpfunnels.com/event-landing-page-examples/
- LinkedIn B2B outreach performance: https://growleads.io/blog/linkedin-outreach-strategy-what-actually-works-in-2025-expert-guide/
- X/Twitter crypto ads: https://coinbound.io/crypto-ad-network-vs-twitter-x-ads-for-web3/
- Event marketing tools stack: https://www.bizzabo.com/blog/best-event-management-tools
- PBW sponsor activations: https://www.parisblockchainweek.com/become-a-sponsor
