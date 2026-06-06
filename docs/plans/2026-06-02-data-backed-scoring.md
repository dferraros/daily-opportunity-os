# Data-Backed Scoring Upgrade — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace AI-guessed scoring with empirically-measured signals from Tavily news search, Firecrawl competitor scraping, and Apify LinkedIn/G2 data.

**Architecture:** Add three new data adapters (Tavily news, Firecrawl structured extraction, Apify actors), pipe their outputs into 8 new Opportunity model fields, derive two new scoring dimensions (market_momentum_score, competitor_weakness_score) from real data in a pre-processing hook, and integrate the enrichment steps into the daily pipeline.

**Tech Stack:** Python 3.11+, uv, httpx, apify-client PyPI package, Pydantic v2, existing scoring_engine.py pre-processing pattern

---

### Task 1 (P0): Upgrade tavily_client.py

**Files:**
- Modify: `src/opportunity_os/tavily_client.py`
- Create: `src/opportunity_os/test_tavily_client.py`

**Step 1: Read the current file**

Read `src/opportunity_os/tavily_client.py` to understand the existing `search()` function and API key loading pattern.

**Step 2: Write the failing tests**

Create `src/opportunity_os/test_tavily_client.py`:

```python
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
```

**Step 3: Run test to confirm it fails**

