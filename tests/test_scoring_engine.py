"""Tests for engines/scoring_engine.py — score_opportunity, kill gate cap, decision filter cap."""
import pytest
from opportunity_os.engines.scoring_engine import score_opportunity, normalize_portfolio_scores


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def base_opp():
    return {
        "id": "test_score_001",
        "name": "Test Opportunity",
        "geography": "global",
        "vertical": "smb_software",
        "kill_decision": False,
        "problem_statement": "Businesses lose money on manual reconciliation",
        "pain_severity": 8,
        "market_size": 7,
        "timing_tailwind": 6,
        "willingness_to_pay": 7,
        "monetization_clarity": 7,
        "speed_to_mvp": 7,
        "capital_efficiency": 7,
        "distribution_accessibility": 6,
        "competition_intensity": 4,
        "defensibility": 5,
        "regional_fit": 5,
        "founder_fit": 6,
        "ai_leverage": 6,
        "operational_simplicity": 6,
        "regulatory_simplicity": 7,
        "revenue_speed_score": 6,
    }


# ─── score_opportunity ────────────────────────────────────────────────────────

def test_score_opportunity_returns_final_score(base_opp):
    result = score_opportunity(base_opp)
    assert "final_score" in result
    assert 0.0 <= result["final_score"] <= 10.0


def test_score_opportunity_returns_layer_scores(base_opp):
    result = score_opportunity(base_opp)
    assert "attractiveness_score" in result
    assert "executability_score" in result
    assert "strategic_value_score" in result


def test_score_opportunity_killed_returns_zero(base_opp):
    opp = {**base_opp, "kill_decision": True}
    result = score_opportunity(opp)
    assert result["final_score"] == 0.0


def test_score_opportunity_decision_filter_caps_at_5(base_opp):
    # First verify the uncapped score is above 5.0 so the cap is non-vacuous.
    uncapped = score_opportunity(base_opp)
    assert uncapped["final_score"] > 5.0, (
        "base_opp scores <= 5.0 before cap — test would pass trivially; raise base dimensions"
    )
    opp = {
        **base_opp,
        "decision_filter_results": {
            "can_sell_fast": False,
            "can_build_lean": False,
            "can_compound": True,
            "should_cap_score": True,
        },
    }
    result = score_opportunity(opp)
    assert result["final_score"] <= 5.0


def test_score_opportunity_preserves_extra_fields(base_opp):
    result = score_opportunity(base_opp)
    assert result["name"] == "Test Opportunity"
    assert result["id"] == "test_score_001"


def test_score_opportunity_does_not_mutate_input(base_opp):
    original_id = base_opp["id"]
    _ = score_opportunity(base_opp)
    assert base_opp["id"] == original_id
    assert "final_score" not in base_opp


def test_score_opportunity_no_dimensions_still_returns_score():
    opp = {"id": "bare", "name": "bare opp", "kill_decision": False}
    result = score_opportunity(opp)
    assert "final_score" in result
    assert result["final_score"] >= 0.0


# ─── normalize_portfolio_scores ───────────────────────────────────────────────

def test_normalize_portfolio_spreads_scores():
    opps = [
        {"id": "a", "final_score": 5.0, "kill_decision": False},
        {"id": "b", "final_score": 7.0, "kill_decision": False},
        {"id": "c", "final_score": 9.0, "kill_decision": False},
        {"id": "d", "final_score": 6.0, "kill_decision": False},
    ]
    result = normalize_portfolio_scores(opps)
    scores = [o["final_score"] for o in result if not o.get("kill_decision")]
    assert min(scores) >= 2.0
    assert max(scores) <= 10.0


def test_normalize_portfolio_skips_killed():
    opps = [
        {"id": "a", "final_score": 5.0, "kill_decision": False},
        {"id": "b", "final_score": 7.0, "kill_decision": False},
        {"id": "c", "final_score": 9.0, "kill_decision": False},
        {"id": "dead", "final_score": 0.0, "kill_decision": True},
    ]
    result = normalize_portfolio_scores(opps)
    killed = next(o for o in result if o["id"] == "dead")
    assert killed["final_score"] == 0.0


def test_normalize_portfolio_requires_3_opps():
    opps = [
        {"id": "a", "final_score": 5.0, "kill_decision": False},
        {"id": "b", "final_score": 9.0, "kill_decision": False},
    ]
    result = normalize_portfolio_scores(opps)
    assert result[0]["final_score"] == 5.0
    assert result[1]["final_score"] == 9.0


