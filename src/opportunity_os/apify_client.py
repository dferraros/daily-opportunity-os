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


MAX_CHARGE_PER_RUN_USD = "0.25"  # hard cost cap per actor run (pay-per-result safety net)


def run_actor(
    actor_id: str,
    run_input: dict,
    timeout_secs: int = 120,
    max_items: Optional[int] = None,
) -> list[dict]:
    """Run an Apify actor synchronously; return dataset items or [] on failure.

    Cost guards: max_items caps billable results at the platform level for
    pay-per-result actors; max_total_charge_usd hard-stops any single run at
    MAX_CHARGE_PER_RUN_USD regardless of actor pricing model.
    """
    if ApifyClient is None:
        logger.warning("apify-client not installed; cannot run actor %r", actor_id)
        return []

    api_key = _get_api_key()
    if not api_key:
        logger.warning("APIFY_API_TOKEN not set; cannot run actor %r", actor_id)
        return []

    try:
        from datetime import timedelta
        from decimal import Decimal

        client = ApifyClient(api_key)
        run = client.actor(actor_id).call(
            run_input=run_input,
            run_timeout=timedelta(seconds=timeout_secs),
            max_items=max_items,
            max_total_charge_usd=Decimal(MAX_CHARGE_PER_RUN_USD),
        )
        if run is None:
            logger.warning("Apify actor %r returned no run (timeout or abort)", actor_id)
            return []
        try:
            dataset_id = run["defaultDatasetId"]
        except (TypeError, KeyError):
            dataset_id = getattr(run, "default_dataset_id", None)
        if not dataset_id:
            logger.warning("Apify actor %r run has no dataset id", actor_id)
            return []
        items = client.dataset(dataset_id).list_items().items
        return list(items)
    except Exception as exc:
        logger.warning("Apify run_actor failed for %r: %s", actor_id, exc, exc_info=True)
        return []


_LINKEDIN_GEO = {
    "venezuela": "Venezuela",
    "spain": "Spain",
    "us": "United States",
    "latam": "Latin America",
    "colombia": "Colombia",
    "mexico": "Mexico",
    "argentina": "Argentina",
}


def fetch_linkedin_jobs(vertical: str, geography: str, max_results: int = 50) -> int:
    """Return count of LinkedIn job postings for a vertical+geo combo, or 0 on failure.

    The actor requires LinkedIn jobs-search URLs (input schema: urls + count),
    so we build one from keywords + mapped location.
    """
    import urllib.parse

    location = _LINKEDIN_GEO.get((geography or "").lower())
    if location:
        params = {"keywords": vertical, "location": location}
    else:
        params = {"keywords": f"{vertical} {geography}".strip()}
    search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)

    run_input = {
        "urls": [search_url],
        "count": max(10, max_results),  # actor validation: count must be >= 10
        "scrapeCompany": False,
    }
    items = run_actor("curious_coder/linkedin-jobs-scraper", run_input, max_items=max_results)
    return len(items)


def fetch_g2_reviews(category: str, max_results: int = 100) -> dict:
    """Return {neg_rate: float, top_complaints: list[str]} for a G2 category, or {} on failure."""
    # Input schema: categories (array) + maxResults + scrapeReviews
    run_input = {
        "categories": [category],
        "maxResults": max_results,
        "scrapeReviews": True,
    }
    items = run_actor("thirdwatch/g2-software-reviews-scraper", run_input, max_items=max_results)
    if not items:
        return {}

    # Category mode can return product summaries (rating: null, 404 pages) instead
    # of individual reviews. Only items with a numeric rating carry usable
    # negative-rate semantics; anything else is skipped, never crashed on.
    rated = [i for i in items if isinstance(i.get("rating"), (int, float))]
    if not rated:
        logger.info(
            "[apify] G2 returned %d item(s) but none with usable ratings for %r -- skipping",
            len(items), category,
        )
        return {}

    neg_count = sum(1 for item in rated if item["rating"] <= 2)
    neg_rate = neg_count / len(rated)

    complaints: list[str] = []
    seen: set[str] = set()
    for item in rated:
        if len(complaints) >= 3:
            break
        text = (
            item.get("cons")
            or item.get("cons_summary")
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
