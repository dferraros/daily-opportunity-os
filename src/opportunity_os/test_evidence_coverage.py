"""
Tests for evidence_coverage + low_evidence_flag (rubric CAL-06 / CAL-07).

Coverage = weight-fraction of the composite resting on data-backed fields.
The flag marks high conviction built on guesses: final >= 7.5 with coverage < 0.20.
"""
from opportunity_os.engines.scoring_engine import (
    HIGH_SCORE_EVIDENCE_BAR,
    MIN_EVIDENCE_COVERAGE,
    compute_evidence_coverage,
    score_opportunity,
)


def high_score_guess_only_opp():
    """All AI-inferred dims at 9, zero data-backed fields -> high score, coverage 0."""
    return {
        "name": "Guess Built",
        "kill_criteria_passed": True,
        "kill_decision": False,
        "market_size": 9, "timing_tailwind": 9, "pain_severity": 9,
        "willingness_to_pay": 9, "monetization_clarity": 9,
        "speed_to_mvp": 9, "capital_efficiency": 9, "distribution_accessibility": 9,
        "competition_intensity": 1, "defensibility": 9, "regional_fit": 9,
        "founder_fit": 9, "ai_leverage": 9, "operational_simplicity": 9,
        "regulatory_simplicity": 9, "revenue_speed_score": 9,
        "gross_margin_potential": 9, "network_effect_strength": 9,
        "switching_cost_score": 9,
    }


class TestComputeEvidenceCoverage:
    def test_half_of_collectable_evidence_collected(self):
        weights = {"weights": {
            "pain_severity": 0.30,           # AI-inferred -- not collectable evidence
            "pain_validation_score": 0.10,   # data-backed, present
            "market_momentum_score": 0.10,   # data-backed, absent
        }}
        opp = {"pain_severity": 8, "pain_validation_score": 7}
        assert compute_evidence_coverage(opp, weights) == 0.5  # 0.10 / 0.20

    def test_all_collectable_evidence_collected(self):
        weights = {"weights": {
            "pain_severity": 0.30,
            "pain_validation_score": 0.10,
            "market_momentum_score": 0.10,
        }}
        opp = {"pain_validation_score": 7, "market_momentum_score": 6}
        assert compute_evidence_coverage(opp, weights) == 1.0

    def test_zero_when_no_data_backed_fields_present(self):
        weights = {"weights": {"pain_severity": 0.5, "pain_validation_score": 0.5}}
        assert compute_evidence_coverage({"pain_severity": 8}, weights) == 0.0

    def test_zero_when_no_evidence_is_collectable(self):
        # Weight map with no data-backed fields at all: nothing to collect
        assert compute_evidence_coverage(
            {"pain_validation_score": 7}, {"weights": {"pain_severity": 0.5}}
        ) == 0.0


class TestScoringStampsCoverage:
    def test_every_scored_opp_gets_coverage(self):
        result = score_opportunity(high_score_guess_only_opp())
        assert "evidence_coverage" in result
        assert 0.0 <= result["evidence_coverage"] <= 1.0

    def test_guess_only_high_scorer_flagged(self):
        result = score_opportunity(high_score_guess_only_opp())
        assert result["final_score"] >= HIGH_SCORE_EVIDENCE_BAR
        assert result["evidence_coverage"] == 0.0
        assert result["low_evidence_flag"] is True

    def test_evidence_backed_high_scorer_not_flagged(self):
        opp = {
            **high_score_guess_only_opp(),
            "pain_validation_score": 9.0,
            "job_posting_count": 50,                  # -> market_momentum_score 10
            "competitor_negative_review_rate": 0.4,   # -> competitor_weakness_score 7.5
            "distribution_validated": True,           # -> distribution_quality 8.0
        }
        result = score_opportunity(opp)
        assert result["final_score"] >= HIGH_SCORE_EVIDENCE_BAR
        assert result["evidence_coverage"] >= MIN_EVIDENCE_COVERAGE
        assert "low_evidence_flag" not in result

    def test_low_scorer_never_flagged(self):
        opp = {**high_score_guess_only_opp()}
        low = {k: (3 if isinstance(v, int) else v) for k, v in opp.items()}
        low["competition_intensity"] = 9  # inverted: high competition -> low score
        result = score_opportunity(low)
        assert result["final_score"] < HIGH_SCORE_EVIDENCE_BAR
        assert "low_evidence_flag" not in result

    def test_unscored_record_never_flagged(self):
        result = score_opportunity({"name": "Empty", "kill_decision": False,
                                    "kill_criteria_passed": True})
        assert result.get("scoring_incomplete") is True
        assert "low_evidence_flag" not in result

    def test_rescoring_is_idempotent_for_coverage_and_flag(self):
        first = score_opportunity(high_score_guess_only_opp())
        second = score_opportunity(first)
        assert second["evidence_coverage"] == first["evidence_coverage"]
        assert second["final_score"] == first["final_score"]
        assert second.get("low_evidence_flag") == first.get("low_evidence_flag")

    def test_flag_cleared_when_evidence_arrives(self):
        flagged = score_opportunity(high_score_guess_only_opp())
        assert flagged["low_evidence_flag"] is True
        enriched = {
            **flagged,
            "pain_validation_score": 9.0,
            "job_posting_count": 50,
            "competitor_negative_review_rate": 0.4,
            "distribution_validated": True,
        }
        result = score_opportunity(enriched)
        assert "low_evidence_flag" not in result

    def test_input_not_mutated(self):
        opp = high_score_guess_only_opp()
        snapshot = dict(opp)
        score_opportunity(opp)
        assert opp == snapshot


class TestResearchQueuePriority:
    """The evidence loop's reinvestment step: flagged opps jump the research queue."""

    def test_flagged_opp_outranks_higher_scored_unflagged(self):
        from opportunity_os.free_research import sort_research_candidates
        opps = [
            {"id": "a", "final_score": 9.0},
            {"id": "b", "final_score": 7.6, "low_evidence_flag": True},
            {"id": "c", "final_score": 8.2},
        ]
        ordered = sort_research_candidates(opps)
        assert [o["id"] for o in ordered] == ["b", "a", "c"]

    def test_score_order_within_groups(self):
        from opportunity_os.free_research import sort_research_candidates
        opps = [
            {"id": "low_flag", "final_score": 7.5, "low_evidence_flag": True},
            {"id": "high_flag", "final_score": 8.1, "low_evidence_flag": True},
            {"id": "plain", "final_score": 9.9},
        ]
        ordered = sort_research_candidates(opps)
        assert [o["id"] for o in ordered] == ["high_flag", "low_flag", "plain"]

    def test_missing_score_treated_as_zero_and_input_unmutated(self):
        from opportunity_os.free_research import sort_research_candidates
        opps = [{"id": "noscore"}, {"id": "scored", "final_score": 1.0}]
        snapshot = [dict(o) for o in opps]
        ordered = sort_research_candidates(opps)
        assert [o["id"] for o in ordered] == ["scored", "noscore"]
        assert opps == snapshot
