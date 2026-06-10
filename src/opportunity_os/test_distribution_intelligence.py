"""Tests for distribution_intelligence.py — execute_distribution_research."""
import pytest
from unittest.mock import MagicMock, patch
from opportunity_os.distribution_intelligence import (
    build_distribution_queries,
    get_recommended_channels,
    execute_distribution_research,
    is_distribution_validated,
    distribution_ease_label,
)


# ─── build_distribution_queries ──────────────────────────────────────────────

def test_build_distribution_queries_returns_list():
    opp = {"geography": "venezuela", "vertical": "fintech"}
    result = build_distribution_queries(opp)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_get_recommended_channels_for_venezuela():
    opp = {"geography": "venezuela", "vertical": "fintech"}
    channels = get_recommended_channels(opp)
    assert len(channels) >= 1
    assert any("whatsapp" in c.lower() or "WhatsApp" in c for c in channels)


# ─── execute_distribution_research ───────────────────────────────────────────

def _make_mock_client(json_text: str):
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = json_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def test_execute_distribution_research_returns_dict_on_success():
    json_text = '{"distribution_validated": true, "top_distribution_channels": ["WhatsApp"], "estimated_cac_logic": "~$12 CAC via WhatsApp", "first_10_customer_path": "Outreach to 50 VE SMBs", "trust_mechanism_latam": "WhatsApp referral"}'
    client = _make_mock_client(json_text)
    opp = {"id": "d1", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=client)
    assert result.get("distribution_validated") is True
    assert "distribution_researched_at" in result


def test_execute_distribution_research_no_api_key_returns_empty():
    opp = {"id": "d2", "name": "Test", "geography": "global", "vertical": "saas"}
    with patch.dict("os.environ", {}, clear=True):
        with patch("opportunity_os.distribution_intelligence._load_api_key", return_value=None):
            result = execute_distribution_research(opp)
    assert result == {}


def test_execute_distribution_research_skips_if_researched_recently():
    from datetime import date
    opp = {
        "id": "d3",
        "name": "Test",
        "geography": "global",
        "distribution_researched_at": date.today().isoformat(),
    }
    result = execute_distribution_research(opp, client=MagicMock())
    assert result == {}


def test_execute_distribution_research_graceful_on_api_error():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("timeout")
    opp = {"id": "d4", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=mock_client)
    assert result == {}


def test_execute_distribution_research_handles_bad_json():
    client = _make_mock_client("not json")
    opp = {"id": "d5", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=client)
    assert result == {}


def test_execute_distribution_research_does_not_mutate_input():
    json_text = '{"distribution_validated": true, "top_distribution_channels": [], "estimated_cac_logic": "n/a", "first_10_customer_path": "n/a", "trust_mechanism_latam": "referral"}'
    client = _make_mock_client(json_text)
    opp = {"id": "d6", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    keys_before = set(opp.keys())
    execute_distribution_research(opp, client=client)
    assert set(opp.keys()) == keys_before


# ─── convenience helpers ──────────────────────────────────────────────────────

def test_is_distribution_validated_true():
    assert is_distribution_validated({"distribution_validated": True}) is True


def test_is_distribution_validated_false_for_none():
    assert is_distribution_validated({}) is False


def test_distribution_ease_label_unscored():
    assert distribution_ease_label(None) == "unscored"


def test_distribution_ease_label_clear():
    assert "clear" in distribution_ease_label(9.5)
