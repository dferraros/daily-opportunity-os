"""Tests for validation_engine.py"""
import pytest
from opportunity_os.validation_engine import (
    run_validation,
    build_validation_queries,
    is_validation_complete,
    validation_status_label,
    AUTO_SECTION_COUNT,
    FULL_SECTION_COUNT,
)


# ─── Minimal valid opp fixture ───────────────────────────────────────────────

@pytest.fixture
def scout_opp():
    return {
        "id": "opp_test_001",
        "name": "USDT Accounting Tool",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.82,
        "geography": "venezuela",
        "vertical": "smb_software",
        "target_customer": "Venezuelan informal SMB operators",
        "problem_statement": "Manual USDT accounting in spreadsheets causes reconciliation errors",
        "trigger_signal": "Reddit: merchants complaining about manual tracking",
        "pain_severity": 8,
        "competition_intensity": 3,
        "executability_score": 7.5,
        "why_now": "USDT volume in VE up 340% YoY",
        "path_to_first_revenue": "Charge $29/mo for automated USDT reconciliation",
        "willingness_to_pay": 6,
        "speed_to_mvp": 7,
        "venezuela_wedge_category": "smb_software_informal_operators",
        "portfolio_lane": "now",
    }


@pytest.fixture
def scout_opp_minimal():
    """Opp with only required fields — tests graceful fallback."""
    return {
        "id": "opp_test_002",
        "name": "Minimal Test Opp",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.1,
        "geography": "global",
        "vertical": "fintech",
        "target_customer": "SMB owners",
        "problem_statement": "Manual processes waste time",
    }


# ─── run_validation — auto mode (sections 1-7) ───────────────────────────────

class TestRunValidationAuto:
    def test_returns_dict(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert isinstance(result, dict)

    def test_has_validation_markdown_key(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert "_validation_markdown" in result
        assert isinstance(result["_validation_markdown"], str)
        assert len(result["_validation_markdown"]) > 100

    def test_auto_has_correct_section_count(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        section_count = md.count("\n## ")
        assert section_count == AUTO_SECTION_COUNT  # 7

    def test_full_has_correct_section_count(self, scout_opp):
        result = run_validation(scout_opp, mode="full")
        md = result["_validation_markdown"]
        section_count = md.count("\n## ")
        assert section_count == FULL_SECTION_COUNT  # 8

    def test_opp_name_in_markdown(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert "USDT Accounting Tool" in result["_validation_markdown"]

    def test_interview_questions_exactly_five(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        # Each question starts with "Q1." "Q2." ... "Q5."
        for i in range(1, 6):
            assert f"Q{i}." in md
        assert "Q6." not in md

    def test_pricing_has_three_options(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        assert "Option A" in md
        assert "Option B" in md
        assert "Option C" in md

    def test_landing_page_has_headline(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        assert "Headline:" in md

    def test_minimal_opp_does_not_crash(self, scout_opp_minimal):
        result = run_validation(scout_opp_minimal, mode="auto")
        assert "_validation_markdown" in result
        assert len(result["_validation_markdown"]) > 50

    def test_schema_fields_returned(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        # These schema fields should be set by the engine
        assert result.get("validation_status") == "in_progress"
        assert result.get("stage") == "validation"
        assert "_opp_id" in result
        assert "_opp_name" in result


# ─── build_validation_queries ────────────────────────────────────────────────

class TestBuildValidationQueries:
    def test_returns_list_of_strings(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        assert isinstance(queries, list)
        assert all(isinstance(q, str) for q in queries)

    def test_returns_5_to_8_queries(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        assert 5 <= len(queries) <= 8

    def test_geography_influences_queries(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        # Venezuela opp should have Spanish-language queries
        combined = " ".join(queries).lower()
        assert any(term in combined for term in ["venezuela", "venezolano", "usdt", "smb"])


# ─── convenience helpers ─────────────────────────────────────────────────────

class TestHelpers:
    def test_is_validation_complete_false_when_in_progress(self):
        opp = {"validation_status": "in_progress"}
        assert is_validation_complete(opp) is False

    def test_is_validation_complete_true_when_passed(self):
        opp = {"validation_status": "passed"}
        assert is_validation_complete(opp) is True

    def test_validation_status_label_returns_string(self):
        assert isinstance(validation_status_label("in_progress"), str)
        assert isinstance(validation_status_label(None), str)
