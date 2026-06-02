"""Firecrawl client -- thin wrapper for crawling Reddit/forums for pain evidence.

Reads FIRECRAWL_API_KEY from .env. If not set, all functions return None gracefully.
Uses Firecrawl /v1/scrape endpoint to extract text content from target URLs.
"""

import logging
import os
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_api_key: Optional[str] = None  # populated lazily via _get_api_key()

BASE_URL = "https://api.firecrawl.dev"

# Target subreddits for pain evidence crawling
PAIN_EVIDENCE_URLS = [
    "https://www.reddit.com/r/vzla/search/?q={query}&sort=new",
    "https://www.reddit.com/r/Colombia/search/?q={query}&sort=new",
    "https://www.reddit.com/r/fintech/search/?q={query}&sort=new",
]

MAX_PHRASES = 5
RATE_LIMIT_SECONDS = 2.0

COMPETITOR_PAGE_SCHEMA: dict = {
    "price_usd": "float",
    "pricing_model": "str",
    "key_features": "list[str]",
    "target_market": "str",
}


def _load_firecrawl_key() -> Optional[str]:
    """Load FIRECRAWL_API_KEY from .env file or environment."""
    key = os.environ.get("FIRECRAWL_API_KEY")
    if key:
        return key
    from pathlib import Path
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FIRECRAWL_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val != "your_key_here":
                            return val
            break
    return None


def _get_api_key() -> Optional[str]:
    """Return module-level _api_key if set, otherwise load from env."""
    global _api_key
    if _api_key:
        return _api_key
    _api_key = _load_firecrawl_key()
    return _api_key


def crawl_pain_evidence(query: str, geography: str = "global") -> Optional[list[str]]:
    """
    Crawl Reddit/forums for pain evidence phrases matching the query.

    Returns list of up to MAX_PHRASES exact customer phrases, or None if Firecrawl unavailable.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    phrases = []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Filter URLs by geography
    urls = PAIN_EVIDENCE_URLS
    if geography == "venezuela":
        urls = [u for u in urls if "vzla" in u or "fintech" in u]
    elif geography in ("colombia", "latam"):
        urls = [u for u in urls if "Colombia" in u or "fintech" in u]

    for url_template in urls[:2]:  # max 2 URLs to stay within rate limits
        url = url_template.format(query=query.replace(" ", "+"))
        try:
            resp = httpx.post(
                f"{BASE_URL}/v1/scrape",
                headers=headers,
                json={"url": url, "formats": ["markdown"]},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("data", {}).get("markdown", "")
                # Extract short pain phrases (sentences with pain indicators)
                for line in content.split("\n"):
                    line = line.strip()
                    if len(line) > 20 and len(line) < 200:
                        pain_words = ["problema", "necesito", "frustrado", "dificil",
                                     "imposible", "caro", "lento", "malo", "no funciona",
                                     "pain", "struggle", "expensive", "broken", "need"]
                        if any(w in line.lower() for w in pain_words):
                            phrases.append(line[:200])
                            if len(phrases) >= MAX_PHRASES:
                                return phrases
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as exc:
            from opportunity_os.pipeline_monitor import log_failure
            log_failure("firecrawl_url", exc)
            continue

    return phrases if phrases else None


def scrape_structured(url: str, schema_dict: dict) -> Optional[dict]:
    """
    Scrape a URL and extract structured data matching schema_dict.
    Uses Firecrawl extract format. Returns None on any failure.
    """
    if not _api_key:
        return None
    try:
        resp = httpx.post(
            f"{BASE_URL}/v1/scrape",
            headers={"Authorization": f"Bearer {_api_key}", "Content-Type": "application/json"},
            json={
                "url": url,
                "formats": ["extract"],
                "extract": {"schema": schema_dict},
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("extract") or (data.get("data") or {}).get("extract")
    except Exception as exc:
        logger.warning("Firecrawl scrape_structured failed for %r: %s", url, exc)
        return None
