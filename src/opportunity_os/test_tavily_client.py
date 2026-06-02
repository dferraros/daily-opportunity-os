import pytest
from unittest.mock import patch, MagicMock


def test_search_news_returns_int_on_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": [{"title": "a"}, {"title": "b"}]}
    with patch("opportunity_os.tavily_client.httpx.post", return_value=mock_resp):
        with patch("opportunity_os.tavily_client._api_key", "test-key"):
            from opportunity_os.tavily_client import search_news
            count = search_news("fintech venezuela")
            assert isinstance(count, int)
            assert count == 2


def test_search_news_returns_zero_on_error():
    with patch("opportunity_os.tavily_client.httpx.post", side_effect=Exception("fail")):
        with patch("opportunity_os.tavily_client._api_key", "test-key"):
            from opportunity_os.tavily_client import search_news
            count = search_news("anything")
            assert count == 0


def test_search_with_content_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": [{"url": "http://a.com", "raw_content": "text"}]}
    with patch("opportunity_os.tavily_client.httpx.post", return_value=mock_resp):
        with patch("opportunity_os.tavily_client._api_key", "test-key"):
            from opportunity_os.tavily_client import search_with_content
            results = search_with_content("fintech")
            assert isinstance(results, list)
            assert len(results) == 1
