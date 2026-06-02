"""Tests for build_competitor_pricing_section() in validation_run."""


def test_build_competitor_pricing_section_returns_markdown():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {
        "name": "PayVE",
        "competitor_pricing_data": [
            {"price_usd": 29.0, "pricing_model": "monthly", "target_market": "SMB"}
        ],
    }
    result = build_competitor_pricing_section(opp)
    assert "## Competitor Pricing" in result
    assert "29.0" in result


def test_build_competitor_pricing_section_empty_when_no_data():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {"name": "PayVE", "competitor_pricing_data": None, "known_competitors": None}
    result = build_competitor_pricing_section(opp)
    assert result == ""


def test_build_competitor_pricing_section_handles_missing_fields():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {
        "name": "X",
        "competitor_pricing_data": [{"target_market": "SMB"}],  # no price_usd
    }
    result = build_competitor_pricing_section(opp)
    assert "## Competitor Pricing" in result
