"""Tests for storage.py — JSONL read/write, deduplication, atomic update."""
import json
import os
import tempfile
import pytest
from opportunity_os.storage import (
    append_opportunity,
    read_all_opportunities,
    update_opportunity,
    dedupe_check,
    get_opportunity_by_id,
    append_opp_score_history,
)


@pytest.fixture
def tmp_path_file(tmp_path):
    return str(tmp_path / "test_opps.jsonl")


# ─── append_opportunity / read_all_opportunities ──────────────────────────────

def test_append_and_read_roundtrip(tmp_path_file):
    opp = {"id": "opp_test_001", "name": "Test Opp", "geography": "global"}
    append_opportunity(opp, path=tmp_path_file)
    result = read_all_opportunities(path=tmp_path_file)
    assert len(result) == 1
    assert result[0]["name"] == "Test Opp"


def test_multiple_appends(tmp_path_file):
    for i in range(3):
        append_opportunity({"id": f"opp_{i}", "name": f"Opp {i}"}, path=tmp_path_file)
    result = read_all_opportunities(path=tmp_path_file)
    assert len(result) == 3


def test_append_auto_generates_id(tmp_path_file):
    opp = {"name": "No ID Opp"}
    opp_id = append_opportunity(opp, path=tmp_path_file)
    assert opp_id is not None
    assert len(opp_id) > 0
    stored = read_all_opportunities(path=tmp_path_file)
    assert stored[0].get("id") == opp_id


def test_append_sets_timestamps(tmp_path_file):
    opp = {"id": "x", "name": "t"}
    append_opportunity(opp, path=tmp_path_file)
    stored = read_all_opportunities(path=tmp_path_file)[0]
    assert "first_seen" in stored
    assert "last_updated" in stored


def test_read_missing_file_returns_empty_list(tmp_path_file):
    result = read_all_opportunities(path=tmp_path_file + ".nonexistent")
    assert result == []


def test_read_skips_malformed_lines(tmp_path_file, caplog):
    with open(tmp_path_file, "w", encoding="utf-8") as f:
        f.write('{"id": "good"}\n')
        f.write("NOT_JSON\n")
        f.write('{"id": "also_good"}\n')
    import logging
    with caplog.at_level(logging.WARNING):
        result = read_all_opportunities(path=tmp_path_file)
    assert len(result) == 2
    assert any("malformed" in r.message.lower() or "Skipping" in r.message for r in caplog.records)


# ─── update_opportunity ───────────────────────────────────────────────────────

def test_update_existing_opportunity(tmp_path_file):
    append_opportunity({"id": "upd_001", "name": "Before"}, path=tmp_path_file)
    updated = update_opportunity("upd_001", {"name": "After"}, path=tmp_path_file)
    assert updated is True
    stored = get_opportunity_by_id("upd_001", path=tmp_path_file)
    assert stored["name"] == "After"


def test_update_nonexistent_returns_false(tmp_path_file):
    append_opportunity({"id": "x"}, path=tmp_path_file)
    result = update_opportunity("does_not_exist", {"name": "ghost"}, path=tmp_path_file)
    assert result is False


def test_update_is_atomic(tmp_path_file):
    append_opportunity({"id": "safe_001", "name": "Original"}, path=tmp_path_file)
    update_opportunity("safe_001", {"stage": "validated"}, path=tmp_path_file)
    assert not os.path.exists(tmp_path_file + ".tmp"), ".tmp file was not cleaned up"


# ─── dedupe_check ─────────────────────────────────────────────────────────────

def test_dedupe_check_finds_recent_duplicate(tmp_path_file):
    from datetime import datetime
    opp = {
        "id": "dup_001",
        "name": "My Opportunity",
        "geography": "global",
        "first_seen": datetime.now().isoformat(),
    }
    append_opportunity(opp, path=tmp_path_file)
    found_id = dedupe_check("My Opportunity", "global", path=tmp_path_file)
    assert found_id == "dup_001"


def test_dedupe_check_returns_none_for_new_opp(tmp_path_file):
    result = dedupe_check("Brand New Opp", "global", path=tmp_path_file)
    assert result is None


def test_dedupe_check_is_case_insensitive(tmp_path_file):
    from datetime import datetime
    opp = {"id": "case_001", "name": "My Opp", "geography": "venezuela", "first_seen": datetime.now().isoformat()}
    append_opportunity(opp, path=tmp_path_file)
    found = dedupe_check("my opp", "venezuela", path=tmp_path_file)
    assert found == "case_001"


# ─── append_opp_score_history ─────────────────────────────────────────────────

def test_score_history_appends_entry(tmp_path_file):
    append_opportunity({"id": "sh_001", "name": "Scored"}, path=tmp_path_file)
    result = append_opp_score_history("sh_001", 7.5, path=tmp_path_file)
    assert result is True
    stored = get_opportunity_by_id("sh_001", path=tmp_path_file)
    history = stored.get("score_history", [])
    assert len(history) == 1
    assert history[0]["score"] == 7.5


def test_score_history_idempotent_same_day(tmp_path_file):
    append_opportunity({"id": "sh_002", "name": "Scored"}, path=tmp_path_file)
    append_opp_score_history("sh_002", 7.5, path=tmp_path_file)
    append_opp_score_history("sh_002", 8.0, path=tmp_path_file)  # same day — should not add
    stored = get_opportunity_by_id("sh_002", path=tmp_path_file)
    assert len(stored.get("score_history", [])) == 1


def test_score_history_returns_false_for_unknown_id(tmp_path_file):
    result = append_opp_score_history("does_not_exist", 7.0, path=tmp_path_file)
    assert result is False


# ─── immutability ─────────────────────────────────────────────────────────────

def test_append_opportunity_does_not_mutate_caller(tmp_path_file):
    """append_opportunity must not add id/first_seen/last_updated to the caller's dict."""
    opp = {"name": "Immutable Test", "geography": "global"}
    keys_before = set(opp.keys())
    append_opportunity(opp, path=tmp_path_file)
    assert set(opp.keys()) == keys_before, "append_opportunity mutated caller dict"


def test_update_opportunity_does_not_mutate_stored_record(tmp_path_file):
    """update_opportunity must not bleed the updates dict into unrelated records."""
    append_opportunity({"id": "imm_001", "name": "Alpha"}, path=tmp_path_file)
    append_opportunity({"id": "imm_002", "name": "Beta"}, path=tmp_path_file)
    update_opportunity("imm_001", {"stage": "validated"}, path=tmp_path_file)
    beta = get_opportunity_by_id("imm_002", path=tmp_path_file)
    assert beta.get("stage") is None, "update leaked into unrelated record"
