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

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

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
# Data-backed score normalisation constants
# ---------------------------------------------------------------------------
JOB_POSTING_COUNT_MAX: int = 50       # 50 job postings -> 10/10 market momentum
NEG_REVIEW_RATE_MAX: float = 0.8      # 80% negative reviews -> 10/10 competitor weakness
NEG_REVIEW_RATE_NEUTRAL_SCORE: float = 5.0  # 0% negative reviews -> 5/10 (neutral)

# ---------------------------------------------------------------------------
# Evidence coverage -- how much of a score rests on data vs AI guesses
# ---------------------------------------------------------------------------
DATA_BACKED_FIELDS = frozenset([
    "pain_validation_score",      # pain research / pain_signal_count fallback
    "market_momentum_score",      # Apify LinkedIn job postings
    "competitor_weakness_score",  # Apify G2 negative review rate
    "distribution_quality",       # derived from distribution_validated test
])
HIGH_SCORE_EVIDENCE_BAR: float = 7.5  # final_score at/above this demands evidence
MIN_EVIDENCE_COVERAGE: float = 0.50   # less than half the collectable evidence = guesswork

# ---------------------------------------------------------------------------
# Kill-thesis cap -- a strong adversarial thesis caps the score like a failed filter
# ---------------------------------------------------------------------------
KILL_THESIS_CAP_THRESHOLD: int = 7    # kill_thesis_strength >= this caps the score

# ---------------------------------------------------------------------------
# Layer field definitions
# ---------------------------------------------------------------------------
ATTRACTIVENESS_FIELDS = [
    "market_size",
    "timing_tailwind",
    "pain_severity",
    "willingness_to_pay",
    "monetization_clarity",
    "pain_validation_score",
]

EXECUTABILITY_FIELDS = [
    "speed_to_mvp",
    "capital_efficiency",
    "distribution_accessibility",
    "distribution_quality",
]

STRATEGIC_VALUE_FIELDS = [
    "competition_intensity",  # NOTE: inverted -- lower competition = higher score
    "defensibility",
    "regional_fit",
    "founder_fit",
    "ai_leverage",
    "operational_simplicity",
    "regulatory_simplicity",
    "revenue_speed_score",
    "gross_margin_potential",       # SaaS/software=9, services=4, hardware=3
    "network_effect_strength",      # marketplace=9, single-player=2; strong moat signal
    "switching_cost_score",         # data lock-in=9, commodity tools=2; retention predictor
    "market_momentum_score",        # derived: job_posting_count -> 0-10 (P3b)
    "competitor_weakness_score",    # derived: competitor_negative_review_rate -> 0-10 (P3b)
]

# ---------------------------------------------------------------------------
# Emergency fallback weights
# ---------------------------------------------------------------------------
# config/scoring_weights.yaml is the SINGLE source of truth for tuned weights.
# This fallback is equal-weight on purpose: a stale tuned copy here drifted
# from the YAML once already and silently scored differently. If the YAML
# cannot be loaded we score with equal weights and log an error instead.
_ALL_SCORED_FIELDS = ATTRACTIVENESS_FIELDS + EXECUTABILITY_FIELDS + STRATEGIC_VALUE_FIELDS

