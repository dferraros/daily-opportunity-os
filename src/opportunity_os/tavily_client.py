"""
Tavily Search client — structured web research for pain + distribution validation.

Uses TAVILY_API_KEY from .env. Falls back gracefully if key not set.
Tavily returns ranked results with title, URL, content snippet — far richer
than raw web_search tool output for structured extraction.

Cost: ~$0.004/search vs $0.01 for Anthropic web_search_20250305
"""

import logging
import time
from typing import Optional

import httpx

from opportunity_os.retry import call_with_retry

logger = logging.getLogger(__name__)

MAX_RESULTS = 5       # 5 results per query gives enough signal
RATE_LIMIT_SECONDS = 0.5
# httpx transient failures worth retrying: timeouts, connection resets, pool drains.
_RETRYABLE_HTTP_ERRORS = (httpx.TimeoutException, httpx.TransportError)

_api_key: Optional[str] = None  # populated lazily via _load_tavily_key()


def _load_tavily_key() -> Optional[str]:
    from opportunity_os.env import get_key
    return get_key("TAVILY_API_KEY")


def _get_api_key() -> Optional[str]:
    """Return module-level _api_key if set, otherwise load from env."""
    global _api_key
    if _api_key:
        return _api_key
    _api_key = _load_tavily_key()
    return _api_key


def search(query: str, max_results: int = MAX_RESULTS, search_depth: str = "basic") -> Optional[list[dict]]:
    """
    Execute a Tavily search. Returns list of result dicts with keys:
    title, url, content, score.

    Returns None if API unavailable.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    def _post():
        return httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=20.0,
        )

    try:
        # Retry transient network failures (timeout/reset); a single blip should
        # not silently drop a research result. Non-200 is not retried -- the
        # server is answering, just not with data we want.
        resp = call_with_retry(
            _post, retry_on=_RETRYABLE_HTTP_ERRORS, label=f"tavily.search({query[:40]!r})"
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
        return None
    except Exception as exc:
        logger.warning("Tavily search failed for %r: %s", query, exc)
        return None


def search_multi(queries: list[str], max_results_per_query: int = 3) -> str:
    """
    Run multiple Tavily searches and return concatenated results as a text block
    suitable for passing to Claude for extraction.

    Returns empty string if Tavily unavailable.
    """
    if not queries:
        return ""

    all_text = []
    for i, query in enumerate(queries[:3]):  # max 3 queries per opp
        results = search(query, max_results=max_results_per_query)
        if results:
            all_text.append(f"### Search: {query}")
            for r in results:
                title = r.get("title", "")
                url = r.get("url", "")
                content = (r.get("content") or "")[:400]
                all_text.append(f"**{title}** ({url})\n{content}")
            all_text.append("")
        if i < len(queries) - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    return "\n".join(all_text)


def is_available() -> bool:
    """Check if Tavily key is configured."""
    return bool(_get_api_key())


NEWS_MAX_RESULTS = 20      # headroom for the relevance filter below
NEWS_RELEVANCE_MIN = 0.5   # only count results Tavily scores as genuinely relevant


def search_news(query: str, time_range: str = "month") -> int:
    """Return count of RELEVANT news results in the time window (0-20). Returns 0 on any failure.

    Raw result counts cannot discriminate: Tavily is a relevance-ranked search
    and fills max_results for any broad query (every opp read news=cap). Counting
    only results with relevance score >= NEWS_RELEVANCE_MIN restores variance --
    strong-momentum topics have many highly-relevant recent articles, weak ones
    pad the list with low-relevance filler.

    Cost: 1 credit per call regardless of max_results.
    """
    api_key = _get_api_key()
    if not api_key:
        return 0
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": NEWS_MAX_RESULTS,
                "topic": "news",
                "time_range": time_range,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=20.0,
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        return sum(
            1 for r in results
            if float(r.get("score") or 0) >= NEWS_RELEVANCE_MIN
        )
    except Exception as exc:
        logger.warning("Tavily search_news failed for %r: %s", query, exc)
        return 0


def search_with_content(query: str, max_results: int = 5) -> Optional[list[dict]]:
    """Search with raw content included. Returns None on failure."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
                "include_answer": False,
                "include_raw_content": True,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json().get("results") or []
    except Exception as exc:
        logger.warning("Tavily search_with_content failed for %r: %s", query, exc)
        return None
