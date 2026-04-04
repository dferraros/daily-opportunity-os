"""
Tavily Search client — structured web research for pain + distribution validation.

Uses TAVILY_API_KEY from .env. Falls back gracefully if key not set.
Tavily returns ranked results with title, URL, content snippet — far richer
than raw web_search tool output for structured extraction.

Cost: ~$0.004/search vs $0.01 for Anthropic web_search_20250305
"""

import json
import os
import time
from typing import Optional


MAX_RESULTS = 5       # 5 results per query gives enough signal
RATE_LIMIT_SECONDS = 0.5


def _load_tavily_key() -> Optional[str]:
    key = os.environ.get("TAVILY_API_KEY")
    if key:
        return key
    from pathlib import Path
    for parent in [Path(__file__).resolve().parent] + list(Path(__file__).resolve().parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TAVILY_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and not val.startswith("tvly-dev") or len(val) > 20:
                            return val
                        if val:
                            return val
            break
    return None


def search(query: str, max_results: int = MAX_RESULTS, search_depth: str = "basic") -> Optional[list[dict]]:
    """
    Execute a Tavily search. Returns list of result dicts with keys:
    title, url, content, score.

    Returns None if API unavailable.
    """
    api_key = _load_tavily_key()
    if not api_key:
        return None

    try:
        import httpx
    except ImportError:
        return None

    try:
        resp = httpx.post(
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
        if resp.status_code == 200:
            data = resp.json()
            return data.get("results", [])
        return None
    except Exception:
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
    return bool(_load_tavily_key())
