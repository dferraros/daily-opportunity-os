"""Tests for 2026-06-10 audit quick wins: research_executor immutability,
backup restore path-traversal guard, and date-free model IDs."""

import re

import pytest

from opportunity_os import backup
from opportunity_os.research_executor import run_research_executor


# --- QW3: run_research_executor must not mutate the caller's dict ------------

def test_research_executor_does_not_mutate_input_on_extraction_failure(monkeypatch):
    """When step 3 (Claude extraction) raises, opp is still the caller's dict;
    the firecrawl merge and research_executed_at stamp must not mutate it."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr("opportunity_os.tavily_client.is_available", lambda: False)
    monkeypatch.setattr(
        "opportunity_os.firecrawl_client.crawl_pain_evidence",
        lambda query, geography="global": ["users hate the manual process"],
    )

    def boom(opp, api_key):
        raise RuntimeError("simulated API failure")

    monkeypatch.setattr(
        "opportunity_os.research_executor._execute_combined_research", boom
    )

    caller_opp = {"id": "opp_x", "name": "Test Opp", "geography": "latam"}
    snapshot = dict(caller_opp)

    result = run_research_executor(caller_opp)

    assert caller_opp == snapshot, "caller's dict was mutated"
    assert result.get("research_executed_at")
    assert result.get("exact_customer_phrases") == ["users hate the manual process"]


# --- QW5: restore_backup must refuse paths outside the backups dir -----------

def test_restore_backup_rejects_path_traversal(tmp_path, monkeypatch):
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    evil = tmp_path / "evil.jsonl"
    evil.write_text('{"id": "evil"}\n', encoding="utf-8")

    monkeypatch.setattr(backup, "_backups_dir", lambda: backups_dir)
    monkeypatch.setattr(backup, "_opps_path", lambda: tmp_path / "opportunities.jsonl")

    result = backup.restore_backup("../evil.jsonl", dry_run=True)

    assert result["success"] is False
    assert "Invalid" in result["message"]


def test_restore_backup_accepts_legitimate_file(tmp_path, monkeypatch):
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    good = backups_dir / "2026-06-10-120000-manual.jsonl"
    good.write_text('{"id": "ok"}\n', encoding="utf-8")

    monkeypatch.setattr(backup, "_backups_dir", lambda: backups_dir)
    monkeypatch.setattr(backup, "_opps_path", lambda: tmp_path / "opportunities.jsonl")

    result = backup.restore_backup("2026-06-10-120000-manual.jsonl", dry_run=True)

    assert result["success"] is True
    assert result["records_restored"] == 1


# --- Model IDs: complete as-is, no date suffixes ------------------------------

@pytest.mark.parametrize(
    "module_name",
    [
        "opportunity_os.ai_scorer",
        "opportunity_os.research_executor",
        "opportunity_os.pain_intelligence",
        "opportunity_os.distribution_intelligence",
    ],
)
def test_model_ids_have_no_date_suffix(module_name):
    """claude-haiku-4-5-20251001 does not exist in the API; dated IDs made
    every Claude extraction call fail silently. IDs are complete as-is."""
    import importlib

    mod = importlib.import_module(module_name)
    assert not re.search(r"-\d{8}$", mod.MODEL), (
        f"{module_name}.MODEL = {mod.MODEL!r} has a date suffix"
    )
