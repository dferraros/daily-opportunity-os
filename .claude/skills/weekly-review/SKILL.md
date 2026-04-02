---
name: weekly-review
description: Use to run the weekly decision ritual. Invoke every Monday or Friday. Produces 4 mandatory outputs.
tools: [Read, Write, Bash]
---
# Weekly Review

## Purpose
Run the weekly decision ritual that keeps the opportunity pipeline moving. Forces three hard decisions (promote, kill, double down) and one strategic direction call. Prevents pipeline bloat and ensures the system is making progress, not just collecting signals.

## When to Use
- Every Monday (plan the week) or every Friday (review the week)
- When the opportunity count exceeds 20 unreviewed items
- When Daniel needs a weekly conviction reset

Do NOT use for individual opportunity analysis — use deep-dive-builder for that.

## 4 Mandatory Outputs
None of these can be skipped. If data is missing, note the gap and produce the best available version.

### Output 1: Top 3 to Validate
Opportunities to promote from scout stage to validation this week.

For each, provide:
- Opportunity name + ID
- Current score + score change since last week (delta)
- Why now: specific external trigger or data point that makes this the right week
- Specific test to run: one falsifiable experiment that produces a signal within 7 days
- Estimated time to signal: hours to first data point
- Owner: Daniel or a specific named collaborator

Format:
```
## TOP 3 TO VALIDATE

### 1. [Opportunity Name] (ID: opp-XXX | Score: X.X | +X.X this week)
**Why now:** [specific reason]
**Test:** [specific falsifiable experiment]
**Signal in:** [X hours / X days]
**Owner:** Daniel
```

### Output 2: Top 3 to Kill
Opportunities to archive permanently. These will not return unless a major external trigger changes.

For each, provide:
- Opportunity name + ID
- Current score
- Specific kill reason referencing failed criteria (not just "low score")
- Kill condition that was triggered (from the opportunity record)

Acceptable kill reasons (must cite one):
- Score below threshold for 2+ consecutive weeks
- Distribution hypothesis failed: 0 responses after X attempts
- Regulatory blocker confirmed
- Market size too small for target bucket
- Competitor already dominates with no exploitable weakness
- Daniel has no wedge advantage in this vertical

```
## TOP 3 TO KILL

### 1. [Opportunity Name] (ID: opp-XXX | Score: X.X)
**Kill reason:** [specific criterion failed]
**Kill condition triggered:** [from opportunity record]
**Action:** Archive to data/archived/
```

### Output 3: Top 3 Rising Signals
Opportunities whose score increased the most since last week. These are gaining momentum and may warrant promotion next week.

For each, provide:
- Score delta: +X.X points
- What drove the increase (new signal found, competitor weakness identified, market shift)
- Current stage
- Recommended next action

```
## TOP 3 RISING SIGNALS

### 1. [Opportunity Name] (ID: opp-XXX | Score: X.X to Y.Y | +Z.Z)
**What changed:** [specific signal or event]
**Current stage:** scout / validation / deep-dive
**Next action:** [specific]
```

### Output 4: 1 Conviction Area
The ONE sector, geography, or archetype to focus on for the next 30 days. This is a decision — not a list of options.

Must specify:
- The conviction area (1 phrase, not a paragraph)
- Why this area now (evidence from this week's signals)
- What "doubling down" means in practice (3 specific actions for next 30 days)
- What would change this conviction (falsifiable exit condition)

```
## CONVICTION AREA (next 30 days)

**Focus:** [single sector / geo / archetype — e.g. "USD payment infrastructure for Venezuelan SMBs"]
**Evidence:** [2-3 specific signals from this week]
**Actions:**
1. [Specific action]
2. [Specific action]
3. [Specific action]
**Exit condition:** [What would make me abandon this focus]
```

## Workflow

### Step 1: Load Pipeline State
Read `data/opportunities.jsonl` — filter to active (not archived) opportunities.
Read `data/opportunity_history.jsonl` — load last 2 weeks of score snapshots for delta calculation.
Count items by stage: scout / validation / deep-dive / archived.

### Step 2: Calculate Score Deltas
For each opportunity: current_score - score_7_days_ago = delta.
Sort by delta (descending) for Rising Signals section.
Sort by current_score (ascending) for Kill candidates.
Sort by current_score (descending) + recency of signals for Validate candidates.

### Step 3: Check Quota Compliance
Load `config/settings.json` — read weekly_quotas block.
Compare actual counts against targets:
- Signals ingested this week (target: 30-50)
- Structured opportunities created (target: 10)
- Deep dives completed (target: 3)

If any quota missed: add a QUOTA WARNING block to the output with the gap and a recovery suggestion.

```
## QUOTA WARNING
- Signals this week: X / 30-50 target [UNDER — recommend running signal-harvester twice more this week]
- Structured opps: X / 10 target [OK]
- Deep dives: X / 3 target [UNDER — recommend promoting 2 more to deep-dive]
```

### Step 4: Generate 4 Outputs
Produce all 4 outputs using the formats above. Every section must be populated. No "[TBD]" or empty sections.

### Step 5: Update Conviction Area in STATE.md
Write the new conviction area to `STATE.md` field: `weekly_conviction_area`.

Format: `weekly_conviction_area: "[area]" — set YYYY-MM-DD, expires YYYY-MM-DD+30`

### Step 6: Execute Archive Actions
For each opportunity in Top 3 to Kill:
- Update opportunity record: set `stage=archived`, `kill_reason=[reason]`, `archived_date=YYYY-MM-DD`
- Move record to `data/archived/YYYY-MM-DD-{opp-id}.jsonl`

### Step 7: Write Weekly Summary
Write full output to `reports/weekly/YYYY-WW-summary.md` where WW is the ISO week number.

## Output Spec
- `reports/weekly/YYYY-WW-summary.md` — full weekly review with all 4 sections
- `STATE.md` — updated `weekly_conviction_area` field
- `data/archived/` — archived opportunity records
- `data/opportunity_history.jsonl` — append this week's snapshot (all active opps with scores and date)

## Quality Gate
Fail if any of these are missing:
- All 4 outputs present and labeled
- Output 4 (Conviction Area) is ONE thing, not a list of options
- Kill reasons cite specific failed criteria — not just "score too low"
- Rising Signals show numeric delta (not just "higher score")
- Quota compliance check completed and logged
- Weekly summary written to correct path with ISO week number
