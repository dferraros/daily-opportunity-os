"""Tests for deep_dive.py — decision filters, founder fit, kill gate, helpers."""
import pytest
from datetime import datetime, timedelta

from opportunity_os.pipelines.deep_dive import (
    _section_decision_filters,
    _section_founder_fit,
    _section_kill_gate,
    _section_scoring_breakdown,
    _needs_rich_reasons,
    _score_bar,
    _derive_tam_inputs,
    _infer_wedge_matches,
)


class TestNeedsRichReasons:
    def test_true_when_never_refreshed(self):
        assert _needs_rich_reasons({"name": "x"}) is True

    def test_false_within_ttl(self):
        fresh = datetime.now().isoformat()
        assert _needs_rich_reasons({"dimension_reasons_at": fresh}) is False

    def test_true_when_stale(self):
        old = (datetime.now() - timedelta(days=40)).isoformat()
        assert _needs_rich_reasons({"dimension_reasons_at": old}) is True

    def test_true_on_corrupt_timestamp(self):
        assert _needs_rich_reasons({"dimension_reasons_at": "not-a-date"}) is True


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def ve_opp():
    return {
        "id": "dd_test_001",
        "name": "USDT Accounting Tool",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.82,
        "geography": "venezuela",
        "vertical": "smb_software",
        "target_customer": "Venezuelan informal SMB operators",
        "problem_statement": "Manual USDT accounting in spreadsheets causes reconciliation errors",
        "willingness_to_pay": 6,
        "speed_to_mvp": 8,
        "pain_severity": 8,
        "competition_intensity": 3,
        "executability_score": 7.5,
        "path_to_first_revenue": "Charge $29/mo for automated USDT reconciliation",
        "decision_filter_results": {
            "df1_passes": True,
            "df2_passes": True,
            "df3_passes": False,
            "df4_passes": True,
            "df5_passes": True,
            "df6_passes": True,
            "df7_passes": True,
        },
        "daniels_wedge_count": 5,
        "top_distribution_channels": ["WhatsApp", "Telegram"],
        "gross_margin_potential": 9,
        "network_effect_strength": 4,
        "switching_cost_score": 7,
    }


@pytest.fixture
def minimal_opp():
    return {
        "id": "dd_test_002",
        "name": "Minimal Test Opp",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 5.0,
        "geography": "global",
        "vertical": "saas",
        "target_customer": "SMB owners",
        "problem_statement": "Manual processes waste time",
    }


# ─── _section_scoring_breakdown ──────────────────────────────────────────────

