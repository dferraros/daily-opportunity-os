"""
Tests that research_executor extracts direct_competitors (the upstream gap that
left competitor_intelligence running on weak category fallbacks).

Mocks the Anthropic client -- no live API.
"""
import sys
import types

from opportunity_os import research_executor as rx


class _FakeBlock:
    def __init__(self, text):
        self.text = text
        self.type = "text"


class _FakeResponse:
    def __init__(self, text):
        self.content = [_FakeBlock(text)]


def _install_fake_anthropic(monkeypatch, json_text):
    """Make `import anthropic` inside the extractor return a client that replies json_text."""
    fake = types.ModuleType("anthropic")

    class _Client:
        def __init__(self, *a, **k):
            pass

        class _Messages:
            @staticmethod
            def create(*a, **k):
                return _FakeResponse(json_text)

        messages = _Messages()

    fake.Anthropic = _Client
    monkeypatch.setitem(sys.modules, "anthropic", fake)


CANNED = (
    '{"pain_validation_score": 7.0, "distribution_validated": true, '
    '"top_distribution_channels": ["WhatsApp"], '
    '"direct_competitors": ["Alegra", "Siigo", "Contpaqi", "Bind ERP", "Extra One"]}'
)


def test_tavily_extractor_parses_and_caps_competitors(monkeypatch):
    _install_fake_anthropic(monkeypatch, CANNED)
    opp = {"name": "E-Invoicing SaaS", "geography": "latam", "vertical": "smb_software"}
    result = rx._extract_from_tavily_results(opp, "fake-key", "some tavily context")
    assert result["direct_competitors"] == ["Alegra", "Siigo", "Contpaqi", "Bind ERP"]  # capped at 4


def test_combined_research_parses_competitors(monkeypatch):
    _install_fake_anthropic(monkeypatch, CANNED)
    opp = {"name": "E-Invoicing SaaS", "geography": "latam", "vertical": "smb_software"}
    result = rx._execute_combined_research(opp, "fake-key")
    assert result["direct_competitors"][:3] == ["Alegra", "Siigo", "Contpaqi"]


def test_empty_competitor_list_yields_empty(monkeypatch):
    _install_fake_anthropic(monkeypatch,
                            '{"pain_validation_score": 5.0, "direct_competitors": []}')
    opp = {"name": "Novel Thing", "geography": "global"}
    result = rx._extract_from_tavily_results(opp, "fake-key", "ctx")
    assert result["direct_competitors"] == []


def test_missing_competitor_key_omits_field(monkeypatch):
    _install_fake_anthropic(monkeypatch, '{"pain_validation_score": 5.0}')
    opp = {"name": "X", "geography": "global"}
    result = rx._extract_from_tavily_results(opp, "fake-key", "ctx")
    assert "direct_competitors" not in result
