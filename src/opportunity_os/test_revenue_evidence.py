"""
Tests for revenue_evidence -- Tavily+Haiku funding/ARR/pricing extraction.

Covers: skip guard (30d TTL), graceful failures (no keys/competitors/results),
extraction robustness, TAM validation notes, model field round-trips, and
tam_engine preference for competitor_revenue/bottom_up methods.
"""
from datetime import datetime, timedelta
from opportunity_os import revenue_evidence
from opportunity_os.models import Opportunity


def base_opp(**over):
    """Minimal valid opportunity for testing."""
    opp = {
        "id": "test_1",
        "name": "Test PayTech SaaS",
        "geography": "latam",
        "vertical": "fintech",
        "direct_competitors": ["Stripe Latin", "Adyen"],
        "tam_usd_estimate": 500_000_000,  # $500M baseline TAM
    }
    opp.update(over)
    return opp


class TestBuildFundingQueries:
    def test_one_query_per_competitor_capped(self):
        opp = base_opp(direct_competitors=["A", "B", "C", "D"])
        qs = revenue_evidence._build_funding_queries(opp)
        assert len(qs) == revenue_evidence.MAX_COMPETITORS
        assert all("funding" in q or "Series" in q for q in qs)

    def test_fallback_to_category_when_no_competitors(self):
        opp = base_opp(direct_competitors=[], vertical="payments", geography="venezuela")
        qs = revenue_evidence._build_funding_queries(opp)
        assert len(qs) == 1
        assert "payments" in qs[0]
        assert "venezuela" in qs[0]

    def test_empty_when_nothing_to_search(self):
        opp = base_opp(direct_competitors=[], vertical="")
        assert revenue_evidence._build_funding_queries(opp) == []


class TestParseFundingExtraction:
    def test_valid_json(self):
        raw = '{"competitor_funding_raised": "$50M Series B", "competitor_arr_usd": 12500000}'
        result = revenue_evidence._parse_funding_extraction(raw)
        assert result["competitor_funding_raised"] == "$50M Series B"
        assert result["competitor_arr_usd"] == 12500000

    def test_arr_clamped_to_reasonable_range(self):
        # Negative ARR
        assert revenue_evidence._parse_funding_extraction('{"competitor_arr_usd": -1000}')["competitor_arr_usd"] is None
        # Zero ARR
        assert revenue_evidence._parse_funding_extraction('{"competitor_arr_usd": 0}')["competitor_arr_usd"] is None
        # Absurdly high
        assert revenue_evidence._parse_funding_extraction('{"competitor_arr_usd": 9999999999}')["competitor_arr_usd"] is None
        # Valid range
        result = revenue_evidence._parse_funding_extraction('{"competitor_arr_usd": 5000000}')
        assert result["competitor_arr_usd"] == 5000000

    def test_missing_arr_is_ok(self):
        raw = '{"competitor_funding_raised": "$10M Seed", "competitor_arr_usd": null}'
        result = revenue_evidence._parse_funding_extraction(raw)
        assert result["competitor_funding_raised"] == "$10M Seed"
        assert result["competitor_arr_usd"] is None

    def test_markdown_fenced(self):
        raw = '```json\n{"competitor_funding_raised": "$25M Series A", "competitor_arr_usd": 6000000}\n```'
        result = revenue_evidence._parse_funding_extraction(raw)
        assert result["competitor_funding_raised"] == "$25M Series A"
        assert result["competitor_arr_usd"] == 6000000

    def test_malformed_returns_none(self):
        assert revenue_evidence._parse_funding_extraction("garbage") is None
        assert revenue_evidence._parse_funding_extraction('{"invalid": "json"') is None


class TestPricingExtraction:
    def test_valid_json(self):
        raw = '{"competitor_pricing_model": "SaaS $29-99/mo per location", "tam_annual_price_usd": 45000}'
        result = revenue_evidence._parse_pricing_extraction(raw)
        assert result["competitor_pricing_model"] == "SaaS $29-99/mo per location"
        assert result["tam_annual_price_usd"] == 45000

    def test_price_clamped_to_reasonable_range(self):
        # Negative price
        assert revenue_evidence._parse_pricing_extraction('{"tam_annual_price_usd": -100}')["tam_annual_price_usd"] is None
        # Zero price
        assert revenue_evidence._parse_pricing_extraction('{"tam_annual_price_usd": 0}')["tam_annual_price_usd"] is None
        # Absurdly high ($10M+/year)
        assert revenue_evidence._parse_pricing_extraction('{"tam_annual_price_usd": 10000001}')["tam_annual_price_usd"] is None
        # Valid range
        result = revenue_evidence._parse_pricing_extraction('{"tam_annual_price_usd": 500000}')
        assert result["tam_annual_price_usd"] == 500000

    def test_markdown_fenced(self):
        raw = '```json\n{"competitor_pricing_model": "Usage-based $0.05/tx", "tam_annual_price_usd": 15000}\n```'
        result = revenue_evidence._parse_pricing_extraction(raw)
        assert result["competitor_pricing_model"] == "Usage-based $0.05/tx"