Run: `uv run pytest src/opportunity_os/test_tavily_client.py -v`
Expected: ImportError or AttributeError (functions don't exist yet)

**Step 4: Implement the two new functions**

Add to `src/opportunity_os/tavily_client.py` after the existing `search()` function:

```python
def search_news(query: str, time_range: str = "month") -> int:
    """Return count of news results for query in the given time window. Returns 0 on any failure."""
    if not _api_key:
        return 0
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": _api_key,
                "query": query,
                "max_results": MAX_RESULTS,
                "topic": "news",
                "time_range": time_range,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=20.0,
        )
        resp.raise_for_status()
        return len(resp.json().get("results") or [])
    except Exception as exc:
        logger.warning("Tavily search_news failed for %r: %s", query, exc)
        return 0


def search_with_content(query: str, max_results: int = 5) -> Optional[list[dict]]:
    """Search with raw content included. Returns None on failure."""
    if not _api_key:
        return None
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": _api_key,
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
```

**Step 5: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/test_tavily_client.py -v`
Expected: All 3 tests PASS

**Step 6: Commit**

```bash
git add src/opportunity_os/tavily_client.py src/opportunity_os/test_tavily_client.py
git commit -m "feat(p0): add search_news and search_with_content to tavily_client"
```

---

### Task 2 (P1): Add structured extraction to firecrawl_client.py

**Files:**
- Modify: `src/opportunity_os/firecrawl_client.py`
- Create: `src/opportunity_os/test_firecrawl_client.py`

**Step 1: Read the current file**

Read `src/opportunity_os/firecrawl_client.py` to understand the existing request pattern, BASE_URL, and API key loading.

**Step 2: Write the failing tests**

Create `src/opportunity_os/test_firecrawl_client.py`:

```python
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
```

**Step 3: Run tests to confirm they fail**

Run: `uv run pytest src/opportunity_os/test_firecrawl_client.py -v`
Expected: ImportError (scrape_structured and COMPETITOR_PAGE_SCHEMA don't exist)

**Step 4: Implement scrape_structured and the schema constant**

Add to `src/opportunity_os/firecrawl_client.py` (after imports, before existing functions):

```python
COMPETITOR_PAGE_SCHEMA: dict = {
    "price_usd": "float",
    "pricing_model": "str",
    "key_features": "list[str]",
    "target_market": "str",
}
```

Then add the function after existing ones:

```python
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
```

**Step 5: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/test_firecrawl_client.py -v`
Expected: All 3 tests PASS

**Step 6: Commit**

```bash
git add src/opportunity_os/firecrawl_client.py src/opportunity_os/test_firecrawl_client.py
git commit -m "feat(p1): add scrape_structured and COMPETITOR_PAGE_SCHEMA to firecrawl_client"
```

---

### Task 3 (P2): Create apify_client.py

**Files:**
- Create: `src/opportunity_os/apify_client.py`
- Create: `src/opportunity_os/test_apify_client.py`

**Step 1: Check pyproject.toml for apify-client**

Read `pyproject.toml`. If `apify-client` is not in dependencies, run: `uv add apify-client`

**Step 2: Write the failing tests**

Create `src/opportunity_os/test_apify_client.py`:

```python
import pytest
from unittest.mock import patch, MagicMock


def test_fetch_linkedin_jobs_returns_int():
    mock_run = {"defaultDatasetId": "ds1"}
    mock_items = [{"title": "Backend Dev"}, {"title": "PM"}]
    mock_client = MagicMock()
    mock_client.actor.return_value.call.return_value = mock_run
    mock_client.dataset.return_value.list_items.return_value.items = mock_items
    with patch("opportunity_os.apify_client.ApifyClient", return_value=mock_client):
        from opportunity_os import apify_client as ac
        ac._APIFY_KEY = "test-key"
        result = ac.fetch_linkedin_jobs("fintech", "venezuela")
        assert isinstance(result, int)
        assert result == 2


def test_fetch_g2_reviews_returns_dict_with_neg_rate():
    mock_run = {"defaultDatasetId": "ds2"}
    mock_items = [
        {"rating": 1, "cons": "Too expensive and painfully slow"},
        {"rating": 5, "cons": ""},
        {"rating": 2, "cons": "Hard to configure correctly"},
    ]
    mock_client = MagicMock()
    mock_client.actor.return_value.call.return_value = mock_run
    mock_client.dataset.return_value.list_items.return_value.items = mock_items
    with patch("opportunity_os.apify_client.ApifyClient", return_value=mock_client):
        from opportunity_os import apify_client as ac
        ac._APIFY_KEY = "test-key"
        result = ac.fetch_g2_reviews("payments")
        assert result is not None
        assert "competitor_negative_review_rate" in result
        assert result["competitor_negative_review_rate"] == pytest.approx(2 / 3, rel=0.01)
        assert len(result["exact_customer_phrases"]) >= 1


def test_fetch_linkedin_jobs_returns_none_when_no_key():
    from opportunity_os import apify_client as ac
    ac._APIFY_KEY = None
    result = ac.fetch_linkedin_jobs("fintech", "venezuela")
    assert result is None


def test_is_available_false_without_key():
    from opportunity_os import apify_client as ac
    ac._APIFY_KEY = None
    assert ac.is_available() is False
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/test_apify_client.py -v`
Expected: ModuleNotFoundError (file doesn't exist yet)

**Step 4: Create apify_client.py**

Write `src/opportunity_os/apify_client.py`:

```python
"""
Apify client — LinkedIn job postings + G2 software reviews.

Mirrors tavily_client.py graceful-fail pattern:
- _load_apify_key() reads .env up the directory tree
- is_available() returns False if no key (callers skip gracefully)
- All public functions return None on any failure (never raise)
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

LINKEDIN_JOBS_ACTOR = "curious_coder/linkedin-jobs-scraper"
G2_REVIEWS_ACTOR = "thirdwatch/g2-software-reviews-scraper"
NEGATIVE_RATING_THRESHOLD = 2
MAX_PHRASES = 3
DEFAULT_TIMEOUT_SECS = 120


def _load_apify_key() -> Optional[str]:
    """Walk up from this file looking for .env with APIFY_API_TOKEN."""
    for parent in Path(__file__).resolve().parents:
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("APIFY_API_TOKEN="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
            break
    return os.environ.get("APIFY_API_TOKEN")


_APIFY_KEY: Optional[str] = None


def _get_key() -> Optional[str]:
    global _APIFY_KEY
    if _APIFY_KEY is None:
        _APIFY_KEY = _load_apify_key()
    return _APIFY_KEY


def is_available() -> bool:
    """Return True if Apify API token is configured."""
    return bool(_get_key())


def _run_actor_raw(
    actor_id: str,
    run_input: dict,
    timeout_secs: int = DEFAULT_TIMEOUT_SECS,
) -> Optional[list[dict]]:
    """
    Run an Apify actor synchronously and return dataset items.
    Returns None on any failure (missing key, timeout, actor error).
    """
    key = _get_key()
    if not key:
        return None
    try:
        from apify_client import ApifyClient
        client = ApifyClient(key)
        run = client.actor(actor_id).call(
            run_input=run_input,
            timeout_secs=timeout_secs,
        )
        if run is None:
            logger.warning("Apify actor %r returned None run", actor_id)
            return None
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return None
        items = client.dataset(dataset_id).list_items().items
        return list(items) if items else []
    except Exception as exc:
        logger.warning("Apify actor %r failed: %s", actor_id, exc)
        return None


def fetch_linkedin_jobs(
    vertical: str,
    geography: str,
    max_results: int = 50,
) -> Optional[int]:
    """
    Return count of LinkedIn job postings for vertical+geography.
    Returns None if Apify unavailable or call fails.
    """
    query = f"{vertical} {geography}"
    items = _run_actor_raw(
        LINKEDIN_JOBS_ACTOR,
        {"keywords": query, "location": geography, "maxItems": max_results},
    )
    if items is None:
        return None
    return len(items)


def fetch_g2_reviews(
    category: str,
    max_results: int = 100,
) -> Optional[dict]:
    """
    Fetch G2 reviews for a software category.

    Returns dict with:
      - competitor_negative_review_rate: float (fraction with rating <= 2)
      - exact_customer_phrases: list[str] (up to 3 verbatim cons)
    Returns None if Apify unavailable or call fails.
    """
    items = _run_actor_raw(
        G2_REVIEWS_ACTOR,
        {"category": category, "maxReviews": max_results},
    )
    if items is None:
        return None
    total = len(items)
    if total == 0:
        return {"competitor_negative_review_rate": 0.0, "exact_customer_phrases": []}
    negative = [r for r in items if (r.get("rating") or 5) <= NEGATIVE_RATING_THRESHOLD]
    neg_rate = round(len(negative) / total, 4)
    phrases: list[str] = []
    for review in negative:
        cons = (review.get("cons") or "").strip()
        if cons and len(cons) > 10:
            phrases.append(cons[:200])
        if len(phrases) >= MAX_PHRASES:
            break
    return {
        "competitor_negative_review_rate": neg_rate,
        "exact_customer_phrases": phrases,
    }
```

**Step 5: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/test_apify_client.py -v`
Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add src/opportunity_os/apify_client.py src/opportunity_os/test_apify_client.py pyproject.toml uv.lock
git commit -m "feat(p2): create apify_client with fetch_linkedin_jobs and fetch_g2_reviews"
```

---

### Task 4 (P3a): Add new fields to models.py

**Files:**
- Modify: `src/opportunity_os/models.py`
- Create: `src/opportunity_os/test_models_new_fields.py`

**Step 1: Read models.py**

Read `src/opportunity_os/models.py`. Find the `# Research / Enrichment` section (around line 200-260).

**Step 2: Write the failing tests**

Create `src/opportunity_os/test_models_new_fields.py`:

```python
from opportunity_os.models import Opportunity


def test_new_scoring_fields_exist_and_default_none():
    opp = Opportunity(name="Test", description="test")
    assert opp.news_signal_count is None
    assert opp.job_posting_count is None
    assert opp.competitor_negative_review_rate is None
    assert opp.competitor_pricing_data is None
    assert opp.apify_researched_at is None
    assert opp.pain_researched_at is None
    assert opp.market_momentum_score is None
    assert opp.competitor_weakness_score is None


def test_market_momentum_score_is_bounded():
    opp = Opportunity(name="Test", description="test", market_momentum_score=9.5)
    assert opp.market_momentum_score == 9.5


def test_news_signal_count_accepts_int():
    opp = Opportunity(name="Test", description="test", news_signal_count=7)
    assert opp.news_signal_count == 7


def test_competitor_pricing_data_accepts_list():
    data = [{"price_usd": 29.0, "pricing_model": "monthly"}]
    opp = Opportunity(name="Test", description="test", competitor_pricing_data=data)
    assert opp.competitor_pricing_data == data
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/test_models_new_fields.py -v`
Expected: AttributeError on the new fields

**Step 4: Add fields to models.py**

In `src/opportunity_os/models.py`, locate the `# Research / Enrichment` section and add these fields:

```python
    # Data-backed scoring signals (populated by enrichment pipeline)
    news_signal_count: Optional[int] = None
    job_posting_count: Optional[int] = None
    competitor_negative_review_rate: Optional[float] = None
    competitor_pricing_data: Optional[List[Dict]] = None
    apify_researched_at: Optional[str] = None
    pain_researched_at: Optional[str] = None

    # Derived scoring dimensions (set by scoring_engine pre-processing hook)
    market_momentum_score: Optional[float] = Field(None, ge=0, le=10)
    competitor_weakness_score: Optional[float] = Field(None, ge=0, le=10)
```

**Step 5: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/test_models_new_fields.py -v`
Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add src/opportunity_os/models.py src/opportunity_os/test_models_new_fields.py
git commit -m "feat(p3a): add data-backed scoring fields to Opportunity model"
```

---

### Task 5 (P3b): Upgrade scoring_engine.py — normalization + new weights

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py`
- Create: `src/opportunity_os/engines/test_scoring_data_backed.py`

**Step 1: Read scoring_engine.py**

Read the full file. Identify:
- DEFAULT_WEIGHTS dict (find exact key names and values)
- ATTRACTIVENESS_FIELDS and STRATEGIC_VALUE_FIELDS lists
- The pre-processing pipeline in `score_opportunity()` where `_derive_distribution_quality()` is called
- Any existing `Optional` import at the top

**Step 2: Write the failing tests**

Create `src/opportunity_os/engines/test_scoring_data_backed.py`:

```python
import pytest


def test_normalize_job_posting_count_zero():
    from opportunity_os.engines.scoring_engine import normalize_job_posting_count
    assert normalize_job_posting_count(0) == 0.0


def test_normalize_job_posting_count_at_max():
    from opportunity_os.engines.scoring_engine import normalize_job_posting_count
    assert normalize_job_posting_count(50) == 10.0
    assert normalize_job_posting_count(200) == 10.0


def test_normalize_job_posting_count_midpoint():
    from opportunity_os.engines.scoring_engine import normalize_job_posting_count
    result = normalize_job_posting_count(25)
    assert 4.9 < result < 5.1


def test_normalize_neg_review_rate_zero_is_neutral():
    from opportunity_os.engines.scoring_engine import normalize_neg_review_rate
    assert normalize_neg_review_rate(0.0) == 5.0


def test_normalize_neg_review_rate_high_is_ten():
    from opportunity_os.engines.scoring_engine import normalize_neg_review_rate
    assert normalize_neg_review_rate(0.8) == 10.0
    assert normalize_neg_review_rate(1.0) == 10.0


def test_normalize_neg_review_rate_none_is_neutral():
    from opportunity_os.engines.scoring_engine import normalize_neg_review_rate
    assert normalize_neg_review_rate(None) == 5.0


def test_derive_data_backed_scores_populates_fields():
    from opportunity_os.engines.scoring_engine import _derive_data_backed_scores
    opp = {"job_posting_count": 25, "competitor_negative_review_rate": 0.4}
    result = _derive_data_backed_scores(opp)
    assert result["market_momentum_score"] is not None
    assert result["competitor_weakness_score"] is not None
    assert result is not opp  # immutability check


def test_derive_data_backed_scores_none_inputs_pass_through():
    from opportunity_os.engines.scoring_engine import _derive_data_backed_scores
    opp = {"job_posting_count": None, "competitor_negative_review_rate": None}
    result = _derive_data_backed_scores(opp)
    assert result.get("market_momentum_score") is None
    assert result.get("competitor_weakness_score") is None


def test_new_weights_sum_within_tolerance():
    from opportunity_os.engines.scoring_engine import DEFAULT_WEIGHTS
    assert "market_momentum_score" in DEFAULT_WEIGHTS
    assert "competitor_weakness_score" in DEFAULT_WEIGHTS
    total = sum(DEFAULT_WEIGHTS.values())
    assert abs(total - 1.0) < 0.02  # weights must sum to ~1.0
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/engines/test_scoring_data_backed.py -v`
Expected: ImportError (functions don't exist yet)

**Step 4: Add normalization functions**

Add to `src/opportunity_os/engines/scoring_engine.py` near the top, after imports:

```python
_MAX_JOB_POSTINGS = 50  # 50+ postings = maximum momentum signal


def normalize_job_posting_count(count: Optional[int]) -> float:
    """Map job posting count to 0-10. 0 jobs=0.0, 50+=10.0, linear interpolation."""
    if count is None or count <= 0:
        return 0.0
    return min(10.0, round(count / _MAX_JOB_POSTINGS * 10.0, 2))


def normalize_neg_review_rate(rate: Optional[float]) -> float:
    """
    Map competitor negative review rate to 0-10 weakness signal.
    0% negative = 5.0 (neutral — no data advantage either way).
    80%+ negative = 10.0 (very weak incumbent, strong entry signal).
    """
    if rate is None:
        return 5.0
    clamped = min(rate, 0.8)
    return round(5.0 + (clamped / 0.8) * 5.0, 2)
```

**Step 5: Add _derive_data_backed_scores hook**

Add to `src/opportunity_os/engines/scoring_engine.py`, after the normalization functions:

```python
def _derive_data_backed_scores(opp: dict) -> dict:
    """
    Pre-processing hook: derive market_momentum_score and competitor_weakness_score
    from raw Apify data. Returns new dict (never mutates opp).
    """
    updates: dict = {}
    job_count = opp.get("job_posting_count")
    if job_count is not None:
        updates["market_momentum_score"] = normalize_job_posting_count(job_count)
    neg_rate = opp.get("competitor_negative_review_rate")
    if neg_rate is not None:
        updates["competitor_weakness_score"] = normalize_neg_review_rate(neg_rate)
    if not updates:
        return opp
    return {**opp, **updates}
```

**Step 6: Update DEFAULT_WEIGHTS**

In DEFAULT_WEIGHTS, make these exact changes (verify the current values by reading first):
- Reduce `market_size` from 0.10 to 0.09
- Reduce `pain_severity` from 0.10 to 0.09
- Add `"market_momentum_score": 0.06`
- Add `"competitor_weakness_score": 0.06`

The net change is +0.12 added, -0.02 removed = net +0.10. Also reduce compensating fields to balance:
- Find `tam_confidence` or similar, reduce by 0.02
- Find `venezuela_lens_applied` or similar, reduce by 0.02
- Find `regional_fit`, reduce by 0.03
- Find `founder_fit`, reduce by 0.03

Adjust until DEFAULT_WEIGHTS.values() sums to 1.0 ± 0.005.

**Step 7: Add new fields to layer lists**

- Add `"market_momentum_score"` to `ATTRACTIVENESS_FIELDS` list
- Add `"competitor_weakness_score"` to `STRATEGIC_VALUE_FIELDS` list

**Step 8: Wire _derive_data_backed_scores into score_opportunity()**

In `score_opportunity()`, add as the FIRST pre-processing step (before `_derive_distribution_quality()`):

```python
    opp = _derive_data_backed_scores(opp)
```

**Step 9: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/engines/test_scoring_data_backed.py -v`
Expected: All 9 tests PASS

**Step 10: Run rescore dry-run**

Run: `uv run python scripts/rescore_all.py --dry-run`
Expected: No errors. Note any score shifts in the output.

**Step 11: Commit**

```bash
git add src/opportunity_os/engines/scoring_engine.py src/opportunity_os/engines/test_scoring_data_backed.py
git commit -m "feat(p3b): normalization hooks and updated weights in scoring_engine"
```

---

### Task 6 (P4a): Add Tavily news signal to free_research.py

**Files:**
- Modify: `src/opportunity_os/free_research.py`

**Step 1: Read free_research.py**

Read `src/opportunity_os/free_research.py`. Find `research_opportunity_free()` and its return statement pattern. Note the import section and how `geo_label` is constructed.

**Step 2: Write the failing test**

Add to a new `src/opportunity_os/test_free_research_news.py`:

```python
def test_news_signal_count_populated(monkeypatch):
    monkeypatch.setattr("opportunity_os.tavily_client.search_news", lambda q, time_range="month": 5)
    from opportunity_os.free_research import research_opportunity_free
    opp = {"name": "PayVE", "vertical": "fintech", "geography": "venezuela"}
    result = research_opportunity_free(opp)
    assert result.get("news_signal_count") == 5


def test_news_signal_count_zero_on_no_results(monkeypatch):
    monkeypatch.setattr("opportunity_os.tavily_client.search_news", lambda q, time_range="month": 0)
    from opportunity_os.free_research import research_opportunity_free
    opp = {"name": "X", "vertical": "saas", "geography": "global"}
    result = research_opportunity_free(opp)
    assert result.get("news_signal_count") == 0
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/test_free_research_news.py -v`
Expected: KeyError or None assertion failure

**Step 4: Add news search call**

In `src/opportunity_os/free_research.py`:

1. Add import at top: `from .tavily_client import search_news`
2. In `research_opportunity_free()`, before the return statement, add:

```python
    # Tavily news signal — count of recent news mentions (last 30 days)
    geo_str = "Venezuela" if (opp.get("geography") or "").lower() == "venezuela" else (opp.get("geography") or "global").upper()
    news_query = f"{opp.get('name', '')} {opp.get('vertical', '')} {geo_str}".strip()
    updates["news_signal_count"] = search_news(news_query, time_range="month")
```

**Step 5: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/test_free_research_news.py -v`
Expected: Both tests PASS

**Step 6: Commit**

```bash
git add src/opportunity_os/free_research.py src/opportunity_os/test_free_research_news.py
git commit -m "feat(p4a): populate news_signal_count via Tavily in free_research"
```

---

### Task 7 (P4b): Add Apify enrichment step 11.7 to enrichment.py

**Files:**
- Modify: `src/opportunity_os/pipelines/enrichment.py`

**Step 1: Read enrichment.py**

Read `src/opportunity_os/pipelines/enrichment.py`. Find:
- Where step 11.6 ends and the final return
- The top-N selection pattern used in existing steps
- The logger name and import style

**Step 2: Write the failing tests**

Create `src/opportunity_os/pipelines/test_enrichment_apify.py`:

```python
import pytest


def test_enrich_apify_skips_when_unavailable(monkeypatch):
    monkeypatch.setattr("opportunity_os.apify_client.is_available", lambda: False)
    from opportunity_os.pipelines.enrichment import _enrich_apify
    opps = [{"name": "Test", "composite_score": 8.0, "id": "1"}]
    result = _enrich_apify(opps)
    assert result == opps


def test_enrich_apify_skips_recently_researched(monkeypatch):
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=3)).isoformat()
    monkeypatch.setattr("opportunity_os.apify_client.is_available", lambda: True)
    monkeypatch.setattr("opportunity_os.apify_client.fetch_linkedin_jobs", lambda v, g, **kw: 10)
    monkeypatch.setattr("opportunity_os.apify_client.fetch_g2_reviews", lambda c, **kw: None)
    from opportunity_os.pipelines.enrichment import _enrich_apify
    opps = [{"name": "T", "composite_score": 8.0, "id": "1", "apify_researched_at": recent}]
    result = _enrich_apify(opps)
    # Should be unchanged -- within skip window
    assert result[0].get("apify_researched_at") == recent
    assert result[0].get("job_posting_count") is None


