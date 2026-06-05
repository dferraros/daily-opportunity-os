"""Tests for _enrich_apify() — the standalone Apify enrichment function."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


def _make_opp(name: str, score: float = 5.0, **kwargs) -> dict:
    return {"name": name, "composite_score": score, "vertical": "fintech", "geography": "venezuela", **kwargs}


# ---------------------------------------------------------------------------
# Import the function under test
# ---------------------------------------------------------------------------
from opportunity_os.pipelines.enrichment import _enrich_apify


def test_dry_run_skips_apify():
    """_enrich_apify must not call Apify when dry_run=True."""
    opps = [_make_opp("opp-a")]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs") as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews") as mock_g2:
        _enrich_apify(opps, dry_run=True)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()


def test_unavailable_apify_skips_fetch():
    """_enrich_apify must not call fetch_ functions if Apify key is not set."""
    opps = [_make_opp("opp-b")]
    with patch("opportunity_os.apify_client.is_available", return_value=False), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs") as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews") as mock_g2:
        _enrich_apify(opps, dry_run=False)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()


def test_job_posting_count_populated():
    """job_posting_count is stored on opp when fetch_linkedin_jobs returns > 0."""
    opps = [_make_opp("opp-c")]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=30), \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={}), \
         patch("opportunity_os.engines.scoring_engine.score_opportunity", side_effect=lambda o: o), \
         patch("opportunity_os.geo_lens.apply_geo_adjustments", side_effect=lambda o: o), \
         patch("time.sleep"):
        result = _enrich_apify(opps, dry_run=False)
    assert result[0].get("job_posting_count") == 30


def test_g2_neg_rate_populated():
    """competitor_negative_review_rate is stored on opp when fetch_g2_reviews returns neg_rate."""
    opps = [_make_opp("opp-g2")]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=0), \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={"neg_rate": 0.4, "top_complaints": ["slow", "expensive"]}), \
         patch("opportunity_os.engines.scoring_engine.score_opportunity", side_effect=lambda o: o), \
         patch("opportunity_os.geo_lens.apply_geo_adjustments", side_effect=lambda o: o), \
         patch("time.sleep"):
        result = _enrich_apify(opps, dry_run=False)
    assert result[0].get("competitor_negative_review_rate") == 0.4
    assert result[0].get("exact_customer_phrases") == ["slow", "expensive"]


def test_skip_guard_14_days():
    """Opps with apify_researched_at within 14 days are not re-processed."""
    recent_ts = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    opps = [_make_opp("opp-d", apify_researched_at=recent_ts)]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs") as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews") as mock_g2:
        _enrich_apify(opps, dry_run=False)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()


def test_research_executor_results_merged_back():
    """Step 11.5 must merge enriched results back into all_opps_sorted."""
    from opportunity_os.pipelines.enrichment import run_enrichment_steps

    opp = {
        "id": "opp_test_merge_001",
        "name": "Test Merge Opp",
        "geography": "global",
        "vertical": "saas",
        "final_score": 8.5,
        "kill_decision": False,
    }
    fake_enriched = {**opp, "pain_validation_score": 7.5, "research_executed_at": "2026-06-01"}

    with patch("opportunity_os.research_executor.run_research_executor", return_value=fake_enriched), \
         patch("opportunity_os.engines.benchmark_engine.run_benchmark", return_value={}), \
         patch("opportunity_os.pain_intelligence.run_pain_intelligence", return_value={}), \
         patch("opportunity_os.pain_intelligence.execute_pain_research", return_value={}), \
         patch("opportunity_os.distribution_intelligence.run_distribution_intelligence", return_value={}), \
         patch("opportunity_os.distribution_intelligence.execute_distribution_research", return_value={}), \
         patch("opportunity_os.free_research.research_opportunity_free", return_value={"free_research_at": "2026-06-01"}), \
         patch("opportunity_os.apify_client.is_available", return_value=False):
        result_opps, _ = run_enrichment_steps([opp], dry_run=False)

    found = next((o for o in result_opps if o.get("id") == "opp_test_merge_001"), None)
    assert found is not None, "opp_test_merge_001 should be in result_opps"
    assert found.get("pain_validation_score") == 7.5, "research_executor results must be merged"
