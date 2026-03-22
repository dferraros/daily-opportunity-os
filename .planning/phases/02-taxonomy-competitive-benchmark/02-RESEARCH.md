# Phase 2: Taxonomy + Competitive Benchmark - Research

**Researched:** 2026-03-22
**Domain:** Trigger-based notification taxonomy design, competitive benchmarking, EU compliance for crypto marketing communications
**Confidence:** MEDIUM-HIGH

## Summary

Phase 2 transforms the safety rails from Phase 1 (consent categories, frequency caps, suppression layers, event schema) into a complete trigger taxonomy -- six families of triggers with explicit eligibility criteria, an asset universe mapped to Bit2Me products, a competitor benchmark matrix, and compliance constraints codified per trigger type. The output is a structured framework that Phase 3 will use to score and tabulate 30+ individual triggers.

The research reveals three critical findings: (1) MiCA does NOT provide a bright-line test between "informational" and "investment advice" in notifications -- ESMA is still developing guidance, so Bit2Me must adopt a conservative internal classification test reviewed by Diego; (2) competitor eligibility rules are surprisingly simple (Coinbase: any tradable asset on watchlist; Binance: Pro-only, max 50 alerts, 10/pair, 90-day expiry) and Bit2Me should avoid Binance's artificial limits while adopting Coinbase's watchlist-first approach; (3) the asset universe must be scoped per product (not all 420+ assets are available in Earn, Pro, Card, etc.) and this product-asset eligibility matrix is foundational to cross-sell trigger design.

**Primary recommendation:** Structure each trigger family with a standardized template (trigger_id, eligibility criteria, consent category, priority tier, asset scope, compliance classification, data source, cooldown) that directly references Phase 1 constructs. Build the asset-product eligibility matrix first -- it is a dependency for Families A, B, E, and F.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TAX-01 | Taxonomia completa de 6 familias de triggers con criterios de elegibilidad | Standardized trigger family template defined; eligibility criteria patterns from competitor research; Phase 1 consent/priority mapping |
| TAX-02 | Familia A -- User Configured (price above/below, % move, target reached, LTV threshold) | Coinbase/Binance alert eligibility rules researched; Binance limits (50 total, 10/pair, 90d expiry) documented as anti-pattern; consent category = CAT-USR, priority = P1 |
| TAX-03 | Familia B -- Market Triggered (volatility spike, volume spike, trending asset, breakout) | Market abuse constraints (MiCA Art. 87-92) researched; public data source requirement; simultaneous send rule; consent = CAT-MKT, priority = P3 |
| TAX-04 | Familia C -- Behavioral (watched not bought, deposit no trade, abandoned order, repeated views) | Event schema from Phase 1 maps directly to behavioral triggers; CleverTap Live Segments for real-time behavioral targeting |
| TAX-05 | Familia D -- Lifecycle (active to at-risk, dormant with balance, first trade, recurring lapsed) | 13 lifecycle stages from LC-OS; Hightouch sync fields (lifecycle_stage, days_since_last_activity, health_score) enable targeting; consent = CAT-MKT/CAT-PRO, priority = P2-P5 |
| TAX-06 | Familia E -- Product Cross-sell (stablecoins not in Earn, eligible for Loan, Space Center missions) | Asset-product eligibility matrix needed; products_active field from Hightouch sync; MiCA advice-vs-information boundary researched; consent = CAT-PRO, priority = P4 |
| TAX-07 | Familia F -- Risk & Protective (LTV approaching threshold, large balance inactivity, failed actions) | Nexo graduated LTV alerts (71.4%, 74.1%, 76.9%) benchmarked; consent = CAT-SEC/CAT-TXN for protective, priority = P0-P1 |
| TAX-08 | Asset universe mapping -- que activos son elegibles para cada familia de trigger | Bit2Me supports 420+ crypto assets; product-specific asset eligibility varies (Earn subset, Pro subset, Card all); scoping rules from Coinbase/Binance researched |
| BENCH-01 | Matriz comparativa de 6 competidores (Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo) | Full matrix already in FEATURES.md; needs deepening on eligibility rules and preference center granularity per competitor |
| BENCH-02 | Por competidor: tipos de alerta, preference center, canales, asset scope, gaps | Detailed per-competitor deep dives in FEATURES.md; additional eligibility data gathered (Binance limits, Coinbase watchlist model, Revolut 2% fixed anti-pattern) |
| BENCH-03 | Recomendaciones concretas: que copiar, que evitar, que innovar | Blue ocean gaps identified; anti-features documented; copy/avoid/innovate framework from FEATURES.md Part C |
| COMP-01 | Compliance checklist por trigger -- MiCA Art. 66, GDPR, ePrivacy, CNMV | MiCA Art. 66 "fair, clear, not misleading" requirements researched; mandatory disclaimer text identified; ESMA marketing guidelines mapped; per-trigger compliance classification template designed |
| COMP-02 | Diego review workflow -- que copy necesita aprobacion y cuando | Four-eyes principle (maker-checker) workflow researched; pre-approved copy library pattern; tiered approval (template-level vs campaign-level) |
| COMP-03 | Investment advice vs informational -- regla clara y ejemplos concretos | ESMA knowledge/competence guidelines (Jan 2026) and suitability guidelines (Feb 2026) researched; NO bright-line test exists in MiCA -- internal conservative classification required; detailed safe/dangerous examples table from PITFALLS.md |
| COMP-04 | Market abuse risk en price/volume triggers -- protocolo de datos publicos y simultaneidad | MiCA Art. 87-92 market abuse framework researched; ESMA April 2025 guidelines on detection/prevention; public data source requirement + simultaneous send + audit log requirements documented |
</phase_requirements>

