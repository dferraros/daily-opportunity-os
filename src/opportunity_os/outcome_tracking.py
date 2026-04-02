"""
Outcome Tracking — calibrate the scoring model from real results.
The scoring model has 18 criteria but zero calibration data.
This module tracks real outcomes and generates weight adjustment suggestions.
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Optional


# ─── Schema documentation ────────────────────────────────────────────────────

OUTCOME_SCHEMA = {
    "opp_id": "str — opportunity ID (e.g. opp_20260401_glo_f1cebc01)",
    "outcome": (
        "str — one of: built_launched | validated_passed | validated_failed | "
        "killed_wrong_score | watching | pivoted"
    ),
    "predicted_score": "float | None — attractiveness_score at time of tracking",
    "final_score": "float | None — composite final_score at time of tracking",
    "date": "str — ISO date YYYY-MM-DD when outcome was recorded",
    "notes": "str — free-text notes about what happened",
    "scoring_criteria": (
        "dict — snapshot of the 14 scoring dimensions at time of tracking, "
        "used for weight adjustment analysis"
    ),
}

VALID_OUTCOMES = frozenset(
    ["built_launched", "validated_passed", "validated_failed",
     "killed_wrong_score", "watching", "pivoted"]
)

SCORING_DIMENSIONS = [
    "pain_severity", "market_size", "timing_tailwind", "monetization_clarity",
    "speed_to_mvp", "capital_efficiency", "distribution_accessibility",
    "competition_intensity", "defensibility", "regional_fit",
    "founder_fit", "ai_leverage", "operational_simplicity", "regulatory_simplicity",
]


# ─── Path helpers ─────────────────────────────────────────────────────────────

def _project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])


def _outcome_file() -> str:
    return os.path.join(_project_root(), "data", "outcome_tracking.jsonl")


def _opportunities_file() -> str:
    return os.path.join(_project_root(), "data", "opportunities", "opportunities.jsonl")


# ─── Lookup helpers ───────────────────────────────────────────────────────────

def _lookup_opportunity(opp_id: str) -> Optional[dict]:
    """Find an opportunity record by ID in opportunities.jsonl."""
    path = _opportunities_file()
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rec = json.loads(line)
                if rec.get("id") == opp_id:
                    return rec
            except json.JSONDecodeError:
                continue
    return None


def _read_outcomes() -> list[dict]:
    """Read all tracked outcomes from outcome_tracking.jsonl."""
    path = _outcome_file()
    if not os.path.exists(path):
        return []
    results = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return results


# ─── Public API ───────────────────────────────────────────────────────────────

def record_outcome(opp_id: str, outcome: str, notes: str = "") -> None:
    """
    Record what actually happened to an opportunity.

    Args:
        opp_id:  Opportunity ID string (e.g. "opp_20260401_glo_f1cebc01").
        outcome: One of the VALID_OUTCOMES values.
        notes:   Optional free-text explanation.

    Raises:
        ValueError: If outcome is not a recognised value.
    """
    if outcome not in VALID_OUTCOMES:
        raise ValueError(
            f"Invalid outcome '{outcome}'. Must be one of: {sorted(VALID_OUTCOMES)}"
        )

    opp = _lookup_opportunity(opp_id)

    # Snapshot scoring criteria for later weight analysis
    criteria_snapshot: dict = {}
    predicted_score: Optional[float] = None
    final_score: Optional[float] = None

    if opp:
        predicted_score = opp.get("attractiveness_score")
        final_score = opp.get("final_score")
        criteria_snapshot = {dim: opp.get(dim) for dim in SCORING_DIMENSIONS}

    record = {
        "opp_id": opp_id,
        "outcome": outcome,
        "predicted_score": predicted_score,
        "final_score": final_score,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes,
        "scoring_criteria": criteria_snapshot,
    }

    path = _outcome_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Initialise file with header if it doesn't exist or is empty
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# outcome tracking — populated by record_outcome()\n")

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    print(f"Outcome recorded: {opp_id} -> {outcome} (score: {predicted_score})")


def get_calibration_report() -> dict:
    """
    Analyse tracked outcomes and generate weight adjustment suggestions.

    Returns a dict with:
        total_tracked         int
        high_score_outcomes   dict — breakdown for opps scored >= 7
        score_accuracy        float — % of high-score opps that passed validation
        worst_misses          list — high-score opps that failed validation
        suggested_weight_adjustments  list[str]
    """
    outcomes = _read_outcomes()

    if not outcomes:
        return {
            "total_tracked": 0,
            "high_score_outcomes": {">=7": {"validated_passed": 0, "validated_failed": 0, "killed": 0}},
            "score_accuracy": 0.0,
            "worst_misses": [],
            "suggested_weight_adjustments": ["No outcomes tracked yet — run record_outcome() first."],
        }

    # ── High-score bucket (attractiveness_score >= 7) ─────────────────────────
    high_score = [o for o in outcomes if (o.get("predicted_score") or 0) >= 7]
    hs_passed = [o for o in high_score if o["outcome"] == "validated_passed"]
    hs_failed = [o for o in high_score if o["outcome"] == "validated_failed"]
    hs_killed = [o for o in high_score if o["outcome"] == "killed_wrong_score"]

    score_accuracy = len(hs_passed) / len(high_score) if high_score else 0.0

    # ── Worst misses — high-score opps that failed ────────────────────────────
    worst_misses = []
    for o in hs_failed + hs_killed:
        miss = {
            "opp_id": o["opp_id"],
            "predicted_score": o.get("predicted_score"),
            "outcome": o["outcome"],
            "notes": o.get("notes", ""),
            "criteria": o.get("scoring_criteria", {}),
        }
        worst_misses.append(miss)

    # ── Weight adjustment analysis ────────────────────────────────────────────
    suggestions = _generate_weight_suggestions(outcomes, hs_failed + hs_killed)

    return {
        "total_tracked": len(outcomes),
        "high_score_outcomes": {
            ">=7": {
                "validated_passed": len(hs_passed),
                "validated_failed": len(hs_failed),
                "killed": len(hs_killed),
            }
        },
        "score_accuracy": round(score_accuracy, 3),
        "worst_misses": worst_misses,
        "suggested_weight_adjustments": suggestions,
    }


# ─── Internal analysis ────────────────────────────────────────────────────────

def _generate_weight_suggestions(
    all_outcomes: list[dict],
    failures: list[dict],
) -> list[str]:
    """
    Compare criterion values in failures vs successes to surface overweighted dims.
    Rule: if a dimension has a high average value in failures but low in successes,
    it may be overweighted.
    """
    if len(failures) < 2:
        return ["Not enough failures to suggest adjustments (need >= 2)."]

    successes = [o for o in all_outcomes if o["outcome"] == "validated_passed"]
    suggestions = []

    for dim in SCORING_DIMENSIONS:
        fail_vals = [
            o["scoring_criteria"][dim]
            for o in failures
            if o.get("scoring_criteria", {}).get(dim) is not None
        ]
        pass_vals = [
            o["scoring_criteria"][dim]
            for o in successes
            if o.get("scoring_criteria", {}).get(dim) is not None
        ]

        if len(fail_vals) < 2:
            continue

        avg_fail = sum(fail_vals) / len(fail_vals)
        avg_pass = sum(pass_vals) / len(pass_vals) if pass_vals else None

        # Flag if failures have high scores (>= 7) on this dimension
        # but the outcomes are bad — suggests overweighting
        if avg_fail >= 7.0:
            if avg_pass is not None and avg_fail > avg_pass + 1.5:
                suggestions.append(
                    f"{dim} may be overweighted — avg {avg_fail:.1f} in "
                    f"{len(fail_vals)} failures vs {avg_pass:.1f} in "
                    f"{len(pass_vals)} successes. Consider reducing its weight."
                )
            elif avg_pass is None:
                suggestions.append(
                    f"{dim} consistently high ({avg_fail:.1f} avg) in "
                    f"{len(fail_vals)} failures — no passing comparisons yet. Watch this dimension."
                )

    if not suggestions:
        suggestions.append(
            "No strong overweighting signals detected yet. "
            f"Analysed {len(failures)} failures across {len(SCORING_DIMENSIONS)} dimensions."
        )

    return suggestions
