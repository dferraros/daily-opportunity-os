# Scoring Model Goal + Calibration Loop — Daily Opportunity OS

> **Loop contract (rubric-first):** this file defines the goal; `uv run pytest` is the
> verifier (every CAL-xx criterion maps to tests in `test_calibration_engine.py` /
> `test_evidence_coverage.py`); the idempotency gate (`opp-os rescore-all --dry-run` -> 0
> changed) is the regression guard. Done = all criteria green, not judgment.

## The goal

**The score must predict reality.** Concretely: top-bucket opportunities (by final_score)
should validate/succeed at a measurably higher rate than bottom-bucket ones, every weight
in `config/scoring_weights.yaml` should eventually be earned from recorded outcomes rather
than asserted, and no high score should hide the fact that it is built on AI guesses
instead of evidence.

North-star metric: **outcome discrimination** — success rate of top score-bucket vs bottom
score-bucket among resolved outcomes. Guardrail: never auto-apply weight changes; proposals
are damped, audited, and applied by Daniel manually.

## Why this is the right goal (gap audit of the current model)

What exists and is good:
- 23 weighted dimensions in 3 layers (50/30/20 composite), weights variance-audited
  2026-05-20 against 95 live opps — weights are tuned for SPREAD (discrimination among
  opportunities), which was the right first move with zero outcome data.
- Data-backed signals live: job postings -> market_momentum, G2 negatives ->
  competitor_weakness, pain signals -> pain_validation fallback, distribution_validated.
- Kill gate + caps + idempotent portfolio normalization (raw_final_score discipline).
- `outcome_tracking.py` records outcomes with score + criteria snapshots, and
  `opp-os outcome` (conviction bridge) feeds it.

What is missing — the open loop:
1. Outcomes are recorded but **nothing quantitative closes the loop**:
   `get_calibration_report()` is a heuristic (>=7 bucket accuracy + text suggestions).
   No bucket discrimination test, no monotonicity check, no probability quality measure,
   no structured weight proposal.
2. **Variance-tuned is not outcome-tuned.** A dimension can spread opportunities apart and
   still be uncorrelated with success. Spread was the bootstrap; outcomes are the truth.
3. **Evidence blindness:** a final_score of 8.2 looks identical whether 60% of its weight
   came from researched signals or 0%. Conviction built on guesses must be visible.
4. **Small-N discipline:** with 10-50 outcomes, naive refits will overfit noise. Every
   adjustment needs minimum-sample guards and damping.

## Checkable criteria (rubric)

| ID | Criterion | Verifier |
|----|-----------|----------|
| CAL-01 | Outcome records snapshot score + dimensions at tracking time | existing `outcome_tracking.py` (covered by bridge tests) |
| CAL-02 | Bucket discrimination report: adaptive terciles/quintiles by final_score, per-bucket success rate, monotonicity verdict (DISCRIMINATIVE / WEAK / INVERTED / INSUFFICIENT) | `test_calibration_engine.py` |
| CAL-03 | Brier score + skill vs base-rate reference (score/10 as success probability) | `test_calibration_engine.py` |
| CAL-04 | Per-dimension effect sizes (success vs failure means) with min-N guards (>= 3 per side) | `test_calibration_engine.py` |
| CAL-05 | Weight proposals: damped (max +/-20% per cycle), renormalized to preserve total, NEVER auto-applied | `test_calibration_engine.py` |
| CAL-06 | `evidence_coverage` (weight-fraction of the score resting on data-backed fields) stamped on every scored opp | `test_evidence_coverage.py` |
| CAL-07 | `low_evidence_flag` stamped when final_score >= 7.5 and evidence_coverage < 0.20; cleared when no longer true (idempotent) | `test_evidence_coverage.py` |
| CAL-08 | No scoring regression: full suite green AND `rescore-all --dry-run` reports 0 score changes on unchanged data | pytest + manual gate |

## The loops this installs