---

## Architecture Patterns

### Standardized Trigger Family Template

Every trigger in every family must follow this template structure. This ensures Phase 3 can tabulate all triggers uniformly in the Master Trigger Table.

```
TRIGGER DEFINITION TEMPLATE
============================
- trigger_id: [FAM]-[NN] (e.g., A-01, B-05, D-03)
- family: A|B|C|D|E|F
- trigger_name: Human-readable name
- business_objective: What business outcome this drives
- description: What fires the trigger

ELIGIBILITY CRITERIA
- who_receives: Segment/lifecycle/product conditions
- who_never_receives: Hard exclusions
- consent_category: CAT-SEC|CAT-TXN|CAT-USR|CAT-MKT|CAT-PRD|CAT-PRO (from Phase 1)
- consent_required: boolean (false for CAT-SEC, CAT-TXN)
- asset_scope: Which assets this trigger applies to

DELIVERY RULES
- priority_tier: P0|P1|P2|P3|P4|P5 (from Phase 1)
- channel: push|email|in-app|multi
- cooldown: Minimum time between fires for same user
- quiet_hours_exempt: boolean (true only for P0)

DATA REQUIREMENTS
- data_source: BigQuery view | CleverTap Live Segment | Cloud Function | SDK event
- required_events: Which events from Phase 1 event schema are needed
- required_user_properties: Which Hightouch-synced fields are needed
- evaluation_frequency: Real-time | Hourly | Daily

COMPLIANCE
- compliance_class: TRANSACTIONAL | INFORMATIONAL | MARKETING | ADVISORY_RISK
- diego_approval: REQUIRED | NOT_REQUIRED | TEMPLATE_PRE_APPROVED
- mica_risk_level: NONE | LOW | MEDIUM | HIGH
- risk_warning_required: boolean
- keyword_blocklist_applies: boolean
```

### Compliance Classification System

Every trigger must be classified into one of four compliance classes. This classification determines the Diego review workflow and MiCA obligations.

| Compliance Class | Definition | Diego Review | MiCA Art. 66 | Risk Warning | Examples |
|------------------|-----------|-------------|-------------|-------------|---------|
| TRANSACTIONAL | Confirms a user-initiated action or protects account security | NOT_REQUIRED | Not applicable (contractual) | No | Trade filled, withdrawal confirmed, login alert |
| INFORMATIONAL | States a fact about market or portfolio state without suggesting action | TEMPLATE_PRE_APPROVED | Applies -- must be fair, clear, not misleading | Link to risk page | "BTC crossed $70,000", "Your BTC holding is up 12%" |
| MARKETING | Promotes a Bit2Me product or encourages a commercial action | REQUIRED per template | Full compliance -- identifiable as marketing, disclaimers, risk warnings | Yes -- in or linked | Cross-sell, reactivation, new listing promo |
| ADVISORY_RISK | Could be construed as suggesting an investment action -- HIGH regulatory risk | REQUIRED per message + legal review | Full compliance + possible MiCA Art. 81 suitability concerns | Yes -- mandatory inline | DO NOT USE without explicit legal clearance. Reserve for V3. |

**Conservative rule for the informational-vs-advisory boundary:**

Since MiCA does NOT provide a bright-line test (ESMA is still developing guidance as of March 2026), Bit2Me must adopt this internal rule:

1. A notification is INFORMATIONAL if it states a verifiable fact without suggesting any action. Examples: "BTC is at $70,000", "Your portfolio changed by X%", "ETH Earn APY is currently 3.2%"
2. A notification crosses into ADVISORY_RISK territory if it: (a) pairs a fact with a value judgment ("great entry point", "beats savings accounts"), (b) implies urgency around a financial action ("don't miss out", "last chance"), (c) compares crypto-asset returns to non-crypto alternatives, or (d) suggests the user should buy, sell, hold, or move assets.
3. When in doubt, classify as MARKETING and require Diego approval. It is always safer to over-classify than under-classify.

**Keyword blocklist for automated pre-screening:**
```
PROHIBITED in notification copy (any compliance class):
  "guaranteed", "risk-free", "pump", "moon", "100x"

FLAGGED -- requires Diego review:
  "should", "opportunity", "don't miss", "good time to", "beats",
  "outperforms", "recommended", "consider buying", "last chance",
  "entry point", "bargain", "undervalued", "profit"

REQUIRED in marketing notifications:
  Risk warning text or link: "Capital at risk. Not investment advice."
  MiCA mandatory disclaimer: "This crypto-asset marketing communication
  has not been reviewed or approved by any competent authority in any
  Member State of the European Union."
```

### Diego Review Workflow (Four-Eyes Principle)

The compliance copy approval workflow for Bit2Me notifications follows a maker-checker (four-eyes) pattern:

