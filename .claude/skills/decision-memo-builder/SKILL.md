---
name: decision-memo-builder
description: Use to generate a 1-page decision memo for a shortlisted opportunity. Invoke when opportunity is promoted to validation stage.
tools: [Read, Write]
---
# Decision Memo Builder

## Purpose
Force clarity before acting. A 1-page memo that Daniel can read in 3 minutes and decide: pursue, defer, or kill. The memo is not a summary of research — it is a structured argument for or against acting on a specific opportunity right now.

## When to Use
- An opportunity has been promoted to validation stage from the weekly review
- Before committing any hours or money to building or validating
- When Daniel needs to communicate an opportunity to a collaborator or co-founder

Do NOT use this as a brainstorming tool. It requires a populated opportunity record as input.

## Memo Structure
8 sections. Each section has a maximum of 3 sentences or 3 bullets. Brevity is required — if you need more than 3 bullets to make the argument, the thinking is not clear enough yet.

```markdown
# Decision Memo: [Opportunity Name]
**Date:** YYYY-MM-DD | **Bucket:** fast_cash / venture_scale / latam_asymmetry | **Lane:** now / soon / strategic | **Score:** X.X/10

## Thesis
One sentence: [X] for [who] in [where] that [does what] better than [current alternative] because [unique insight].

## Target Customer
Specific: not "SMBs" but "Venezuelan retail shop owners in Caracas with 2-5 employees, using WhatsApp for invoicing."
One sentence only. Name the person, not the category.

## Market Size
[Method]: TAM $XM / SAM $XM / SOM $XM. Confidence: high / medium / low.
If two methods were used: show both and note convergence or divergence.

## Why Now (3 bullets max)
- [External timing reason 1 — market shift, regulatory change, tech unlock, competitor failure]
- [External timing reason 2]
- [External timing reason 3]

## Why Daniel Wins
Which of Daniel's 6 wedges apply?
Wedges: growth_gtm | narrative_positioning | latam_intuition | fintech_crypto_adjacency | speed_to_prototype | distribution_instincts
Score: X/6. One sentence on the strongest wedge.

## First EUR 1,000 Path
Customer: [specific person/company type]. Offer: [specific product/service + price]. Channel: [specific outreach method]. Proof point: [what makes them say yes].

## Key Risks (3 max)
1. [Risk] — [specific mitigation, not "we will monitor"]
2. [Risk] — [specific mitigation]
3. [Risk] — [specific mitigation]

## Kill Conditions
Stop immediately if:
- [Falsifiable condition 1 — e.g. "10 cold outreach attempts yield 0 responses by Friday"]
- [Falsifiable condition 2 — e.g. "Regulatory check reveals banking license required"]

## Next Test (this week)
[Specific action] by [day of week]. Expected signal: [binary outcome — what yes or no looks like].
```

## Workflow

### Step 1: Load Opportunity Record
Read the opportunity from `data/opportunities.jsonl` using the opportunity ID.
Check that the following fields are populated: name, bucket, portfolio_lane, score, pain_cluster_id, tam_estimate, first_revenue_path.

If any field is missing, flag it as `[NEEDS RESEARCH: specific question]` before proceeding.

### Step 2: Populate All 8 Sections
Use the opportunity record fields as source material. Map fields to memo sections:

| Memo Section | Source Fields |
|-------------|--------------|
| Thesis | opportunity name + target_customer + differentiation |
| Target Customer | target_customer field (must be specific) |
| Market Size | tam_estimate + tam_method + tam_confidence |
| Why Now | timing_signals array (3 max) |
| Why Daniel Wins | wedge_scores array |
| First EUR 1,000 Path | first_revenue_path object (5 subfields) |
| Key Risks | risks array (3 max) |
| Kill Conditions | kill_conditions array |
| Next Test | next_test field |

### Step 3: Flag Missing Data
For every section where the opportunity record does not provide enough specificity:
Write `[NEEDS RESEARCH: {specific question that would fill this gap}]`

Example: `[NEEDS RESEARCH: What is the regulatory requirement for USD payment processing in Venezuela for non-bank entities?]`

This is a signal to Daniel that a research run is needed before making the decision. Do NOT invent data to fill gaps.

### Step 4: Evaluate Decision Readiness
After populating all sections, score the memo:
- Count sections with `[NEEDS RESEARCH]` tags
- 0 tags: memo is decision-ready
- 1-2 tags: memo is partially ready — note which runs are needed
- 3+ tags: memo requires more research before decision — do not promote stage

### Step 5: Write Memo File
Write to `reports/deep-dives/YYYY-MM-DD-{opp-id}-memo.md`

### Step 6: Update Opportunity Stage
If memo is decision-ready (0-2 NEEDS RESEARCH tags):
- Set `stage=validation`
- Set `memo_status=complete`
- Set `memo_path=reports/deep-dives/YYYY-MM-DD-{opp-id}-memo.md`

If 3+ NEEDS RESEARCH tags:
- Set `memo_status=incomplete`
- Set `memo_blockers=[list of research gaps]`

## Output Spec
- `reports/deep-dives/YYYY-MM-DD-{opp-id}-memo.md` — the 1-page memo
- Updated opportunity record with `stage`, `memo_status`, `memo_path` fields

## Quality Gate
Fail if any of these conditions are not met:
- No section is empty or contains only "[TBD]" — use `[NEEDS RESEARCH: question]` instead
- Thesis is exactly 1 sentence
- Target Customer names a specific person type, not a category
- Why Now has 3 bullets max (not a list of 6)
- Kill Conditions are falsifiable within 7 days (not "if market conditions change")
- Next Test names a specific action AND a specific signal (binary outcome)
- Memo does not exceed 1 printed page (approximately 600 words)
