import pytest
from unittest.mock import patch, MagicMock


def test_search_news_counts_only_relevant_results():
    """Raw counts saturate at max_results for any broad query (every opp read
    news=cap on live data) -- only results scoring >= NEWS_RELEVANCE_MIN count."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": [
        {"title": "hot", "score": 0.9},
        {"title": "relevant", "score": 0.55},
        {"title": "filler", "score": 0.3},
        {"title": "noise", "score": 0.1},
        {"title": "no score"},
    ]}
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


def test_search_retries_transient_timeout_then_succeeds():
    """A single httpx timeout must not drop the result -- the retry helper
    recovers on the next attempt. Sleep is patched out so the test is instant."""
    import httpx

    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {"results": [{"title": "recovered"}]}
    flaky = [httpx.TimeoutException("transient"), ok]

    with patch("opportunity_os.tavily_client.httpx.post", side_effect=flaky):
        with patch("opportunity_os.tavily_client._api_key", "test-key"):
            with patch("opportunity_os.retry.time.sleep"):  # no real backoff wait
                from opportunity_os.tavily_client import search
                results = search("fintech")
    assert results == [{"title": "recovered"}]


def test_search_gives_up_after_persistent_timeouts():
    """Persistent transient errors exhaust retries and return None (not crash)."""
    import httpx

    with patch("opportunity_os.tavily_client.httpx.post",
               side_effect=httpx.TimeoutException("down")):
        with patch("opportunity_os.tavily_client._api_key", "test-key"):
            with patch("opportunity_os.retry.time.sleep"):
                from opportunity_os.tavily_client import search
                assert search("fintech") is None
