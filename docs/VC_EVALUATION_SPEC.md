# VC-Grade Evaluation Framework for Daily Opportunity OS
**Version**: 1.0 | **Date**: 2026-07-22 | **Audience**: Architects & Automation Engineers

---

## Executive Summary

This spec extends the current 16-dimension scoring model with **8 new VC-critical variables** that professional early-stage investors systematically evaluate but the current system omits. It establishes a **machine-readable sourcing playbook** for each variable (using Tavily, Firecrawl, Apify, free sources), proposes a **revised weighting model** that incorporates evidence confidence, adds a **2-level LATAM/Spain industry taxonomy** (~50 verticals), and specifies exact queries to establish "revenue evidence" in markets.

**Key gap being filled**: Current system scores "market_size" as TAM without differentiating between TAM and *validated* TAM (competitor ARR, funding rounds, pricing power). It scores "monetization_clarity" at the model level but not evidence of *successful* monetization in the market. VCs invert this: they start with evidence of revenue, then build the TAM upward.

---

## Part 1: VC-Grade Variable Set (8 New Variables)

### Current 16 Dimensions (retained)
pain_severity, market_size, timing_tailwind, willingness_to_pay, monetization_clarity, speed_to_mvp, capital_efficiency, distribution_accessibility, competition_intensity, defensibility, regional_fit, founder_fit, ai_leverage, operational_simplicity, regulatory_simplicity, revenue_speed_score

### 8 New VC Variables to Add

---

#### **1. Market CAGR / Growth Rate (estimated_market_growth_rate)**
**Why it matters**: A $20M shrinking market vs $20M growing 40% CAGR are not equivalent opportunities. Growth rate is THE leading indicator of whether you enter a winner-take-most dynamic or mature consolidation.

**Definition**: Estimated annual compound growth rate (CAGR %) of the addressable market segment over next 3-5 years.

**0-10 Anchors**:
- **10**: >50% CAGR (emerging vertical, early adoption phase). Examples: AI automation tools (2023-2026), USDT remittances (2020-2026), Venezuelan e-commerce (2018-2024 despite macro headwinds).
- **8-9**: 25-50% CAGR (solid tailwind). SaaS benchmarks: median SaaS 15-25% CAGR, high-growth 30%+.
- **6-7**: 10-25% CAGR (market growing but not explosive).
- **5**: ~5-10% CAGR (GDP-rate growth, mature market).
- **3-4**: 0-5% CAGR (flat or slow decline).
- **1-2**: Negative growth (market shrinking).

**How to source it** (automated):

1. **Global markets**: Tavily news search for "market research reports [vertical] CAGR 2024-2029"
   - Query: `"[vertical] market size CAGR forecast 2024-2029"` (e.g., "SMB payroll software market CAGR 2024-2029")
   - Extract numeric CAGR % from results. Match patterns: `(\d{1,3})\s*%\s*CAGR`, `growing at (\d{1,3})\s*%`
   - Sources: Mordor Intelligence, Grand View Research, Allied Market Research (these label CAGR explicitly).

2. **LATAM/Venezuela-specific**: 
   - Search: `"[vertical] mercado latam crecimiento 2024 proyecciones"` via Tavily (Spanish language research)
   - Search: Contxto.com articles (LATAM tech intelligence site) via Firecrawl: `site:contxto.com [vertical] mercado latam`
   - Venezuela specifically: LatAmList.com founder profiles + news (organic growth signals), Trending market signals from Twitter/X LATAM tech accounts
   - Fallback heuristic: If market is Venezuela or LATAM SMB software, assume 20-30% CAGR (tech adoption catch-up to US levels).

3. **Startup density proxy** (if market report unavailable):
   - Tavily search: `"[vertical] funding 2024 2025"` → count funding rounds/year, trend line
   - If funding activity increasing YoY, market CAGR likely >20%; if flat/declining, <10%.
   - Apify: search G2 Capterra for new entrants added per quarter (indicates market heating).

4. **Confidence flags**:
   - HIGH (8-10): Explicit CAGR % from analyst firm + corroborating news.
   - MEDIUM (5-7): Inferred from funding trends + startup density + GDP growth signals.
   - LOW (1-4): No data; heuristic assumption only.

**Data storage**: `estimated_market_growth_rate (int 1-10)`, `market_growth_rate_confidence (enum: high|medium|low)`, `market_growth_cagr_percent (optional float)`, `market_growth_source (list of URLs)`.

---

#### **2. Competitor Revenue Evidence (competitor_revenue_evidence)**
**Why it matters**: "There's a market for this" (claimed) vs "They're making $50-200K ARR" (validated) are fundamentally different risk profiles. Revenue evidence is the single strongest signal of product-market fit and pricing power.

**Definition**: Existence and quantity of evidence that direct competitors are earning revenue. Not TAM — actual verified or estimated ARR of 2-3 key competitors in the segment.

**0-10 Anchors**:
- **10**: 3+ competitors with public/disclosed revenue (Series A+ funded, transparent pricing). Examples: Stripe, HubSpot, Notion competitors all post ARR. Or private fundraising announcements that imply ARR.
- **9**: 2+ competitors with estimated ARR via funding rounds + public SaaS benchmarks (e.g., "raised $5M Series A, runs 20% GMV as ARR per SaaS multiples" = $1-2M ARR). PayPal, Wise, TransferWise founding rounds imply revenue from the math.
- **7-8**: 1 competitor with visible revenue proof (app store/G2 reviews, press mentions of revenue). Zapier (famous "no VC" company) publishes ARR milestones.
- **5-6**: Competitor pricing visible (site, G2) but no actual revenue disclosed; indirect signals (hiring, office expansion).
- **3-4**: Market exists but competitor revenue opaque; only TAM claims.
- **1-2**: No evidence any competitor has revenue; only product announcements or beta.

**How to source it** (automated):

1. **Crunchbase / PitchBook via Tavily search**:
   - Query: `site:crunchbase.com OR site:pitchbook.com "[competitor] Series A B C funding" revenue`
   - Extract: Funding round $ → estimate ARR via multiples (SaaS: Series A typical 5-10x revenue multiple; B 3-5x; C 2-3x).
   - If Company raised $5M Series A, implied ARR = $500K-$1M.

2. **Pricing page + app store / G2 Capterra**:
   - Firecrawl scrape: Competitor pricing page → extract price points, tiers.
   - G2 Capterra reviews: Extract install/review count trends. If 1,000 reviews, assume ~5-10K users (1-2% review rate). At $50-100/mo SaaS = $2.5-10M ARR heuristic.
   - Apify Google Play / App Store: review count growth YoY → revenue proxy (if reviews growing 50% YoY, revenue likely growing 30-50%).

3. **News / press releases**:
   - Tavily search: `"[competitor] revenue" OR "[competitor] ARR" OR "[competitor] profitability" 2024 2025`
   - Look for keywords: "reached $X million ARR", "profitable", "cash flow positive", "$Y MRR".
   - Example: "Wise hits $2B revenue" (public), "Anthropic profitable" (private but announced), "Notion raised at $10B valuation" (implies $30-100M ARR).

