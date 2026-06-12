"""
Calibration Engine -- quantitative validation of the scoring model against outcomes.

Closes the loop that outcome_tracking.py opens: outcomes are recorded there;
this module measures whether final_score actually predicts them, and proposes
damped weight adjustments that a human applies to config/scoring_weights.yaml.

Design rules (see docs/plans/2026-06-12-scoring-calibration-goal.md):
- Pure functions over outcome lists -- no file IO here (CLI does the loading).
- Small-N guards everywhere: < MIN_RESOLVED outcomes -> INSUFFICIENT, no proposals.
- Proposals are damped (max +/-20% per cycle), renormalized, NEVER auto-applied.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

SUCCESS_OUTCOMES = frozenset(["validated_passed", "built_launched"])
FAILURE_OUTCOMES = frozenset(["validated_failed", "killed_wrong_score"])
# watching / pivoted are unresolved -- excluded from calibration.

# Conviction-bridge stamps (opp-os outcome <id> <status>) mapped to calibration outcomes
BRIDGE_OUTCOME_MAP = {
    "validated": "validated_passed",
    "killed": "validated_failed",
    "shipped": "built_launched",
    "revenue": "built_launched",
}

MIN_RESOLVED = 6            # below this: INSUFFICIENT, nothing computed
QUINTILE_THRESHOLD = 15     # >= this many resolved outcomes -> 5 buckets, else 3
REFIT_MIN_RESOLVED = 30     # below this: proposals are VALIDATE_ONLY (research: refits
                            # under N=30 fit noise -- hold weights, just measure)
MIN_PER_SIDE = 3            # dimension effects need >= 3 success AND >= 3 failure values
MAX_WEIGHT_CHANGE = 0.20    # damping: no weight moves more than 20% per cycle
MIN_EFFECT = 0.05           # |effect| below this (0.5 pts on the 0-10 scale) is noise
REDUNDANCY_THRESHOLD = 0.6  # |spearman| above this between two dims = double-counted signal
REDUNDANCY_MIN_PAIRS = 10   # need >= 10 opps with both values to trust a correlation

VERDICT_DISCRIMINATIVE = "DISCRIMINATIVE"
VERDICT_WEAK = "WEAK"
VERDICT_INVERTED = "INVERTED"
VERDICT_INSUFFICIENT = "INSUFFICIENT"


def resolve_outcomes(outcomes: list[dict]) -> list[dict]:
    """Filter to resolved outcomes (success/failure) that carry a final_score.

    Returns new dicts with a binary `success` field added; input is not mutated.
    """
    resolved = []
    for o in outcomes:
        outcome = o.get("outcome")
        score = o.get("final_score")
        if score is None:
            continue
        if outcome in SUCCESS_OUTCOMES:
            resolved.append({**o, "success": 1})
        elif outcome in FAILURE_OUTCOMES:
            resolved.append({**o, "success": 0})
    return resolved


def outcomes_from_opportunity_stamps(opps: list[dict], dimensions: list[str]) -> list[dict]:
    """Derive calibration records from conviction-bridge outcome stamps.

    Best-effort historical backfill: bridge stamps don't snapshot the score at
    outcome time, so the current stored final_score stands in for it. Killed
    opps whose score was already zeroed by the kill cap are skipped -- a 0.0
    "prediction" for every failure would fake perfect discrimination.
    """
    derived = []
    for o in opps:
        mapped = BRIDGE_OUTCOME_MAP.get(o.get("outcome"))
        score = o.get("final_score")
        if mapped is None or score is None:
            continue
        if o.get("kill_decision") and float(score) == 0.0:
            continue
        derived.append({
            "opp_id": o.get("id"),
            "outcome": mapped,
            "final_score": score,
            "scoring_criteria": {d: o.get(d) for d in dimensions},
            "derived_from": "bridge_stamp",
        })
    return derived


def _bucket_boundaries(scores: list[float], n_buckets: int) -> list[float]:
    """Quantile cut points (exclusive of min/max) for n_buckets buckets."""
    ordered = sorted(scores)
    return [
        ordered[min(len(ordered) - 1, (len(ordered) * k) // n_buckets)]
        for k in range(1, n_buckets)
    ]


def discrimination_report(outcomes: list[dict]) -> dict:
    """Bucket resolved outcomes by final_score; test that success rate ranks with score.

    Adaptive bucketing: terciles under QUINTILE_THRESHOLD resolved outcomes,
    quintiles at or above. Verdict:
    - INSUFFICIENT: fewer than MIN_RESOLVED resolved outcomes
    - DISCRIMINATIVE: top bucket rate > bottom bucket rate AND no adjacent inversion
      worse than one bucket pair
    - INVERTED: top bucket rate < bottom bucket rate
    - WEAK: anything else (flat or noisy ordering)
    """
    resolved = resolve_outcomes(outcomes)
    if len(resolved) < MIN_RESOLVED:
        return {
            "verdict": VERDICT_INSUFFICIENT,
            "resolved_count": len(resolved),
            "needed": MIN_RESOLVED,
            "buckets": [],
        }

    n_buckets = 5 if len(resolved) >= QUINTILE_THRESHOLD else 3
    cuts = _bucket_boundaries([float(o["final_score"]) for o in resolved], n_buckets)

    buckets: list[list[dict]] = [[] for _ in range(n_buckets)]
    for o in resolved:
        idx = sum(1 for c in cuts if float(o["final_score"]) >= c)
        buckets[min(idx, n_buckets - 1)].append(o)

    rows = []
    for i, members in enumerate(buckets):
        rate = (sum(m["success"] for m in members) / len(members)) if members else None
        rows.append({
            "bucket": i + 1,  # 1 = lowest scores, n = highest
            "n": len(members),
            "success_rate": round(rate, 3) if rate is not None else None,
        })

    rated = [r for r in rows if r["success_rate"] is not None and r["n"] > 0]
    verdict = _discrimination_verdict(rated)
    return {
        "verdict": verdict,
        "resolved_count": len(resolved),
        "n_buckets": n_buckets,
        "buckets": rows,
        "low_n_warning": len(resolved) < QUINTILE_THRESHOLD,
    }


def _discrimination_verdict(rated_rows: list[dict]) -> str:
    """Verdict from non-empty bucket rows ordered low score -> high score."""
    if len(rated_rows) < 2:
        return VERDICT_WEAK
    bottom = rated_rows[0]["success_rate"]
    top = rated_rows[-1]["success_rate"]
    if top < bottom:
        return VERDICT_INVERTED
    if top == bottom:
        return VERDICT_WEAK
    inversions = sum(
        1
        for a, b in zip(rated_rows, rated_rows[1:])
        if b["success_rate"] < a["success_rate"]
    )
    return VERDICT_DISCRIMINATIVE if inversions <= 1 else VERDICT_WEAK


def brier_report(outcomes: list[dict]) -> dict:
    """Brier score treating final_score/10 as P(success), plus skill vs base rate.

    skill = 1 - brier/brier_ref where brier_ref always predicts the base rate.
    skill > 0 means the score carries information beyond "predict the average".
    """
    resolved = resolve_outcomes(outcomes)
    if len(resolved) < MIN_RESOLVED:
        return {"verdict": VERDICT_INSUFFICIENT, "resolved_count": len(resolved)}

    pairs = [(min(1.0, max(0.0, float(o["final_score"]) / 10.0)), o["success"]) for o in resolved]
    brier = sum((p - y) ** 2 for p, y in pairs) / len(pairs)

    base_rate = sum(y for _, y in pairs) / len(pairs)
    brier_ref = sum((base_rate - y) ** 2 for _, y in pairs) / len(pairs)
    skill = 1.0 - (brier / brier_ref) if brier_ref > 0 else 0.0

    return {
        "resolved_count": len(resolved),
        "base_rate": round(base_rate, 3),
        "brier": round(brier, 4),
        "brier_reference": round(brier_ref, 4),
        "skill": round(skill, 4),
    }


def dimension_effects(outcomes: list[dict], dimensions: list[str]) -> list[dict]:
    """Per-dimension success-vs-failure mean difference, scaled to [-1, 1].

    effect = (mean(success values) - mean(failure values)) / 10.
    Positive effect = dimension is higher in successes (predictive as weighted).
    Dimensions with fewer than MIN_PER_SIDE values on either side are skipped.
    """
    resolved = resolve_outcomes(outcomes)
    effects = []
    for dim in dimensions:
        succ_vals, fail_vals = [], []
        for o in resolved:
            val = (o.get("scoring_criteria") or {}).get(dim)
            if val is None:
                continue
            (succ_vals if o["success"] else fail_vals).append(float(val))
        if len(succ_vals) < MIN_PER_SIDE or len(fail_vals) < MIN_PER_SIDE:
            continue
        avg_s = sum(succ_vals) / len(succ_vals)
        avg_f = sum(fail_vals) / len(fail_vals)
        effects.append({
            "dimension": dim,
            "avg_success": round(avg_s, 2),
            "avg_failure": round(avg_f, 2),
            "effect": round((avg_s - avg_f) / 10.0, 4),
            "n_success": len(succ_vals),
            "n_failure": len(fail_vals),
        })
    return sorted(effects, key=lambda e: abs(e["effect"]), reverse=True)


def propose_weight_adjustments(effects: list[dict], current_weights: dict) -> dict:
    """Damped weight proposal from dimension effects. NEVER auto-applied.

    Each dimension with |effect| >= MIN_EFFECT gets a multiplicative nudge in the
    effect's direction, capped at MAX_WEIGHT_CHANGE. The full weight map is then
    renormalized so total weight is preserved. Returns proposal data for human
    review; callers must not write config/scoring_weights.yaml from this.
    """
    adjustments = {}
    for e in effects:
        dim = e["dimension"]
        if dim not in current_weights or abs(e["effect"]) < MIN_EFFECT:
            continue
        # effect 0.20 (= 2.0 points of separation) saturates the damping cap
        scale = max(-1.0, min(1.0, e["effect"] / 0.20))
        factor = 1.0 + MAX_WEIGHT_CHANGE * scale
        adjustments[dim] = {
            "current": current_weights[dim],
            "nudged": current_weights[dim] * factor,
            "effect": e["effect"],
            "n": e["n_success"] + e["n_failure"],
        }

    nudged_map = {
        dim: adjustments[dim]["nudged"] if dim in adjustments else w
        for dim, w in current_weights.items()
    }
    total_before = sum(current_weights.values())
    total_after = sum(nudged_map.values())
    norm = total_before / total_after if total_after > 0 else 1.0
    proposed_map = {dim: round(w * norm, 4) for dim, w in nudged_map.items()}

    return {
        "adjusted_dimensions": {
            dim: {
                "current": round(a["current"], 4),
                "proposed": proposed_map[dim],
                "effect": a["effect"],
                "n": a["n"],
            }
            for dim, a in adjustments.items()
        },
        "proposed_weights": proposed_map,
        "total_weight_preserved": round(sum(proposed_map.values()), 4),
        "auto_apply": False,
    }


def _average_ranks(values: list[float]) -> list[float]:
    """Average ranks with tie handling (1-based)."""
    indexed = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def _spearman(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation (Pearson on average ranks). Returns 0.0 on zero variance."""
    rx, ry = _average_ranks(xs), _average_ranks(ys)
    n = len(rx)
    mean_x, mean_y = sum(rx) / n, sum(ry) / n
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry))
    var_x = sum((a - mean_x) ** 2 for a in rx)
    var_y = sum((b - mean_y) ** 2 for b in ry)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / (var_x ** 0.5 * var_y ** 0.5)


