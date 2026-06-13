"""
Tests for competitor_intelligence -- the Tavily+Haiku G2 retool.

Covers query construction, extraction parsing/clamping, the never-fabricate
graceful-fail contract, and the verbatim-phrases-only-if-empty rule.
"""
from opportunity_os import competitor_intelligence as ci


def base_opp(**over):
    opp = {"name": "Test Opp", "vertical": "fintech",
           "direct_competitors": ["Acme Pay", "Beta Bank"]}
    opp.update(over)
    return opp


class TestBuildCompetitorQueries:
    def test_one_query_per_competitor_capped(self):
        opp = base_opp(direct_competitors=["A", "B", "C", "D"])
        qs = ci.build_competitor_queries(opp)
        assert len(qs) == ci.MAX_COMPETITORS
        assert all("reviews complaints" in q for q in qs)

    def test_name_keywords_preferred_over_internal_labels(self):
        # The name carries real product keywords; bucket/vertical are internal labels.
        qs = ci.build_competitor_queries(
            {"name": "E-Invoicing Compliance SaaS for Mandatory LATAM Regulations",
             "vertical": "smb_software", "bucket": "latam_asymmetry", "direct_competitors": []}
        )
        assert "Invoicing" in qs[0] or "LATAM" in qs[0]
        assert "smb_software" not in qs[0]
        assert "latam_asymmetry" not in qs[0]

    def test_snake_case_bucket_skipped_as_internal_label(self):
        # No usable name -> snake_case bucket is an internal taxonomy label, skip to vertical
        qs = ci.build_competitor_queries(
            {"name": "", "bucket": "latam_asymmetry", "vertical": "logistics", "direct_competitors": []}
        )
        assert "logistics" in qs[0]
        assert "latam_asymmetry" not in qs[0]

    def test_vertical_fallback_when_only_vertical(self):
        qs = ci.build_competitor_queries({"vertical": "logistics", "direct_competitors": []})
        assert len(qs) == 1
        assert "logistics" in qs[0]

    def test_empty_when_nothing_to_search(self):
        assert ci.build_competitor_queries({"direct_competitors": []}) == []


class TestParseExtraction:
    def test_valid_json(self):
        raw = ('{"competitor_negative_review_rate": 0.7, '
               '"complaint_themes": ["slow support", "buggy"], '
               '"verbatim_phrases": ["support takes days"]}')
        result = ci._parse_extraction(raw)
        assert result["competitor_negative_review_rate"] == 0.7
        assert result["competitor_complaint_themes"] == ["slow support", "buggy"]
        assert result["exact_customer_phrases"] == ["support takes days"]

    def test_rate_clamped(self):
        assert ci._parse_extraction('{"competitor_negative_review_rate": 1.8}')["competitor_negative_review_rate"] == 1.0
        assert ci._parse_extraction('{"competitor_negative_review_rate": -0.5}')["competitor_negative_review_rate"] == 0.0

    def test_lists_capped_at_three(self):
        raw = ('{"competitor_negative_review_rate": 0.5, '
               '"complaint_themes": ["a","b","c","d","e"]}')
        assert len(ci._parse_extraction(raw)["competitor_complaint_themes"]) == 3

    def test_missing_rate_returns_none(self):
        assert ci._parse_extraction('{"complaint_themes": ["x"]}') is None

    def test_malformed_returns_none(self):
        assert ci._parse_extraction("garbage") is None
        assert ci._parse_extraction('{"competitor_negative_review_rate": "bad"}') is None

    def test_markdown_fenced(self):
        raw = '```json\n{"competitor_negative_review_rate": 0.4}\n```'
        assert ci._parse_extraction(raw)["competitor_negative_review_rate"] == 0.4


class TestAnalyzeGracefulFail:
    def test_empty_when_tavily_unavailable(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: False)
        assert ci.analyze_competitor_weakness(base_opp()) == {}

    def test_empty_when_no_competitors_or_vertical(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        assert ci.analyze_competitor_weakness({"name": "x", "direct_competitors": []}) == {}

    def test_empty_when_search_returns_nothing(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: [])
        assert ci.analyze_competitor_weakness(base_opp()) == {}

    def test_empty_when_extraction_fails(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: [{"content": "users complain about X"}])
        monkeypatch.setattr(ci, "_extract_weakness", lambda opp, digest: None)
        assert ci.analyze_competitor_weakness(base_opp()) == {}

    def test_fresh_within_ttl_skipped(self, monkeypatch):
        monkeypatch.setattr(ci, "_is_fresh", lambda o: True)
        called = {"searched": False}
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: called.__setitem__("searched", True) or [])
        assert ci.analyze_competitor_weakness(base_opp(competitor_research_at="x")) == {}
        assert called["searched"] is False

    def test_success_returns_updates_without_mutating_input(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: [{"content": "support takes days, very buggy"}])
        monkeypatch.setattr(ci, "_extract_weakness", lambda opp, digest: {
            "competitor_negative_review_rate": 0.65,
            "competitor_complaint_themes": ["slow support"],
            "exact_customer_phrases": ["support takes days"],
        })
        opp = base_opp()
        updates = ci.analyze_competitor_weakness(opp)
        assert updates["competitor_negative_review_rate"] == 0.65
        assert updates["exact_customer_phrases"] == ["support takes days"]
        assert updates["competitor_signal_basis"] == "named_competitors"
        assert updates["competitor_research_at"]
        assert "competitor_research_at" not in opp  # input not mutated

    def test_basis_tagged_category_fallback_when_no_named_competitors(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: [{"content": "buggy and slow"}])
        monkeypatch.setattr(ci, "_extract_weakness", lambda opp, digest: {
            "competitor_negative_review_rate": 0.3,
            "competitor_complaint_themes": ["slow"],
            "exact_customer_phrases": [],
        })
        opp = {"name": "E-Invoicing SaaS", "vertical": "smb_software", "direct_competitors": []}
        updates = ci.analyze_competitor_weakness(opp)
        assert updates["competitor_signal_basis"] == "category_fallback"

    def test_does_not_overwrite_existing_phrases(self, monkeypatch):
        monkeypatch.setattr(ci.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(ci.tavily_client, "search_with_content",
                            lambda q, max_results=3: [{"content": "buggy"}])
        monkeypatch.setattr(ci, "_extract_weakness", lambda opp, digest: {
            "competitor_negative_review_rate": 0.5,
            "competitor_complaint_themes": [],
            "exact_customer_phrases": ["new phrase"],
        })
        opp = base_opp(exact_customer_phrases=["existing real phrase"])
        updates = ci.analyze_competitor_weakness(opp)
        assert "exact_customer_phrases" not in updates  # existing phrases preserved
