"""Tests for T1.2: research source failures must log warnings, never vanish,
and the CLI must surface unconfigured sources upfront."""

import logging
import urllib.request

import pytest

from opportunity_os.free_research import (
    get_unavailable_sources,
    search_hn,
    serper_search,
)


def _raise_urlopen(*args, **kwargs):
    raise urllib.request.URLError("simulated network failure")


def test_hn_failure_logs_warning(monkeypatch, caplog):
    """A failed HN call must return [] AND leave a warning in the log —
    silence here previously made API outages look like 'no signals'."""
    monkeypatch.setattr(urllib.request, "urlopen", _raise_urlopen)

    with caplog.at_level(logging.WARNING, logger="opportunity_os.free_research"):
        result = search_hn("fintech venezuela")

    assert result == []
    assert any("fetch failed" in r.message for r in caplog.records)


def test_serper_failure_logs_warning(monkeypatch, caplog):
    monkeypatch.setenv("SERPER_API_KEY", "test-key")
    monkeypatch.setattr(urllib.request, "urlopen", _raise_urlopen)

    with caplog.at_level(logging.WARNING, logger="opportunity_os.free_research"):
        result = serper_search("test query")

    assert result == []
    assert any("Serper search failed" in r.message for r in caplog.records)


def test_serper_missing_key_returns_empty_without_warning(monkeypatch, caplog):
    """Missing key is a configuration state, not a failure — no warning spam."""
    monkeypatch.delenv("SERPER_API_KEY", raising=False)

    with caplog.at_level(logging.WARNING, logger="opportunity_os.free_research"):
        result = serper_search("test query")

    assert result == []
    assert not caplog.records


def test_get_unavailable_sources_all_missing(monkeypatch):
    for var in ("SERPER_API_KEY", "EXA_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("opportunity_os.tavily_client.is_available", lambda: False)

    missing = get_unavailable_sources()

    assert len(missing) == 4
    assert any("TAVILY_API_KEY" in m for m in missing)
    assert any("SERPER_API_KEY" in m for m in missing)


def test_get_unavailable_sources_all_configured(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "k")
    monkeypatch.setenv("EXA_API_KEY", "k")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "k")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "k")
    monkeypatch.setattr("opportunity_os.tavily_client.is_available", lambda: True)

    assert get_unavailable_sources() == []