def test_enrich_apify_enriches_top_opp(monkeypatch):
    from datetime import date, timedelta
    old = (date.today() - timedelta(days=20)).isoformat()
    monkeypatch.setattr("opportunity_os.apify_client.is_available", lambda: True)
    monkeypatch.setattr("opportunity_os.apify_client.fetch_linkedin_jobs", lambda v, g, **kw: 30)
    monkeypatch.setattr("opportunity_os.apify_client.fetch_g2_reviews", lambda c, **kw: {
        "competitor_negative_review_rate": 0.4,
        "exact_customer_phrases": ["Too slow"]
    })
    from opportunity_os.pipelines.enrichment import _enrich_apify
    opps = [{"name": "T", "composite_score": 8.0, "id": "1",
             "vertical": "fintech", "geography": "venezuela",
             "apify_researched_at": old}]
    result = _enrich_apify(opps)
    assert result[0].get("job_posting_count") == 30
    assert result[0].get("competitor_negative_review_rate") == 0.4
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/pipelines/test_enrichment_apify.py -v`
Expected: ImportError (_enrich_apify doesn't exist)

**Step 4: Implement _enrich_apify()**

Add to `src/opportunity_os/pipelines/enrichment.py`:

```python
def _enrich_apify(opps: list[dict]) -> list[dict]:
    """
    Step 11.7 — Apify enrichment on top 10 opps (by composite_score).
    Skip guard: 14 days from apify_researched_at.
    Returns new list (never mutates input dicts).
    """
    from .. import apify_client
    from datetime import date, timedelta
    from ..engines.scoring_engine import score_opportunity

    if not apify_client.is_available():
        logger.info("Step 11.7 skipped — Apify not configured")
        return opps

    cutoff = (date.today() - timedelta(days=14)).isoformat()
    sorted_by_score = sorted(
        opps, key=lambda o: float(o.get("composite_score") or 0), reverse=True
    )
    top_ids = {o.get("id") for o in sorted_by_score[:10] if o.get("id")}

    enriched: list[dict] = []
    for opp in opps:
        if opp.get("id") not in top_ids:
            enriched.append(opp)
            continue
        if (opp.get("apify_researched_at") or "") >= cutoff:
            enriched.append(opp)
            continue

        updates: dict = {"apify_researched_at": date.today().isoformat()}
        vertical = (opp.get("vertical") or "").lower()
        geography = (opp.get("geography") or "global").lower()

        job_count = apify_client.fetch_linkedin_jobs(vertical, geography)
        if job_count is not None:
            updates["job_posting_count"] = job_count

        g2_data = apify_client.fetch_g2_reviews(vertical)
        if g2_data:
            updates.update(g2_data)

        enriched_opp = score_opportunity({**opp, **updates})
        enriched.append(enriched_opp)
        logger.info(
            "Step 11.7 enriched %r: jobs=%s neg_rate=%s",
            opp.get("name"), job_count,
            updates.get("competitor_negative_review_rate"),
        )

    return enriched