DEFAULT_WEIGHTS = {
    "weights": {field: 1.0 for field in _ALL_SCORED_FIELDS},
    "modifiers": {
        "venezuela_wedge_match": 1.5,
        "daniels_wedge_low": -1.0,
        "non_obviousness_high": 0.5,
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
    """Load scoring weights from config/scoring_weights.yaml (single source of truth).

    On any load failure, falls back to equal-weight DEFAULT_WEIGHTS and logs an
    ERROR -- equal weights keep the pipeline alive but scores are NOT calibrated.
    YAML weights are used as-is (no merge with defaults): a tuned 0.05-0.12 scale
    must never be mixed with the 1.0-scale fallback. Missing fields are warned
    about and simply do not contribute (score_layer skips weight 0).
    """
    path = config_path or CONFIG_PATH

    if not _YAML_AVAILABLE:
        logger.error(
            "PyYAML not installed -- using EQUAL-WEIGHT emergency fallback; scores are NOT calibrated"
        )
        return DEFAULT_WEIGHTS

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        logger.error(
            "scoring_weights.yaml not found at %s -- using EQUAL-WEIGHT emergency fallback; "
            "scores are NOT calibrated", path
        )
        return DEFAULT_WEIGHTS

    if not data or "weights" not in data:
        logger.error(
            "scoring_weights.yaml at %s is empty or has no 'weights' key -- "
            "using EQUAL-WEIGHT emergency fallback; scores are NOT calibrated", path
        )
        return DEFAULT_WEIGHTS

    yaml_weights = data.get("weights", {})
    missing = [f for f in _ALL_SCORED_FIELDS if f not in yaml_weights]
    if missing:
        logger.warning(
            "scoring_weights.yaml missing %d scored field(s) -- they will not contribute: %s",
            len(missing), ", ".join(missing),
        )

    return {
        "weights": yaml_weights,
        "modifiers": {**DEFAULT_WEIGHTS["modifiers"], **data.get("modifiers", {})},
        "caps": {**DEFAULT_WEIGHTS["caps"], **data.get("caps", {})},
    }


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


def apply_venezuela_wedge_bonus(opp: dict, weights: dict) -> dict:
    """Apply the Venezuela +1.5 structural wedge bonus to regional_fit dimension.

    Must be called BEFORE score_layer() runs on STRATEGIC_VALUE_FIELDS so the
    bonus is subject to the 20% strategic weight instead of bypassing it.
    Returns a new dict (does not mutate input).
    """
    geo = (opp.get("geography") or "").lower().strip()
    if not (geo == "venezuela" and opp.get("venezuela_wedge_match", False)):
        return opp

    mods = weights.get("modifiers", {})
    bonus = float(mods.get("venezuela_wedge_match", 1.5))
    current = float(opp.get("regional_fit") or 5.0)
    # Shallow copy is safe here: regional_fit is a scalar. If this function
    # ever needs to update a nested dict (e.g. payment_rail_context), copy
    # that nested structure too -- {**opp} alone would alias it.
    return {**opp, "regional_fit": min(10.0, current + bonus)}


def apply_modifiers(score: float, opp: dict, weights: dict) -> float:
    """Apply composite-level score modifiers.

    - daniels_wedge_low penalty if daniels_wedge_score < 2
    Note: Venezuela wedge bonus is applied to regional_fit before layer scoring,
    not here, so it is correctly weighted through the strategic layer.
    """
    mods = weights.get("modifiers", {})
    adjusted = score

    # Daniels wedge low penalty
    daniels_wedge = opp.get("daniels_wedge_score")
    if daniels_wedge is not None and float(daniels_wedge) < 2:
        adjusted += float(mods.get("daniels_wedge_low", -1.0))

    # Non-obviousness bonus
    non_obviousness = opp.get("non_obviousness_score")
    if non_obviousness is not None and float(non_obviousness) >= 6.0:
        adjusted += float(mods.get("non_obviousness_high", 0.5))

    return adjusted


def apply_caps(score: float, opp: dict, weights: dict) -> float:
    """Apply hard caps to the final score.

    - kill_decision == True            ->  0.0 (overrides everything)
    - 2+ decision filters failed        ->  cap at 5.0
    - kill_thesis_strength >= threshold ->  cap at 5.0 (adversarial pass, Wave 2.1)

    Non-fatal caps combine by taking the minimum, so a score hit by both a failed
    filter and a strong kill thesis is capped once, not stacked.
    """
    caps = weights.get("caps", {})

    # Hard kill — overrides all other caps
    if opp.get("kill_decision") is True:
        return float(caps.get("kill_decision_true", 0.0))

    capped = score

    # Decision filter cap: should_cap_score flag, or 2+ filters failed
    filter_results = opp.get("decision_filter_results") or {}
    should_cap = filter_results.get("should_cap_score", False)
    if not should_cap:
        filters_failed = opp.get("decision_filters_failed", 0) or 0
        should_cap = int(filters_failed) >= 2
    if should_cap:
        capped = min(capped, float(caps.get("decision_filter_2_failed", 5.0)))

    # Kill-thesis cap: a strong adversarial thesis caps the score like a failed filter
    strength = opp.get("kill_thesis_strength")
    if strength is not None:
        try:
            if int(strength) >= KILL_THESIS_CAP_THRESHOLD:
                capped = min(capped, float(caps.get("kill_thesis_strong", 5.0)))
        except (TypeError, ValueError):
            logger.warning(
                "Opportunity '%s' has non-numeric kill_thesis_strength %r -- cap skipped",
                opp.get("name", "<unknown>"), strength,
            )

    return capped


def _true_raw_score(opp: dict, raw_field: str, output_field: str):
    """The normalization input: the raw composite, never a normalized value.

    Falls back to output_field only for legacy records that predate
    raw_final_score being stamped at scoring time.
    """
    val = opp.get(raw_field)
    return val if val is not None else opp.get(output_field)


def normalize_portfolio_scores(
    opps: list,
    raw_field: str = "raw_final_score",
    output_field: str = "final_score",
    output_min: float = 2.0,
    output_max: float = 9.5,
    max_inflation: float = 1.5,
) -> list:
    """Spread final_score across a portfolio while preserving absolute quality.

    Problem: AI scorer clusters all post-kill-gate opps at 7-9 (they passed the gate).
    Solution: Spread scores for differentiation, but cap how much we inflate the top.

    IDEMPOTENCY (2026-06-10): input is ALWAYS raw_final_score (the raw composite
    stamped by score_opportunity), never the normalized final_score. Previously,
    partial rescores (e.g. free-research touching 20 of 80 opps) normalized a pool
    mixing fresh raw scores with stale normalized ones — every write shifted the
    whole portfolio (~75/80 phantom deltas per rescore). Normalizing from raw is
    a pure function of the data: same dimensions in, same scores out.

    max_inflation: maximum points added to the top scorer (default 1.5, was 2.5).
    Lowered 2026-05-20: max_inflation=2.5 allowed raw 6.9 → 8.0+, making 63% of opps
    look like top-tier. With 1.5 + output_max=9.5, a raw 7.2+ is needed to reach 8+.

    Only operates on non-killed, scored opps.
    Requires >= 3 opps with spread > 0.1 to activate; otherwise returns unchanged.
    """
    live = [
        o for o in opps
        if _true_raw_score(o, raw_field, output_field) is not None
        and not o.get("kill_decision")
    ]
    if len(live) < 3:
        return opps

    scores = [float(_true_raw_score(o, raw_field, output_field)) for o in live]
    min_s, max_s = min(scores), max(scores)
    spread = max_s - min_s

    if spread < 0.1:  # All scores identical — skip
        return opps

    # Cap output_max so the top scorer rises by at most max_inflation points
    capped_output_max = min(output_max, max_s + max_inflation)
    output_spread = capped_output_max - output_min

    result = []
    for opp in opps:
        raw_val = _true_raw_score(opp, raw_field, output_field)
        if raw_val is None or opp.get("kill_decision"):
            result.append(opp)
            continue
        normalized = ((float(raw_val) - min_s) / spread) * output_spread + output_min
        result.append({
            **opp,
            raw_field: round(float(raw_val), 4),
            output_field: round(max(output_min, min(output_max, normalized)), 4),
        })

    return result


def _derive_distribution_quality(opp: dict) -> dict:
    validated = opp.get("distribution_validated")
    if validated is None:
        return opp
    quality_score = 8.0 if validated else 3.0
    return {**opp, "distribution_quality": quality_score}


def _apply_pain_signal_fallback(opp: dict) -> dict:
    """Derive a pain_validation_score proxy from pain_signal_count when paid research is absent.

    Formula: min(6.0, 4.0 + pain_signal_count * 0.3)
    Capped at 6.0 so paid research results (typically 7-9) always dominate.
    Only fires when pain_validation_score is None and pain_signal_count >= 3.
    """
    if opp.get("pain_validation_score") is not None:
        return opp
    count = opp.get("pain_signal_count")
    if count is None or int(count) < 3:
        return opp
    fallback = min(6.0, 4.0 + int(count) * 0.3)
    return {**opp, "pain_validation_score": round(fallback, 2)}


def _normalize_data_backed_scores(opp: dict) -> dict:
    """Derive data-backed sub-scores from raw signals; return partial dict of new fields.

    Returns an empty dict if no recognised signals are present.
    Only keys that can be computed are included -- callers must NOT assume all keys exist.
    Pure function: no external calls, no mutation of input.
    """
    updates: dict = {}

    # market_momentum_score: job_posting_count -> 0-10
    # None = no data = don't set (leave as-is for neutral contribution).
    # 0 is ALSO treated as no-signal: apify_client.fetch_linkedin_jobs returns 0
    # on failure, so a 0 here cannot be distinguished from an Apify outage or a
    # bad scrape query. Callers already guard with `if job_count:` before
    # writing -- this mirrors that guard so a stray 0 can never zero the score.
    job_count = opp.get("job_posting_count")
    if job_count is not None and float(job_count) > 0:
        updates["market_momentum_score"] = round(min(job_count / JOB_POSTING_COUNT_MAX * 10, 10.0), 2)

    # competitor_weakness_score: neg_review_rate -> 0-10
    # 0% neg = 5 (neutral); 80%+ neg = 10
    neg_rate = opp.get("competitor_negative_review_rate")
    if neg_rate is not None:
        neg_rate_clamped = max(0.0, float(neg_rate))
        raw = NEG_REVIEW_RATE_NEUTRAL_SCORE + (neg_rate_clamped / NEG_REVIEW_RATE_MAX) * NEG_REVIEW_RATE_NEUTRAL_SCORE
        updates["competitor_weakness_score"] = round(min(raw, 10.0), 2)

    return updates


def compute_evidence_coverage(opp: dict, weights: dict) -> float:
    """Fraction of COLLECTABLE evidence weight actually collected for this opp.

    Only 4 of 23 dimensions can be data-backed, so an absolute weight-fraction
    would max out around 0.19 even with every signal collected -- structurally
    unreachable thresholds. Instead: denominator = total weight of all
    data-backed fields in the weight map (what evidence COULD exist),
    numerator = weight of those actually present on the opp.
    0.0 = pure AI inference; 1.0 = every collectable signal collected.
    """
    weight_map = weights.get("weights", {})
    collectable = sum(
        w for field, w in weight_map.items()
        if field in DATA_BACKED_FIELDS and w > 0
    )
    if collectable == 0:
        return 0.0
    collected = sum(
        weight_map.get(field, 0.0)
        for field in DATA_BACKED_FIELDS
        if opp.get(field) is not None
    )
    return collected / collectable


def score_opportunity(opp_dict: dict) -> dict:
    """Main scoring function.

    Takes a raw opportunity dict and returns an updated dict with:
    - attractiveness_score   (Layer 1, 0-10)
    - executability_score    (Layer 2, 0-10)
    - strategic_value_score  (Layer 3, 0-10)
    - final_score            (weighted composite + modifiers + caps applied)
    """
    opp = dict(opp_dict)  # shallow copy

    # Populate data-backed sub-scores from raw signals before any layer scoring.
    data_backed = _normalize_data_backed_scores(opp)
    opp = {**opp, **data_backed}

    opp = _derive_distribution_quality(opp)
    opp = _apply_pain_signal_fallback(opp)

    if opp.get("kill_criteria_passed") is None:
        logger.warning(
            "score_opportunity called before kill gate for opp '%s' — kill_criteria_passed is None",
            opp.get("name", "<unknown>"),
        )

    weights = load_weights()

    # --- Layer 1: Attractiveness ---
    attractiveness = score_layer(opp, ATTRACTIVENESS_FIELDS, weights)

    # --- Layer 2: Executability ---
    executability = score_layer(opp, EXECUTABILITY_FIELDS, weights)

    # --- Venezuela wedge bonus: applied to regional_fit before Layer 3 ---
    # Bonus must go through the 20% strategic weight, not added to composite.
    opp = apply_venezuela_wedge_bonus(opp, weights)

    # --- Layer 3: Strategic Value ---
    strategic = score_layer(opp, STRATEGIC_VALUE_FIELDS, weights)

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

    # Return a new dict — never mutate via direct key assignment.
    # raw_final_score is the pre-normalization composite: portfolio normalization
    # must always read THIS field, never a previously-normalized final_score —
    # mixing the two pools is what caused scores to drift on every rescore.
    final = round(max(0.0, min(10.0, composite)), 4)
    result = {
        **opp,
        "attractiveness_score": round(attractiveness, 4),
        "executability_score": round(executability, 4),
        "strategic_value_score": round(strategic, 4),
        "final_score": final,
        "raw_final_score": final,
    }

    # Disambiguate "no scoreable dimensions" from "killed": both produce
    # final_score 0.0, but a record with zero scored fields was never
    # evaluated -- downstream filters on final_score must not silently treat
    # it as rejected. The flag is stamped only when true and cleared once the
    # record becomes scoreable, so rescoring stays idempotent.
    has_scoreable_field = any(opp.get(f) is not None for f in _ALL_SCORED_FIELDS)
    if not has_scoreable_field:
        logger.warning(
            "Opportunity '%s' has no scoreable dimensions -- final_score 0.0 means "
            "UNSCORED, not killed (scoring_incomplete=True)",
            opp.get("name", "<unknown>"),
        )
        result["scoring_incomplete"] = True
    else:
        result.pop("scoring_incomplete", None)

    # Evidence coverage: make guess-built conviction visible. A high score with
    # near-zero coverage is a research-queue signal, not a green light. The flag
    # is stamped only when true and cleared otherwise so rescoring stays idempotent.
    coverage = compute_evidence_coverage(opp, weights)
    result["evidence_coverage"] = round(coverage, 4)
    if (
        has_scoreable_field
        and final >= HIGH_SCORE_EVIDENCE_BAR
        and coverage < MIN_EVIDENCE_COVERAGE
    ):
        result["low_evidence_flag"] = True
    else:
        result.pop("low_evidence_flag", None)

    return result