```
TIER 1: Template-Level Approval (one-time per template)
========================================================
For: Notification templates with fixed copy (no dynamic content beyond asset name/price)
Process:
  1. Katy/Growth creates notification template with copy + channel + deep link
  2. Template passes automated keyword blocklist scan
  3. Diego reviews template copy against MiCA Art. 66 checklist:
     - Fair, clear, not misleading?
     - Identifiable as marketing (if applicable)?
     - Risk warning present or linked?
     - No prohibited keywords?
     - No investment advice language?
  4. Diego approves (written record in Lark/Notion with timestamp)
  5. Template marked as PRE_APPROVED in CleverTap template library
  6. Any change to template copy requires re-approval

TIER 2: Campaign-Level Approval (per campaign launch)
========================================================
For: Campaigns using dynamic copy, new segment targeting, or first use of a template
Process:
  1. Katy creates campaign with template + targeting + schedule
  2. Send test to internal QA segment
  3. Diego reviews: template (if not pre-approved), targeting segment, channel, schedule
  4. Diego approves (written record)
  5. Campaign activated

TIER 3: Emergency Override (P0 security/compliance only)
========================================================
For: Security alerts, regulatory-mandated communications
Process:
  1. Engineering/Compliance creates alert using pre-approved security template
  2. No Diego review required (templates are contractual necessity)
  3. Post-send notification to Diego for audit trail
```

**SLA targets:**
- Tier 1: Diego turnaround within 48 hours (not a blocker for campaign creation, only for go-live)
- Tier 2: Diego turnaround within 24 hours
- Tier 3: Immediate (no review needed)

### Asset Universe Architecture

The asset-product eligibility matrix is a foundational data structure that determines which assets are eligible for which trigger types across Bit2Me products.

```
ASSET UNIVERSE STRUCTURE
=========================

Layer 1: All Listed Assets (~420+ cryptocurrencies)
  - Source: Bit2Me listing database
  - Eligible for: Family A (user-configured price alerts), Family B (market triggers)
  - Any asset listed on Bit2Me can have price alerts and market triggers

Layer 2: Product-Specific Asset Subsets
  - Wallet: All listed assets (buy, hold, send, receive)
  - Brokerage (Buy & Sell): All listed assets (simple buy/sell)
  - Pro (Order Book): Subset with sufficient liquidity (trading pairs)
  - Earn: Subset with active staking/earn programs (variable, typically 20-50 assets)
  - Card: All assets (spend any held crypto)
  - Loan: Collateral-eligible assets only (typically BTC, ETH, stablecoins)
  - Launchpad: New token launches (event-driven, not persistent)
  - Space Center: B2M token primarily (gamification/loyalty)
  - Pay: Payment-eligible assets
  - Wealth: TBD (not yet launched as of March 2026)
  - API: All listed assets

Layer 3: Trigger-Asset Eligibility Matrix
  - Family A triggers: Any Layer 1 asset
  - Family B triggers: Top 50-100 by volume (avoid noise from illiquid assets)
  - Family C triggers: Assets the user has interacted with (viewed, traded, held)
  - Family D triggers: Not asset-specific (lifecycle stage-based)
  - Family E triggers: Product-specific subsets (Earn-eligible, Loan-eligible, Pro-eligible)
  - Family F triggers: Assets the user currently holds or has collateralized
```

### Recommended Project Structure for Phase 2 Deliverables

```
.planning/phases/02-taxonomy-competitive-benchmark/
  playbook-section-trigger-taxonomy.md      # TAX-01: Overview + template + all 6 families
  playbook-section-family-A-user-configured.md  # TAX-02: Family A detailed triggers
  playbook-section-family-B-market.md           # TAX-03: Family B detailed triggers
  playbook-section-family-C-behavioral.md       # TAX-04: Family C detailed triggers
  playbook-section-family-D-lifecycle.md        # TAX-05: Family D detailed triggers
  playbook-section-family-E-crosssell.md        # TAX-06: Family E detailed triggers
  playbook-section-family-F-risk.md             # TAX-07: Family F detailed triggers
  playbook-section-asset-universe.md            # TAX-08: Asset-product eligibility matrix
  playbook-section-competitor-benchmark.md      # BENCH-01, BENCH-02, BENCH-03
  playbook-section-compliance-per-trigger.md    # COMP-01, COMP-02, COMP-03, COMP-04
```

---

## Competitor Benchmark -- Deepened Findings

### Eligibility Rules by Competitor

| Competitor | Alert Scope | Limits | Eligibility | Preference Granularity |
|-----------|-----------|-------|------------|----------------------|
| **Coinbase** | Any tradable asset (crypto + stocks) | Unlimited | Watchlist-first: star asset, then bell icon. Per-alert channel selection | Per-alert: channel, frequency dropdown |
| **Binance** | All pairs (Pro mode only) | 50 total, 10/pair, 90-day expiry | Pro-only. Price target OR % change. One-off/daily/always frequency | Per-alert: mute toggle, frequency. Global: marketing/ops/risk categories |
| **Kraken** | All spot + futures pairs | Undocumented (no published limits) | Chart-integrated: right-click chart to set alert. Pro web + mobile sync | No per-alert customization beyond price target |
| **Bitpanda** | All listed (crypto, stocks, ETFs, metals) | Undocumented | Email-only for price targets. Savings Plan failure alerts automatic | No preference center for notification categories |
| **Revolut** | 280+ crypto (limited alerts); 4000+ stocks (richer alerts) | Undocumented | Fixed 2% volatility toggle (crypto). Watchlist auto-alerts at 5% (stocks only) | Simple on/off per notification type |
| **Nexo** | All listed assets | Undocumented | AI Insights auto-pushed to all. LTV alerts automatic. Loyalty tier alerts automatic | Per-type toggle (marketing/ops/risk) |