```

**Step 5: Wire _enrich_apify into the main enrichment orchestrator**

In the main orchestrator function (look for where steps are called in sequence), add after the step 11.6 call:

```python
    # Step 11.7 — Apify enrichment (top 10 only, 14-day skip guard)
    opps = _enrich_apify(opps)
```

**Step 6: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/pipelines/test_enrichment_apify.py -v`
Expected: All 3 tests PASS

**Step 7: Commit**

```bash
git add src/opportunity_os/pipelines/enrichment.py src/opportunity_os/pipelines/test_enrichment_apify.py
git commit -m "feat(p4b): add Apify step 11.7 to enrichment pipeline"
```

---

### Task 8 (P5): Add competitor pricing snapshot to validation_run.py

**Files:**
- Modify: `src/opportunity_os/pipelines/validation_run.py`

**Step 1: Read validation_run.py**

Read `src/opportunity_os/pipelines/validation_run.py`. Find where the markdown report sections are assembled and where the final save happens.

**Step 2: Write the failing tests**

Create `src/opportunity_os/pipelines/test_validation_pricing.py`:

```python
def test_build_competitor_pricing_section_returns_markdown():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {
        "name": "PayVE",
        "competitor_pricing_data": [
            {"price_usd": 29.0, "pricing_model": "monthly", "target_market": "SMB"}
        ],
    }
    result = build_competitor_pricing_section(opp)
    assert "## Competitor Pricing" in result
    assert "29.0" in result


def test_build_competitor_pricing_section_empty_when_no_data():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {"name": "PayVE", "competitor_pricing_data": None, "known_competitors": None}
    result = build_competitor_pricing_section(opp)
    assert result == ""


def test_build_competitor_pricing_section_handles_missing_fields():
    from opportunity_os.pipelines.validation_run import build_competitor_pricing_section
    opp = {
        "name": "X",
        "competitor_pricing_data": [{"target_market": "SMB"}],
    }
    result = build_competitor_pricing_section(opp)
    assert "## Competitor Pricing" in result
```

