"""P1 wiring tests: decision filters fire, scores carry sources, wedge survives normalization.

These pin the 2026-07-22 reconnection work: capabilities that existed in code
but were never invoked by the pipeline (decision filters, confidence tagging)
plus a regression guard on the Venezuela wedge bonus surviving portfolio
normalization ordering.
"""

from opportunity_os.engines.scoring_engine import (
    evaluate_decision_filters,
    normalize_portfolio_scores,
    score_opportunity,
)
from opportunity_os.pipelines.daily_run import _enrich_fields


def _base_opp(**overrides) -> dict:
    opp = {
        "id": "opp_test_p1",
        "name": "Test Opp",
        "geography": "latam",
        "kill_criteria_passed": 7,
        "pain_severity": 8,
        "market_size": 8,
        "timing_tailwind": 8,
        "willingness_to_pay": 8,
        "monetization_clarity": 8,
        "speed_to_mvp": 8,
        "capital_efficiency": 8,
        "distribution_accessibility": 8,
        "competition_intensity": 3,
        "defensibility": 7,
        "regional_fit": 7,
        "founder_fit": 7,
    }
    return {**opp, **overrides}


# ── evaluate_decision_filters ────────────────────────────────────────────────

class TestDecisionFilters:
    def test_all_pass(self):
        result = evaluate_decision_filters({
            "distribution_validated": True,
            "capital_efficiency": 7,
            "benchmark_archetype": "local_clone",
        })
        assert result["can_sell_fast"] is True
        assert result["can_build_lean"] is True
        assert result["can_compound"] is True
        assert result["failures"] == 0
        assert result["should_cap_score"] is False

    def test_two_failures_flag_cap(self):
        result = evaluate_decision_filters({
            "distribution_validated": False,
            "capital_efficiency": 2,
        })
        assert result["failures"] == 2
        assert result["should_cap_score"] is True

    def test_unknowns_are_not_failures(self):
        result = evaluate_decision_filters({})
        assert result["can_sell_fast"] is None
        assert result["can_build_lean"] is None
        assert result["can_compound"] is None
        assert result["failures"] == 0
        assert result["should_cap_score"] is False

    def test_distribution_accessibility_fallback(self):
        assert evaluate_decision_filters(
            {"distribution_accessibility": 8})["can_sell_fast"] is True
        assert evaluate_decision_filters(
            {"distribution_accessibility": 2})["can_sell_fast"] is False
        assert evaluate_decision_filters(
            {"distribution_accessibility": 5})["can_sell_fast"] is None

    def test_moat_dimensions_back_up_archetype(self):
        result = evaluate_decision_filters({
            "benchmark_archetype": "one_off_service",
            "network_effect_strength": 8,
            "switching_cost_score": 2,
        })
        assert result["can_compound"] is True

    def test_known_archetype_with_weak_moats_fails_compound(self):
        result = evaluate_decision_filters({
            "benchmark_archetype": "one_off_service",
            "network_effect_strength": 2,
            "switching_cost_score": 2,
        })
        assert result["can_compound"] is False


class TestDecisionFilterCapWired:
    def test_two_failed_filters_cap_final_score(self):
        opp = _base_opp(distribution_validated=False, capital_efficiency=2)
        scored = score_opportunity(opp)
        assert scored["decision_filter_results"]["failures"] >= 2
        assert scored["final_score"] <= 5.0

    def test_passing_filters_do_not_cap(self):
        opp = _base_opp(distribution_validated=True, benchmark_archetype="local_clone")
        scored = score_opportunity(opp)
        assert scored["decision_filter_results"]["should_cap_score"] is False
        assert scored["final_score"] > 5.0

    def test_filters_recomputed_each_pass(self):
        opp = _base_opp(distribution_validated=False, capital_efficiency=2)
        first = score_opportunity(opp)
        assert first["decision_filter_results"]["source"] == "inferred"
        healed = score_opportunity({
            **first, "distribution_validated": True, "capital_efficiency": 8,
        })
        assert healed["decision_filter_results"]["failures"] == 0
        assert healed["final_score"] > 5.0

    def test_manual_filter_verdicts_survive_rescoring(self):
        # A human False (e.g. from a validation review) must not be healed away
        # by optimistic evidence fields on the next pass.
        opp = _base_opp(
            distribution_validated=True,
            decision_filter_results={
                "can_sell_fast": False,
                "can_build_lean": False,
                "can_compound": True,
                "source": "manual",
            },
        )
        scored = score_opportunity(opp)
        assert scored["decision_filter_results"]["can_sell_fast"] is False
        assert scored["decision_filter_results"]["failures"] == 2
        assert scored["final_score"] <= 5.0