class TestFreshGuard:
    def test_fresh_within_ttl(self):
        stamp = (datetime.now() - timedelta(days=15)).isoformat()
        opp = base_opp(revenue_evidence_at=stamp)
        assert revenue_evidence._is_fresh(opp) is True

    def test_stale_beyond_ttl(self):
        stamp = (datetime.now() - timedelta(days=35)).isoformat()
        opp = base_opp(revenue_evidence_at=stamp)
        assert revenue_evidence._is_fresh(opp) is False

    def test_missing_stamp_not_fresh(self):
        opp = base_opp()
        assert revenue_evidence._is_fresh(opp) is False

    def test_invalid_timestamp_not_fresh(self):
        opp = base_opp(revenue_evidence_at="garbage")
        assert revenue_evidence._is_fresh(opp) is False


class TestSearchFundingEvidence:
    def test_skips_if_fresh(self, monkeypatch):
        stamp = (datetime.now() - timedelta(days=15)).isoformat()
        opp = base_opp(revenue_evidence_at=stamp)
        result = revenue_evidence.search_funding_evidence(opp)
        assert result == {}

    def test_skips_without_tavily_key(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: False)
        opp = base_opp()
        result = revenue_evidence.search_funding_evidence(opp)
        assert result == {}

    def test_returns_empty_when_no_competitors(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        opp = base_opp(direct_competitors=[], vertical="")
        result = revenue_evidence.search_funding_evidence(opp)
        assert result == {}

    def test_returns_empty_on_no_search_results(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(revenue_evidence.tavily_client, "search_with_content",
                            lambda q, max_results: [])
        opp = base_opp()
        result = revenue_evidence.search_funding_evidence(opp)
        assert result == {}

    def test_returns_empty_on_extraction_failure(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(revenue_evidence.tavily_client, "search_with_content",
                            lambda q, max_results: [{"url": "http://x", "content": "some text"}])
        monkeypatch.setattr(revenue_evidence, "_extract_funding", lambda opp, digest: None)
        opp = base_opp()
        result = revenue_evidence.search_funding_evidence(opp)
        assert result == {}

    def test_success_returns_updates_dict(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(revenue_evidence.tavily_client, "search_with_content",
                            lambda q, max_results: [
                                {"url": "http://techcrunch.com/1", "content": "raised 50M"},
                                {"url": "http://crunchbase.com/1", "content": "ARR 15M"}
                            ])
        monkeypatch.setattr(revenue_evidence, "_extract_funding", lambda opp, digest: {
            "competitor_funding_raised": "$50M Series B",
            "competitor_arr_usd": 15000000,
        })
        opp = base_opp()
        result = revenue_evidence.search_funding_evidence(opp)
        assert result["competitor_funding_raised"] == "$50M Series B"
        assert result["competitor_arr_usd"] == 15000000
        assert isinstance(result["revenue_evidence_sources"], list)
        assert all("url" in s and "claim" in s for s in result["revenue_evidence_sources"])

    def test_sources_only_added_when_evidence_found(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(revenue_evidence.tavily_client, "search_with_content",
                            lambda q, max_results: [{"url": "http://x", "content": "text"}])
        monkeypatch.setattr(revenue_evidence, "_extract_funding", lambda opp, digest: {
            "competitor_funding_raised": None,
            "competitor_arr_usd": None,
        })
        opp = base_opp()
        result = revenue_evidence.search_funding_evidence(opp)
        # No evidence found, so sources should be None or empty
        assert result.get("revenue_evidence_sources") is None


class TestScrapePricingEvidence:
    def test_skips_if_fresh(self, monkeypatch):
        stamp = (datetime.now() - timedelta(days=15)).isoformat()
        opp = base_opp(revenue_evidence_at=stamp)
        result = revenue_evidence.scrape_pricing_evidence(opp)
        assert result == {}

    def test_returns_empty_when_no_competitors(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        opp = base_opp(direct_competitors=[])
        result = revenue_evidence.scrape_pricing_evidence(opp)
        assert result == {}

    def test_success_returns_pricing_dict(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(revenue_evidence.tavily_client, "search_with_content",
                            lambda q, max_results: [{"url": "http://stripe.com/pricing", "content": "29 per month"}])
        monkeypatch.setattr(revenue_evidence, "_extract_pricing", lambda opp, digest: {
            "competitor_pricing_model": "SaaS $29-99/mo",
            "tam_annual_price_usd": 45000,
        })
        opp = base_opp()
        result = revenue_evidence.scrape_pricing_evidence(opp)
        assert result["competitor_pricing_model"] == "SaaS $29-99/mo"
        assert result["tam_annual_price_usd"] == 45000


class TestRunRevenueEvidence:
    def test_returns_opp_unchanged_if_fresh(self, monkeypatch):
        stamp = (datetime.now() - timedelta(days=15)).isoformat()
        opp = base_opp(revenue_evidence_at=stamp)
        original = dict(opp)
        result = revenue_evidence.run_revenue_evidence(opp)
        assert result == original

    def test_returns_opp_unchanged_if_no_evidence_found(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence, "search_funding_evidence", lambda opp, force=False: {})
        monkeypatch.setattr(revenue_evidence, "scrape_pricing_evidence", lambda opp, force=False: {})
        opp = base_opp()
        result = revenue_evidence.run_revenue_evidence(opp)
        assert result == opp

    def test_merges_all_evidence_fields(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence, "search_funding_evidence", lambda opp, force=False: {
            "competitor_funding_raised": "$50M Series B",
            "competitor_arr_usd": 12000000,
            "revenue_evidence_sources": [{"url": "http://x", "claim": "funding"}],
        })
        monkeypatch.setattr(revenue_evidence, "scrape_pricing_evidence", lambda opp, force=False: {
            "competitor_pricing_model": "SaaS $29-99/mo",
            "tam_annual_price_usd": 45000,
        })
        opp = base_opp()
        result = revenue_evidence.run_revenue_evidence(opp)
        assert result["competitor_funding_raised"] == "$50M Series B"
        assert result["competitor_arr_usd"] == 12000000
        assert result["competitor_pricing_model"] == "SaaS $29-99/mo"
        assert result["tam_annual_price_usd"] == 45000
        assert result["revenue_evidence_at"]

    def test_builds_tam_validation_note(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence, "search_funding_evidence", lambda opp, force=False: {
            "competitor_arr_usd": 10_000_000,  # $10M ARR
        })
        monkeypatch.setattr(revenue_evidence, "scrape_pricing_evidence", lambda opp, force=False: {})
        opp = base_opp(tam_usd_estimate=200_000_000)  # $200M existing TAM
        result = revenue_evidence.run_revenue_evidence(opp)
        # Competitor with $10M ARR at 5% share implies $200M TAM
        assert result["tam_validation_note"]
        assert "Competitor ARR" in result["tam_validation_note"]
        assert "$10000000" in result["tam_validation_note"] or "$10M" in result["tam_validation_note"] or "10000000" in result["tam_validation_note"]

    def test_does_not_mutate_input_opp(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence, "search_funding_evidence", lambda opp, force=False: {
            "competitor_arr_usd": 5000000,
        })
        monkeypatch.setattr(revenue_evidence, "scrape_pricing_evidence", lambda opp, force=False: {})
        opp = base_opp()
        original_keys = set(opp.keys())
        result = revenue_evidence.run_revenue_evidence(opp)
        # Input opp should not be mutated
        assert set(opp.keys()) == original_keys
        # Result should have new keys
        assert set(result.keys()) > set(opp.keys())


class TestModelFieldRoundTrip:
    def test_opportunity_model_includes_revenue_evidence_fields(self):
        """Verify all revenue_evidence fields exist in Opportunity model."""
        opp = Opportunity.empty()
        # These fields should serialize and deserialize without dropping
        fields = [
            "competitor_funding_raised",
            "competitor_arr_usd",
            "competitor_pricing_model",
            "tam_annual_price_usd",
            "revenue_evidence_sources",
            "revenue_evidence_at",
            "tam_validation_note",
        ]
        for field in fields:
            assert hasattr(opp, field), f"Opportunity missing field {field}"

    def test_jsonl_round_trip_preserves_revenue_fields(self):
        """Verify fields survive JSONL serialization."""
        opp = Opportunity.empty(
            name="Test",
            geography="latam",
            vertical="fintech",
            target_customer="SMBs",
            problem_statement="Problem",
            trigger_signal="Signal",
        )
        # Set revenue evidence fields
        opp_dict = opp.model_dump()
        opp_dict.update({
            "competitor_funding_raised": "$50M Series B",
            "competitor_arr_usd": 15000000,
            "competitor_pricing_model": "SaaS $29-99/mo",
            "tam_annual_price_usd": 45000,
            "revenue_evidence_sources": [{"url": "http://x", "claim": "test"}],
            "revenue_evidence_at": datetime.now().isoformat(),
            "tam_validation_note": "Test note",
        })
        # Round-trip through JSONL
        opp2 = Opportunity(**opp_dict)
        opp2_dict = opp2.model_dump()

        assert opp2_dict["competitor_funding_raised"] == "$50M Series B"
        assert opp2_dict["competitor_arr_usd"] == 15000000
        assert opp2_dict["competitor_pricing_model"] == "SaaS $29-99/mo"
        assert opp2_dict["tam_annual_price_usd"] == 45000
        assert opp2_dict["revenue_evidence_sources"]
        assert opp2_dict["revenue_evidence_at"]
        assert opp2_dict["tam_validation_note"] == "Test note"


class TestTAMEngineIntegration:
    def test_tam_prefers_competitor_revenue_method(self):
        """Verify tam_engine uses competitor_revenue when competitor_arr_usd present."""
        from opportunity_os.engines.tam_engine import estimate_tam_from_opp
        opp = base_opp(
            competitor_arr_usd=5_000_000,  # $5M ARR
            tam_target_customers=50_000,
            tam_annual_price_usd=100,
        )
        result = estimate_tam_from_opp(opp)
        # Should use competitor_revenue method (which back-calculates from ARR)
        assert result["tam_method"] == "competitor_revenue"
        # At 5% market share, $5M ARR implies $100M TAM
        assert result["tam_usd_estimate"] is not None
        assert result["tam_usd_estimate"] > 0

    def test_tam_uses_bottom_up_with_revenue_evidence_price(self):
        """Verify tam_engine uses bottom_up when tam_annual_price_usd from revenue_evidence."""
        from opportunity_os.engines.tam_engine import estimate_tam_from_opp
        opp = base_opp(
            competitor_arr_usd=None,
            tam_target_customers=100_000,
            tam_annual_price_usd=45_000,  # from revenue_evidence
        )
        result = estimate_tam_from_opp(opp)
        assert result["tam_method"] == "bottom_up"
        # 100k customers × $45k/year = $4.5B
        assert result["tam_usd_estimate"] is not None

    def test_tam_falls_back_to_proxy_when_no_evidence(self):
        """Verify tam_engine falls back to proxy when no revenue_evidence data."""
        from opportunity_os.engines.tam_engine import estimate_tam_from_opp
        opp = base_opp(
            competitor_arr_usd=None,
            tam_annual_price_usd=None,
            tam_target_customers=None,
            tam_total_market_usd=None,
        )
        result = estimate_tam_from_opp(opp)
        assert result["tam_method"] == "proxy"
        assert result["tam_usd_estimate"] is not None


class TestPricingCitations:
    """Review fix 2026-07-27: pricing evidence must carry a citation trail --
    tam_annual_price_usd feeds the TAM engine and uncited claims are banned."""

    def test_pricing_sources_merged_into_revenue_evidence_sources(self, monkeypatch):
        monkeypatch.setattr(revenue_evidence.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(
            revenue_evidence.tavily_client, "search_with_content",
            lambda q, max_results=5: [
                {"url": "https://competitor.com/pricing", "content": "Pro plan $49/mo"}
            ],
        )
        from opportunity_os import firecrawl_client
        monkeypatch.setattr(firecrawl_client, "scrape_structured", lambda url, schema: None)
        monkeypatch.setattr(revenue_evidence, "_extract_funding", lambda opp, digest: None)
        monkeypatch.setattr(revenue_evidence, "_extract_pricing", lambda opp, digest: {
            "competitor_pricing_model": "SaaS $49/mo",
            "tam_annual_price_usd": 588.0,
        })
        result = revenue_evidence.run_revenue_evidence(base_opp())
        sources = result["revenue_evidence_sources"]
        assert sources, "pricing evidence must produce citations"
        assert any(s["url"] == "https://competitor.com/pricing" for s in sources)
        assert any(s["claim"] == "pricing evidence" for s in sources)
        # The intermediate key must not leak onto the record
        assert "pricing_evidence_sources" not in result

    def test_pricing_query_targets_open_web_not_news_sites(self):
        qs = revenue_evidence._build_pricing_queries(base_opp())
        assert qs and all("site:" not in q for q in qs), (
            "site: allowlists exclude the competitor's own pricing page"
        )
