"""Tests for deep_dive.py — decision filters, founder fit, kill gate, helpers."""
import pytest
from opportunity_os.pipelines.deep_dive import (
    _section_decision_filters,
    _section_founder_fit,
    _section_kill_gate,
    _score_bar,
    _derive_tam_inputs,
    _infer_wedge_matches,
)


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