### What to Copy, Avoid, and Innovate

**COPY (proven patterns):**
1. **Coinbase watchlist-first model** -- star + bell = two-step mental model with zero friction. This is the gold standard for user-configured alerts.
2. **Binance alert frequency options** -- one-off / daily / always. Critical for anti-fatigue.
3. **Nexo graduated LTV alerts** -- three progressive thresholds (71.4%, 74.1%, 76.9%). Not binary. Builds trust for Loan product.
4. **Coinbase per-alert channel selection** -- each alert independently chooses push, email, or in-app.
5. **Nexo anti-phishing code in emails** -- unique code users verify. Low cost, high trust.

**AVOID (proven anti-patterns):**
1. **Revolut fixed 2% volatility threshold** -- BTC moves 2% daily = daily spam. Users complain heavily. Let users set their own threshold (default 5% for crypto).
2. **Binance Pro-only alerts** -- excludes the largest user segment. Alerts for ALL users, not just power traders.
3. **Binance 50 alert limit + 90-day expiry** -- arbitrary restrictions that frustrate power users. No artificial limits; archive inactive alerts instead.
4. **Bitpanda email-only price alerts** -- no push for price targets is a missed engagement opportunity.

**INNOVATE (blue ocean for Bit2Me):**
1. **Cross-product notification triggers** -- No competitor connects products via alerts. "Your stablecoins could be earning 3.2% APY in Earn" is unique to multi-product platforms.
2. **Space Center gamification triggers** -- "You're 200 B2M from Tier 4" has zero competitor equivalent.
3. **Portfolio-level alerts** -- Nobody sends "Your portfolio dropped 10% today." This is V2 but should be designed into the taxonomy now.
4. **Alert-to-action deep links** -- All competitors land on generic asset pages. One-tap trade from notification is a conversion multiplier.
5. **Earn rate change alerts** -- When APY changes, nobody notifies proactively. Easy win for retention.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|------------|------------|-----|
| Compliance classification per trigger | Ad-hoc review per campaign | Structured 4-class compliance system (TRANSACTIONAL / INFORMATIONAL / MARKETING / ADVISORY_RISK) with pre-approved templates | Consistency, audit trail, reduced Diego bottleneck |
| Trigger eligibility evaluation | Custom logic per trigger | Standardized trigger template with eligibility criteria mapped to BigQuery views + CleverTap user properties | Maintainability; Phase 3 Master Trigger Table requires uniform structure |
| Asset-product mapping | Hard-coded asset lists | Dynamic BigQuery view (`asset_product_eligibility`) that updates when new assets are listed or product eligibility changes | 420+ assets change; hard-coding is unmaintainable |
| Competitor benchmarking | Free-form prose comparison | Structured matrix with consistent columns per competitor | Enables gap analysis and prioritization |
| Diego review workflow | Informal Slack approvals | Tiered approval workflow with written records in Lark/Notion | Audit trail for MiCA compliance |

---

## Common Pitfalls

### Pitfall 1: Over-Scoping the Asset Universe for Market Triggers
**What goes wrong:** Team enables volatility alerts for all 420+ assets. Obscure microcap tokens with $500 daily volume trigger "volume spike" alerts constantly -- noise, not signal.
**Why it happens:** Treating all listed assets equally without liquidity/volume filtering.
**How to avoid:** Family B (market triggers) should only fire for assets in the Top 50-100 by volume on Bit2Me. Assets below a minimum daily volume threshold (e.g., EUR 10,000) are excluded from proactive market alerts. User-configured alerts (Family A) have no asset scope restriction -- users choose what they want.
**Warning signs:** Low CTR on market trigger notifications; high dismissal rates for notifications about obscure assets.

### Pitfall 2: Treating All Cross-Sell Triggers as Equivalent Risk
**What goes wrong:** "You might like Pro" is treated the same as "Your BTC could earn 3.2% in Earn." The second one is much closer to the investment advice boundary.
**Why it happens:** Cross-sell triggers are lumped into one category without compliance risk differentiation.
**How to avoid:** Sub-classify Family E triggers by compliance risk. Product awareness ("Did you know about Earn?") = MARKETING. Product comparison with returns ("Earn 3.2% vs. holding in Wallet") = ADVISORY_RISK. Only the former should be in V1.
**Warning signs:** Diego rejecting cross-sell copy repeatedly; inconsistent approval decisions.

### Pitfall 3: Lifecycle Triggers Conflicting with Active Journeys
**What goes wrong:** User enters the J-Post-FM 48h journey (Phase 1 lifecycle journey). Simultaneously, a lifecycle trigger fires "You haven't traded in 30 days." User gets conflicting messages.
**Why it happens:** Lifecycle triggers (Family D) and CleverTap Journeys (J1-J6) operate independently.
**How to avoid:** Every Family D trigger must check whether the user is currently in an active journey. Add `active_journey` as a Hightouch-synced user property. If `active_journey IS NOT NULL`, suppress Family D triggers for that user.
**Warning signs:** Users receiving 2+ lifecycle-related notifications on the same day; journey conversion rates declining after trigger launch.

