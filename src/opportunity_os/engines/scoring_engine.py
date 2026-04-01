"""
Scoring Engine -- 3-layer weighted scoring model.

Layer 1: Attractiveness (market pull)
Layer 2: Executability (founder push)
Layer 3: Strategic Value (portfolio fit)

Each layer produces a 0-10 score. Final score is weighted composite.
Hard caps applied after scoring:
- kill_decision = True -> final_score = 0.0
- 2+ decision filters failed -> cap at 5.0
"""

import os
from typing import Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# This file lives at: src/opportunity_os/engines/scoring_engine.py
# Project root is 4 levels up.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "scoring_weights.yaml")

# ---------------------------------------------------------------------------
# Layer field definitions
# ---------------------------------------------------------------------------
ATTRACTIVENESS_FIELDS = [
    "market_size",
    "timing_tailwind",
    "pain_severity",
    "willingness_to_pay",
    "monetization_clarity",
]

EXECUTABILITY_FIELDS = [
    "speed_to_mvp",
    "capital_efficiency",
    "distribution_accessibility",
    "operational_simplicity",
    "path_to_first_revenue",
]

STRATEGIC_VALUE_FIELDS = [
    "competition_intensity",  # NOTE: inverted -- lower competition = higher score
    "defensibility",
    "regional_fit",
    "founder_fit",
    "ai_leverage",
    "regulatory_simplicity",
]

# ---------------------------------------------------------------------------
# Default weights (fallback if YAML not found)
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {
    "weights": {
        "market_size": 0.10,
        "timing_tailwind": 0.08,
        "pain_severity": 0.10,
        "willingness_to_pay": 0.08,
        "monetization_clarity": 0.08,
        "speed_to_mvp": 0.08,
        "capital_efficiency": 0.07,
        "distribution_accessibility": 0.08,
        "competition_intensity": 0.07,
        "defensibility": 0.07,
        "regional_fit": 0.07,
        "founder_fit": 0.05,
        "ai_leverage": 0.04,
        "operational_simplicity": 0.05,
        "regulatory_simplicity": 0.04,
        "path_to_first_revenue": 0.04,
    },
    "modifiers": {
        "venezuela_wedge_match": 1.5,
        "daniels_wedge_low": -1.0,
    },
    "caps": {
        "kill_decision_true": 0.0,
        "decision_filter_2_failed": 5.0,
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_weights(config_path: Optional[str] = None) -> dict:
    """Load scoring weights from config/scoring_weights.yaml.

    Falls back to DEFAULT_WEIGHTS if the file is not found or PyYAML is not installed.
    """
    path = config_path or CONFIG_PATH

    if not _YAML_AVAILABLE:
        return DEFAULT_WEIGHTS

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data or "weights" not in data:
            return DEFAULT_WEIGHTS
        # Merge with defaults to ensure all keys are present
        merged = {
            "weights": {**DEFAULT_WEIGHTS["weights"], **data.get("weights", {})},
            "modifiers": {**DEFAULT_WEIGHTS["modifiers"], **data.get("modifiers", {})},
            "caps": {**DEFAULT_WEIGHTS["caps"], **data.get("caps", {})},
        }
        return merged
    except FileNotFoundError:
        return DEFAULT_WEIGHTS


def score_layer(opp_fields: dict, field_list: list, weights: dict) -> float:
    """Score one layer as a weighted average of available fields.

    Skips None fields; adjusts denominator so missing fields do not penalise.
    Returns a 0-10 float.
    """
    weight_map = weights.get("weights", {})

    total_weighted_score = 0.0
    total_weight = 0.0

    for field in field_list:
        value = opp_fields.get(field)
        if value is None:
            continue  # skip missing fields

        w = weight_map.get(field, 0.0)
        if w == 0.0:
            continue

        try:
            # Invert competition_intensity: lower competition = higher score
            if field == "competition_intensity":
                effective_value = 10.0 - float(value)
            else:
                effective_value = float(value)
        except (TypeError, ValueError):
            continue  # skip non-numeric field values

        total_weighted_score += effective_value * w
        total_weight += w

    if total_weight == 0.0:
        return 0.0

    # Normalise back to 0-10 scale (weights are absolute, not per-layer)
    raw = total_weighted_score / total_weight
    return max(0.0, min(10.0, raw))


def apply_modifiers(score: float, opp: dict, weights: dict) -> float:
    """Apply score modifiers.

    + venezuela_wedge_match bonus if geography=venezuela and venezuela_wedge_category set
    - daniels_wedge_low penalty if daniels_wedge_score < 2
    """
    mods = weights.get("modifiers", {})
    geo = (opp.get("geography") or "").lower().strip()
    adjusted = score

    # Venezuela wedge match bonus
    if geo == "venezuela" and opp.get("venezuela_wedge_match", False):
        adjusted += float(mods.get("venezuela_wedge_match", 1.5))

    # Daniels wedge low penalty
    daniels_wedge = opp.get("daniels_wedge_score")
    if daniels_wedge is not None and float(daniels_wedge) < 2:
        adjusted += float(mods.get("daniels_wedge_low", -1.0))

    return adjusted


def apply_caps(score: float, opp: dict, weights: dict) -> float:
    """Apply hard caps to the final score.

    - kill_decision == True  ->  0.0
    - 2+ decision filters failed  ->  cap at 5.0
    """
    caps = weights.get("caps", {})

    # Hard kill
    if opp.get("kill_decision") is True:
        return float(caps.get("kill_decision_true", 0.0))

    # Check DecisionFilterResults for should_cap_score flag
    filter_results = opp.get("DecisionFilterResults") or opp.get("decision_filter_results") or {}
    should_cap = filter_results.get("should_cap_score", False)

    # Also check simple integer counter: decision_filters_failed >= 2
    if not should_cap:
        filters_failed = opp.get("decision_filters_failed", 0) or 0
        should_cap = int(filters_failed) >= 2

    if should_cap:
        cap_value = float(caps.get("decision_filter_2_failed", 5.0))
        return min(score, cap_value)

    return score


def score_opportunity(opp_dict: dict) -> dict:
    """Main scoring function.

    Takes a raw opportunity dict and returns an updated dict with:
    - attractiveness_score   (Layer 1, 0-10)
    - executability_score    (Layer 2, 0-10)
    - strategic_value_score  (Layer 3, 0-10)
    - final_score            (weighted composite + modifiers + caps applied)
    """
    opp = dict(opp_dict)  # shallow copy
    weights = load_weights()

    # --- Layer 1: Attractiveness ---
    attractiveness = score_layer(opp, ATTRACTIVENESS_FIELDS, weights)
    opp["attractiveness_score"] = round(attractiveness, 4)

    # --- Layer 2: Executability ---
    executability = score_layer(opp, EXECUTABILITY_FIELDS, weights)
    opp["executability_score"] = round(executability, 4)

    # --- Layer 3: Strategic Value ---
    strategic = score_layer(opp, STRATEGIC_VALUE_FIELDS, weights)
    opp["strategic_value_score"] = round(strategic, 4)

    # --- Composite: 50% attractiveness + 30% executability + 20% strategic ---
    composite = (
        0.50 * attractiveness +
        0.30 * executability +
        0.20 * strategic
    )

    # --- Modifiers ---
    composite = apply_modifiers(composite, opp, weights)

    # --- Caps ---
    composite = apply_caps(composite, opp, weights)

    opp["final_score"] = round(max(0.0, min(10.0, composite)), 4)

    return opp
