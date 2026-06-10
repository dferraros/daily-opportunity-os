"""Tests for Wave 1 (conviction-to-action bridge): like CLI, report export,
and Claude Code kickoff pack."""

import json

import pytest
from click.testing import CliRunner

from opportunity_os.export_report import build_opportunity_report_md, write_report_bundle
from opportunity_os.kickoff import build_kickoff_prompt, build_project_md, write_kickoff_pack
from opportunity_os.main import cli


SAMPLE_OPP = {
    "id": "opp_test_w1_001",
    "name": "WhatsApp Inventory for VE Bodegas",
    "geography": "venezuela",
    "vertical": "smb_software",
    "bucket": "fast_cash",
    "stage": "scout",
    "portfolio_lane": "now",
    "final_score": 8.2,
    "raw_final_score": 7.1,
    "attractiveness_score": 8.0,
    "executability_score": 7.5,
    "strategic_value_score": 6.9,
    "kill_decision": False,
    "kill_criteria_passed": 7,
    "problem_statement": "Bodega owners lose 15-30% of stock value to manual tracking errors",
    "target_customer": "Venezuelan bodega owner, 1-3 employees",
    "trigger_signal": "Reddit threads on inventory chaos",
    "why_now": "Smartphone penetration + economic necessity",
    "pain_severity": 8,
    "pain_severity_reason": "Daily money loss, explicit workarounds on forums",
    "speed_to_mvp": 8,
    "speed_to_mvp_reason": "WhatsApp bot + sheet backend, 2-3 weeks",
    "exact_customer_phrases": ["pierdo plata cada semana", "lo llevo en un cuaderno"],
    "pain_evidence_sources": ["https://reddit.com/r/vzla/example"],
    "direct_competitors": ["Treinta", "Tiendita"],
    "pricing_benchmark": "Treinta freemium, $5/mo pro",
    "tam": 80_000_000,
    "tam_method": "bottom_up",
    "tam_confidence": "medium",
    "path_to_first_revenue": "$5-10/mo via WhatsApp cold outreach to 30 bodegas",
    "top_distribution_channels": ["whatsapp_cold_ve", "referral_network"],
    "estimated_cac_logic": "WhatsApp cold ~$2-5 CPL in VE",
    "first_10_customer_path": "Personal network + bodega WhatsApp groups",
    "trust_mechanism_latam": "Referral from known operator, pay-after-results",
    "risks": ["Treinta expands to VE", "payment rail friction"],
    "news_signal_count": 4,
    "pain_signal_count": 7,
}


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    """Point storage at a tmp JSONL store seeded with SAMPLE_OPP."""
    store = tmp_path / "opportunities.jsonl"
    store.write_text(json.dumps(SAMPLE_OPP) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "opportunity_os.storage._default_opps_path", lambda: str(store)
    )
    return store


# --- 1.1 like / liked ---------------------------------------------------------

def test_like_sets_flag_and_recommendation(tmp_store):
    runner = CliRunner()
    result = runner.invoke(cli, ["like", "opp_test_w1_001"])

    assert result.exit_code == 0, result.output
    assert "Liked:" in result.output
    stored = json.loads(tmp_store.read_text(encoding="utf-8").strip())
    assert stored["liked_at"]
    assert stored["recommendation"] == "build"


def test_like_undo_clears_flag(tmp_store):
    runner = CliRunner()
    runner.invoke(cli, ["like", "opp_test_w1_001"])
    result = runner.invoke(cli, ["like", "opp_test_w1_001", "--undo"])

    assert result.exit_code == 0
    stored = json.loads(tmp_store.read_text(encoding="utf-8").strip())
    assert stored["liked_at"] is None


def test_like_unknown_id_errors(tmp_store):
    runner = CliRunner()
    result = runner.invoke(cli, ["like", "opp_nope"])
    assert result.exit_code == 1


def test_liked_lists_marked_opps(tmp_store):
    runner = CliRunner()
    runner.invoke(cli, ["like", "opp_test_w1_001"])
    result = runner.invoke(cli, ["liked"])

    assert result.exit_code == 0
    assert "WhatsApp Inventory" in result.output


# --- 1.2 export ----------------------------------------------------------------

def test_report_md_contains_core_sections():
    md = build_opportunity_report_md(SAMPLE_OPP)

    assert "# WhatsApp Inventory for VE Bodegas" in md
    assert "8.20/10" in md
    assert "## Scoring" in md and "pain_severity | 8" in md
    assert "## Evidence" in md and "pierdo plata cada semana" in md
    assert "## Market" in md and "$80.0M" in md
    assert "## Distribution" in md and "whatsapp_cold_ve" in md
    assert "## Risks & Assumptions" in md and "7/7 criteria passed" in md


def test_export_cli_writes_bundle(tmp_store, tmp_path):
    out = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(cli, ["export", "opp_test_w1_001", "--to", str(out)])

    assert result.exit_code == 0, result.output
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "WhatsApp Inventory" in report


def test_export_unknown_id_errors(tmp_store, tmp_path):
    result = CliRunner().invoke(cli, ["export", "opp_nope", "--to", str(tmp_path)])
    assert result.exit_code == 1


# --- 1.3 kickoff ----------------------------------------------------------------

def test_project_md_carries_pipeline_knowledge():
    md = build_project_md(SAMPLE_OPP)

    assert "Bodega owners lose 15-30%" in md
    assert "Treinta" in md
    assert "$3-15/mo SaaS ceiling" in md  # Venezuela WTP anchor
    assert "whatsapp_cold_ve" in md
    assert "Treinta expands to VE" in md  # kill risk


def test_kickoff_prompt_references_workflow():
    prompt = build_kickoff_prompt(SAMPLE_OPP)

    assert "PROJECT.md" in prompt
    assert "/spec" in prompt and "/plan" in prompt
    assert "first 10 customers" in prompt
    assert "$2K" in prompt


def test_kickoff_cli_writes_both_files(tmp_store, tmp_path):
    out = tmp_path / "pack"
    result = CliRunner().invoke(cli, ["kickoff", "opp_test_w1_001", "--to", str(out)])

    assert result.exit_code == 0, result.output
    assert (out / "PROJECT.md").exists()
    assert (out / "kickoff-prompt.md").exists()


def test_write_report_bundle_unknown_id(tmp_store):
    result = write_report_bundle("opp_does_not_exist")
    assert "error" in result


def test_kickoff_pack_unknown_id(tmp_store):
    result = write_kickoff_pack("opp_nope")
    assert "error" in result


def test_project_md_handles_legacy_field_types():
    """Legacy records hold None in why_now and a numeric score in
    path_to_first_revenue -- neither may leak into the brief verbatim."""
    legacy = {
        **SAMPLE_OPP,
        "why_now": None,
        "path_to_first_revenue": 6,
        "tam_method": None,
    }
    md = build_project_md(legacy)

    assert "**Why now:** None" not in md
    assert "**First revenue path:** 6" not in md
    assert "method: None" not in md
    assert "TBD" in md
