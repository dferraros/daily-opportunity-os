# Scoring Criteria — Daily Opportunity OS
## 16 Dimensions, each scored 1-10
## Date: 2026-04-02

---

## How Scoring Works

Every opportunity is scored on 16 dimensions. Each dimension is 1-10.
Dimensions feed into 3 scoring layers (Attractiveness, Executability, Strategic Value).
Final score = composite of 3 layers + modifiers + caps.

**Score thresholds:**
- 7.5-10.0 → `now` lane (validate in 14-30 days)
- 6.0-7.4  → `soon` lane (60-90 day horizon)
- 4.0-5.9  → `strategic` lane (6-18 months)
- <4.0     → `no` lane (killed)

---

## Layer 1: Attractiveness (50% weight)
*Does this market deserve attention?*

### 1. Pain Severity (weight: 0.10)
**Question:** How urgent and daily is this pain?
**Scale:**
- 10: Emergency-level daily pain. People losing money/time every day. Explicit workarounds.
- 7-9: Significant recurring pain. Clear frustration. Frequent complaints online.
- 5-6: Moderate pain. Annoyance but workarounds exist.
- 3-4: Nice-to-have improvement. Low urgency.
- 1-2: Unclear if pain exists. Assumed need.

**Automatic +1 signals:** no existing tool, manual/Excel/paper workflow, daily occurrence, money/time loss, forum complaints, Venezuela geography (necessity pain)

---

### 2. Market Size (weight: 0.10)
**Question:** How large is the addressable market if this works?
**Scale:**
- 10: TAM >$1B, multiple major players validate size
- 7-9: TAM $100M-$1B, growing sector with VC funding
- 5-6: TAM $10M-$100M, solid SMB niche
- 3-4: TAM $1M-$10M, micro-niche
- 1-2: <$1M TAM or unclear

**Automatic scoring:** $Xb/Xm mentions, user counts, bucket signals (venture_scale=+2, latam_asymmetry=+1)

---

### 3. Timing Tailwind (weight: 0.08)
**Question:** Is now the right time? What creates urgency?
**Scale:**
- 10: New regulation just mandated it, or explosive growth signal (15%/week), or first-mover window closing
- 7-9: Strong macro tailwind (regulatory mandate, platform shift, tech cost drop)
- 5-6: General market growth, no specific catalyst
- 3-4: Mature market, late entry
- 1-2: Contracting market or wrong timing

**Automatic +1 signals:** 2024/2025 date context, mandatory/regulation keywords, "growing fast", "first mover window", Venezuela necessity (timing = now or never)

---

### 4. Willingness to Pay (weight: 0.08)
**Question:** Will the target customer actually pay? At what price?
**Scale:**
- 10: Currently paying for worse solution, clear price point, high ROI vs alternative
- 7-9: Strong WTP signal, competitive pricing benchmarks exist
- 5-6: WTP assumed, needs validation
- 3-4: Low WTP, price-sensitive market, unclear
- 1-2: No evidence of payment willingness

**Venezuela adjustment:** Base -1 (WTP 0.25x US baseline, max $3-15/month SaaS)
**Automatic +1 signals:** specific price points mentioned, mandatory compliance (forced WTP), cost savings proof

---

### 5. Monetization Clarity (weight: 0.08)
**Question:** Is the revenue model clear and believable?
**Scale:**
- 10: Specific model (X% take rate, $Y/month/user) validated by analogous businesses
- 7-9: Clear model, comparable companies show it works
- 5-6: Model exists but needs validation
- 3-4: Unclear how money flows
- 1-2: No monetization logic

**Automatic +1 signals:** per-transaction/subscription/fee keywords, % rate mentioned, fast_cash or latam_asymmetry bucket

---

## Layer 2: Executability (30% weight)
*Can Daniel and a small team actually build and launch this?*