# ── score_sources confidence tagging ─────────────────────────────────────────

class TestScoreSources:
    def test_heuristic_default_without_ai_stamp(self):
        scored = score_opportunity(_base_opp())
        assert scored["score_sources"]["pain_severity"] == "heuristic"

    def test_ai_stamp_tags_ai(self):
        scored = score_opportunity(_base_opp(ai_scored_at="2026-07-22"))
        assert scored["score_sources"]["pain_severity"] == "ai"

    def test_data_backed_dimensions_tag_data(self):
        scored = score_opportunity(_base_opp(
            job_posting_count=25,
            distribution_validated=True,
        ))
        assert scored["score_sources"]["market_momentum_score"] == "data"
        assert scored["score_sources"]["distribution_quality"] == "data"

    def test_researched_pain_tags_data_fallback_tags_heuristic(self):
        researched = score_opportunity(_base_opp(pain_validation_score=8.0))
        assert researched["score_sources"]["pain_validation_score"] == "data"

        fallback = score_opportunity(_base_opp(pain_signal_count=5))
        assert fallback["score_sources"]["pain_validation_score"] == "heuristic"

    def test_every_present_dimension_has_a_source(self):
        scored = score_opportunity(_base_opp(ai_scored_at="2026-07-22"))
        for field, source in scored["score_sources"].items():
            assert source in ("data", "ai", "heuristic"), field
        assert "pain_severity" in scored["score_sources"]


# ── Venezuela wedge bonus survives normalization ordering ────────────────────

class TestWedgeNormalizationOrdering:
    def test_wedge_twin_outranks_after_normalization(self):
        plain = _base_opp(id="opp_plain")
        wedge = _base_opp(
            id="opp_wedge",
            geography="venezuela",
            venezuela_wedge_match=True,
        )
        filler = _base_opp(id="opp_filler", pain_severity=3, market_size=3)

        scored = [score_opportunity(o) for o in (plain, wedge, filler)]
        assert scored[1]["raw_final_score"] > scored[0]["raw_final_score"]

        normalized = normalize_portfolio_scores(scored)
        by_id = {o["id"]: o for o in normalized}
        assert by_id["opp_wedge"]["final_score"] > by_id["opp_plain"]["final_score"]


class TestCapsSurviveNormalization:
    def test_capped_score_stays_capped_after_normalization(self):
        # A capped raw 5.0 sitting among high scorers must not be remapped
        # above 5.0 by the portfolio spread.
        capped = score_opportunity(_base_opp(
            id="opp_capped",
            decision_filter_results={
                "can_sell_fast": False, "can_build_lean": False,
                "can_compound": True, "source": "manual",
            },
        ))
        assert capped["final_score"] <= 5.0
        high = score_opportunity(_base_opp(id="opp_high", pain_severity=9, market_size=9))
        low = score_opportunity(_base_opp(id="opp_low", pain_severity=3, market_size=3))

        normalized = normalize_portfolio_scores([capped, high, low])
        by_id = {o["id"]: o for o in normalized}
        assert by_id["opp_capped"]["final_score"] <= 5.0
        assert by_id["opp_high"]["final_score"] > 5.0


# ── Pain-statement schema flag ───────────────────────────────────────────────

class TestPainStatementSchema:
    def test_structured_english_statement_flagged(self):
        opp = _enrich_fields({
            "geography": "venezuela",
            "problem_statement": (
                "A distributor loses cash visibility because payment rails do not "
                "share one reference, and staff currently reconcile in spreadsheets."
            ),
        })
        assert opp["pain_statement_structured"] is True

    def test_structured_spanish_statement_flagged(self):
        opp = _enrich_fields({
            "geography": "venezuela",
            "problem_statement": (
                "Un distribuidor pierde visibilidad de caja porque los rieles de pago "
                "no comparten referencia, y el personal lo resuelve actualmente en Excel."
            ),
        })
        assert opp["pain_statement_structured"] is True

    def test_vague_statement_not_flagged(self):
        opp = _enrich_fields({
            "geography": "latam",
            "problem_statement": "SMBs lack digitalization and have bad UX.",
        })
        assert opp["pain_statement_structured"] is False