4. **Secondary: Glassdoor salary + headcount**:
   - Infer revenue from: headcount (from LinkedIn/Crunchbase) × avg SaaS revenue per employee ($500K-$1M per engineer, sales rep, etc.).
   - If 50 employees, likely $25-50M ARR (rough heuristic).

5. **LATAM/Venezuela-specific**:
   - Local competitors often have zero public funding data. Search: Spanish-language news sites (Contxto, StartupDetails, LinkedIn profiles).
   - Query: `site:contxto.com "[competitor] ingresos" OR "facturación" OR "usuarios pagos"`
   - Fallback: If no local competitor revenue evidence found, score must be ≤4 (market unvalidated).

**Data storage**: `competitor_revenue_evidence (int 1-10)`, `competitor_revenue_confidence (enum: high|medium|low)`, `key_competitors_with_revenue (list: [{name, est_arr_usd, source_url}])`.

---

#### **3. Gross Margin Profile (implied_gross_margin_percent)**
**Why it matters**: A $1M ARR marketplace at 20% margin is half the value of a 60% margin SaaS. Margin profile is the ultimate determinant of venture scalability and exit multiple.

**Definition**: Estimated gross margin (%) for a successful operator in this vertical. Not a company-specific forecast—what do profitable players in this category typically achieve?

**0-10 Anchors**:
- **10**: 80%+ margin (software, no COGS). Most SaaS. Marketplace with low take-rate enforcement.
- **9**: 70-80% margin. SaaS with some infrastructure costs (payment processing, AWS).
- **7-8**: 55-70% margin. High-touch SaaS, productivity software, fintech payments (e.g., Stripe 80% gross margin).
- **5-6**: 40-55% margin. Subscription with moderate fulfillment (education platform, learning, content delivery). Marketplaces with active curation.
- **3-4**: 20-40% margin. Services business, agency model, productized services (high labor).
- **1-2**: <20% margin. Heavy logistics, physical goods, compliance-heavy (banking, insurance license costs).

**How to source it** (automated):

1. **Public SaaS companies** (highest confidence):
   - Search public filings (10-K/10-Q) for gross margin % on SEC Edgar via Tavily:
   - Query: `site:sec.gov [competitor SaaS company] gross profit margin 10-K`
   - Match pattern: "Gross profit: $XXX (YY% of revenue)"
   - Database: If competitor raised Series A+, assume standard SaaS 70-80% if no special hardware/fulfillment.

2. **Pricing + unit economics research**:
   - Scrape competitor pricing + support model (Firecrawl).
   - If fully automated / self-serve SaaS = high margin (estimate 70%+).
   - If requires customer success / implementation = medium margin (50-70%).
   - If requires fulfillment / logistics = low margin (20-40%).

3. **Industry benchmarks**:
   - Tavily search: `"[industry] gross margin benchmark" saas fintech`
   - SaaS benchmarks: Benchmarking reports (SaaS Capital, Bain & Company, McKinsey) usually public or available via news summaries.
   - LATAM-specific: Payroll SaaS in Brazil (Gupy, BambooHR LATAM) are 70-80% margin (software). Logistics in LATAM 30-40% (labor, vehicle costs).

4. **Competitive intelligence via Apify**:
   - Scan G2 reviews for complaint patterns. If "high implementation cost" or "requires manual work" appears, margin lower.
   - If "easy self-serve" or "quick setup", margin higher.

5. **LATAM adjustment**: 
   - Venezuelan SMB software: Often 60-70% margin (lower infrastructure cost, no complex compliance).
   - LATAM logistics: 25-35% margin (cheaper labor than US but still fulfillment cost).

**Data storage**: `implied_gross_margin_percent (int 20-95)`, `margin_profile_confidence (enum: high|medium|low)`, `margin_derivation (string: public_filing|benchmark|heuristic)`.

---

#### **4. Revenue Velocity / Sales Cycle Length (estimated_sales_cycle_days)**
**Why it matters**: A $50K deal closed in 14 days vs 120 days is a 8x difference in cash flow and team workload. Directly impacts burn rate and runway.

**Definition**: Estimated time (in days) from first customer contact to payment received, for a median deal in this vertical.

**0-10 Anchors** (inverted—lower cycle = higher score):
- **10**: 0-7 days (instant payment, service biz, freemium upgrade). WhatsApp business, productized services.
- **9**: 7-14 days (fast closing, product-led SaaS, SMB software). Stripe, Square sign-up & charge.
- **7-8**: 14-30 days (free trial → trial-to-paid). Most B2B SMB software.
- **5-6**: 30-90 days (sales cycle, demo, proof of concept). Mid-market SaaS, enterprise pilots.
- **3-4**: 90-180 days (complex selling, multi-stakeholder, procurement). Enterprise, fintech, insurance.
- **1-2**: >180 days (banking, heavily regulated, government sales).

**How to source it** (automated):

1. **G2 Capterra "sales" / "implementation" comment mining**:
   - Firecrawl scrape G2 reviews for keywords: "took 2 weeks to close", "implementation took 30 days", "90-day ramp".
   - Extract time phrases via regex and average.
   - Note: Reviews often mention cycle, especially if painful (e.g., "slow procurement process").

2. **Competitor sales methodology**:
   - Scrape pricing page for trial length (Firecrawl). If 14-day free trial, implies 14-day sales cycle (trial-to-paid).
   - If "contact us for demo", likely longer cycle (30-90 days).
   - LinkedIn job postings for "Sales Development Rep" roles: Tavily search `"[competitor] SDR job posting"`
   - Job postings that emphasize "deal closure" or "forecasting" → longer cycles (30+ days).

3. **Industry reports**:
   - Tavily: `"[vertical] B2B SaaS sales cycle benchmark" 2024`
   - SaaS benchmarks: B2B SMB software typically 14-30 days; Enterprise 60-180 days.
   - LATAM context: Often faster than US (less rigid procurement) → assume -20% from US baseline.

4. **Founder/operator interviews** (if available in research_executor context):
   - Ask: "How long does a typical customer take to decide?"
   - This field is often revealed in early conversations.

5. **Venezuela-specific heuristic**:
   - Assume 7-14 days (very fast, informal business, WhatsApp-first). Score: 9-10.
   - Exception: If selling to formal sector (banks, multinationals), assume 30-90 days.

**Data storage**: `estimated_sales_cycle_days (int 1-365)`, `sales_cycle_confidence (enum: high|medium|low)`, `sales_cycle_source (string)`.

---

#### **5. Regulatory Moat vs Regulatory Risk (regulatory_moat_strength)**
**Why it matters**: Some opportunities are defensible *because* of regulation (fintech licensing creates a barrier); others are *threatened* by it (crypto, cannabis, money transmission). VCs must distinguish between the two.

**Definition**: Net regulatory position (1-10 scale). Positive = regulation creates defensibility. Negative = regulation is a threat.

