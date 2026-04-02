---
name: latam-venezuela-lens
description: Use to re-score and enrich opportunities through LATAM and Venezuela market reality. Invoke after initial scoring to apply regional adjustments.
tools: [Read, Write, WebSearch]
---

# LATAM & Venezuela Lens

## Purpose
Applies regional market intelligence to raw or partially-scored opportunities. Adjusts willingness-to-pay estimates, identifies structural Venezuela wedge categories, adds payment rail context, and ensures every Venezuela opportunity has passed the 5-question WhyNowVenezuela framework. Produces geo-enriched opportunity records ready for final scoring.

## When to Use
- After signal harvesting, before or after initial TAM estimation
- When an opportunity is flagged as geography=venezuela or geography=latam
- When re-running scoring after new regional data is added
- When auditing opportunity records for missing venezuela_wedge_category

## Workflow

### Step 1: Load Geo Context
Import VENEZUELA_ADJUSTMENTS and LATAM_ADJUSTMENTS from `geo_lens.py`. Note the current WTP multipliers, regional_fit bonuses, and payment rail notes. These values govern all enrichment in this run.

### Step 2: Enrich Each Opportunity
For each opportunity in scope:
- Apply the WTP multiplier for the geography to the `willingness_to_pay` field
- If `venezuela_wedge_category` is already set, validate it is one of the 10 canonical categories (see list below). If invalid, reset to null and reclassify
- If `venezuela_wedge_category` is not set and geography includes Venezuela, classify now (Step 4)
- Add a `geo_context_note` field: 1-2 sentences on payment rails, USD dynamics, or informal market context relevant to the opportunity
- Apply +1.5 regional_fit score bonus for any Venezuela wedge-classified opportunity

### Step 3: LATAM Opportunity Identification
Scan all opportunities regardless of current geography tag. Flag any global opportunity with cross-border LATAM potential by setting `latam_potential: true` and adding a note on which LATAM market is the primary entry point and why.

### Step 4: Venezuela Wedge Classification
For each opportunity where geography=venezuela (or latam_potential=true and VE is relevant), assign exactly one category from the canonical list:

| Category | Key signal |
|----------|-----------|
| payments_and_collections | receiving/sending money for businesses |
| remittances_and_diaspora_finance | cross-border money flows, VE diaspora |
| smb_software_informal_operators | software for cash-based or informal SMBs |
| retail_inventory_working_capital | inventory financing or stock management |
| logistics_coordination | freight, last-mile, or carrier matching |
| commerce_trust_layers | escrow, verification, identity for trade |
| creator_monetization | YouTubers, freelancers, remote workers getting paid |
| cross_border_service_businesses | services sold by VE talent to foreign buyers |
| diaspora_finance_and_commerce | financial products for VE diaspora communities |
| ai_labor_replacement_tools | AI replacing expensive or unavailable labor |

### Step 5: WhyNowVenezuela Framework
For every Venezuela opportunity, answer all 5 questions and append to `venezuela_why_now` field:
1. What structural condition in Venezuela makes this urgent NOW (not 2 years ago)?
2. What payment rail will customers actually use? (Zelle, USD cash, USDT, bolivar?)
3. Who are the first 10 paying customers and where do you find them?
4. What is the biggest regulatory or political risk and what is the mitigation?
5. How does USD dollarization create or close this opportunity?

### Step 6: Update Scores
Re-run scoring with updated fields (adjusted WTP, regional_fit bonus). Write enriched records back to the opportunity JSONL file.

## Output Spec
Updated opportunity records with:
- `geo_context_note` (str): regional context note
- `venezuela_wedge_category` (str|null): one of 10 canonical categories
- `venezuela_why_now` (dict): 5-question answers for VE opportunities
- `latam_potential` (bool): cross-border LATAM flag
- Adjusted `regional_fit` score and `willingness_to_pay`

## Quality Gate
- Every opportunity with geography=venezuela must have a `venezuela_wedge_category` assigned — block if missing
- Every `venezuela_wedge_category` must be from the canonical 10-item list — reject unknown values
- Every Venezuela opportunity must have all 5 `venezuela_why_now` questions answered
- WTP adjustments must be applied before `final_score` is computed
