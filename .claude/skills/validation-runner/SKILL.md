---
name: validation-runner
description: Use to run Stage 2 validation workflow for shortlisted opportunities. Invoke when promoting an opportunity from scout to validation.
tools: [WebSearch, WebFetch, Read, Write]
---
# Validation Runner

## Purpose
Stage 2 is the bridge between intelligence and action. It takes the top 3-5 opportunities from the weekly review and generates specific, falsifiable validation experiments. The output is not more research — it is a set of concrete tests that produce a yes/no signal within 7 days.

## When to Use
- Weekly review has named an opportunity in "Top 3 to Validate"
- Decision memo has been written and is decision-ready (0-2 NEEDS RESEARCH tags)
- Daniel wants to move from "thinking about it" to "testing it"

Do NOT run validation on scouting-stage opportunities. They must be scored and reviewed first.

## 6-Step Validation Workflow
All 6 steps are required. No step can be skipped or replaced with "will do later."

### Step 1: Customer Pain Check
Validate that real people are actively searching for a solution to this problem.

Run 5 specific search queries and document what you find:
1. Direct problem query: "[pain description] solution" — are there results? How many?
2. Forum search: `site:reddit.com [problem]` — are people asking about this?
3. Product hunt search: "site:producthunt.com [vertical] [pain keyword]" — have others tried to build this?
4. Job board signal: search LinkedIn Jobs for roles related to solving this problem manually — this confirms the pain is real and companies pay people to handle it
5. Google Trends or keyword volume signal (qualitative): is search interest growing, flat, or declining?

Document findings for each query. A strong pain signal = multiple Reddit threads + LinkedIn job postings + at least 1 existing (but flawed) solution.

### Step 2: Landing Page Test Hypothesis
Write a specific, falsifiable landing page hypothesis. This is NOT a real landing page — it is a structured prediction that can be tested with a 1-day build.

Required fields:
- **Headline**: exact copy, max 10 words
- **Subheadline**: exact copy, max 20 words
- **Primary CTA**: button text + what it does (e.g. "Join waitlist — collects email")
- **Expected conversion rate**: X% of visitors click CTA (set a specific number to beat or fail)
- **Traffic source**: exactly how you will get 100 visitors to the page within 7 days
- **Pass condition**: if conversion rate exceeds X%, hypothesis is confirmed

Example:
```
Headline: "Get paid in USD. No bank. No 8% fee."
Subheadline: "Venezuelan freelancers get paid directly to their digital wallet in 24 hours."
CTA: "Get early access" — collects email + WhatsApp
Expected conversion: 15%
Traffic: 50 LinkedIn posts in Venezuelan freelancer groups + 3 Reddit posts
Pass condition: >12% conversion (within 20% of target)
```

### Step 3: Pricing Test Hypothesis
Identify 3 price points to test. For each price point:
- Expected acceptance rate (what % of people asked will say "yes, I'd pay that")
- Expected primary objection (what will people say when they decline)
- Test method: how will you ask 5 people this week (WhatsApp cold, LinkedIn DM, personal network)
- What a "yes" looks like: verbal confirmation? Pre-payment? Waitlist signup with intent to pay?

Format:
```
Price A: [EUR/month] — Expected acceptance: X% — Primary objection: [expected pushback]
Price B: [EUR/month] — Expected acceptance: X% — Primary objection: [expected pushback]
Price C: [EUR/month] — Expected acceptance: X% — Primary objection: [expected pushback]
Test method: [specific — e.g. "5 WhatsApp cold messages to Venezuelan shop owners identified via Instagram"]
```

### Step 4: Demand Interview Script
Write exactly 5 questions for customer discovery interviews. Target: complete 5 interviews within 7 days.

Rules for questions:
- Open-ended (no yes/no questions)
- Non-leading (do not hint at the solution you are building)
- Focused on the past (what people have actually done, not what they might do)
- Time-boxed answers (each question should take 1-2 minutes to answer)

The 5 questions must cover:
1. The current workflow (how do they handle this problem today?)
2. The last time the pain was acute (tell me about a specific incident)
3. What they tried and why it failed (current workarounds and their limits)
4. The cost of the problem (time, money, stress — make them quantify it)
5. The ideal outcome (if this were solved perfectly, what would that look like?)

Interview logistics:
- Who to interview: [specific person type and how to reach them]
- How to find them: [specific source — LinkedIn search, community, network]
- Scheduling method: [WhatsApp cold, email, warm intro]
- Target: 5 completed interviews by [day of week]

### Step 5: Competitor Weakness Analysis
Using the benchmark-mapper output for this opportunity (or a fresh search if not available):

Answer these 3 questions for the top 2 competitors:
1. What is the #1 complaint in their public reviews? (quote from Step 1 of deep-dive or a fresh search)
2. What does their pricing model penalize? (e.g. volume-based pricing that hurts heavy users)
3. What customer segment do they ignore? (who is underserved by their product/marketing)

The intersection of "what customers hate" + "who is underserved" = Daniel's entry wedge.

Write a 1-sentence wedge statement:
"We win with [specific customer type] who are frustrated by [specific competitor weakness]."

### Step 6: First Distribution Hypothesis
How do you reach the first 10 paying customers — specifically?

Must name:
- **Channel**: 1 specific channel (not "multiple channels")
- **Message**: exact opening line or hook (the first sentence of the outreach)
- **List source**: where do you get the names/handles/emails? (be specific — e.g. "Instagram hashtag #comerciovenezuela", "LinkedIn search: 'operations manager' + 'Venezuela' + 'retail'")
- **Expected response rate**: X% reply to the outreach
- **Expected CAC**: EUR per acquired customer
- **Time to first paid customer**: X days from starting outreach
- **Fallback if this channel fails**: what is the Plan B channel?

## Output Spec
- `reports/validation/YYYY-MM-DD-{opp-id}-validation.md` with all 6 sections
- Update opportunity record: set `stage=validation`, `validation_status=in_progress`, `validation_start_date=YYYY-MM-DD`
- Set `validation_deadline` = today + 7 days

## Quality Gate
Hard requirements — fail if any are missing:
- All 6 steps present and populated
- Landing page hypothesis has a specific headline (not "[insert headline]")
- Pricing test has exactly 3 price points with specific EUR amounts
- Interview script has exactly 5 questions (no more, no less)
- Interview script questions are open-ended and non-leading (review each one)
- Distribution hypothesis names ONE specific channel with a CAC estimate in EUR
- Kill conditions are set: what signal within 7 days would kill this opportunity immediately?