**0-10 Anchors**:
- **10**: Licensing creates moat (banking, insurance, brokerage). High barrier to entry protects you if you have license. Example: Wise EU license.
- **8-9**: Light compliance + first-mover advantage in regulated space. Example: LATAM payroll SaaS that secures labor compliance certifications first.
- **6-7**: Moderate compliance cost but no *regulatory advantage*. You comply, competitors comply. No moat. Example: GDPR (SaaS compliance is cost, not advantage).
- **4-5**: Regulatory load moderate; clear path but cost is a headwind. Example: Brazilian tax software (complex, but well-defined).
- **2-3**: High regulatory load + unclear path. Regulatory risk > regulatory moat. Example: crypto lending (license status uncertain).
- **1**: Existential regulatory risk. Could be outlawed or severely restricted. Example: sanctioned payments rails, unlicensed financial services.

**How to source it** (automated):

1. **Regulatory research via Tavily**:
   - Query: `"[vertical] regulatory requirements" OR "[vertical] licensing requirements" [country]`
   - Scan results for keywords: "license required", "exemption available", "regulatory sandbox", "pending legislation".
   - For Venezuela/LATAM: `"[vertical] regulación" OR "licencia" [país]` (Spanish).

2. **Legal/compliance landscape**:
   - Tavily search: `"[vertical] [country] regulatory changes 2024 2025"` → identify recent tightening or loosening.
   - Example: "Brazil fintech regulations clarified Q1 2025" (positive signal) vs "India crypto ban risk 2025" (negative).

3. **Competitor regulatory status**:
   - Crunchbase / LinkedIn: Check if competitors have regulatory/compliance leadership (VP Regulatory Affairs, General Counsel). If many hires in this role, regulation is becoming more central.
   - Press releases: Tavily search `"[competitor] regulatory approval" OR "license granted" OR "regulatory fine"`

4. **Licensing/certification burden**:
   - If vertical requires *easy* certification (online course, $500 fee), moat is weak.
   - If vertical requires *expensive* licensing (2-3 year process, $1M+ cost), moat is strong but risk of failure is high.
   - Query: `"[vertical] [country] licensing cost requirements timeline"`

5. **Venezuela-specific**:
   - Most sectors have minimal formal regulation (informal market dominates).
   - Exception: Banking, payments, fintech (BCV oversight, heavy).
   - Advantage: Low regulatory moat but also low regulatory *threat* for informal sectors.
   - Score: 5-7 (neutral to slight advantage of low compliance burden).

**Data storage**: `regulatory_moat_strength (int 1-10)`, `regulatory_threat_level (enum: low|medium|high)`, `regulatory_source (list of URLs)`.

---

#### **6. Pricing Power / Price Elasticity (pricing_power_evidence)**
**Why it matters**: Can you raise prices without losing customers? Do customers have better alternatives? This is the difference between a commodity and a premium product. VCs call this "pricing power"—the ability to command premium margins.

