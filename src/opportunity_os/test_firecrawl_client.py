from unittest.mock import patch, MagicMock

import opportunity_os.firecrawl_client as fc


def test_scrape_structured_returns_dict_on_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"extract": {"price_usd": 99.0, "pricing_model": "monthly"}}
    with patch.object(fc, "_api_key", "test-key"), \
         patch("httpx.post", return_value=mock_resp):
        result = fc.scrape_structured("https://example.com/pricing", {})
    assert isinstance(result, dict)


def test_scrape_structured_returns_none_on_error():
    import httpx
    with patch.object(fc, "_api_key", "test-key"), \
         patch("httpx.post", side_effect=httpx.RequestError("network error")):
        result = fc.scrape_structured("https://example.com/pricing", {})
    assert result is None


def test_competitor_page_schema_has_required_keys():
    assert fc.COMPETITOR_PAGE_SCHEMA["type"] == "object"
    props = fc.COMPETITOR_PAGE_SCHEMA["properties"]
    for key in ("price_usd", "pricing_model", "key_features", "target_market"):
        assert key in props
