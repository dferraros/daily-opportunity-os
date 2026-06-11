"""Tests for venture_pack module: validation kit, requirements seed, business plan."""

import json
from pathlib import Path

import pytest

from opportunity_os.venture_pack import (
    build_validation_kit,
    build_business_plan,
    build_requirements_seed,
    write_venture_pack,
)


SAMPLE_OPP = {
    "id": "opp_test_venture_001",
    "name": "WhatsApp Inventory for VE Bodegas",
    "geography": "venezuela",
    "vertical": "smb_software",
    "problem_statement": "Bodega owners lose 15-30% of stock value to manual tracking errors",
    "target_customer": "Venezuelan bodega owner, 1-3 employees",
    "exact_customer_phrases": [
        "pierdo plata cada semana",
        "lo llevo en un cuaderno",
    ],
    "path_to_first_revenue": "$5-10/mo via WhatsApp cold outreach to 30 bodegas",
    "top_distribution_channels": ["whatsapp_cold_ve", "referral_network"],
    "estimated_cac_logic": "WhatsApp cold ~$2-5 CPL in VE",
    "first_10_customer_path": "Personal network + bodega WhatsApp groups",
    "risks": [
        "Treinta expands to VE",
        "payment rail friction",
        "smartphone penetration plateaus",
    ],
    "willingness_to_pay": 8.0,
}


def test_build_validation_kit_contains_exact_phrases():
    """Validation kit must include exact_customer_phrases verbatim."""
    kit = build_validation_kit(SAMPLE_OPP)
    assert kit
    assert "pierdo plata cada semana" in kit
    assert "lo llevo en un cuaderno" in kit


def test_build_validation_kit_contains_decision_rule():
    """Validation kit must include the decision rule for proceeding."""
    kit = build_validation_kit(SAMPLE_OPP)
    assert "4 of 5" in kit
    assert "willingness to pay" in kit.lower()
    assert "BUILD mode" in kit


def test_build_validation_kit_handles_empty_phrases():
    """Should not crash with empty or missing phrases."""
    opp = {**SAMPLE_OPP, "exact_customer_phrases": []}
    kit = build_validation_kit(opp)
    assert kit
    assert "Interview Script" in kit


def test_build_validation_kit_handles_empty_risks():
    """Should not crash with empty or missing risks."""
    opp = {**SAMPLE_OPP, "risks": []}
    kit = build_validation_kit(opp)
    assert kit
    assert "Disqualifying Evidence" in kit


def test_build_requirements_seed_has_phase_0_and_phase_1():
    """REQUIREMENTS.md seed must have Phase 0 (validation) and Phase 1 (build)."""
    req = build_requirements_seed(SAMPLE_OPP)
    assert "Phase 0" in req
    assert "Phase 1" in req
    assert "Acceptance Criteria" in req


def test_build_business_plan_returns_none_when_no_api_key(monkeypatch):
    """Should return None gracefully when ANTHROPIC_API_KEY is missing."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")

    result = build_business_plan(SAMPLE_OPP)
    assert result is None


def test_write_venture_pack_to_tmp(tmp_path):
    """write_venture_pack should create files atomically."""
    result = write_venture_pack(SAMPLE_OPP, tmp_path, include_business_plan=False)

    assert "files" in result
    assert "skipped" in result
    assert len(result["files"]) >= 2  # validation-kit + REQUIREMENTS

    # Check files exist
    for fpath in result["files"]:
        assert Path(fpath).exists()


def test_write_venture_pack_skips_business_plan_when_flag_false(tmp_path):
    """write_venture_pack should skip business-plan.md when include_business_plan=False."""
    result = write_venture_pack(SAMPLE_OPP, tmp_path, include_business_plan=False)

    files = [Path(f).name for f in result["files"]]
    assert "business-plan.md" not in files
    assert "business-plan.md" in " ".join(result["skipped"])


def test_write_venture_pack_returns_correct_file_list(tmp_path):
    """Returned file list should match actual created files."""
    result = write_venture_pack(SAMPLE_OPP, tmp_path, include_business_plan=False)

    for fpath in result["files"]:
        path = Path(fpath)
        assert path.exists()
        assert path.is_file()


def test_validation_kit_has_deadline_14_days():
    """Validation kit should mention 14-day deadline."""
    kit = build_validation_kit(SAMPLE_OPP)
    assert "14" in kit or "two weeks" in kit.lower()


def test_requirements_seed_has_tbd_placeholders():
    """REQUIREMENTS.md should have [TBD] placeholders for downstream /spec to fill."""
    req = build_requirements_seed(SAMPLE_OPP)
    assert "[TBD]" in req