### Pitfall 4: Forgetting the MiCA Mandatory Disclaimer
**What goes wrong:** Marketing notifications go out without the mandatory MiCA disclaimer: "This crypto-asset marketing communication has not been reviewed or approved by any competent authority in any Member State of the European Union."
**Why it happens:** The disclaimer is new (MiCA became fully enforceable December 2024) and teams are not accustomed to including it.
**How to avoid:** Every notification template classified as MARKETING must include the disclaimer -- either inline (for email) or linked (for push, where character limits apply). Add this as a required field in the template creation checklist. Automated validation: reject templates missing the disclaimer.
**Warning signs:** Templates going to Diego without disclaimers; Diego flagging the same issue repeatedly.

### Pitfall 5: Building Taxonomy Without Testing Data Availability
**What goes wrong:** Taxonomy defines a trigger like "Repeated views of asset page without purchase" but the event `Product_Viewed` is not being tracked consistently, or the `duration_sec` property is always null.
**Why it happens:** Taxonomy design happens in isolation from data reality.
**How to avoid:** For every trigger, verify that the required events (from Phase 1 event schema) and user properties (from Phase 1 Hightouch sync) are actually populated. Add a "data_readiness" column to the trigger template: GREEN (data exists), AMBER (data exists but quality unknown), RED (data not yet collected).
**Warning signs:** Triggers defined that reference events or properties not in the Phase 1 event schema.

---

## Code Examples

### Trigger Family A -- User-Configured Alert Example

```
TRIGGER DEFINITION: A-01 Price Target Alert
=============================================
trigger_id: A-01
family: A (User Configured)
trigger_name: Price Target Alert (Above/Below)
business_objective: Engagement, trading activation
description: User sets a price target for a specific asset. Notification fires
             when the asset price crosses the target.

ELIGIBILITY CRITERIA
- who_receives: Any user who has created a price alert via Price_Alert_Set event
- who_never_receives: C8_Whale_Suppression, Excluded_Users
- consent_category: CAT-USR (Art. 6(1)(b) -- contract performance)
- consent_required: false (user explicitly requested this)
- asset_scope: All listed assets (Layer 1 -- no restriction)

DELIVERY RULES
- priority_tier: P1 (user-configured -- exempt from global caps)
- channel: Push (primary), Email (fallback if push disabled)
- cooldown: 1 per asset per 4 hours (prevent spam during volatile markets)
- quiet_hours_exempt: false (unless user opts into 24/7 delivery)

DATA REQUIREMENTS
- data_source: Cloud Function (Price_Alert_Triggered event)
- required_events: Price_Alert_Set (SDK), Price_Alert_Triggered (Cloud Function)
- required_user_properties: None (alert config stored separately)
- evaluation_frequency: Real-time (Cloud Function polls CoinGecko every 5 min)

COMPLIANCE
- compliance_class: TRANSACTIONAL (user-requested service)
- diego_approval: NOT_REQUIRED (transactional -- user asked for this)
- mica_risk_level: NONE
- risk_warning_required: false
- keyword_blocklist_applies: false
```

### Trigger Family E -- Cross-Sell Example

```
TRIGGER DEFINITION: E-01 Stablecoins Not in Earn
==================================================
trigger_id: E-01
family: E (Product Cross-sell)
trigger_name: Stablecoin Earn Opportunity
business_objective: Product adoption (Earn), revenue expansion
description: User holds stablecoins (USDT, USDC, DAI) in Wallet but has not
             subscribed to Earn for any of them.

ELIGIBILITY CRITERIA
- who_receives: lifecycle_stage IN (ACTIVE, POWER) AND
                holds_stablecoins = true AND
                'earn' NOT IN products_active AND
                consent_marketing_push = true
- who_never_receives: C8_Whale_Suppression, Excluded_Users,
                      notification_fatigue_score > 0.7,
                      users who dismissed E-family notification in last 7 days
- consent_category: CAT-PRO (promotional -- requires explicit consent)
- consent_required: true
- asset_scope: Earn-eligible stablecoins only (USDT, USDC, DAI -- from Layer 2)

DELIVERY RULES
- priority_tier: P4 (cross-sell)
- channel: Email (primary -- richer context), In-App (secondary)
- cooldown: 1/week, 2/month maximum
- quiet_hours_exempt: false

DATA REQUIREMENTS
- data_source: BigQuery (Hightouch sync -- products_active, asset holdings)
- required_events: None (state-based, not event-based)
- required_user_properties: products_active, total_balance_eur,
                            lifecycle_stage, holds_stablecoins (computed)
- evaluation_frequency: Daily (Hightouch sync)

COMPLIANCE
- compliance_class: MARKETING (promotes Earn product)
- diego_approval: REQUIRED (template-level -- Tier 1)
- mica_risk_level: MEDIUM (mentions yield -- must not compare to savings accounts)
- risk_warning_required: true ("APY is variable. Capital at risk.")
- keyword_blocklist_applies: true

COPY CONSTRAINTS:
  SAFE: "Your USDT could be earning rewards in Bit2Me Earn. Current APY: 3.2%.
         Variable rate. Capital at risk."
  UNSAFE: "Earn more than your bank with Bit2Me Earn!" (comparative = advisory risk)
  UNSAFE: "Don't miss this opportunity to earn passive income" (urgency + advisory)
```

