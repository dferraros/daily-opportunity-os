---
name: deep-dive-builder
description: Use to produce a comprehensive opportunity deep dive. Invoke when an opportunity is shortlisted for validation (portfolio_lane=now or soon).
tools: [WebSearch, WebFetch, Read, Write]
---
# Deep Dive Builder

## Purpose
Produce a fully-sourced, decision-ready deep dive on a shortlisted opportunity. This is the final intelligence gate before committing time or money to validation. Every claim must be backed by research. Every section must be specific enough to act on.

## When to Use
- An opportunity has been scored and promoted to `portfolio_lane=now` or `portfolio_lane=soon`
- The weekly review has surfaced it in the Top 3 to validate
- Daniel wants to make a build/defer/kill decision with full data

Do NOT invoke for scouting-stage opportunities. Deep dives are earned after scoring.

## Workflow

### Step 1: Customer Pain Validation
Search Reddit, G2, Trustpilot, App Store, and Play Store for evidence the problem is real and recurring.

Queries to run:
- `site:reddit.com [vertical] [problem keyword] frustrated OR struggling OR hate`
- `site:g2.com [competitor name] reviews`
- `site:trustpilot.com [competitor name]`
- App Store: search competitor app name + filter by 1-2 star reviews

Extract minimum 5 verbatim customer complaints. Each quote must include: source URL, platform, approximate date.

Tag each quote by pain_type: workflow | trust | cost | compliance | distribution | other

### Step 2: Market Size Deep Research
Run 2 independent TAM estimation methods. Both must produce a number. If they diverge by more than 3x, note the discrepancy and explain why.

Method A — Top-down: Find industry report, total addressable universe, apply penetration rate.
Method B — Bottom-up: Count target customers x average annual spend x serviceable fraction.

Validate at least one method with a snippet from a credible source (Statista, IBISWorld, Euromonitor, CB Insights, or government data). Do not use other startup pitch decks as sources.

Output: TAM / SAM / SOM with method label and confidence rating (high / medium / low).

### Step 3: Competitor Forensics
Map 3-5 direct and adjacent competitors. For each:
- Pricing (exact tiers if public)
- Positioning (their own words from homepage)
- Review summary (what do customers complain about most — exact pattern from Step 1)
- Estimated size (revenue range, headcount, funding if known)
- The specific weakness Daniel could exploit

Format as a comparison table.

### Step 4: Distribution Hypothesis
Answer: how does Daniel reach the first 10 paying customers — specifically?

Must name:
- Exact channel (not "social media" — e.g. "LinkedIn DMs to logistics ops managers in Venezuela")
- Exact message hook (1 sentence)
- Estimated response rate
- Estimated CAC (in EUR)
- Time to first sale (days)

If Daniel has an existing network edge for this vertical, name it explicitly.

### Step 5: Venezuela/LATAM Angle
Apply the LATAM lens:
- Does this problem exist in Venezuela, Colombia, Mexico, or broader LATAM?
- What modifications are needed for Spanish-speaking markets (regulation, pricing, UX, trust signals)?
- Is the LATAM version easier or harder to build than the global version?
- Are there LATAM-specific structural advantages (lower competition, USD hunger, informal economy fit)?

If LATAM angle is weak, write "LATAM FIT: LOW" and explain why.

### Step 6: First Revenue Path
Complete all 5 fields with specifics. No placeholders.

- **Exact customer type**: Not "SMBs" — e.g. "Venezuelan car dealerships in Caracas with 5-20 staff doing >50 units/month"
- **Exact first offer**: Not "a product" — e.g. "199 EUR/month SaaS for inventory tracking, first 3 months free"
- **Exact price**: Include rationale (comparable product pricing, WTP signal from interviews, or cost-based)
- **Exact proof point needed**: What would make the first customer say yes? (e.g. "a working demo that imports their WhatsApp orders")
- **Exact sales motion**: Cold outreach / warm intro / inbound / event / marketplace listing

### Step 7: Why Now
3 timing reasons this opportunity is timely — not "it is a good idea." Reasons must be external (market shift, regulatory change, technology unlock, competitor failure, macro event).

Bad example: "The market is growing."
Good example: "Venezuela lifted USD transaction restrictions in Jan 2025, creating the first legal path for digital B2B payments."

### Step 8: Decision Memo
Write the final 1-page structured memo using the Decision Memo format. This is the output Daniel reads to make the call.

```
# Decision Memo: [Opportunity Name]
**Date:** YYYY-MM-DD | **Bucket:** fast_cash / venture_scale / latam_asymmetry | **Lane:** now / soon / strategic | **Score:** X.X/10

## Thesis (1 sentence)
[X] for [who] in [where] that [does what] better than [current alternative] because [unique insight].

## Target Customer (specific)
Not a category. A person. Name their job, company size, country, and current workaround.

## Market Size (TAM/SAM/SOM + method)
TAM: $XM ([method])
SAM: $XM ([constraint applied])
SOM: $XM ([realistic 3-year capture])
Confidence: high / medium / low

## Why Now (3 bullets max)
- [External timing reason 1]
- [External timing reason 2]
- [External timing reason 3]

## Why Daniel Wins
Wedges that apply: [list from: growth_gtm / narrative_positioning / latam_intuition / fintech_crypto_adjacency / speed_to_prototype / distribution_instincts]
Score: X/6
One sentence on the strongest wedge.

## First EUR 1,000 Path
Customer: [specific]. Offer: [specific]. Channel: [specific]. Price: [specific]. Proof point: [specific].

## Key Risks (3 max)
1. [Risk] — [mitigation]
2. [Risk] — [mitigation]
3. [Risk] — [mitigation]

## Kill Conditions
These would make me stop immediately:
- [Falsifiable condition 1]
- [Falsifiable condition 2]

## Next Test (this week)
[Specific action] by [day of week]. Expected signal: [what you will learn].
```

## Output Spec
- Primary output: `reports/deep-dives/YYYY-MM-DD-{opportunity-id}.md`
- Update opportunity record: set `deep_dive_status=complete`, `stage=validation`
- If LATAM angle is strong: add `latam_fit=true` flag to opportunity record

## Quality Gate
All 8 steps must be completed before writing the memo.

Hard requirements — fail if any are missing:
- Minimum 5 verbatim customer quotes with source URLs
- Market size produced by 2 independent methods
- Distribution hypothesis names a specific channel with CAC estimate
- "Next Test" is something that can be started this week (not "do more research")
- No section in the memo is blank or contains "[TBD]"

If data is insufficient for any section, write `[NEEDS RESEARCH: specific question]` — this still counts as a failure signal. Flag it and note what additional research run is needed.
