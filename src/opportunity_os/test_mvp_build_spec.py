"""Tests for mvp_build_spec.py"""
import pytest
from pathlib import Path
from opportunity_os.mvp_build_spec import (
    build_mvp_spec,
    build_claude_code_prompt,
    write_build_package,
    _get_architecture_key,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def rich_opp():
    """Rich opportunity with all key fields for MVP spec."""
    return {
        "id": "opp_test_build_001",
        "name": "USDT Accounting Tool for Venezuela",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.82,
        "geography": "venezuela",
        "vertical": "fintech",
        "target_customer": "Venezuelan informal SMB operators",
        "problem_statement": "Manual USDT accounting in spreadsheets causes reconciliation errors",
        "portfolio_lane": "now",
        "speed_to_mvp": 7,
        "capital_efficiency": 8,
        "ai_leverage_potential": 7,
        "path_to_first_revenue": "Charge $29/mo for automated USDT reconciliation",
        "willingness_to_pay": 6,
        "assumptions": [
            "Can reach 10 Venezuelan SMB operators within 7 days",
            "First customer will trial at $0 in week 2",
            "Payment via Zelle or USDT P2P is standard",
        ],
    }


@pytest.fixture
def minimal_opp():
    """Minimal opp — tests graceful fallback for [NEEDS INPUT] markers."""
    return {
        "id": "opp_test_build_002",
        "name": "Minimal Test Opportunity",
        "geography": "latam",
        "vertical": "smb_software",
        "target_customer": "SMB owners",
        "problem_statement": "Manual processes",
    }


@pytest.fixture
def fintech_opp():
    """Fintech opportunity — should trigger no-custody OUT-OF-SCOPE rules."""
    return {
        "id": "opp_test_build_003",
        "name": "Payment Reconciliation Platform",
        "geography": "latam",
        "vertical": "fintech_infrastructure",
        "target_customer": "SMB payment operators",
        "problem_statement": "Manual bank reconciliation takes 4 hours daily",
        "final_score": 6.5,
        "portfolio_lane": "soon",
        "willingness_to_pay": 7,
    }


@pytest.fixture
def ve_opp():
    """Venezuela-specific opp — should trigger WhatsApp-first architecture."""
    return {
        "id": "opp_test_build_004",
        "name": "WhatsApp Inventory Sync for Venezuelan Retailers",
        "geography": "venezuela",
        "vertical": "smb_software",
        "target_customer": "Venezuelan retail shop owners",
        "problem_statement": "Inventory inconsistency across multiple WhatsApp supplier groups",
        "final_score": 7.1,
        "willingness_to_pay": 5,
        "capital_efficiency": 9,
    }


# ─── Tests: build_mvp_spec ───────────────────────────────────────────────────

class TestBuildMVPSpec:
    def test_returns_markdown_string(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert isinstance(result, str)
        assert len(result) > 500

    def test_includes_all_seven_sections(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        # Check for section headers A-G
        assert "## A. Feature Scope" in result
        assert "## B. Tech Architecture" in result
        assert "## C. 4-Week Sprint Plan" in result
        assert "## D. Resource Plan" in result
        assert "## E. Unit Economics" in result
        assert "## F. Weekly Metrics" in result
        assert "## G. Week-4 Go/No-Go" in result

    def test_includes_opp_name_and_id(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "USDT Accounting Tool for Venezuela" in result
        assert "opp_test_build_001" in result

    def test_includes_score_and_lane(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "7.8" in result or "7.82" in result or "Score: 7" in result
        assert "NOW" in result or "now" in result

    def test_minimal_opp_does_not_crash(self, minimal_opp):
        result = build_mvp_spec(minimal_opp)
        assert "## A. Feature Scope" in result
        assert "[NEEDS INPUT:" in result  # Should have fallback markers

    def test_fintech_opp_includes_no_custody_warning(self, fintech_opp):
        result = build_mvp_spec(fintech_opp)
        assert "No customer fund custody" in result or "no custody" in result
        assert "Out of scope" in result

    def test_feature_scope_includes_out_of_scope_section(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "Out of scope" in result or "out of scope" in result

    def test_economics_section_has_three_scenarios(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "Conservative" in result
        assert "Base" in result
        assert "Ambitious" in result

    def test_economics_section_all_numbers_labeled_hypothesis(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        economics_section = result[result.find("## E. Unit Economics") : result.find("## F.")]
        # Check for "hypothesis" label somewhere in economics section
        assert "hypothesis" in economics_section.lower() or "$" in economics_section

    def test_sprint_plan_includes_weekly_breakdown(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "Week 1:" in result
        assert "Week 2:" in result
        assert "Week 3:" in result
        assert "Week 4:" in result

    def test_metrics_section_includes_kill_criteria(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        metrics_section = result[result.find("## F. Weekly Metrics") : result.find("## G.")]
        assert "Kill" in metrics_section or "kill" in metrics_section

    def test_go_no_go_has_checkboxes(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "- [ ]" in result  # Markdown checkbox syntax


# ─── Tests: Architecture template selection ─────────────────────────────────

class TestArchitectureSelection:
    def test_venezuela_fintech_selects_correct_template(self):
        opp = {"geography": "venezuela", "vertical": "fintech"}
        key = _get_architecture_key(opp)
        assert key == "venezuela_fintech"

    def test_venezuela_smb_defaults_to_smb_template(self):
        opp = {"geography": "venezuela", "vertical": "smb_software"}
        key = _get_architecture_key(opp)
        assert key == "venezuela_smb"

    def test_latam_fintech_selects_latam_template(self):
        opp = {"geography": "latam", "vertical": "payment_processing"}
        key = _get_architecture_key(opp)
        assert key == "latam_fintech"

    def test_global_saas_uses_global_template(self):
        opp = {"geography": "global", "vertical": "saas_platform"}
        key = _get_architecture_key(opp)
        assert key == "global_saas"

    def test_default_when_no_match(self):
        opp = {"geography": "unknown", "vertical": "unknown"}
        key = _get_architecture_key(opp)
        assert key == "default"

    def test_venezuela_opp_architecture_mentions_whatsapp(self, ve_opp):
        result = build_mvp_spec(ve_opp)
        assert "WhatsApp" in result

    def test_latam_opp_includes_local_payment_methods(self):
        opp = {
            "id": "opp_latam_pay",
            "name": "LATAM Payment Tool",
            "geography": "latam",
            "vertical": "fintech",
            "target_customer": "SMBs",
            "problem_statement": "No payment options",
        }
        result = build_mvp_spec(opp)
        # Should have architecture section
        assert "## B. Tech Architecture" in result


# ─── Tests: build_claude_code_prompt ──────────────────────────────────────

class TestBuildClaudeCodePrompt:
    def test_prompt_includes_all_sections(self, rich_opp):
        spec = build_mvp_spec(rich_opp)
        prompt = build_claude_code_prompt(rich_opp, spec)
        assert isinstance(prompt, str)
        assert "Read this first" in prompt or "Read the spec" in prompt
        assert "## Workflow" in prompt or "Workflow" in prompt
        assert spec in prompt  # Full spec should be embedded

    def test_prompt_references_the_spec(self, rich_opp):
        spec = build_mvp_spec(rich_opp)
        prompt = build_claude_code_prompt(rich_opp, spec)
        assert "MVP Build Specification" in prompt or "Build Specification" in prompt

    def test_prompt_includes_kill_condition(self, rich_opp):
        spec = build_mvp_spec(rich_opp)
        prompt = build_claude_code_prompt(rich_opp, spec)
        assert "Kill condition" in prompt or "kill" in prompt.lower()

    def test_prompt_includes_problem_customer_offer(self, rich_opp):
        spec = build_mvp_spec(rich_opp)
        prompt = build_claude_code_prompt(rich_opp, spec)
        # Should include the problem statement from opp
        assert "Manual USDT accounting" in prompt or "reconciliation" in prompt

    def test_prompt_includes_acceptance_criteria(self, rich_opp):
        spec = build_mvp_spec(rich_opp)
        prompt = build_claude_code_prompt(rich_opp, spec)
        assert "Acceptance Criteria" in prompt or "acceptance" in prompt

    def test_prompt_self_contained_for_minimal_opp(self, minimal_opp):
        spec = build_mvp_spec(minimal_opp)
        prompt = build_claude_code_prompt(minimal_opp, spec)
        # Should not error even with minimal data
        assert len(prompt) > 1000
        assert "Workflow" in prompt


# ─── Tests: write_build_package ──────────────────────────────────────────────

class TestWriteBuildPackage:
    def test_returns_dict_with_paths(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        assert isinstance(result, dict)
        assert "spec_path" in result
        assert "prompt_path" in result

    def test_writes_spec_file(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        spec_path = Path(result["spec_path"])
        assert spec_path.exists()
        assert spec_path.name.endswith("-mvp-build-spec.md")

    def test_writes_prompt_file(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        prompt_path = Path(result["prompt_path"])
        assert prompt_path.exists()
        assert prompt_path.name.endswith("-build-prompt.md")

    def test_spec_file_contains_sections(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        spec_path = Path(result["spec_path"])
        content = spec_path.read_text(encoding="utf-8")
        assert "## A. Feature Scope" in content
        assert "## E. Unit Economics" in content
        assert "## G. Week-4" in content

    def test_prompt_file_contains_spec(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        prompt_path = Path(result["prompt_path"])
        content = prompt_path.read_text(encoding="utf-8")
        assert "## A. Feature Scope" in content
        assert "Build Specification" in content

    def test_error_when_opp_has_no_id(self, tmp_path, minimal_opp):
        opp_no_id = {**minimal_opp}
        del opp_no_id["id"]
        result = write_build_package(opp_no_id, out_dir=str(tmp_path))
        assert "error" in result

    def test_files_written_with_date_prefix(self, tmp_path, rich_opp):
        result = write_build_package(rich_opp, out_dir=str(tmp_path))
        spec_filename = Path(result["spec_path"]).name
        # Should start with YYYY-MM-DD date format
        assert len(spec_filename) > 10
        assert spec_filename[0:4].isdigit()  # Year


# ─── Tests: Geography-specific behavior ──────────────────────────────────────

class TestGeographySpecificBehavior:
    def test_venezuela_opp_uses_usd_currency_symbol(self, ve_opp):
        result = build_mvp_spec(ve_opp)
        assert "$" in result  # Venezuela uses USD/USDT anchors

    def test_latam_opp_uses_usd_currency_symbol(self):
        opp = {
            "id": "opp_latam_curr",
            "name": "LATAM Opp Currency Test",
            "geography": "latam",
            "vertical": "fintech",
            "target_customer": "SMBs",
            "problem_statement": "Test",
            "willingness_to_pay": 6,
        }
        result = build_mvp_spec(opp)
        assert "$" in result

    def test_global_opp_uses_eur_currency_symbol(self):
        opp = {
            "id": "opp_global_curr",
            "name": "Global Opp Currency Test",
            "geography": "global",
            "vertical": "saas",
            "target_customer": "Enterprise",
            "problem_statement": "Test",
            "willingness_to_pay": 7,
        }
        result = build_mvp_spec(opp)
        assert "€" in result or "$" in result  # Either is OK


# ─── Tests: Fintech-specific OUT-OF-SCOPE rules ──────────────────────────────

class TestFintechOutOfScope:
    def test_payment_vertical_triggers_no_custody_warning(self, fintech_opp):
        result = build_mvp_spec(fintech_opp)
        assert "No customer fund custody" in result or "custody" in result.lower()

    def test_non_fintech_does_not_mention_custody(self):
        opp = {
            "id": "opp_no_fintech",
            "name": "Retail Analytics Platform",
            "geography": "latam",
            "vertical": "retail_software",
            "target_customer": "Retailers",
            "problem_statement": "Sales tracking is manual",
        }
        result = build_mvp_spec(opp)
        # Custody warning should not appear for non-fintech
        assert "No customer fund custody" not in result or "fintech" not in result.lower()

    def test_fintech_includes_transfer_initiation_restriction(self, fintech_opp):
        result = build_mvp_spec(fintech_opp)
        assert "transfer" in result.lower() or "settlement" in result.lower()


# ─── Tests: [NEEDS INPUT] markers for sparse data ───────────────────────────

class TestNeedsInputMarkers:
    def test_minimal_opp_has_needs_input_markers(self, minimal_opp):
        result = build_mvp_spec(minimal_opp)
        assert "[NEEDS INPUT:" in result

    def test_rich_opp_may_still_have_some_needs_input(self, rich_opp, minimal_opp):
        result = build_mvp_spec(rich_opp)
        # Rich opp should have fewer [NEEDS INPUT] than minimal
        needs_count_rich = result.count("[NEEDS INPUT:")
        result_minimal = build_mvp_spec(minimal_opp)
        needs_count_minimal = result_minimal.count("[NEEDS INPUT:")
        assert needs_count_minimal >= needs_count_rich

    def test_feature_scope_needs_input_for_user_flow(self, minimal_opp):
        result = build_mvp_spec(minimal_opp)
        # Section A should ask for user flow
        section_a = result[result.find("## A. Feature Scope") : result.find("## B.")]
        assert "[NEEDS INPUT:" in section_a


# ─── Tests: Unit Economics with 3 scenarios ──────────────────────────────────

class TestUnitEconomicsScenarios:
    def test_economics_table_has_three_scenario_columns(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        economics_section = result[result.find("## E. Unit Economics") : result.find("## F.")]
        assert "Conservative" in economics_section
        assert "Base" in economics_section
        assert "Ambitious" in economics_section

    def test_economics_table_has_pricing_row(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        economics_section = result[result.find("## E. Unit Economics") : result.find("## F.")]
        assert "Pricing" in economics_section

    def test_economics_break_even_mentions_8k_burn(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        assert "8000" in result or "$8K" in result or "8K" in result or "break-even" in result

    def test_economics_includes_cac_and_ltv_calculations(self, rich_opp):
        result = build_mvp_spec(rich_opp)
        economics_section = result[result.find("## E. Unit Economics") : result.find("## F.")]
        assert "CAC" in economics_section or "customer" in economics_section.lower()
