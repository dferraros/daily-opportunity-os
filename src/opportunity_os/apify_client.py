"""
Apify client -- thin wrapper for running Apify actors to gather market signals.

Reads APIFY_API_TOKEN from .env. If not set, all functions return safe defaults.
Supports LinkedIn job-count scraping and G2 review sentiment extraction.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from apify_client import ApifyClient
except ImportError:
    ApifyClient = None  # type: ignore


def _load_apify_key() -> Optional[str]:
    """Walk up from this file looking for a .env with APIFY_API_TOKEN."""
    key = os.environ.get("APIFY_API_TOKEN")
    if key:
        return key
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("APIFY_API_TOKEN="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val != "your_key_here":
                            return val
            break
    return None


@lru_cache(maxsize=1)
def _get_api_key() -> Optional[str]:
    """Return the Apify API key, caching the result for the process lifetime."""
    return _load_apify_key()


def run_actor(actor_id: str, run_input: dict, timeout_secs: int = 120) -> list[dict]:
    """Run an Apify actor synchronously; return dataset items or [] on failure."""
    if ApifyClient is None:
        logger.warning("apify-client not installed; cannot run actor %r", actor_id)
        return []

    api_key = _get_api_key()
    if not api_key:
        logger.warning("APIFY_API_TOKEN not set; cannot run actor %r", actor_id)
        return []

    try:
        client = ApifyClient(api_key)
        run = client.actor(actor_id).call(run_input=run_input, timeout_secs=timeout_secs)
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        return list(items)
    except Exception as exc:
        logger.warning("Apify run_actor failed for %r: %s", actor_id, exc, exc_info=True)
        return []


def fetch_linkedin_jobs(vertical: str, geography: str, max_results: int = 50) -> int:
    """Return count of LinkedIn job postings for a vertical+geo combo, or 0 on failure."""
    run_input = {
        "queries": [f"{vertical} {geography}"],
        "maxItems": max_results,
    }
    items = run_actor("curious_coder/linkedin-jobs-scraper", run_input)
    return len(items)


def fetch_g2_reviews(category: str, max_results: int = 100) -> dict:
    """Return {neg_rate: float, top_complaints: list[str]} for a G2 category, or {} on failure."""
    run_input = {
        "category": category,
        "maxItems": max_results,
    }
    items = run_actor("thirdwatch/g2-software-reviews-scraper", run_input)
    if not items:
        return {}

    neg_count = sum(1 for item in items if item.get("rating", 5) <= 2)
    neg_rate = neg_count / len(items)

    complaints: list[str] = []
    seen: set[str] = set()
    for item in items:
        if len(complaints) >= 3:
            break
        text = (
            item.get("cons")
            or item.get("negativeReview")
            or ""
        ).strip()
        if text and text not in seen:
            seen.add(text)
            complaints.append(text)

    return {"neg_rate": neg_rate, "top_complaints": complaints}


def is_available() -> bool:
    """Check if Apify token is configured."""
    return bool(_get_api_key())
