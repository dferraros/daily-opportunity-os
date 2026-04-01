---
name: pain-library-mapper
description: Use to map new opportunities to the pain library and identify recurring pain clusters. Invoke after signal harvesting.
tools: [Read, Write]
---
# Pain Library Mapper

## Purpose
Build a persistent understanding of pain patterns across verticals and geographies. New opportunities should connect back to known pain clusters — this reveals whether the system is finding genuinely new signals or recycling the same problems. A saturated pain cluster is a stronger build signal than a novel one.

## When to Use
- After running signal-harvester (new opportunities need pain_cluster_id before scoring)
- After running customer-language-miner (new verbatim quotes may reveal new pain clusters)
- Weekly, to consolidate the pain library and prevent cluster drift
- When the pain library exceeds 50 distinct clusters (force consolidation)

Every opportunity MUST have a pain_cluster_id before it enters the scoring pipeline.

## Pre-defined Pain Categories
Use these 12 categories. Do not create new categories — consolidate into the closest match:

| Category | What it covers |
|----------|---------------|
| `payments_friction` | Sending, receiving, or converting money is slow, expensive, or blocked |
| `inventory_chaos` | Stock tracking, ordering, or reconciliation is manual or error-prone |
| `customer_acquisition_pain` | Finding, reaching, or converting customers is too expensive or ineffective |
| `trust_problems` | Customers don't trust the provider, product, or payment method |
| `cash_flow_visibility` | Businesses cannot see their real cash position in real time |
| `bad_tooling` | Existing software is too complex, too expensive, or built for the wrong market |
| `manual_workflows` | Processes that should be automated are done by hand (spreadsheets, WhatsApp) |
| `cross_border_friction` | Moving money, goods, or data across borders is slow, expensive, or legally unclear |
| `compliance_confusion` | Regulatory requirements are unclear, expensive, or change frequently |
| `distribution_failure` | Products exist but cannot reach their intended customers at scale |
| `talent_access` | Finding, hiring, or retaining skilled workers is difficult or expensive |
| `informal_economy_friction` | Businesses operating informally face barriers to formalizing or scaling |

## Pain Library Entry Format
```json
{
  "pain_id": "PAY-001",
  "category": "payments_friction",
  "description": "SMBs cannot collect USD digitally without losing 3-8% to intermediaries",
  "geographies": ["venezuela", "latam"],
  "affected_segments": ["smb_retail", "freelancers"],
  "severity": 9,
  "frequency": 3,
  "current_workarounds": ["Zelle manual", "WhatsApp invoice + cash"],
  "opportunities_mapped": ["opp-001", "opp-007"],
  "evidence_links": ["https://reddit.com/r/vzla/...", "https://g2.com/..."],
  "first_seen": "2026-04-01",
  "last_updated": "2026-04-01"
}
```

ID format: 3-letter category prefix + 3-digit number. Examples: PAY-001, INV-003, TRU-012.

## Workflow

### Step 1: Load Pain Library
Read `data/pain_library.jsonl` — load all existing pain entries.
If the file does not exist, create it empty and proceed.
Index entries by: pain_id, category, description keywords.

### Step 2: Load New Opportunities
Read `data/opportunities.jsonl` — filter to opportunities where `pain_cluster_id` is null or missing.
These are the opportunities that need mapping.

### Step 3: Map Each Opportunity to a Pain Cluster
For each unmapped opportunity:

A. Read the opportunity's `problem_description`, `vertical`, and `geography` fields.

B. Search the existing pain library for the closest match:
   - Exact category match AND geography overlap AND similar description
   - If found: use the existing pain_cluster_id — do NOT create a duplicate

C. If no match found: create a new pain library entry:
   - Assign next available ID in the category sequence (e.g. PAY-004 if PAY-001 to PAY-003 exist)
   - Populate all required fields
   - Set frequency=1, opportunities_mapped=[this opp's ID]

D. If a close-but-not-exact match exists: decide whether to consolidate or create a sub-cluster.
   Rule: if the pain can be described as a specific instance of an existing cluster, consolidate (increment frequency, add to opportunities_mapped). Only create a new entry if the underlying mechanism is genuinely different.

### Step 4: Update Opportunity Records
For each newly mapped opportunity:
- Set `pain_cluster_id` = the matched or created pain_id
- Set `pain_category` = the category string
- Set `pain_severity` = the severity score from the pain entry (1-10)

Write updated records back to `data/opportunities.jsonl`.

### Step 5: Update Pain Library
For each existing pain entry that received a new opportunity mapping:
- Increment `frequency`
- Add opportunity ID to `opportunities_mapped` list
- Update `last_updated` to today's date

For each newly created pain entry:
- Append to `data/pain_library.jsonl`

### Step 6: Consolidation Check
After updates, count distinct pain clusters.
If count exceeds 50:
- Identify clusters with frequency=1 that are older than 30 days
- Propose consolidation: merge into the closest existing cluster
- Write consolidation proposals to console as a WARNING — do not auto-merge without confirmation
- Note: "CONSOLIDATION NEEDED: [cluster A] and [cluster B] appear to describe the same pain. Recommend merging into [cluster A]."

### Step 7: Write Pain Insights Summary
After mapping, produce a brief insights block:
- Top 5 pain clusters by frequency
- Top 3 clusters by severity
- Clusters with the most opportunities mapped (highest signal density)
- Any new clusters created this run

## Output Spec
- `data/pain_library.jsonl` — updated with new entries and frequency increments
- `data/opportunities.jsonl` — updated with pain_cluster_id, pain_category, pain_severity
- Console: pain insights summary + any consolidation warnings

## Quality Gate
Fail if any of these conditions are not met:
- Every opportunity processed in this run has a pain_cluster_id after completion
- No duplicate pain IDs in the library (each ID appears exactly once)
- Pain library does not exceed 50 distinct clusters without a consolidation proposal
- All new pain entries have all required fields populated (no nulls in required fields)
- Frequency counts are accurate (each opportunity mapped is counted exactly once per cluster)