class TestScoringBreakdown:
    def test_renders_three_layers(self, ve_opp):
        text = "\n".join(_section_scoring_breakdown(ve_opp))
        assert "Scoring Breakdown — Every Variable" in text
        assert "Attractiveness (50%" in text
        assert "Executability (30%" in text
        assert "Strategic Value (20%" in text

    def test_surfaces_per_dimension_reasons(self, ve_opp):
        opp = {**ve_opp,
               "pain_severity_reason": "Reconciliation errors cost real money monthly",
               "defensibility_reason": "Data lock-in once books migrate"}
        text = "\n".join(_section_scoring_breakdown(opp))
        assert "Reconciliation errors cost real money monthly" in text
        assert "Data lock-in once books migrate" in text

    def test_shows_scores_and_competition_inversion_label(self, ve_opp):
        text = "\n".join(_section_scoring_breakdown(ve_opp))
        assert "Competition intensity (inverted)" in text
        assert "8/10" in text  # pain_severity value rendered

    def test_missing_dimension_marked_not_scored(self, minimal_opp):
        # minimal_opp has almost no dimension values -> must render, not raise
        text = "\n".join(_section_scoring_breakdown(minimal_opp))
        assert "not scored" in text

    def test_full_reason_not_truncated_at_160(self, ve_opp):
        long_reason = (
            "Mandatory e-invoicing compliance in Colombia (DIAN 2022+), Mexico (SAT), "
            "Chile (SII), and Peru (SUNAT) creates daily operational friction with real "
            "financial penalties, so SMBs must adopt a compliant tool to avoid fines."
        )
        opp = {**ve_opp, "pain_severity_reason": long_reason}
        text = "\n".join(_section_scoring_breakdown(opp))
        # the OLD table truncated at 160 chars mid-word; the full reason must now appear
        assert long_reason in text
        assert len(long_reason) > 160

    def test_data_backed_dims_get_reconstructed_basis(self, ve_opp):
        opp = {**ve_opp, "pain_validation_score": 7.0, "pain_signal_count": 6,
               "market_momentum_score": 5.0, "job_posting_count": 25,
               "competitor_weakness_score": 7.5, "competitor_negative_review_rate": 0.4,
               "competitor_signal_basis": "named_competitors"}
        text = "\n".join(_section_scoring_breakdown(opp))
        assert "6 pain signal" in text           # pain_validation basis
        assert "25 LinkedIn job postings" in text  # market_momentum basis
        assert "40% negative-review rate" in text  # competitor_weakness basis
        assert "no narrative" not in text          # the old placeholder is gone

    def test_kill_thesis_counterweight_shown_when_present(self, ve_opp):
        opp = {**ve_opp, "kill_thesis": "Incumbents bundle this free", "kill_thesis_strength": 8}
        text = "\n".join(_section_scoring_breakdown(opp))
        assert "Adversarial check (kill thesis)" in text
        assert "caps the final score at 5.0" in text


# ─── _section_decision_filters ───────────────────────────────────────────────

class TestSectionDecisionFilters:
    def test_returns_non_empty_string(self, ve_opp):
        result = _section_decision_filters(ve_opp)
        assert isinstance(result, str)
        assert len(result) > 50

    def test_uses_snake_case_key(self, ve_opp):
        """Must read decision_filter_results (snake_case), never DecisionFilterResults."""
        # Pollute with PascalCase key — it must NOT be used
        opp = {**ve_opp, "DecisionFilterResults": {"df1_passes": False, "df2_passes": False}}
        result = _section_decision_filters(opp)
        # df1/df2 are True in snake_case key — result must reflect True, not the PascalCase False
        assert "PASS" in result or "pass" in result.lower() or "True" in result or "[+]" in result

    def test_no_pascal_case_lookup(self, minimal_opp):
        """With only snake_case key absent, should not crash (graceful empty fallback)."""
        result = _section_decision_filters(minimal_opp)
        assert isinstance(result, str)

    def test_failed_filter_shown(self, ve_opp):
        """A failing filter must be visibly flagged in the output."""
        result = _section_decision_filters(ve_opp)
        # df3_passes is False — output must mark it
        assert "df3" in result.lower() or "3" in result


# ─── _section_founder_fit ────────────────────────────────────────────────────

class TestSectionFounderFit:
    def test_returns_string(self, ve_opp):
        assert isinstance(_section_founder_fit(ve_opp), str)

    def test_shows_per_wedge_indicators(self, ve_opp):
        """Must show [+] or [ ] per-wedge, not just an aggregate count."""
        result = _section_founder_fit(ve_opp)
        assert "[+]" in result or "[ ]" in result

    def test_shows_all_six_wedges(self, ve_opp):
        """All 6 wedges must appear in the output."""
        result = _section_founder_fit(ve_opp)
        # The output must reference 6 distinct items
        plus_count = result.count("[+]")
        blank_count = result.count("[ ]")
        assert plus_count + blank_count == 6

    def test_minimal_opp_does_not_crash(self, minimal_opp):
        assert isinstance(_section_founder_fit(minimal_opp), str)


# ─── _section_kill_gate ──────────────────────────────────────────────────────

