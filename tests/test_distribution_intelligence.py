"""Tests for distribution_intelligence.py — run_distribution_executor."""
import sys
import pytest
from unittest.mock import MagicMock, patch
from opportunity_os.distribution_intelligence import (
    build_distribution_queries,
    get_recommended_channels,
    run_distribution_executor,
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


# ─── run_distribution_executor ───────────────────────────────────────────────

def _make_mock_anthropic_client(json_text: str):
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = json_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def _mock_tavily_available(json_text: str, opp: dict):
    """Context managers to patch Tavily and Anthropic for run_distribution_executor."""
    mock_anthropic_client = _make_mock_anthropic_client(json_text)
    mock_tavily = MagicMock()
    mock_tavily.is_available.return_value = True
    mock_tavily.search_multi.return_value = "some distribution research context"

    return (
        patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}),
        patch.dict(sys.modules, {"opportunity_os.tavily_client": mock_tavily}),
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
    )


def test_run_distribution_executor_returns_dict_on_success():
    json_text = (
        '{"distribution_validated": true, '
        '"top_distribution_channels": ["WhatsApp"], '
        '"estimated_cac_logic": "~$12 CAC via WhatsApp", '
        '"first_10_customer_path": "Outreach to 50 VE SMBs", '
        '"trust_mechanism_latam": "WhatsApp referral"}'
    )
    opp = {"id": "d1", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    env_patch, tavily_patch, anthropic_patch = _mock_tavily_available(json_text, opp)
    with env_patch, tavily_patch, anthropic_patch:
        result = run_distribution_executor(opp)
    assert result.get("distribution_validated") is True
    assert "distribution_validated_date" in result


def test_run_distribution_executor_no_api_key_returns_empty():
    opp = {"id": "d2", "name": "Test", "geography": "global", "vertical": "saas"}
    with patch.dict("os.environ", {}, clear=True):
        with patch("opportunity_os.distribution_intelligence._load_api_key", return_value=None):
            result = run_distribution_executor(opp)
    assert result == {}


def test_run_distribution_executor_no_tavily_returns_empty():
    opp = {"id": "d3", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    mock_tavily = MagicMock()
    mock_tavily.is_available.return_value = False
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch.dict(sys.modules, {"opportunity_os.tavily_client": mock_tavily}):
            result = run_distribution_executor(opp)
    assert result == {}


def test_run_distribution_executor_graceful_on_api_error():
    opp = {"id": "d4", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    mock_tavily = MagicMock()
    mock_tavily.is_available.return_value = True
    mock_tavily.search_multi.return_value = "context"
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("timeout")
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch.dict(sys.modules, {"opportunity_os.tavily_client": mock_tavily}):
            with patch("anthropic.Anthropic", return_value=mock_client):
                result = run_distribution_executor(opp)
    assert result == {}


def test_run_distribution_executor_handles_bad_json():
    opp = {"id": "d5", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    mock_tavily = MagicMock()
    mock_tavily.is_available.return_value = True
    mock_tavily.search_multi.return_value = "context"
    mock_client = _make_mock_anthropic_client("not json")
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch.dict(sys.modules, {"opportunity_os.tavily_client": mock_tavily}):
            with patch("anthropic.Anthropic", return_value=mock_client):
                result = run_distribution_executor(opp)
    assert result == {}


def test_run_distribution_executor_does_not_mutate_input():
    json_text = (
        '{"distribution_validated": true, '
        '"top_distribution_channels": [], '
        '"estimated_cac_logic": "n/a", '
        '"first_10_customer_path": "n/a", '
        '"trust_mechanism_latam": "referral"}'
    )
    opp = {"id": "d6", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    keys_before = set(opp.keys())
    mock_tavily = MagicMock()
    mock_tavily.is_available.return_value = True
    mock_tavily.search_multi.return_value = "context"
    mock_client = _make_mock_anthropic_client(json_text)
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch.dict(sys.modules, {"opportunity_os.tavily_client": mock_tavily}):
            with patch("anthropic.Anthropic", return_value=mock_client):
                run_distribution_executor(opp)
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