### Compliance Checklist Per Trigger (COMP-01 Template)

```
COMPLIANCE CHECKLIST: [trigger_id]
====================================
1. GDPR Lawful Basis
   [ ] Art. 6(1)(a) explicit consent (marketing) OR
   [ ] Art. 6(1)(b) contractual necessity (transactional/user-configured)
   Basis: _______________

2. ePrivacy Per-Channel Consent
   [ ] Push: consent_marketing_push = true (if marketing)
   [ ] Email: consent_marketing_email = true (if marketing)
   [ ] In-App: consent_marketing_inapp = true (if promotional in-app)
   Channels used: _______________

3. MiCA Art. 66 -- Fair, Clear, Not Misleading
   [ ] Copy reviewed against keyword blocklist
   [ ] No prohibited terms (guaranteed, risk-free, pump, moon)
   [ ] Marketing clearly identifiable as marketing
   [ ] Risk warning present or linked
   [ ] MiCA mandatory disclaimer included/linked (marketing only):
       "This crypto-asset marketing communication has not been reviewed
       or approved by any competent authority in any Member State of the EU."

4. MiCA Investment Advice Boundary
   [ ] Copy states facts only -- no action suggestions
   [ ] No comparisons to non-crypto alternatives
   [ ] No urgency language implying financial opportunity
   [ ] Classified as: TRANSACTIONAL / INFORMATIONAL / MARKETING / ADVISORY_RISK
   If ADVISORY_RISK: STOP -- escalate to Diego + legal team

5. MiCA Art. 87-92 Market Abuse (for Family B triggers only)
   [ ] Data source is publicly available (CoinGecko API, not internal order book)
   [ ] All eligible users receive notification simultaneously (no staggering)
   [ ] Notification not timed to internal platform events (listings, delistings)
   [ ] Audit log captures: trigger_id, timestamp, user_count, data_source

6. CNMV / Spain-Specific
   [ ] Disclaimers retained (MiCA-aligned, not removed post-Circular 1/2022 repeal)
   [ ] Internal campaign register maintained (good practice, may be re-required)

7. Diego Approval Gate
   [ ] Template sent to Diego for review
   [ ] Diego written approval received (date: ___, medium: ___)
   [ ] Approval stored in Lark/Notion with timestamp

REVIEWED BY: _______________
DATE: _______________
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|-------------|-----------------|-------------|--------|
| CNMV Circular 1/2022 (prior notification for mass campaigns >100K) | MiCA Art. 66 applies directly; Circular 1/2022 repealed Dec 28, 2024 | Dec 2024 | No more prior notification requirement, but MiCA marketing rules are stricter |
| Informal compliance review | Tiered four-eyes principle (maker-checker) with audit trail | MiCA enforcement Dec 2024 | Every template needs documented approval |
| Single "notifications opt-in" toggle | Per-category, per-channel consent (GDPR + ePrivacy) | Always required, but enforcement increasing 2025-2026 | Separate consent flags per channel per category |
| Generic disclaimer ("Invest responsibly") | MiCA mandatory disclaimer + risk warnings per notification type | MiCA Dec 2024 | Specific disclaimer text required in all marketing communications |
| ESMA suitability guidelines for crypto | Published Feb 2026, effective July 2026 | Feb 2026 | Staff giving advice need 20h CPD; staff giving information need 10h CPD |

---

## Open Questions

1. **Bit2Me Earn -- which assets currently have active Earn programs?**
   - What we know: Earn exists as a product; likely includes major assets (BTC, ETH, stablecoins) but the exact list is needed for Family E trigger scoping.
   - What is unclear: Exact list of Earn-eligible assets and current APY rates.
   - Recommendation: Katy or product team provides the current Earn asset list. The taxonomy uses a dynamic reference ("Earn-eligible assets") rather than hard-coding.

2. **Loan product -- which assets are accepted as collateral?**
   - What we know: Bit2Me offers Loan. Nexo's model uses BTC, ETH, stablecoins as collateral.
   - What is unclear: Bit2Me's specific collateral-eligible assets and LTV thresholds.
   - Recommendation: Product team confirms collateral rules. Family F trigger (LTV alerts) depends on this.

3. **Space Center data availability in BigQuery**
   - What we know: Space Center has 7 tiers. B2M holders advance 100x faster.
   - What is unclear: Whether Space Center progression data (current tier, points to next tier, mission completion) is in BigQuery or only in the app backend.
   - Recommendation: Confirm with Alvaro. If not in BigQuery, Space Center triggers (Family E) are V2.

4. **Active journey tracking**
   - What we know: CleverTap journeys J1-J6 exist. Phase 1 defined J-Post-FM.
   - What is unclear: Whether CleverTap exposes "user is currently in journey X" as a property that Hightouch can sync.
   - Recommendation: Investigate CleverTap Journey API. If not available, use BigQuery to track journey entry/exit events.

5. **MiCA mandatory disclaimer in push notifications**
   - What we know: The disclaimer must appear in all marketing communications. Push has 40-60 character sweet spot.
   - What is unclear: Whether linking to the disclaimer (instead of inline) satisfies MiCA Art. 66 for push notifications.
   - Recommendation: Diego confirms with legal counsel. If linking is acceptable, include a short risk statement inline + disclaimer link. If inline is required, push may not be viable for marketing notifications without severe copy constraints.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python 3 script with file content validation |
| Config file | None -- validation scripts are self-contained |
| Quick run command | `python3 .planning/phases/02-taxonomy-competitive-benchmark/validate_phase2.py` |
| Full suite command | Same as quick run |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TAX-01 | Taxonomy overview with 6 families defined | content-check | Verify trigger-taxonomy.md contains all 6 family headers | Wave 0 |
| TAX-02 | Family A triggers with eligibility criteria | content-check | Verify family-A file contains trigger template fields | Wave 0 |
| TAX-03 | Family B triggers with eligibility criteria | content-check | Verify family-B file contains trigger template fields | Wave 0 |
| TAX-04 | Family C triggers with eligibility criteria | content-check | Verify family-C file contains trigger template fields | Wave 0 |
| TAX-05 | Family D triggers with eligibility criteria | content-check | Verify family-D file contains trigger template fields | Wave 0 |
| TAX-06 | Family E triggers with eligibility criteria | content-check | Verify family-E file contains trigger template fields | Wave 0 |
| TAX-07 | Family F triggers with eligibility criteria | content-check | Verify family-F file contains trigger template fields | Wave 0 |
| TAX-08 | Asset universe mapping | content-check | Verify asset-universe.md contains product-asset matrix | Wave 0 |
| BENCH-01 | Competitor matrix with 6 competitors | content-check | Verify benchmark file contains all 6 competitor names | Wave 0 |
| BENCH-02 | Per-competitor analysis | content-check | Verify benchmark file has per-competitor sections | Wave 0 |
| BENCH-03 | Copy/avoid/innovate recommendations | content-check | Verify benchmark file has recommendations section | Wave 0 |
| COMP-01 | Compliance checklist per trigger | content-check | Verify compliance file has checklist template | Wave 0 |
| COMP-02 | Diego review workflow | content-check | Verify compliance file has Tier 1/2/3 workflow | Wave 0 |
| COMP-03 | Investment advice vs informational | content-check | Verify compliance file has safe/dangerous examples | Wave 0 |
| COMP-04 | Market abuse protocol | content-check | Verify compliance file has public data source requirements | Wave 0 |

### Sampling Rate

- **Per task commit:** Quick run validation
- **Per wave merge:** Full suite
- **Phase gate:** All validations green before `/gsd:verify-work`

### Validation Script

The following Python script validates Phase 2 deliverables. Create at `.planning/phases/02-taxonomy-competitive-benchmark/validate_phase2.py`:

```python
#!/usr/bin/env python3
"""Validation script for Phase 2: Taxonomy + Competitive Benchmark."""
import os
import sys

PHASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = []

def check_file(filename, required_strings, req_id, description):
    filepath = os.path.join(PHASE_DIR, filename)
    if not os.path.exists(filepath):
        RESULTS.append(f"FAIL [{req_id}] {description}: file {filename} not found")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    missing = [s for s in required_strings if s.lower() not in content.lower()]
    if missing:
        RESULTS.append(f"FAIL [{req_id}] {description}: missing: {missing}")
    else:
        RESULTS.append(f"PASS [{req_id}] {description}")

# TAX-01: Taxonomy overview with 6 families
check_file("playbook-section-trigger-taxonomy.md",
    ["Family A", "Family B", "Family C", "Family D", "Family E", "Family F",
     "trigger_id", "eligibility", "consent_category", "priority_tier"],
    "TAX-01", "Trigger taxonomy with 6 families and template fields")

# TAX-02 through TAX-07: Individual family files
families = [
    ("TAX-02", "playbook-section-family-A-user-configured.md", "Family A",
     ["price target", "who_receives", "who_never_receives", "cooldown", "CAT-USR"]),
    ("TAX-03", "playbook-section-family-B-market.md", "Family B",
     ["volatility", "who_receives", "who_never_receives", "cooldown", "CAT-MKT"]),
    ("TAX-04", "playbook-section-family-C-behavioral.md", "Family C",
     ["watched not bought", "who_receives", "who_never_receives", "cooldown"]),
    ("TAX-05", "playbook-section-family-D-lifecycle.md", "Family D",
     ["at_risk", "who_receives", "who_never_receives", "cooldown"]),
    ("TAX-06", "playbook-section-family-E-crosssell.md", "Family E",
     ["earn", "who_receives", "who_never_receives", "cooldown", "CAT-PRO"]),
    ("TAX-07", "playbook-section-family-F-risk.md", "Family F",
     ["LTV", "who_receives", "who_never_receives", "cooldown"]),
]
for req_id, filename, family, required in families:
    check_file(filename, required, req_id,
               f"{family} triggers with eligibility criteria")

# TAX-08: Asset universe mapping
check_file("playbook-section-asset-universe.md",
    ["wallet", "brokerage", "pro", "earn", "card", "loan", "launchpad",
     "space center", "asset scope", "eligibility"],
    "TAX-08", "Asset universe with product-asset mapping")

# BENCH-01, BENCH-02, BENCH-03: Competitor benchmark
check_file("playbook-section-competitor-benchmark.md",
    ["Coinbase", "Binance", "Kraken", "Bitpanda", "Revolut", "Nexo"],
    "BENCH-01", "Competitor matrix with 6 competitors")