### 6. Speed to MVP (weight: 0.08)
**Question:** How fast can a functional MVP be built?
**Scale:**
- 10: MVP in <2 weeks. WhatsApp bot, Google Sheet + Zapier, existing API
- 7-9: MVP in 2-6 weeks. Standard SaaS features, no custom infrastructure
- 5-6: MVP in 6-12 weeks. Some complexity
- 3-4: MVP in 3-6 months. Hardware, regulatory, complex data
- 1-2: >6 months. Platform play or heavy infrastructure

**Automatic +1 signals:** "simple"/"lightweight"/"minimal", WhatsApp native, QR-based, concierge-first, fast_cash bucket, Venezuela (lower cost to build)

---

### 7. Capital Efficiency (weight: 0.07)
**Question:** How much capital is needed to reach first revenue?
**Scale:**
- 10: <$500. Phone + existing tools.
- 7-9: $500-$5K. API costs, basic hosting, minimal tooling
- 5-6: $5K-$50K. Some development, infrastructure
- 3-4: $50K-$500K. Team hire, paid channels needed
- 1-2: >$500K. Marketplace inventory, regulated capital, hardware

**Automatic +1 signals:** bootstrap/no inventory/software-only mentions, fast_cash bucket, latam_asymmetry bucket, smb_software vertical

---

### 8. Distribution Accessibility (weight: 0.08)
**Question:** Can Daniel reach the first 10 customers in <2 weeks?
**Scale:**
- 10: Customers visible on WhatsApp groups, LinkedIn, warm intros. Channel clear.
- 7-9: Community or outreach path clear. Distribution playbook exists.
- 5-6: Channel exists but requires work to activate
- 3-4: Distribution is the hard problem. No clear path
- 1-2: No clear distribution hypothesis

**LATAM/VE automatic +1:** WhatsApp + community-based distribution always scores higher in LATAM/VE vs outbound or paid

---

## Layer 3: Strategic Value (20% weight)
*Does this create lasting advantage?*

### 9. Competition Intensity (weight: 0.07)
**Question:** How competitive is the space? (Lower = less competition = higher score)
**Scale:**
- 8-10: No direct competitor. First-mover. Gap confirmed.
- 6-7: 1-2 weak incumbents. Clear differentiation path.
- 4-5: Competitive market but room for positioning
- 2-3: Crowded space with strong players
- 1: Dominated by large funded competitors

**Venezuela automatic bonus:** VE market has almost no software competition → typically scores 8+

---

### 10. Defensibility (weight: 0.07)
**Question:** What prevents competitors from copying this in 12 months?
**Scale:**
- 10: Data moat + network effects + switching costs. All three.
- 7-9: 2 of 3 defensibility levers. Clear compounding advantage.
- 5-6: First-mover advantage, brand trust, or community
- 3-4: Replicable product. Defensibility unclear.
- 1-2: No moat. Easily copied.

**Venezuela automatic +1:** First-mover data advantage in USDT/informal commerce data compounds fast

---

### 11. Regional Fit (weight: 0.07)
**Question:** How well does this match VE/LATAM/Spanish-speaking market dynamics?
**Scale:**
- 10: Built specifically for VE/LATAM. Leverages local infrastructure (USDT, WhatsApp, bolivar). Exploits friction global players ignore.
- 7-9: Strong LATAM fit. Pricing, distribution, payment rails aligned.
- 5-6: Adaptable. Global model with LATAM version.
- 3-4: Western-first. Requires significant adaptation.
- 1-2: Wrong market. Wrong pricing. Wrong trust model.

**Automatic bonus:** latam_asymmetry bucket +2, Venezuela geography +2, Spanish/USDT/WhatsApp/informal keywords +1 each

---

### 12. Founder Fit — Daniel's 6 Wedges (weight: 0.05)
**Question:** Does this match Daniel's unfair advantages?
**6 Wedges (1 point each):**
1. Growth & GTM edge (lifecycle, CRM, paid, organic, A/B testing)
2. Narrative & positioning edge (frame and sell a story fast)
3. LATAM + Spanish intuition (VE, Spain, Colombia patterns)
4. Fintech & crypto adjacency (exchange ops, payment rails, USDT)
5. Speed to prototype (Claude Code, MVP systems fast)
6. Distribution instincts (WhatsApp funnels, performance, referral)

