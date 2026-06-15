"""Tests for the Sonnet deep-dive synthesis (Wave 2.2)."""
from opportunity_os import deep_dive_synthesis as dds


VALID = (
    '{"bull_case": "Mandatory e-invoicing creates forced demand.", '
    '"key_risks": ["incumbent ERPs bundle it free", "regulatory timeline slips"], '
    '"swing_factors": ["per-country certification feasibility solo", "contador channel access"], '
    '"key_unknown": "Whether one country cert path is achievable by a solo founder.", '
    '"recommendation": "validate", "rationale": "Demand is real but distribution is unproven."}'
)


class TestParseSynthesis:
    def test_valid_parsed_and_normalized(self):
        result = dds._parse_synthesis(VALID)
        assert result["synthesis_recommendation"] == "validate"
        assert len(result["synthesis_key_risks"]) == 2
        assert result["synthesis_bull_case"].startswith("Mandatory")

    def test_swing_factors_and_unknown_parsed(self):
        result = dds._parse_synthesis(VALID)
        assert len(result["synthesis_swing_factors"]) == 2
        assert "certification" in result["synthesis_swing_factors"][0]
        assert result["synthesis_key_unknown"].startswith("Whether one country")

    def test_swing_factors_default_empty_when_absent(self):
        raw = '{"bull_case": "x", "recommendation": "go", "key_risks": []}'
        result = dds._parse_synthesis(raw)
        assert result["synthesis_swing_factors"] == []
        assert result["synthesis_key_unknown"] == ""

    def test_recommendation_lowercased(self):
        raw = '{"bull_case": "x", "recommendation": "GO", "key_risks": []}'
        assert dds._parse_synthesis(raw)["synthesis_recommendation"] == "go"

    def test_invalid_recommendation_rejected(self):
        raw = '{"bull_case": "x", "recommendation": "maybe", "key_risks": []}'
        assert dds._parse_synthesis(raw) is None

    def test_missing_bull_or_rec_returns_none(self):
        assert dds._parse_synthesis('{"recommendation": "go"}') is None
        assert dds._parse_synthesis('{"bull_case": "x"}') is None

    def test_risks_capped_and_coerced(self):
        raw = ('{"bull_case": "x", "recommendation": "pass", '
               '"key_risks": ["a", "b", "c", "d"]}')
        assert len(dds._parse_synthesis(raw)["synthesis_key_risks"]) == 3

    def test_markdown_fenced(self):
        raw = "```json\n" + VALID + "\n```"
        assert dds._parse_synthesis(raw)["synthesis_recommendation"] == "validate"

    def test_garbage_returns_none(self):
        assert dds._parse_synthesis("no json here") is None


class TestBuildSection:
    def test_empty_synthesis_yields_no_lines(self):
        assert dds.build_synthesis_section(None) == []
        assert dds.build_synthesis_section({}) == []

    def test_section_contains_recommendation_and_risks(self):
        synthesis = dds._parse_synthesis(VALID)
        lines = dds.build_synthesis_section(synthesis)
        text = "\n".join(lines)
        assert "Analyst Synthesis (Sonnet)" in text
        assert "VALIDATE" in text
        assert "incumbent ERPs bundle it free" in text

    def test_section_contains_swing_factors_and_unknown(self):
        synthesis = dds._parse_synthesis(VALID)
        text = "\n".join(dds.build_synthesis_section(synthesis))
        assert "Swing factors" in text
        assert "contador channel access" in text
        assert "Decisive unknown:" in text


class TestSynthesizeGracefulFail:
    def test_none_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setattr("opportunity_os.ai_scorer._load_env_key", lambda: None)
        assert dds.synthesize_opportunity({"name": "x"}) is None


class TestDossier:
    def test_omits_empty_fields(self):
        opp = {"name": "Test", "vertical": "fintech", "problem_statement": "",
               "exact_customer_phrases": [], "final_score": 8.0}
        dossier = dds._build_dossier(opp)
        assert "Test" in dossier
        assert "fintech" in dossier
        assert "problem_statement" not in dossier  # empty string omitted
        assert "exact_customer_phrases" not in dossier  # empty list omitted