**Step 3: Run tests to confirm fail**

Run: `uv run pytest src/opportunity_os/pipelines/test_validation_pricing.py -v`
Expected: ImportError

**Step 4: Implement build_competitor_pricing_section()**

Add to `src/opportunity_os/pipelines/validation_run.py`:

```python
def build_competitor_pricing_section(opp: dict) -> str:
    """
    Build markdown competitor pricing snapshot for the validation report.
    Uses competitor_pricing_data if pre-populated, else tries Firecrawl on known_competitors.
    Returns empty string when no data is available.
    """
    pricing_data = opp.get("competitor_pricing_data") or []
    if not pricing_data:
        competitors = opp.get("known_competitors") or []
        if competitors:
            from ..firecrawl_client import scrape_structured, COMPETITOR_PAGE_SCHEMA
            for comp_url in competitors[:2]:
                result = scrape_structured(str(comp_url), COMPETITOR_PAGE_SCHEMA)
                if result:
                    pricing_data.append(result)
    if not pricing_data:
        return ""
    lines = ["## Competitor Pricing Snapshot\n"]
    for item in pricing_data:
        price = item.get("price_usd")
        model = item.get("pricing_model", "unknown")
        market = item.get("target_market", "unknown")
        features = item.get("key_features") or []
        price_str = f"${price}/mo" if price is not None else "unknown"
        lines.append(f"- **Price:** {price_str} ({model}) | Target: {market}")
        if features:
            lines.append(f"  Features: {', '.join(str(f) for f in features[:4])}")
    return "\n".join(lines)
```