def test_normalize_portfolio_backs_up_raw_score():
    opps = [
        {"id": "a", "final_score": 5.0, "kill_decision": False},
        {"id": "b", "final_score": 7.0, "kill_decision": False},
        {"id": "c", "final_score": 9.0, "kill_decision": False},
        {"id": "d", "final_score": 6.0, "kill_decision": False},
    ]
    result = normalize_portfolio_scores(opps)
    for opp in result:
        if not opp.get("kill_decision"):
            assert "raw_final_score" in opp


# ─── Venezuela +1.5 wedge bonus ───────────────────────────────────────────────

def test_venezuela_wedge_bonus_raises_final_score(base_opp):
    """Venezuela +1.5 regional_fit bonus must flow through Layer 3 and lift final_score."""
    opp_no_bonus = {**base_opp, "geography": "venezuela", "venezuela_wedge_match": False}
    opp_with_bonus = {**base_opp, "geography": "venezuela", "venezuela_wedge_match": True}

    result_no = score_opportunity(opp_no_bonus)
    result_yes = score_opportunity(opp_with_bonus)

    assert result_yes["final_score"] > result_no["final_score"], (
        "Venezuela wedge_match=True must produce a higher final_score than False"
    )


def test_venezuela_wedge_bonus_capped_at_10(base_opp):
    """regional_fit + 1.5 must not exceed 10.0."""
    opp = {**base_opp, "geography": "venezuela", "venezuela_wedge_match": True, "regional_fit": 9.5}
    result = score_opportunity(opp)
    assert result["final_score"] <= 10.0


def test_venezuela_wedge_bonus_not_applied_outside_venezuela(base_opp):
    """Bonus must not fire for non-Venezuela geographies even if flag is True."""
    opp_global = {**base_opp, "geography": "global", "venezuela_wedge_match": True}
    opp_ve = {**base_opp, "geography": "venezuela", "venezuela_wedge_match": True}

    result_global = score_opportunity(opp_global)
    result_ve = score_opportunity(opp_ve)

    assert result_ve["final_score"] > result_global["final_score"], (
        "Bonus should only apply to Venezuela, not global"
    )


# ─── pain_validation_score dimension ─────────────────────────────────────────

def test_pain_validation_score_raises_final_score(base_opp):
    low = score_opportunity({**base_opp, "pain_validation_score": 3.0})
    high = score_opportunity({**base_opp, "pain_validation_score": 9.0})
    assert high["final_score"] > low["final_score"]


def test_pain_validation_score_absent_unchanged(base_opp):
    without = score_opportunity(base_opp)
    with_none = score_opportunity({**base_opp, "pain_validation_score": None})
    assert without["final_score"] == with_none["final_score"]


# ─── distribution_quality dimension ──────────────────────────────────────────

def test_distribution_quality_validated_true_raises_score(base_opp):
    unresearched = score_opportunity(base_opp)
    researched = score_opportunity({**base_opp, "distribution_validated": True})
    assert researched["final_score"] >= unresearched["final_score"]


def test_distribution_quality_validated_false_lowers_score(base_opp):
    unresearched = score_opportunity(base_opp)
    poor = score_opportunity({**base_opp, "distribution_validated": False})
    assert poor["final_score"] <= unresearched["final_score"]


def test_distribution_validated_absent_unchanged(base_opp):
    without = score_opportunity(base_opp)
    with_none = score_opportunity({**base_opp, "distribution_validated": None})
    assert without["final_score"] == with_none["final_score"]


# ─── non_obviousness_high modifier ───────────────────────────────────────────

def test_non_obviousness_high_applies_bonus(base_opp):
    """non_obviousness_score >= 6 must add +0.5 to final_score."""
    below = score_opportunity({**base_opp, "non_obviousness_score": 5.0})
    above = score_opportunity({**base_opp, "non_obviousness_score": 7.0})
    assert above["final_score"] > below["final_score"]


def test_non_obviousness_below_threshold_no_bonus(base_opp):
    """non_obviousness_score < 6 must not change the score vs. field absent."""
    without_field = score_opportunity(base_opp)
    with_low = score_opportunity({**base_opp, "non_obviousness_score": 4.9})
    assert with_low["final_score"] == pytest.approx(without_field["final_score"])


def test_non_obviousness_absent_no_bonus(base_opp):
    """No non_obviousness_score field must not crash or add bonus."""
    result = score_opportunity(base_opp)
    assert "final_score" in result
    assert result["final_score"] <= 10.0