**Definition**: Evidence that customers will pay premium prices (relative to substitutes) or that pricing is inelastic (raising prices won't cause churn).

**0-10 Anchors**:
- **10**: Inelastic pricing + switching costs high. Example: Stripe (no good substitute, switching cost is high); Notion (network effects, data lock-in).
- **8-9**: Clear pricing premium vs substitutes + loyal customer base. Example: Figma (faster, better collaboration than Photoshop). Ability to raise 10-20% without churn.
- **6-7**: Competitive pricing, customer retention moderate. Standard SaaS. Can raise 5-10%.
- **4-5**: Price-sensitive market, thin margins. Commodity software. Can raise 0-5%.
- **2-3**: Intense price competition. Customers constantly shop. Discounting culture. Downward pressure.
- **1**: Race to the bottom. Customers defect for marginal price difference.

**How to source it** (automated):

1. **Pricing history / price changes via Wayback Machine + Tavily**:
   - Find competitor pricing pages from 12-18 months ago (Wayback Machine or Tavily search for press mentions of pricing changes).
   - Compare to current pricing. If 10-20% increases with no major feature additions, pricing power is strong.
   - If prices held flat for 3+ years, pricing power is weak.

2. **Customer retention / churn signals from G2**:
   - G2 comment mining: Look for phrases "too expensive", "switched to [competitor]", "hard to justify price", "best value", "worth the cost".
   - If "worth the cost" appears more often than "too expensive", pricing power high.

3. **Competitor pricing benchmarks**:
   - Scrape 3-5 competitor pricing pages (Firecrawl).
   - Calculate coefficient of variation (CV) across competitors.
   - Low CV (<20%) = commoditized, low pricing power.
   - High CV (>50%) = differentiated, high pricing power (some players command premium).

4. **Substitute analysis**:
   - Tavily search: `"[vertical] alternative solutions" OR "[vertical] substitute products"`
   - Count and evaluate substitute quality.
   - If no good substitute exists (e.g., Stripe alternatives are weak), pricing power high.

5. **LATAM-specific**: 
   - Willingness-to-pay is lower (0.25-0.4x US), but within LATAM, price elasticity often high (customers are price-sensitive).
   - Adjustment: If product is "must-have", pricing power 7-9. If "nice-to-have", pricing power 2-4.
   - Currency-based moat: USDT-priced services have pricing power in Venezuela (immune to bolivar collapse).

**Data storage**: `pricing_power_evidence (int 1-10)`, `pricing_power_confidence (enum: high|medium|low)`, `pricing_premium_percent (optional int: % premium vs cheapest substitute)`.

---

#### **7. Retention / Frequency of Use (retention_rate_signal)**
**Why it matters**: Does the product get used every day (high stickiness) or once a quarter (high churn risk)? Retention is the ultimate SaaS metric. Net revenue retention >110% means you're winning; <90% means you're shrinking.

**Definition**: Estimated monthly/annual retention rate or frequency-of-use signal for this vertical's software.

**0-10 Anchors** (based on typical usage):
- **10**: Daily use. NRR typically >120%. Examples: Slack, Notion, WhatsApp. High stickiness.
- **8-9**: 3-5x per week. NRR >110%. CRM, project management, communication tools.
- **6-7**: 2-3x per week or 1-2x per month. NRR 100-110%. Regular but not daily. Accounting, HR, payroll.
- **4-5**: Weekly or monthly. NRR 90-100%. Less sticky. Analytics, reporting tools.
- **2-3**: Quarterly or annual. NRR 70-90%. High churn risk. Compliance tools, annual reviews.
- **1**: One-time or episodic. NRR <70%. Extreme churn. One-off services.

**How to source it** (automated):

1. **Product usage patterns from G2 Capterra**:
   - Firecrawl scrape reviews for keywords: "use daily", "check weekly", "monthly reporting", "quarterly review".
   - Extract frequency phrases, aggregate.

2. **Public SaaS retention benchmarks**:
   - Tavily search: `"[product category] retention rate benchmark" OR "NRR net revenue retention"`
   - SaaS benchmarks: Slack 99%+ monthly retention (daily use). Zoom (episodic) 85% annual. Typical SaaS 90-95% annual (translates to 5-10% monthly churn).

3. **Community/engagement signals**:
   - LinkedIn company page: Follower growth rate indicates sticky products (high follower growth = high engagement).
   - Slack/Discord/community size relative to user base: High engagement = high retention.

4. **App store reviews frequency**:
   - If reviews posted frequently (daily/weekly), implies active users. If stale (quarterly), implies episodic use.

5. **LATAM SMB context**:
   - Venezuelan SMBs use WhatsApp daily (essential tool) but many B2B SaaS periodically.
   - Adjust down 10-20% for LATAM (lower digital maturity, more manual work still).

**Data storage**: `retention_rate_signal (int 1-10)`, `typical_use_frequency (string: daily|weekly|monthly|quarterly|annual)`, `retention_confidence (enum: high|medium|low)`.

---

#### **8. Why-Now Strength (timing_catalyst_evidence)**
**Why it matters**: "Build a better X" is a weak thesis. "Build a better X right now because [recent market shift]" is strong. VCs obsess over the "why now"—what changed that makes this solvable/valuable today vs last year?

**Definition**: Strength of evidence that a recent catalyst (regulatory change, technology shift, market trend, geopolitical event, platform/API availability) created a timing window.

**0-10 Anchors**:
- **10**: Major regulatory change just mandated this (e.g., GDPR enforcement → privacy SaaS boom). Or platform opened new API (Stripe, Plaid). Or geopolitical shift (sanctions = diaspora finance need).
- **8-9**: Clear market tailwind launched 2023-2024 (e.g., "AI automation tools viable after GPT-4 release", "USDT availability in Venezuela 2023", "TikTok SMB creator tools 2024").
- **6-7**: General macro trend (AI, remote work, ESG) but not a specific catalyst.
- **4-5**: Market opportunity exists but no specific "why now" — you're competing against incumbents on pure execution.
- **2-3**: Weak timing. Market mature, many incumbents.
- **1**: Wrong timing. Market shrinking or new disruptors making your approach obsolete.

**How to source it** (automated):

1. **Regulatory catalyst search**:
   - Tavily: `"[vertical] regulation PASSED law effective 2024 2025"` OR `"[vertical] [country] regulatory mandate"`
   - Match: "As of [date], companies must now...", "New law requires...", "Compliance deadline [date]"
   - Examples: "Brazil data privacy law LGPD enforcement Q4 2024", "Argentina financial tech sandbox opened 2024".

2. **Technology catalyst**:
   - Tavily: `"[API/platform] launched 2024" OR "[technology] available now [date]"`
   - Examples: "OpenAI API released GPT-4 March 2024", "Anthropic Claude API released 2024".
   - Track announcements from major platforms (Stripe, AWS, Google, Meta).

3. **Market/macro catalyst**:
   - Tavily news search: `"[market/sector] growth 2024 2025" OR "[market/sector] crisis shift"`
   - Detect: "Spending on [category] projected to grow X% in 2025" (Gartner, Forrester reports).
   - Example: "AI automation tool spending grows 100%+ in 2025" (Gartner Magic Quadrant).

4. **Geopolitical catalyst (especially LATAM/Venezuela)**:
   - Tavily: `"Venezuela [sector] [year]" OR "[LATAM country] regulatory change"`
   - Examples: "USDT becomes de facto currency Venezuela 2022-2024", "Brazil opens fintech sandbox 2023".
   - Diaspora finance: "Remittances to LATAM grow 10-15% annual" (increasing need).

5. **Platform/API dependency catalyst**:
   - Tavily: `"[platform] API changes 2024 2025" OR "[platform] new features"` → Enables what wasn't possible before
   - Examples: "Meta opens WhatsApp Business API", "Stripe adds [feature]".

**Data storage**: `timing_catalyst_evidence (int 1-10)`, `catalyst_type (enum: regulatory|technology|market|geopolitical|platform)`, `catalyst_date (string: YYYY-MM)`, `catalyst_description (string)`.

---

## Part 2: Industry Taxonomy (2-Level for LATAM/Spain Opportunities)

### Top-Level Verticals (12)

1. **Fintech & Payments** → [payments, lending, lending-alternative, remittances, wallets, invoice-financing, expense-management]
2. **SMB Software & Operations** → [invoicing, crm, payroll, hr-compliance, accounting, inventory-management, point-of-sale]
3. **E-commerce & Retail** → [storefront-builder, order-management, logistics-fulfillment, retail-analytics, inventory-sync]
4. **Logistics & Supply Chain** → [route-optimization, last-mile, warehouse-management, tracking, freight-brokerage]
5. **Healthtech & Wellness** → [telemedicine, patient-management, health-records, pharmacy-logistics, wellness-platform]
6. **Edtech & Skills** → [vocational-training, language-learning, professional-development, k12-adaptive, certification-platform]
7. **Creator & Marketplace** → [creator-monetization, livestream-commerce, influencer-platform, gig-marketplace, service-marketplace]
8. **Agtech & Rural** → [farm-management, precision-agriculture, agri-finance, rural-logistics, farmer-marketplace]
9. **AI & Automation** → [document-processing, customer-service-automation, code-generation, business-process-automation]
10. **Enterprise Software** → [data-analytics, business-intelligence, erpcompact, martech, saas-infrastructure]
11. **Community & Social** → [neighborhood-apps, local-commerce, hyperlocal-community, gaming, social-commerce]
12. **Sustainability & Compliance** → [environmental-tracking, carbon-accounting, regulatory-compliance-tools, audit-automation]

### Sub-Verticals (50 total, shown for 3 parent categories)

**Fintech & Payments** (8):
- payments: P2P, B2B, international transfers, domestic payments
- lending: SMB working capital, short-term loans, invoice financing
- lending-alternative: BNPL, revenue-based financing, peer lending
- remittances: diaspora → home country, digital wallets for diaspora
- wallets: Digital wallets, USDT-native wallets, mobile money
- invoice-financing: Early payment advances, factoring
- expense-management: Corporate card, spend controls, reimbursement
- cross-border-finance: FX, multi-currency, crypto on/off ramps

**SMB Software & Operations** (8):
- invoicing: Invoice generation, payment collection, invoice tracking
- crm: Sales pipeline, customer data, sales automation
- payroll: Salary management, tax withholding, compliance, payment
- hr-compliance: Labor compliance, benefits, worker classification
- accounting: General ledger, reconciliation, financial reporting
- inventory-management: Stock tracking, reorder points, multi-location
- point-of-sale: In-store POS, receipt printing, cash handling
- workflow-automation: Task automation, approval routing, form builder

**E-commerce & Retail** (8):
- storefront-builder: No-code storefronts, cart, checkout
- order-management: Order aggregation, fulfillment, shipping
- logistics-fulfillment: Warehouse, packing, shipping integration
- retail-analytics: Sales dashboards, traffic analysis, conversion metrics
- inventory-sync: Real-time inventory across channels
- omnichannel: Unified inventory, customer data, order routing
- marketplace-seller: Vendor management, commission, seller support
- dynamic-pricing: Price optimization, competitor monitoring

[Remaining 7 parent categories follow same 7-8 sub-vertical pattern]

### Per-Vertical Scoring Modifiers (applied to attractiveness_score)

Applied *after* base 16-dimension scoring. Example: a vertical with high regulatory drag and proven low margins gets -0.5 multiplier.

| Vertical | Capital Intensity | Typical Margin | LATAM Friction | Regulatory Drag | Multiplier |
|----------|-------------------|-----------------|-----------------|-----------------|-----------|
| Fintech/Payments | High | 60-70% | Medium (rails) | High | 0.85x (venture defensible but regulated) |
| SMB Payroll | Low-Med | 65-75% | Low (clear ROI) | Medium | 1.1x (fits LATAM playbook) |
| SMB CRM | Low | 70-80% | Low (pure SaaS) | Low | 1.0x (neutral) |
| E-commerce | Medium | 30-40% | Medium (fulfillment) | Low | 0.9x (margin pressure) |
| Logistics | High | 20-30% | High (ops-heavy) | Low | 0.7x (high capital, low margin) |
| Edtech | Low-Med | 60-70% | Low (digital-first) | Low | 1.05x (slight positive) |
| Creator Economy | Low | 60-80% | Low (platform native) | Low | 1.0x |
| Agtech | Medium-High | 40-55% | High (physical infra) | Medium | 0.75x (capital intense, regulation complex) |
| AI & Automation | Low | 70-85% | Low (pure software) | Low-Medium | 1.15x (high margins, strong tailwind 2024-2025) |
| Enterprise SaaS | Low-Med | 70-85% | Medium (sales cycle) | Low | 0.95x (enterprise sales friction) |
| Community & Social | Low | 50-70% | Low | Low-Medium | 1.0x |
| Sustainability | Low-Med | 65-75% | Low | Medium-High | 0.85x (regulatory uncertain) |

**Application rule**: If vertical has known headwinds (logistics = high capital + low margin + LATAM friction), cap final attractiveness_score at 6.0 even if dimensions score high. Conversely, AI & Automation + strong founder fit can boost to 8.5+.

---

## Part 3: Revenue Evidence Search Playbook

Goal: Systematically establish "is anyone making money here?" before scoring TAM optimistically.

### Query Patterns & Sources (Tavily + Firecrawl + Apify)

---

#### **Step 1: Funding Rounds as Revenue Proxy**

**Why**: Series A funding ≈ $500K-$2M annual revenue (SaaS median 1x-2x revenue at Series A). If 3+ competitors raised Series A in last 2 years, market validated.

| Query Pattern | Source | Extraction |
|--------------|--------|-----------|
| `"[vertical] startup [country] Series A B funding 2024 2025"` | Tavily news search | Funding $X raised → estimate ARR = X × 0.5 to X × 2 depending on stage |
| `"[vertical] [country] funding round crunchbase"` | Tavily site search | Count funded companies, trend |
| `site:contxto.com "[vertical] [country] ronda financiación 2024"` | Tavily/Firecrawl | LATAM-specific: Spanish term = "ronda de financiación" |
| `"Venezuela [vertical] startup investment 2024"` | Tavily | Very limited (capital controls), but count any funding as major signal |

**Success criteria**: ≥3 competitors raised A+ in last 2 years → score competitive_revenue_evidence 7-9.

---

#### **Step 2: Pricing Page Extraction & Comparison**

**Why**: Public pricing reveals willingness to pay and gives revenue estimates (if combined with user count).

| Query | Source | Extraction |
|-------|--------|-----------|
| `[competitor] pricing` (in URL) | Firecrawl scrape | Extract tiers: e.g., "Starter $29/mo, Pro $99/mo, Enterprise custom" |
| Parse pricing across 3-5 competitors | Firecrawl batch scrape | Calculate average tier pricing; identify premiums |
| Extract trial length (14-day vs 30-day) | Firecrawl DOM parse | Shorter trial = faster sales cycle → lower CAC potential |
| Extract MRR caps ("starts at $29/mo") | Regex + LLM parse | Lowest price point = lowest viable market (Venezuela might be $3-5) |

**Success criteria**: 3+ competitors with published pricing; price points make sense for geog → willingness_to_pay likely 6+ and monetization_clarity 7+.

---

#### **Step 3: App Store / Google Play Reviews & Install Counts**

**Why**: Public app installs + review velocity + review sentiment = revenue estimate without access to private financials.

| Metric | Source | Extraction | Revenue Heuristic |
|--------|--------|-----------|-------------------|
| Total reviews | Apify Google Play / App Store actor | Parse app page (e.g., "2.5K reviews") | 2K reviews ≈ 5-10K active installs (20-40% review rate) |
| Reviews per month | Apify historical scrape (if available) OR G2 trending | Trend: 50 reviews/mo growing to 200 reviews/mo YoY | 200 reviews/mo = ~50K installed, growing fast |
| Review sentiment | Apify + LLM analyze | Extract keywords: "expensive", "worth it", "saves time", "integration issues" | Positive sentiment = retention + pricing power |
| Install growth YoY | Apify (if historical data available) | Scrape App Store Rank trends over time | 50% install growth YoY = likely 30-40% revenue growth |

**Success criteria**: Competitor has 5K+ reviews or 100+ monthly reviews → active user base → revenue validation 7-9.

---

#### **Step 4: G2 / Capterra Trends & Sentiment**

**Why**: G2 reviews aggregate buyer sentiment, pricing discussions, and feature requests (revealing pain points). Review velocity = market heating.

| Metric | Source | Method |
|--------|--------|--------|
| Review count & trend | Firecrawl scrape G2 page | "3,450 reviews" → 200 added last quarter (velocity) |
| Average rating | Firecrawl parse | <4.0 = product/market issues; >4.5 = solid retention signal |
| Negative review keywords | Firecrawl + LLM sentiment | "too expensive", "integrations missing", "support slow" |
| "Alternative solutions" section | Firecrawl DOM | Competitors listed = direct competition; count them |
| Peer reviews from [country] | Firecrawl search G2 by geography | Filter by reviewer location (especially for LATAM-specific) |

**Query**: `site:g2.com "[product]" reviews` or `site:capterra.com "[product]" reviews`

**Success criteria**: ≥500 reviews + 4.0+ rating + 50+ new reviews per quarter = strong retention signal → retention_rate_signal 7-9.

---

#### **Step 5: Job Postings as Growth Proxy**

**Why**: Hiring spike = revenue growth + scaling phase. If competitor hiring 50% YoY while market flat, they're winning.

| Signal | Query | Source |
|--------|-------|--------|
| Revenue-indicative roles | `"[competitor] hiring Sales Development Rep OR Account Executive OR Customer Success 2024"` | LinkedIn, site:jobs.[company].com |
| Headcount trends | `site:linkedin.com "[competitor]" "now at [competitor]" 2024 2025` | LinkedIn alumni page growth |
| Role concentration | Count: Sales reps, CS reps, engineers, ops. Ratio reveals: 50% sales = strong growth mode; 30% sales = optimization | LinkedIn company page → "People" → roles |

**Interpretation**: 
- Growing headcount 30%+ YoY with high sales/CS ratio = revenue growth 30-50%+ YoY.
- Flat headcount = revenue flat or declining.

---

#### **Step 6: News & Press Releases for Revenue Announcements**

**Why**: Some companies announce revenue milestones ("reached $1M ARR") or use press coverage to signal traction.

| Query | Source | Extraction |
|-------|--------|-----------|
| `"[competitor] revenue" OR "ARR" OR "MRR" 2024 2025` | Tavily news search | Extract: "$X million ARR" or "reached profitability" |
| `"[competitor] customers" OR "users" growth 2024` | Tavily news | "Onboarded 1,000 customers" = ~$300K-$1M ARR (depends on ARPU) |
| `"[vertical] market grows X% 2024"` | Tavily analyst reports | Top-down: Market growing 30% → leader probably growing 40-60% |
| Earnings calls / investor updates | Tavily site search on company investor relations | Direct financials if public |

---

#### **Step 7: LATAM-Specific: Contxto, LatAmList, Local News**

**Why**: Most LATAM startups have zero Crunchbase/VC data. Local reporting (Spanish-language) is primary source.

| Source | Query Pattern | Extraction |
|--------|---------------|-----------|
| Contxto | `site:contxto.com "[company/vertical] [country]"` | News, funding announcements, customer counts |
| LatAmList | `site:latamlist.com "[company]"` | Founder profiles, revenue hints in interviews |
| LinkedIn profiles | `"[founder] [company]" "About" section` | Founder often mentions "helped 1K+ customers", revenue milestones |
| Twitter/X LATAM tech | Search `#[vertical] [country] 2024 OR 2025` in Spanish | Organic signals, complaints, traction announcements |
| WhatsApp groups / Telegram | Manual research or community signals | Direct operator feedback (informal, but real) |

---

#### **Step 8: Substitute Product Research**

**Why**: If [substitute X] has 100K users, market is real. If no substitutes exist, market may not be validated yet.

| Query | Source | Interpretation |
|-------|--------|-----------------|
| `"best alternatives to [product]"` | Tavily search | Lists substitutes + their traction (reviews, ratings) |
| `[product category] reddit` | Reddit search via Reddit native search or Tavily | Community discusses best tool, reveals incumbent |
| G2 alternatives section | Firecrawl scrape G2 alternatives | Direct competitor list with review counts |

**Scoring**: If 5+ viable substitutes exist with 1K+ reviews each = market is proven → market_size 6-7+.

---

#### **Step 9: Pricing Benchmark Compilation (for Willingness to Pay)**

Once you've extracted 3-5 competitor pricing pages:

| Price Point | WTP Interpretation |
|-------------|-------------------|
| All products $0-49/mo | Ultra price-sensitive market (Venezuela, SMB budget-conscious, free-tier SaaS). WTP: 3-4. |
| Mix $29-149/mo | Standard SMB SaaS. WTP: 6-7. Willing to pay for productivity. |
| Significant $300+/mo SKUs | Enterprise software or high-value vertical (fintech, HR compliance). WTP: 8+. |
| LATAM pricing 50-70% of US for same features | Clear geographic price discrimination. LATAM customers identified as lower WTP. |
| Venezuela/informal SMB pricing $3-15/mo only | VE-specific WTP: 2-3 absolute. Product must be deeply adapted. |

---

## Part 4: Revised Scoring Model with Confidence Dimension

### Architectural Change: Confidence-Weighted Scoring

**Current model**: 16 dimensions × 1-10 score → weighted aggregate.

**Revised model**: 16 + 8 dimensions, each with:
- **Score** (1-10)
- **Confidence** (enum: high | medium | low)
- **Evidence count** (int: number of sources)

**Final attractiveness_score = (weighted sum of scores × average confidence) + confidence bonus**

Where:
- `average_confidence` = (high=1.0, medium=0.8, low=0.6)
- `confidence_bonus` = +0.5 for ≥3 high-confidence dimensions, +0.25 for ≥5 medium, 0 for mostly low

### New 24-Dimension Model Structure

#### **Attractiveness Layer** (50% weight, unchanged structure but now with confidence)
1. pain_severity
2. market_size (now informed by competitor_revenue_evidence + market_growth_rate)
3. timing_tailwind (now informed by timing_catalyst_evidence)
4. willingness_to_pay (now informed by pricing_power_evidence)
5. monetization_clarity

#### **Executability Layer** (30% weight)
6. speed_to_mvp
7. capital_efficiency
8. distribution_accessibility
9. estimated_sales_cycle_days (NEW — inverted, lower = better)

#### **Strategic Layer** (20% weight)
10. competition_intensity
11. defensibility (now informed by regulatory_moat_strength)
12. regional_fit
13. founder_fit

#### **Market Validation Layer** (NEW, 15% weight) 
14. competitor_revenue_evidence
15. estimated_market_growth_rate
16. gross_margin_profile (inferred)

#### **Moat & Pricing Layer** (NEW, 10% weight)
17. regulatory_moat_strength
18. pricing_power_evidence
19. retention_rate_signal

#### **Product & Team Fit** (existing redefined)
20. ai_leverage
21. operational_simplicity
22. regulatory_simplicity
23. revenue_speed_score
24. timing_catalyst_evidence (NEW, captures "why now")

### Revised Weighting Formula

```
attractiveness_score = (
  0.50 × [pain, market_size, timing_tailwind, wtp, monetization] 
  + 0.15 × [speed_to_mvp, capital_efficiency, distribution, sales_cycle]
  + 0.10 × [competition, defensibility, regional_fit, founder_fit]
  + 0.15 × [competitor_revenue, market_cagr, margin_profile]
  + 0.10 × [regulatory_moat, pricing_power, retention]
) × average_confidence

confidence_bonus = {
  +0.5 if ≥3 dimensions scored "high" confidence
  +0.25 if ≥5 dimensions scored "medium" confidence
  0 otherwise
}

final_score = min(10, attractiveness_score + confidence_bonus)
```

### Confidence Scoring Rules (automated)

Each dimension auto-assessed for confidence based on evidence count:

| Evidence Count | Confidence |
|---|---|
| ≥3 independent sources + direct data | HIGH |
| 1-2 sources OR analyst reports OR inferred from benchmarks | MEDIUM |
| Heuristic assumption only, no primary data | LOW |

**Example**: 
- `market_size` scored 7 with 5 market research reports + Crunchbase funding data = HIGH confidence
- `estimated_sales_cycle_days` scored 6 with 1 G2 review comment = LOW confidence
- Final average confidence = (HIGH + LOW + other 22 scores) / 24 ≈ 0.75

---

### Kill Gate: Unchanged (7 binary questions → kill_decision boolean)

No change to kill gate. Dimensions 1-7 below are binary blockers before scoring occurs.

---

### Decision Filters: Unchanged

No change to three decision filters (can_sell_fast, can_build_lean, can_compound). 2+ failures → cap score at 5.0.

---

### New Confidence-Based Output Fields

```json
{
  "id": "opp_uuid",
  "name": "...",
  "attractiveness_score": 7.2,
  "attractiveness_confidence": 0.82,
  "attractiveness_evidence_count": 18,
  "dimensions_by_confidence": {
    "high": ["pain_severity", "monetization_clarity", "competitor_revenue_evidence"],
    "medium": ["market_size", "sales_cycle_days", "founder_fit"],
    "low": ["regulatory_moat_strength", "timing_catalyst_evidence"]
  },
  "score_note": "High confidence in pain & monetization (direct research). Medium confidence in market size (analyst reports + benchmarks). Low confidence in regulatory position (no concrete evidence). Recommend further validation on [dimension].",
  "suggested_next_research": ["regulatory_moat_strength", "timing_catalyst_evidence", "customer_retention_rate"]
}
```

---

## Part 5: Data Sourcing Architecture

### Tool Assignments

| Sourcing Task | Primary Tool | Backup | Cost/Query |
|---|---|---|---|
| News search (funding, announcements) | Tavily | Claude native web search | $0.01-0.05 |
| Web scraping (pricing pages, G2, Capterra) | Firecrawl | Jina fetch | Free-$0.01 |
| App store data (reviews, installs) | Apify Google Play + App Store actors | Manual scraping | $0.01-0.05 |
| Spanish-language research | Tavily (with ES language filters) | Jina search | $0.01-0.05 |
| Crunchbase/VC data | Tavily site search | Exa.ai semantic search | $0.005 |
| Reddit/HN signals | Free (Jina + HN Algolia + Reddit API) | Tavily | $0-0.01 |
| Pricing intelligence | Wayback Machine (free) + Tavily | Firecrawl | $0-0.01 |

### Pipeline Execution Order

For each opportunity, in priority:

1. **Rapid validation** (1-2 min, $0.01): Tavily news search for competitor + funding + revenue keywords
2. **Pricing + G2 extraction** (2-3 min, $0.02-0.05): Firecrawl scrape 3-5 competitor pricing pages + G2 Capterra reviews
3. **App store proxy** (1-2 min, $0.01-0.05): Apify Google Play/App Store actor if mobile product
4. **Regulatory + "why now"** (2-3 min, $0.01-0.02): Tavily search for recent regulatory changes + market catalysts
5. **LATAM deep dive** (2-3 min, $0.01-0.05): Tavily Spanish-language search + Contxto + LatAmList if LATAM/VE
6. **Confidence assessment**: Auto-score based on evidence count + source quality

**Total per opportunity**: ~5-10 minutes wall time, $0.05-0.20 cost, produces 8 new confidence-backed dimensions.

---

## Part 6: Implementation Checklist

### Code Changes Required

- [ ] Add 8 new dimension fields to `Opportunity` model (models.py)
- [ ] Add confidence enum + evidence_count fields for all 24 dimensions
- [ ] Create `evidence_sourcer.py` module with functions:
  - `source_competitor_revenue(opp)` → calls Tavily + Crunchbase
  - `source_market_cagr(opp)` → Tavily market research reports
  - `source_pricing_power(opp)` → Firecrawl + competitor pricing
  - `source_sales_cycle(opp)` → G2 sentiment + keyword extraction
  - `source_regulatory_moat(opp)` → Tavily regulatory news
  - `source_timing_catalyst(opp)` → Tavily + platform announcement tracking
  - `source_retention_signal(opp)` → G2 + usage pattern keywords
  - `source_margin_profile(opp)` → SEC Edgar + industry benchmarks
- [ ] Update `ai_scorer.py` RUBRIC with 8 new dimensions
- [ ] Update `scoring_engine.py` weighting formula to 24 dimensions + confidence formula
- [ ] Create `confidence_calculator.py`: Auto-assess confidence based on evidence count
- [ ] Add `suggested_next_research` field to output (based on low-confidence dims)

### Data Schema Additions

```python
class OpportunityScoringDetail(BaseModel):
    dimension_name: str
    score: int  # 1-10
    confidence: Literal["high", "medium", "low"]
    evidence_count: int  # number of sources
    sources: List[str]  # URLs or source names
    reasoning: str  # one-line explanation
    
class OpportunityScoringResult(BaseModel):
    attractiveness_score: float  # 1-10
    attractiveness_confidence: float  # 0.6-1.0
    dimensions: Dict[str, OpportunityScoringDetail]
    dimensions_by_confidence: Dict[str, List[str]]  # high/medium/low → [dim_names]
    suggested_next_research: List[str]  # dims with low confidence
    score_note: str  # summary of confidence gaps
```

### Tavily + Firecrawl Configuration

- Ensure API keys available in ENV
- Rate limit: 10-20 queries/minute for Tavily (sufficient for daily run)
- Firecrawl: 100 scrapes/month on free tier; upgrade if needed
- Apify: 30-day free trial then ~$5-10/month for app store actors

---

## Part 7: Example Queries (Exact Patterns)

### Example 1: SMB Payroll Software (LATAM)

**Vertical**: SMB Software > Payroll

**Raw signal**: "Venezuelan SMBs using WhatsApp for payroll coordination with accountants"

**Evidence sourcing playbook**:

1. **Competitor revenue** → Tavily: `"payroll software LATAM Series A funding 2024 2025"`
   - Results: Gupy (Brazil), Nómina Fácil (Mexico), Persona Latam (Colombia) all raised ~$5-20M A/B
   - Estimate: $1-5M ARR each
   - **Score: 8/10, HIGH confidence** (funded competitors validate market)

2. **Market CAGR** → Tavily: `"payroll SaaS market LATAM Brazil Mexico Colombia growth rate 2024-2029"`
   - Results: "LATAM payroll software market growing 18% CAGR" (Mordor Intelligence)
   - **Score: 7/10, HIGH confidence** (explicit CAGR in analyst report)

3. **Gross margin** → Tavily: `"payroll SaaS gross margin benchmark"`
   - Results: Gupy, Rippling disclose 70-75% gross margin
   - **Score: 8/10, HIGH confidence** (public filings + competitor data)

4. **Sales cycle** → Firecrawl G2 payroll category:
   - Reviews mention "30-day trial, then monthly subscription"
   - Assumption: 14-30 day sales cycle
   - **Score: 8/10, MEDIUM confidence** (inferred from trial length)

5. **Regulatory moat** → Tavily: `"Brazil payroll compliance LGPD CLT requirements 2024"`
   - Results: Brazil law requires accurate tax filing; payroll SaaS critical for compliance
   - **Score: 7/10, MEDIUM confidence** (regulatory requirement validated)

6. **Pricing power** → Firecrawl scrape Gupy/Nómina Fácil pricing pages:
   - Payroll: $50-200/mo depending on employee count
   - No major price wars visible (prices stable YoY)
   - **Score: 7/10, MEDIUM confidence** (stable pricing + compliance need = inelastic demand)

7. **Retention** → G2 Capterra payroll reviews:
   - "Use daily" (payroll runs monthly but system used for HR data, leave requests daily)
   - 4.6/5 stars, 2K+ reviews, 50+ monthly
   - **Score: 8/10, HIGH confidence** (active review base, high ratings)

8. **Why now** → Tavily: `"Brazil LGPD enforcement 2024" OR "payroll digitalization mandate LATAM"`
   - Results: "LGPD compliance deadline Oct 2024 pushes payroll software adoption" (news)
   - **Score: 8/10, HIGH confidence** (regulatory catalyst just happened)

**Result**:
- attractiveness_score = 0.50 × 7.5 (atractiveness dims avg) + 0.15 × 7.5 (exec dims) + 0.10 × 7.5 (strategic) + 0.15 × 8 (validation) + 0.10 × 7 (moat)
- ≈ 7.5 × (avg confidence 0.88) = 6.6
- confidence_bonus = +0.5 (6 HIGH confidence dims)
- **Final: 7.1/10, HIGH confidence, "Ready for validation"**

---

### Example 2: Venezuelan SMB Informal Commerce Tool

**Vertical**: E-commerce & Retail > Point-of-Sale (informal)

**Raw signal**: "Venezuelan bodegeros (corner store owners) manage inventory via WhatsApp groups; high theft; informal accounting"

**Evidence sourcing**:

1. **Competitor revenue** → Tavily: `"Venezuela POS software startup"`
   - Results: Almost zero competition; maybe 1-2 SMB POS tools in Spanish
   - **Score: 2/10, LOW confidence** (no validated competitors = market may be unproven)

2. **Market CAGR** → Tavily: `"Venezuela retail SMB 2024 growth projections"`
   - Results: "Venezuela retail market shrinking 5% YoY (macro crisis)" OR "E-commerce growing despite macro"
   - Mixed signal: offline retail down, but USDT-enabled informal commerce up
   - **Score: 4/10, LOW confidence** (macro headwind vs digital shift)

3. **Regulatory moat** → Tavily: `"Venezuela retail POS regulation requirements"`
   - Results: Minimal; informal sector operates with no formal POS requirements
   - **Score: 6/10, MEDIUM confidence** (light regulation = low barrier to entry, no moat)

4. **Pricing power** → Manual context + Reddit:
   - Search Reddit Venezuelan SMB communities: "how much would you pay for inventory tracking?"
   - Responses: "$3-5/month max" (informal economy, tight budgets)
   - **Score: 3/10, MEDIUM confidence** (low WTP validated by community)

5. **Why now** → Tavily: `"Venezuela USDT 2024 adoption"`
   - Results: "USDT becomes accepted payment method in Venezuela 2023-2024" (news, Twitter)
   - **Score: 8/10, HIGH confidence** (technology catalyst: USDT payments now viable)

6. **Distribution** → Implicit Venezuela heuristic:
   - "WhatsApp-first distribution" for Venezuelan SMBs
   - **Score: 9/10, HIGH confidence** (founder context + geography-specific)

**Result**:
- attractiveness_score ≈ 5.2 × 0.72 (avg confidence: 1 HIGH, 2 MED, 3 LOW) = 3.7
- No confidence bonus (mostly LOW)
- **Final: 3.7/10, LOW confidence, "Kill or deep research required"**
- suggested_next_research: ["market_cagr", "competitor_revenue_evidence", "willingness_to_pay"] (validate via founder interviews)

---

## Appendix: Full Dimension Reference Card

| # | Dimension | Type | 0-10 Anchor | Confidence Driver | Source Priority |
|---|-----------|------|------------|-------------------|------------------|
| 1 | pain_severity | Orig | Emergency pain (10) vs nice-to-have (1) | Reddit/forum complaints | Research executor |
| 2 | market_size | Orig | TAM > $1B (10) vs < $1M (1) | Analyst reports + competitor $ | Market research |
| 3 | timing_tailwind | Orig | New regulation (10) vs contracting (1) | News search for catalysts | Tavily news |
| 4 | willingness_to_pay | Orig | High price points (10) vs free (1) | Competitor pricing + customer research | Firecrawl pricing |
| 5 | monetization_clarity | Orig | Proven model (10) vs unclear (1) | Competitor revenue evidence | Firecrawl + news |
| 6 | speed_to_mvp | Orig | < 2 weeks (10) vs > 6 months (1) | Product complexity | Founder interview |
| 7 | capital_efficiency | Orig | < $500 (10) vs > $500K (1) | Infrastructure requirements | Founder + vertical heuristic |
| 8 | distribution_accessibility | Orig | Warm intros clear (10) vs no path (1) | Geography + vertical heuristic | Distribution research |
| 9 | competition_intensity | Orig | No competitor (10) vs dominated (1) | Competitor landscape scan | Tavily + G2 |
| 10 | defensibility | Orig | 3x moat levers (10) vs none (1) | Moat analysis (data, network, switching) | Strategic analysis |
| 11 | regional_fit | Orig | Built for VE/LATAM (10) vs Western (1) | Payment rails + distribution fit | Geography-specific research |
| 12 | founder_fit | Orig | 6 wedges (10) vs 0 (4) | Daniel's background match | Self-assessment |
| 13 | ai_leverage | Orig | Core product (10) vs irrelevant (1) | Product architecture | Founder + tech analysis |
| 14 | operational_simplicity | Orig | Fully async (10) vs ops-heavy (1) | Team requirements | Business model analysis |
| 15 | regulatory_simplicity | Orig | No license (10) vs banking (1) | Regulatory research | Tavily regulatory search |
| 16 | revenue_speed_score | Orig | < 7 days (10) vs > 6 months (1) | First revenue model | Founder + vertical heuristic |
| **17** | **estimated_market_growth_rate** | **NEW** | **> 50% CAGR (10) vs shrinking (1)** | **Market reports + startup funding trends** | **Tavily market research** |
| **18** | **competitor_revenue_evidence** | **NEW** | **3+ competitors with ARR (10) vs none (1)** | **Crunchbase + funding news + pricing** | **Tavily + Firecrawl** |
| **19** | **implied_gross_margin_percent** | **NEW** | **80%+ (10) vs < 20% (1)** | **Public filings + industry benchmarks** | **SEC Edgar + analyst reports** |
| **20** | **estimated_sales_cycle_days** | **NEW** | **< 7 days (10) vs > 180 (1)** | **G2 reviews + competitor sales info** | **Firecrawl G2** |
| **21** | **regulatory_moat_strength** | **NEW** | **License creates moat (10) vs threat (1)** | **Regulatory research + competitor licensing** | **Tavily regulatory** |
| **22** | **pricing_power_evidence** | **NEW** | **Inelastic + high switching (10) vs commodity (1)** | **Price history + competitor pricing** | **Firecrawl + Wayback Machine** |
| **23** | **retention_rate_signal** | **NEW** | **Daily use NRR 120%+ (10) vs episodic churn (1)** | **G2 usage keywords + benchmarks** | **G2 Capterra sentiment** |
| **24** | **timing_catalyst_evidence** | **NEW** | **Major regulatory/tech catalyst (10) vs no catalyst (1)** | **News + platform announcements** | **Tavily news search** |

---

## Conclusion

This spec systematizes what professional VCs already evaluate manually:

1. **Evidence before narrative**: Start with competitor revenue + market growth, not TAM claims.
2. **Regional adaptation**: LATAM ≠ US. Apply geography-specific pricing, distribution, regulatory lenses.
3. **Confidence transparency**: Not all scores are equally valid. Mark which scores are backed by data vs heuristics.
4. **Automated sourcing**: Tavily + Firecrawl + Apify can establish revenue evidence, pricing power, retention, regulatory risk without manual research.
5. **Confidence-weighted scoring**: A 7.0 attractiveness_score backed by 2 sources is different from 7.0 backed by 10 sources. Make that visible.

The system moves from "score based on problem description" to "score based on market validation evidence." This is how real VCs decide.
