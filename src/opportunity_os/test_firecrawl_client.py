from unittest.mock import patch, MagicMock


def test_scrape_structured_returns_dict_on_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"extract": {"price_usd": 29.0, "pricing_model": "monthly"}}
    with patch("opportunity_os.firecrawl_client.httpx.post", return_value=mock_resp):
        with patch("opportunity_os.firecrawl_client._api_key", "test-key"):
            from opportunity_os.firecrawl_client import scrape_structured
            result = scrape_structured("https://example.com/pricing", {"price_usd": "float"})
            assert isinstance(result, dict)
            assert result.get("price_usd") == 29.0


def test_scrape_structured_returns_none_on_error():
    with patch("opportunity_os.firecrawl_client.httpx.post", side_effect=Exception("fail")):
        with patch("opportunity_os.firecrawl_client._api_key", "test-key"):
            from opportunity_os.firecrawl_client import scrape_structured
            result = scrape_structured("https://example.com", {})
            assert result is None


def test_competitor_page_schema_has_required_keys():
    from opportunity_os.firecrawl_client import COMPETITOR_PAGE_SCHEMA
    assert "price_usd" in COMPETITOR_PAGE_SCHEMA
    assert "pricing_model" in COMPETITOR_PAGE_SCHEMA
    assert "key_features" in COMPETITOR_PAGE_SCHEMA
    assert "target_market" in COMPETITOR_PAGE_SCHEMA
