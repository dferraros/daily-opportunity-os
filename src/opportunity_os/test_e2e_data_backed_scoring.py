"""
End-to-end smoke tests for data-backed scoring upgrade.

Verifies the full signal -> normalization -> layer scoring -> final_score path
for all new data-backed fields introduced in the P0-P5 upgrade.
"""
import pytest
from opportunity_os.engines.scoring_engine import (
    score_opportunity,
    _normalize_data_backed_scores,
    JOB_POSTING_COUNT_MAX,
    NEG_REVIEW_RATE_MAX,
    NEG_REVIEW_RATE_NEUTRAL_SCORE,
)


_BASE_OPP = {
    "name": "E2E Test Opp",
    "vertical": "fintech",
    "geography": "global",
    "kill_criteria_passed": True,
    "kill_decision": False,
    "market_size": 7,
    "timing_tailwind": 6,
    "pain_severity": 8,
    "willingness_to_pay": 7,
    "monetization_clarity": 7,
    "speed_to_mvp": 8,
    "capital_efficiency": 7,
    "distribution_accessibility": 7,
    "competition_intensity": 4,
    "defensibility": 6,
    "regional_fit": 7,
    "founder_fit": 7,
    "ai_leverage": 7,
    "operational_simplicity": 7,
    "regulatory_simplicity": 6,
    "revenue_speed_score": 7,
    "gross_margin_potential": 8,
    "network_effect_strength": 5,
    "switching_cost_score": 6,
}


class TestJobPostingNormalization:
    def test_max_jobs_gives_10(self):
        result = _normalize_data_backed_scores({"job_posting_count": JOB_POSTING_COUNT_MAX})
        assert result["market_momentum_score"] == 10.0

    def test_zero_jobs_treated_as_no_signal(self):
        # Changed 2026-06-10: fetch_linkedin_jobs returns 0 on failure, so 0
        # is indistinguishable from an Apify outage -- treated as no-signal,
        # never scored as zero momentum.
        result = _normalize_data_backed_scores({"job_posting_count": 0})
        assert "market_momentum_score" not in result

    def test_half_max_jobs_gives_5(self):
        result = _normalize_data_backed_scores({"job_posting_count": JOB_POSTING_COUNT_MAX // 2})
        assert result["market_momentum_score"] == 5.0

    def test_over_max_capped_at_10(self):
        result = _normalize_data_backed_scores({"job_posting_count": 999})
        assert result["market_momentum_score"] == 10.0

    def test_none_produces_no_key(self):
        result = _normalize_data_backed_scores({"job_posting_count": None})
        assert "market_momentum_score" not in result


class TestNegReviewNormalization:
    def test_zero_neg_rate_gives_neutral(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": 0.0})
        assert result["competitor_weakness_score"] == NEG_REVIEW_RATE_NEUTRAL_SCORE

    def test_max_neg_rate_gives_10(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": NEG_REVIEW_RATE_MAX})
        assert result["competitor_weakness_score"] == 10.0

    def test_half_max_gives_7_5(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": 0.4})
        assert result["competitor_weakness_score"] == 7.5

    def test_over_max_capped_at_10(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": 1.0})
        assert result["competitor_weakness_score"] == 10.0

    def test_negative_rate_clamped_to_neutral(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": -0.5})
        assert result["competitor_weakness_score"] == NEG_REVIEW_RATE_NEUTRAL_SCORE

    def test_none_produces_no_key(self):
        result = _normalize_data_backed_scores({"competitor_negative_review_rate": None})
        assert "competitor_weakness_score" not in result


class TestFullScoreOppWithDataBackedFields:
    def test_scores_with_all_new_fields_populated(self):
        opp = {
            **_BASE_OPP,
            "job_posting_count": 50,
            "competitor_negative_review_rate": 0.4,
            "pain_signal_count": 5,
        }
        result = score_opportunity(opp)
        assert result["market_momentum_score"] == 10.0
        assert result["competitor_weakness_score"] == 7.5
        assert result["pain_validation_score"] == 5.5
        assert result["final_score"] is not None
        assert 0.0 <= result["final_score"] <= 10.0

    def test_scores_without_new_fields_unchanged_structure(self):
        result = score_opportunity(_BASE_OPP)
        for field in ("attractiveness_score", "executability_score", "strategic_value_score", "final_score"):
            assert field in result, f"Missing expected field: {field}"
        assert 0.0 <= result["final_score"] <= 10.0

    def test_new_fields_absent_do_not_penalise(self):
        # Opp with no data-backed fields should score the same as the base
        base_result = score_opportunity(_BASE_OPP)
        # Adding None explicitly should produce identical result
        opp_with_nones = {
            **_BASE_OPP,
            "job_posting_count": None,
            "competitor_negative_review_rate": None,
        }
        result_with_nones = score_opportunity(opp_with_nones)
        assert base_result["final_score"] == result_with_nones["final_score"]

    def test_data_backed_fields_improve_score(self):
        base_result = score_opportunity(_BASE_OPP)
        enriched = {
            **_BASE_OPP,
            "job_posting_count": 40,
            "competitor_negative_review_rate": 0.6,
        }
        enriched_result = score_opportunity(enriched)
        # Strong signals should produce higher strategic layer (market momentum + competitor weakness both > neutral)
        assert enriched_result["strategic_value_score"] > base_result["strategic_value_score"]

    def test_kill_decision_produces_zero(self):
        opp = {**_BASE_OPP, "kill_decision": True, "job_posting_count": 50}
        result = score_opportunity(opp)
        assert result["final_score"] == 0.0

    def test_original_opp_dict_not_mutated(self):
        original = dict(_BASE_OPP)
        original["job_posting_count"] = 30
        score_opportunity(original)
        assert original == dict(_BASE_OPP) | {"job_posting_count": 30}