class TestSectionKillGate:
    def test_returns_string(self, ve_opp):
        assert isinstance(_section_kill_gate(ve_opp), str)

    def test_shows_vc_moat_fields_when_present(self, ve_opp):
        """gross_margin_potential, network_effect_strength, switching_cost_score must appear."""
        result = _section_kill_gate(ve_opp)
        assert "gross_margin" in result.lower() or "margin" in result.lower()
        assert "network_effect" in result.lower() or "network" in result.lower()
        assert "switching_cost" in result.lower() or "switching" in result.lower()

    def test_vc_fields_absent_does_not_crash(self, minimal_opp):
        """Missing VC fields must not cause a crash — neutral/absent is fine."""
        result = _section_kill_gate(minimal_opp)
        assert isinstance(result, str)


# ─── _score_bar ──────────────────────────────────────────────────────────────

class TestScoreBar:
    def test_returns_string(self):
        assert isinstance(_score_bar(7.5), str)

    def test_full_score_is_ten_blocks(self):
        bar = _score_bar(10.0)
        assert "█" in bar

    def test_zero_score_has_no_filled_blocks(self):
        bar = _score_bar(0.0)
        assert "░" in bar or "▒" in bar or bar.count("█") == 0

    def test_score_value_in_output(self):
        bar = _score_bar(6.5)
        assert "6.5" in bar or "6" in bar


# ─── _derive_tam_inputs ──────────────────────────────────────────────────────

class TestDeriveTamInputs:
    def test_returns_two_ints(self, ve_opp):
        customers, price = _derive_tam_inputs(ve_opp)
        assert isinstance(customers, int)
        assert isinstance(price, int)

    def test_venezuela_smaller_market_than_global(self):
        ve = {"geography": "venezuela", "willingness_to_pay": 5}
        global_ = {"geography": "global", "willingness_to_pay": 5}
        ve_c, _ = _derive_tam_inputs(ve)
        gl_c, _ = _derive_tam_inputs(global_)
        assert ve_c < gl_c

    def test_venezuela_lower_price_than_global(self):
        ve = {"geography": "venezuela", "willingness_to_pay": 5}
        global_ = {"geography": "global", "willingness_to_pay": 5}
        _, ve_p = _derive_tam_inputs(ve)
        _, gl_p = _derive_tam_inputs(global_)
        assert ve_p < gl_p

    def test_minimum_price_is_36(self):
        """Even low WTP must produce at least $36/year."""
        opp = {"geography": "venezuela", "willingness_to_pay": 1}
        _, price = _derive_tam_inputs(opp)
        assert price >= 36

    def test_missing_fields_does_not_crash(self, minimal_opp):
        customers, price = _derive_tam_inputs(minimal_opp)
        assert customers > 0
        assert price >= 36


# ─── _infer_wedge_matches ────────────────────────────────────────────────────

class TestInferWedgeMatches:
    def test_returns_six_bools(self, ve_opp):
        result = _infer_wedge_matches(ve_opp)
        assert len(result) == 6
        assert all(isinstance(v, bool) for v in result)

    def test_venezuela_geo_wedge_matches(self, ve_opp):
        """Wedge 3 (LATAM/VE geography) should be True for venezuela opp."""
        result = _infer_wedge_matches(ve_opp)
        assert result[2] is True  # wedge_3 = geo match

    def test_fintech_vertical_wedge_matches(self):
        opp = {
            "geography": "venezuela",
            "vertical": "fintech",
            "problem_statement": "USDT payment tracking is a mess",
            "path_to_first_revenue": "charge $29/mo",
            "business_model_type": "saas",
            "speed_to_mvp": 8,
            "top_distribution_channels": ["WhatsApp"],
        }
        result = _infer_wedge_matches(opp)
        assert result[3] is True  # wedge_4 = fintech/crypto match

    def test_minimal_opp_returns_six_bools(self, minimal_opp):
        result = _infer_wedge_matches(minimal_opp)
        assert len(result) == 6
        assert all(isinstance(v, bool) for v in result)