| Loop | Cadence | Input -> Action -> Output -> Reinvestment |
|------|---------|-------------------------------------------|
| Outcome loop | per event (existing) | like/kickoff/validate -> `opp-os outcome` -> outcome_tracking.jsonl -> calibration input |
| Calibration loop | monthly (new) | outcomes -> `opp-os calibrate` -> discrimination + Brier + effects + damped proposal -> Daniel edits scoring_weights.yaml with audit comment (precedent: the 2026-05-20 variance audit block) |
| Evidence loop | per scoring run (new) | evidence_coverage -> low_evidence_flag on high scorers -> research queue prioritizes flagged opps -> coverage rises -> conviction is earned |
| Variance re-audit | quarterly (existing precedent) | live portfolio -> re-run variance audit -> retire near-constant dimensions |

## Small-N rules (non-negotiable until ~50 resolved outcomes)

- < 6 resolved outcomes: report INSUFFICIENT, propose nothing.
- 6-14 resolved: terciles, directional read only; proposals printed but labeled LOW-N.
- >= 15 resolved: quintiles; proposals usable with the +/-20% damping cap.
- watching/pivoted outcomes are excluded from resolution (neither success nor failure).

## Out of scope (YAGNI)

- Auto-writing scoring_weights.yaml (human gate is the point).
- ML models over 23 dims with < 100 outcomes (guaranteed overfit; weighted-average +
  damped nudges is the honest ceiling at this scale).
- Changing the kill gate or normalization (already correct and idempotency-tested).

## Research appendix (focused pass, June 12 2026)

Small-N calibration (N = 10-50 outcomes):
- **Brier Skill Score is the primary small-N metric** -- no bucketing required, meaningful
  vs the base-rate reference even at 10-20 outcomes; a single misranked outcome can flip
  the sign below N=20, so read direction not decimals.
  [emergentmind.com Brier-skill-score; machinelearningplus.com brier-score]
- Tercile/decile buckets with 1-3 observations swing wildly on single outcomes -- bucket
  reads are directional only at our scale. [ncbi PMC9787734]
- **Hold weights fixed below ~30 outcomes; validate only.** Refitting on tiny samples fits
  noise (MLE instability); damping/shrinkage is the mitigation. Encoded as
  REFIT_MIN_RESOLVED = 30 -> proposals labeled HOLD_WEIGHTS_VALIDATE_ONLY.
  [arxiv 2007.02153; ML regularization literature]

Predictive validity of structured scoring:
- Meehl-line evidence (136 comparisons over 50+ years): **mechanical aggregation equals or
  beats holistic judgment in nearly all domains** -- the weighted-rubric approach is the
  right architecture; the weights just need outcome grounding.
  [zaldlab.psy.vanderbilt.edu wmg00pa; argmin.net clinical-vs-statistical]
- Venture-competition rubric study (67 competitions, 118 funding rounds): scorecards carry
  real but moderate predictive signal; **score clustering at the top range** is the main
  failure mode (matches our normalize_portfolio_scores motivation). [mdpi 2079-8954/9/3/55]
- Dimension evidence: founder/team strongest (95% of 885 VCs), traction medium, **market
  timing weak** (success at any entry point) -- our timing_tailwind at 0.06 weight is
  consistent. [business.columbia.edu founder-personalities-vc]
- **Criteria redundancy inflates shared signal**: dimensions correlating > 0.6 double-count
  one underlying factor -- implemented as dimension_redundancy(); first live run flagged
  speed_to_mvp correlating 0.71-0.82 with capital_efficiency, competition_intensity,
  operational_simplicity, and distribution_accessibility (one "ease of execution" factor
  counted five times). [researchgate multicollinearity feature selection]

## First live findings (calibrate run, June 12 2026)

- 0 resolved outcomes yet (the 8 prior records were test leakage, now guarded + cleaned) --
  the loop's bottleneck is outcome recording, which the bridge now feeds automatically.
- Redundancy cluster around speed_to_mvp (rho 0.71-0.82 with 4 dims, n=76). Candidate
  action for the next weight edit: treat {speed_to_mvp, capital_efficiency,
  operational_simplicity} as one "execution ease" factor -- their combined 0.10 weight is
  effectively one signal counted three times.
