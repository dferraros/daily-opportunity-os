"""Tests for Tavily news signal in research_opportunity_free."""
from unittest.mock import patch

import opportunity_os.free_research as fr
import opportunity_os.tavily_client as tc


def test_news_signal_count_populated():
    """research_opportunity_free sets news_signal_count from search_news result."""
    opp = {"name": "test-opp", "vertical": "fintech", "geography": "venezuela"}
    with patch.object(tc, "search_news", return_value=7) as mock_news, \
         patch.object(fr, "jina_search", return_value=[]), \
         patch.object(fr, "search_hn", return_value=[]), \
         patch.object(fr, "search_reddit_official", return_value=[]), \
         patch.object(fr, "serper_search", return_value=[]), \
         patch.object(fr, "exa_search", return_value=[]):
        updates = fr.research_opportunity_free(opp)
    assert updates.get("news_signal_count") == 7
    mock_news.assert_called_once()


def test_news_signal_count_zero_stored():
    """news_signal_count is 0 (not None) when Tavily finds no news."""
    opp = {"name": "obscure-niche", "vertical": "", "geography": "global"}
    with patch.object(tc, "search_news", return_value=0), \
         patch.object(fr, "jina_search", return_value=[]), \
         patch.object(fr, "search_hn", return_value=[]), \
         patch.object(fr, "search_reddit_official", return_value=[]), \
         patch.object(fr, "serper_search", return_value=[]), \
         patch.object(fr, "exa_search", return_value=[]):
        updates = fr.research_opportunity_free(opp)
    assert updates.get("news_signal_count") == 0
