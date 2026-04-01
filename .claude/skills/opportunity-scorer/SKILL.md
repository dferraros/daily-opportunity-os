---
name: opportunity-scorer
description: Use to apply weighted scoring to a batch of opportunities and produce a ranked list. Invoke after signals are normalized and TAM is estimated.
tools: [Read, Write, Bash]
---

# Opportunity Scorer

## Purpose
Applies a three-layer weighted scoring model to all unscored opportunities, runs kill gate checks, assigns portfolio lanes, and produces a ranked leaderboard. Ensures score calibration is sane (distribution check) and writes all scores back to the opportunity JSONL before reporting.

## When to Use
- After signal harvesting and TAM estimation, to produce the daily ranked list
- When new opportunities are added to the pipeline and need initial scores
- When geo enrichment (latam-venezuela-lens) has been applied and scores need recomputing
- When auditing scoring calibration across the existing opportunity pool

## Workflow

### Step 1: Load Unscored Opportunities
Read from `data/opportunities/opportunities.jsonl`. Filter to records where `final_score` is null or where `rescore_requested: true`.

### Step 2: Run Kill Gate
For each opportunity, evaluate all 7 kill criteria. Mark `kill_decision: true` if 2 or more criteria fail.

| Code | Kill Criterion |
|------|---------------|
| KG-01 | No clear monetization path (willingness_to_pay = 0 or unknown) |
| KG-02 | Regulatory or legal blocker with no mitigation path |
| KG-03 | Requires >$500K capital before first revenue |
| KG-04 | Incumbent has >80% market share with no wedge available |
| KG-05 | MVP cannot be built in under 90 days with 2-person team |
| KG-06 | TAM < $10M (applied by tam-estimator, validate here) |
| KG-07 | No distribution channel exists or can be built without paid ads only |

Record which criteria failed in `kill_criteria_failed` (list). If kill_decision=true, skip to the next opportunity.

### Step 3: Skip Killed Opportunities
Do not score opportunities with `kill_decision: true`. Mark their `final_score: null` and `portfolio_lane: "killed"`.

### Step 4: Score Surviving Opportunities
Run `scoring_engine.py score_opportunity()` for each surviving opportunity, or apply the three-layer model manually:

**Layer 1 — Attractiveness (50% weight):**
| Dimension | Weight | Score 1-10 |
|-----------|--------|-----------|
| market_size | 12% | Based on TAM: >$1B=10, >$100M=7, >$10M=4 |
| timing_tailwind | 10% | Is there a structural tailwind NOW? |
| pain_severity | 10% | How acute is the customer pain (hair-on-fire vs. nice-to-have)? |
| willingness_to_pay | 10% | Can customers pay and will they? |
| monetization_clarity | 8% | Is the revenue model clear and proven by analogs? |

**Layer 2 — Executability (30% weight):**
| Dimension | Weight | Score 1-10 |
|-----------|--------|-----------|
| speed_to_mvp | 8% | Can an MVP be shipped in <90 days? |
| capital_efficiency | 7% | Can first revenue be reached with <$50K? |
| distribution | 8% | Is there a non-paid distribution channel available? |
| operational_simplicity | 7% | Can this be operated by 1-2 people initially? |

**Layer 3 — Strategic Value (20% weight):**
| Dimension | Weight | Score 1-10 |
|-----------|--------|-----------|
| competition | 5% | Inverted: low competition = high score |
| defensibility | 5% | Can a moat be built within 12 months? |
| regional_fit | 5% | Fit to LATAM/Venezuela context (boosted by latam-venezuela-lens) |
| founder_fit | 5% | Does this match the builder's skills and network? |

**Final score:** weighted sum across all 13 dimensions, normalized to 0-10.

### Step 5: Apply Geo Lens
If geography is VE or LATAM and `latam-venezuela-lens` has been run, the `regional_fit` dimension should already reflect the +1.5 bonus. Verify this is reflected before writing `final_score`.

### Step 6: Assign Portfolio Lanes
For each scored opportunity, use `filters.py PortfolioLaneAssigner` or apply:
- `final_score >= 7.0` AND `speed_to_mvp >= 7` → lane: `"now"`
- `final_score >= 6.0` AND `defensibility >= 7` → lane: `"strategic"`
- `final_score >= 5.0` → lane: `"watch"`
- `final_score < 5.0` → lane: `"no"`
- `kill_decision: true` → lane: `"killed"`

### Step 7: Rank
Sort all scored opportunities by `final_score` descending. Assign `rank` (integer, 1 = highest) to each.

### Step 8: Write Scores
Update each opportunity record in `data/opportunities/opportunities.jsonl` with:
- `attractiveness_score` (float)
- `executability_score` (float)
- `strategic_value_score` (float)
- `final_score` (float)
- `portfolio_lane` (str)
- `rank` (int)
- `kill_decision` (bool)
- `kill_criteria_failed` (list)
- `scored_at` (YYYY-MM-DD)

### Step 9: Report
Print ranked top-10 table to terminal with columns: rank, name, final_score, portfolio_lane, geography, tam_usd_estimate.

## Output Spec
All opportunities in `data/opportunities/opportunities.jsonl` updated with full scoring fields. Terminal output: ranked top-10 table.

## Quality Gate
- Score distribution sanity check: if ALL surviving opportunities score > 7.0, flag as calibration issue and re-review scoring inputs
- Expected distribution: ~20% "now/strategic", ~30% "watch", ~50% "no/killed"
- No opportunity should have `final_score` set without `scored_at` timestamp
- Kill gate must be evaluated before scoring, not after
- `rank` field must be unique integers — no ties allowed (use secondary sort by `tam_usd_estimate` to break ties)