def dimension_redundancy(opps: list[dict], dimensions: list[str]) -> list[dict]:
    """Find dimension pairs whose values rank-correlate above REDUNDANCY_THRESHOLD.

    Redundant pairs double-count one underlying signal, silently inflating its
    weight in the composite. Computed over live (non-killed) opportunities with
    both values present; pairs with < REDUNDANCY_MIN_PAIRS observations skipped.
    """
    live = [o for o in opps if not o.get("kill_decision")]
    flagged = []
    for i, dim_a in enumerate(dimensions):
        for dim_b in dimensions[i + 1:]:
            xs, ys = [], []
            for o in live:
                va, vb = o.get(dim_a), o.get(dim_b)
                if va is not None and vb is not None:
                    xs.append(float(va))
                    ys.append(float(vb))
            if len(xs) < REDUNDANCY_MIN_PAIRS:
                continue
            rho = _spearman(xs, ys)
            if abs(rho) >= REDUNDANCY_THRESHOLD:
                flagged.append({
                    "dim_a": dim_a,
                    "dim_b": dim_b,
                    "spearman": round(rho, 3),
                    "n": len(xs),
                })
    return sorted(flagged, key=lambda f: abs(f["spearman"]), reverse=True)


def calibration_summary(outcomes: list[dict], weights: dict, dimensions: list[str]) -> dict:
    """Full calibration readout: discrimination + Brier + effects + damped proposal."""
    discrimination = discrimination_report(outcomes)
    insufficient = discrimination["verdict"] == VERDICT_INSUFFICIENT
    resolved_count = discrimination["resolved_count"]

    effects = [] if insufficient else dimension_effects(outcomes, dimensions)
    if insufficient:
        proposal = {"adjusted_dimensions": {}, "proposed_weights": {}, "auto_apply": False,
                    "note": "INSUFFICIENT outcomes -- no proposal"}
    else:
        proposal = propose_weight_adjustments(effects, weights)

    # Research rule: refitting under ~30 outcomes fits noise. Below the bar the
    # proposal is informational only -- hold weights, keep recording outcomes.
    proposal = {
        **proposal,
        "recommendation": (
            "REVIEW_AND_APPLY" if resolved_count >= REFIT_MIN_RESOLVED
            else f"HOLD_WEIGHTS_VALIDATE_ONLY (resolved {resolved_count} < {REFIT_MIN_RESOLVED})"
        ),
    }

    return {
        "discrimination": discrimination,
        "brier": brier_report(outcomes),
        "dimension_effects": effects,
        "weight_proposal": proposal,
    }