check_file("playbook-section-competitor-benchmark.md",
    ["preference center", "channels", "asset scope", "gaps"],
    "BENCH-02", "Per-competitor analysis dimensions")
check_file("playbook-section-competitor-benchmark.md",
    ["copy", "avoid", "innovate"],
    "BENCH-03", "Copy/avoid/innovate recommendations")

# COMP-01: Compliance checklist
check_file("playbook-section-compliance-per-trigger.md",
    ["MiCA", "GDPR", "ePrivacy", "CNMV", "checklist"],
    "COMP-01", "Compliance checklist per trigger")

# COMP-02: Diego review workflow
check_file("playbook-section-compliance-per-trigger.md",
    ["Tier 1", "Tier 2", "Diego", "approval", "four-eyes"],
    "COMP-02", "Diego review workflow")

# COMP-03: Investment advice vs informational
check_file("playbook-section-compliance-per-trigger.md",
    ["informational", "advisory", "bright line", "safe", "dangerous"],
    "COMP-03", "Investment advice vs informational boundary")

# COMP-04: Market abuse protocol
check_file("playbook-section-compliance-per-trigger.md",
    ["market abuse", "public data", "simultaneous", "audit log", "Article 87"],
    "COMP-04", "Market abuse prevention protocol")

# Print results
print("=" * 60)
print("Phase 2 Validation Results")
print("=" * 60)
passed = sum(1 for r in RESULTS if r.startswith("PASS"))
failed = sum(1 for r in RESULTS if r.startswith("FAIL"))
for r in RESULTS:
    print(r)
print(f"\n{passed} passed, {failed} failed out of {len(RESULTS)} checks")
sys.exit(0 if failed == 0 else 1)
```

### Wave 0 Gaps

- [ ] `validate_phase2.py` -- validation script (create at start of execution)
- [ ] All 10 playbook section files listed above (created by plan execution)

---

## Sources

### Primary (HIGH confidence)
- [MiCA Article 66 -- White & Case Analysis](https://www.whitecase.com/insight-alert/mica-regulation-new-regulatory-framework-crypto-assets-issuers-and-crypto-asset) -- Art. 66 fair/clear/not misleading requirements
- [MiCA Full Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32023R1114) -- Articles 66, 81, 86-92
- [ESMA MiCA Market Abuse Guidelines (April 2025)](https://www.esma.europa.eu/sites/default/files/2025-04/ESMA75-453128700-1408_Final_Report_MiCA_Guidelines_on_prevention_and_detection_of_market_abuse.pdf)
- [ESMA MiCA Knowledge & Competence Guidelines (Jan 2026)](https://www.esma.europa.eu/sites/default/files/2026-01/ESMA35-24871704-2922_Guidelines_for_the_criteria_on_the_assessment_of_knowledge_and_competence_under_MiCA.pdf)
- [ESMA MiCA Suitability Guidelines (March 2025)](https://www.esma.europa.eu/sites/default/files/2025-03/ESMA35-1872330276-2031_Guidelines_on_suitability_and_periodic_statement_MiCA.pdf)
- [Coinbase: Price Alerts Help](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/what-are-price-alerts)
- [Coinbase: Real-Time Alerts Blog](https://www.coinbase.com/blog/new-real-time-price-alerts-for-the-coinbase-app)
- [Binance: Set Price Alert](https://www.binance.com/en/support/faq/how-to-set-a-price-alert-on-binance-53349d11525b42f79ff20d3ea1dc312b)
- [Nexo: Loyalty Program](https://support.nexo.com/article/nexo-loyalty-program-explained)

### Secondary (MEDIUM confidence)
- [Lexology: Marketing under MiCA](https://www.lexology.com/library/detail.aspx?g=18c07b71-9b06-451d-9508-562339cb7bd4)
- [InnReg: MiCA Regulation Updated Guide 2026](https://www.innreg.com/blog/mica-regulation-guide)
- [Manimama: Crypto Advertising Under MiCA](https://manimama.eu/crypto-advertising-under-mica-new-eu-compliance-reality/)
- [Sedric.ai: Marketing Compliance Review Workflow](https://www.sedric.ai/blog/how-to-build-a-marketing-compliance-review-workflow-that-doesnt-kill-growth)
- [PITFALLS.md](.planning/research/PITFALLS.md) -- Internal research: 14 pitfalls
- [FEATURES.md](.planning/research/FEATURES.md) -- Internal research: full competitor matrix

### Tertiary (LOW confidence)
- Exact Bit2Me Earn-eligible assets -- not verified, assumed from typical exchange
- Bit2Me Loan collateral rules -- not verified, inferred from Nexo model
- Space Center data availability in BigQuery -- not verified

## Metadata

**Confidence breakdown:**
- Trigger taxonomy architecture: HIGH -- based on Phase 1 constructs and competitor patterns
- Competitor benchmark: HIGH -- based on official help centers and engineering blogs
- Compliance framework: MEDIUM-HIGH -- MiCA Art. 66 verified; bright-line gap confirmed
- Asset universe mapping: MEDIUM -- products confirmed, per-product eligibility not verified
- Open questions: 5 unresolved items needing product team input

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days -- MiCA enforcement stable through July 2026)