**Score = 4 + matching wedges (max 10 = 4 base + 6 wedges)**
Opportunities with <2 matching wedges are flagged "founder-fit risk"

---

### 13. AI Leverage (weight: 0.04)
**Question:** Can AI accelerate this business model significantly?
**Scale:**
- 10: AI is the core product. Not buildable without AI. 10x human efficiency gain.
- 7-9: AI dramatically reduces CAC, improves product quality, or enables automation
- 5-6: AI useful but not core to the value prop
- 3-4: Traditional software. AI nice-to-have.
- 1-2: AI irrelevant or harmful to trust (e.g., cash-heavy informal transactions)

---

### 14. Operational Simplicity (weight: 0.05)
**Question:** Can this be operated by 1-2 people?
**Scale:**
- 10: Fully async. No physical operations. 1 person can run at scale.
- 7-9: Small team (2-3). Remote. Software handles most of it.
- 5-6: Requires some ops (customer support, onboarding, fulfillment)
- 3-4: Ops-heavy. Requires local team or physical presence.
- 1-2: Requires large team, physical logistics, or 24/7 ops

---

### 15. Regulatory Simplicity (weight: 0.04)
**Question:** How much regulatory burden before launch?
**Scale:**
- 10: No license needed. Launch tomorrow.
- 7-9: Basic business registration. No sector-specific license.
- 5-6: Some compliance work (privacy policy, T&Cs, local tax registration)
- 3-4: Sector license required (fintech, insurance, broker). Months of work.
- 1-2: Banking license, AML registration, or securities regulation required

**latam_asymmetry bonus:** +2 base (informal market = less regulatory scrutiny)
**fintech penalty:** -1 (always more regulated than pure software)

---

### 16. Path to First Revenue (weight: 0.04)
**Question:** How fast is the first dollar in the door?
**Scale:**
- 10: First revenue in <7 days. Service business, existing customer, immediate payment.
- 7-9: First revenue in 7-30 days. Direct outreach + quick close.
- 5-6: First revenue in 30-90 days. Need product, some sales cycle.
- 3-4: First revenue in 3-6 months. Product build + GTM required.
- 1-2: First revenue >6 months. Platform, regulatory, or long sales cycle.

**Automatic +1 signals:** "first customer", "30 days", productized service, concierge-first, WhatsApp outreach, fast_cash bucket, Venezuela (faster close due to urgency)

---

## Modifiers and Caps

### Kill Gate (runs BEFORE scoring)
7 binary questions. Fail 2+ = kill_decision = True. Score set to 0. Move to ignore list.
1. Can the pain be explained in 1 sentence?
2. Can a specific buyer be named?
3. Is CAC < 3x monthly price achievable?
4. Is first revenue possible in <90 days?
5. Can an MVP be built in 2-6 weeks?
6. Is TAM > $10M?
7. Is there a wedge (edge, timing, distribution advantage)?

### Three Decision Filters (post-scoring cap)
If 2+ fail → cap final_score at 5.0, set portfolio_lane to "watch":
1. Can Daniel sell this fast? (reach buyer + real interest in <2 weeks)
2. Can Daniel build this lean? (MVP <$2K, <2 people, <6 weeks)
3. Can this compound? (software, data, network effects, or repeatable distribution)

---

## Venezuela Structural Wedge Bonus (+1.5 to regional_fit)
If geography = venezuela AND maps to one of these wedge categories:
- payments_and_collections
- remittances_and_diaspora_finance
- smb_software_informal_operators
- retail_inventory_working_capital
- logistics_coordination
- commerce_trust_layers
- creator_monetization
- cross_border_service_businesses
- diaspora_finance_and_commerce
- ai_labor_replacement_tools

---

*Scoring Criteria v1.0 — 2026-04-02 — daily-opportunity-os*
