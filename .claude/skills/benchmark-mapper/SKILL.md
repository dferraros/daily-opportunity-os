---
name: benchmark-mapper
description: Use to map an opportunity to benchmark archetypes and identify competitive whitespace. Invoke during deep analysis phase.
tools: [WebSearch, WebFetch, Read, Write]
---

# Benchmark Mapper

## Purpose
Maps each opportunity to one of 8 canonical business archetypes, finds real-world analog companies, researches the competitive landscape with pricing data, and identifies the whitespace that the opportunity can credibly own. Produces a structured benchmark section for the opportunity card that grounds abstract ideas in proven market patterns.

## When to Use
- Opportunity has passed kill gates and TAM estimation but lacks archetype classification
- Deep-dive analysis is requested and competitive context is needed
- Opportunity notes say "no competition found" and this needs verification
- Preparing an opportunity card for investor or partner presentation

## Workflow

### Step 1: Classify Archetype
Use `benchmark_engine.py classify_archetype()` or apply the following classification logic manually. Assign exactly one archetype from the canonical 8:

| Archetype | Core pattern |
|-----------|-------------|
| `local_clone` | Proven global model replicated in an underserved geography |
| `regional_wedge` | Entering a large market through a defensible regional niche |
| `workflow_unbundling` | Carving out one job-to-be-done from an incumbent's bloated product |
| `trust_compliance_layer` | Adding verification, legal, or compliance infrastructure a market lacks |
| `ai_operator_replacement` | Automating a role previously done by expensive or scarce human operators |
| `fragmented_supply_marketplace` | Aggregating a supply side that is fragmented and hard to discover |
| `smb_operating_system` | All-in-one software for a specific SMB type (e.g., restaurant OS, trucking OS) |
| `diaspora_bridge` | Products serving cross-border flows between a diaspora community and home country |

### Step 2: Find Analogs
Use `benchmark_engine.py get_analog_benchmarks()` for the vertical + geography combo. Additionally search:
```
[archetype pattern] [vertical] company founded 2015 2020 acquired OR IPO
[vertical] [geography] "series b" OR "series c" 2022 2023 2024
```
Find 2-4 analog companies. For each, record: company name, geography, year founded, exit or current status, and what made them win or fail.

### Step 3: Research Competitors
Search for direct competitors in the opportunity's specific geography and vertical:
```
[opportunity name or description] competitors 2024
"[vertical] [geography] market leaders" site:crunchbase.com OR site:tracxn.com
[problem description] "best solution" OR "market leader" [geography]
```
Name at least 2 real competitors. If none are found after 3 distinct search queries, document the search queries used and flag whitespace as "uncontested entry."

### Step 4: Pricing Research
Find 3 competitor pricing data points via their websites, AppSumo listings, G2 profiles, or funding announcement context. Record:
- Company name
- Pricing model (per seat, per transaction, flat monthly, etc.)
- Price point or range

### Step 5: Whitespace Analysis
Use `benchmark_engine.py detect_whitespace()` or answer these questions:
- Who is currently not being served by existing solutions?
- What geography, segment, or use case is underserved?
- What pricing point has no current player (e.g., SMB tier below enterprise tools)?
- What is the wedge that creates a durable right to win?

Document in `whitespace_summary`: 2-4 sentences describing the open space.

### Step 6: Analog Lessons
For the 2 best analog companies found in Step 2, write 1-2 lessons each:
- What did this company do right that the new opportunity should replicate?
- What mistake did this company make that the new opportunity should avoid?

### Step 7: Write Benchmark Section
Update the opportunity record with:
- `benchmark_archetype` (str): one of 8 canonical archetypes
- `analog_companies` (list): 2-4 analog companies with notes
- `competitor_landscape` (str): summary of direct competitors and pricing
- `whitespace_summary` (str): 2-4 sentence whitespace description
- `analog_lessons` (str): key lessons from analog companies

## Output Spec
Opportunity record updated with `benchmark_archetype`, `analog_companies`, `competitor_landscape`, `whitespace_summary`, and `analog_lessons`. Terminal output: one-line summary per opportunity processed.

## Quality Gate
- `benchmark_archetype` must be one of the 8 canonical values — no custom archetypes
- At least 2 real competitors named with pricing data (not "pricing not available")
- "No competitors found" is not acceptable without documenting 3+ search queries attempted
- `whitespace_summary` must be specific (name the segment, geography, or use case) — no generic "there is whitespace in this market"
- At least 2 analog companies with lessons documented
