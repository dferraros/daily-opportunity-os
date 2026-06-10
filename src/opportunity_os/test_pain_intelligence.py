"""Tests for pain_intelligence.py — build_pain_queries, execute_pain_research."""
import pytest
from unittest.mock import MagicMock, patch
from opportunity_os.pain_intelligence import (
    build_pain_queries,
    execute_pain_research,
    is_pain_validated,
    pain_score_label,
)


# ─── build_pain_queries ───────────────────────────────────────────────────────

def test_build_pain_queries_returns_list():
    opp = {"vertical": "fintech", "geography": "venezuela"}
    result = build_pain_queries(opp)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_build_pain_queries_uses_wedge_category():
    opp = {"venezuela_wedge_category": "payments_and_collections"}
    result = build_pain_queries(opp)
    assert any("USDT" in q or "cobrar" in q or "pago" in q for q in result)


def test_build_pain_queries_deduplicates():
    opp = {
        "venezuela_wedge_category": "payments_and_collections",
        "vertical": "payments",
        "geography": "venezuela",
    }
    result = build_pain_queries(opp)
    assert len(result) == len(set(result)), "queries must be deduplicated"


# ─── execute_pain_research ────────────────────────────────────────────────────

def _make_mock_client(json_text: str):
    """Return a mock Anthropic client that returns json_text in its response."""
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = json_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def test_execute_pain_research_returns_dict_on_success():
    json_text = '{"pain_validation_score": 8.0, "exact_customer_phrases": ["no puedo cobrar"], "pain_evidence_sources": ["reddit r/vzla"], "workarounds_found": ["USDT P2P"]}'
    client = _make_mock_client(json_text)
    opp = {"id": "t1", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=client)
    assert result.get("pain_validation_score") == 8.0
    assert "pain_researched_at" in result


def test_execute_pain_research_no_api_key_returns_empty():
    """When no API key and no client passed, return empty dict gracefully."""
    opp = {"id": "t2", "name": "Test", "geography": "global", "vertical": "saas"}
    with patch.dict("os.environ", {}, clear=True):
        with patch("opportunity_os.pain_intelligence._load_api_key", return_value=None):
            result = execute_pain_research(opp)
    assert result == {}


def test_execute_pain_research_skips_if_researched_recently():
    """Skip if pain_researched_at is within the last 7 days."""
    from datetime import date
    opp = {
        "id": "t3",
        "name": "Test",
        "geography": "global",
        "pain_researched_at": date.today().isoformat(),
    }
    result = execute_pain_research(opp, client=MagicMock())
    assert result == {}


def test_execute_pain_research_graceful_on_api_error():
    """API exception must return empty dict, not raise."""
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("network error")
    opp = {"id": "t4", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=mock_client)
    assert result == {}


def test_execute_pain_research_handles_bad_json():
    """Malformed JSON from the model must return empty dict."""
    client = _make_mock_client("not valid json at all")
    opp = {"id": "t5", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=client)
    assert result == {}


def test_execute_pain_research_does_not_mutate_input():
    json_text = '{"pain_validation_score": 7.0, "exact_customer_phrases": [], "pain_evidence_sources": [], "workarounds_found": []}'
    client = _make_mock_client(json_text)
    opp = {"id": "t6", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    keys_before = set(opp.keys())
    execute_pain_research(opp, client=client)
    assert set(opp.keys()) == keys_before, "must not mutate input"


# ─── is_pain_validated ────────────────────────────────────────────────────────

def test_is_pain_validated_true_for_score_7():
    assert is_pain_validated({"pain_validation_score": 7.0}) is True


def test_is_pain_validated_false_for_score_6():
    assert is_pain_validated({"pain_validation_score": 6.9}) is False


def test_is_pain_validated_false_for_none():
    assert is_pain_validated({}) is False


# ─── pain_score_label ─────────────────────────────────────────────────────────

def test_pain_score_label_critical():
    assert "critical" in pain_score_label(9.5)


def test_pain_score_label_unscored():
    assert pain_score_label(None) == "unscored"