**Step 5: Wire it into the report assembly**

In the validation report builder, find where sections are assembled and add:

```python
    competitor_section = build_competitor_pricing_section(opp)
    if competitor_section:
        report_parts.append(competitor_section)
```

**Step 6: Run tests to confirm pass**

Run: `uv run pytest src/opportunity_os/pipelines/test_validation_pricing.py -v`
Expected: All 3 tests PASS

**Step 7: Commit**

```bash
git add src/opportunity_os/pipelines/validation_run.py src/opportunity_os/pipelines/test_validation_pricing.py
git commit -m "feat(p5): add competitor pricing snapshot to validation report"
```

---

### Task 9: End-to-end smoke test

**Files:** No changes — verification only.

**Step 1: Run full test suite**

Run: `uv run pytest src/ -v --tb=short 2>&1 | tail -30`
Expected: All new tests PASS, no regressions in existing tests.

**Step 2: Run rescore dry-run**

Run: `uv run python scripts/rescore_all.py --dry-run`
Expected: No errors. All 79+ opportunities rescore without crashes. Note any score delta in output.

**Step 3: Verify new model fields are importable**

Run:
```bash
uv run python -c "
from opportunity_os.models import Opportunity
o = Opportunity(name='test', description='t')
new_fields = ['news_signal_count', 'job_posting_count', 'competitor_negative_review_rate',
              'market_momentum_score', 'competitor_weakness_score', 'apify_researched_at']
for f in new_fields:
    assert hasattr(o, f), f'Missing field: {f}'
print('All new fields present')
"
```
Expected: `All new fields present`

**Step 4: Verify dashboard loads**

Run: `uv run streamlit run src/opportunity_os/dashboard.py --server.headless true &`
Wait 8 seconds, check stdout for errors.
Expected: `You can now view your Streamlit app` with no ImportError or AttributeError.

**Step 5: Final commit if cleanup needed**

If any files need formatting or minor cleanup:
```bash
git add .
git commit -m "chore: post-upgrade smoke test and cleanup"
```
