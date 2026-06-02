"""Tests for step 11.7 Apify enrichment in run_enrichment_steps."""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


def _make_opp(name: str, score: float = 5.0, **kwargs) -> dict:
    return {"name": name, "composite_score": score, "vertical": "fintech", "geography": "venezuela", **kwargs}


def _run_step_117_only(opps: list, dry_run: bool) -> list:
    """Import and invoke run_enrichment_steps but mock all other steps so only 11.7 runs."""
    from opportunity_os.pipelines import enrichment as enr

    no_op = MagicMock(return_value={})
    with patch("opportunity_os.pipelines.enrichment.log_failure"), \
         patch("opportunity_os.engines.benchmark_engine.run_benchmark", no_op, create=True), \
         patch("opportunity_os.pain_intelligence.run_pain_intelligence", no_op, create=True), \
         patch("opportunity_os.pain_intelligence.execute_pain_research", no_op, create=True), \
         patch("opportunity_os.distribution_intelligence.run_distribution_intelligence", no_op, create=True), \
         patch("opportunity_os.distribution_intelligence.execute_distribution_research", no_op, create=True), \
         patch("opportunity_os.research_executor.run_research_executor", no_op, create=True), \
         patch("opportunity_os.free_research.research_opportunity_free", no_op, create=True), \
         patch("opportunity_os.pain_library.upsert_pain_cluster", MagicMock(return_value=False), create=True):
        result_opps, _ = enr.run_enrichment_steps(opps, dry_run)
    return result_opps


def test_step_117_skipped_in_dry_run():
    """Step 11.7 must not call Apify when dry_run=True."""
    opps = [_make_opp("opp-a")]
    with patch("opportunity_os.apify_client.is_available", return_value=True) as mock_avail, \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=25) as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={"neg_rate": 0.4, "top_complaints": []}) as mock_g2:
        _run_step_117_only(opps, dry_run=True)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()


def test_step_117_skipped_when_apify_unavailable():
    """Step 11.7 must not call fetch_ functions if Apify key is not set."""
    opps = [_make_opp("opp-b")]
    with patch("opportunity_os.apify_client.is_available", return_value=False), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=25) as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={}) as mock_g2:
        _run_step_117_only(opps, dry_run=False)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()


def test_step_117_populates_job_posting_count():
    """job_posting_count is stored on opp when fetch_linkedin_jobs returns > 0."""
    opps = [_make_opp("opp-c")]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=30), \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={}), \
         patch("opportunity_os.engines.scoring_engine.score_opportunity", side_effect=lambda o: o), \
         patch("opportunity_os.geo_lens.apply_geo_adjustments", side_effect=lambda o: o):
        result = _run_step_117_only(opps, dry_run=False)
    assert result[0].get("job_posting_count") == 30


def test_step_117_skip_guard_14_days():
    """Opps with apify_researched_at within 14 days are not re-processed."""
    recent_ts = (datetime.now() - timedelta(days=3)).isoformat()
    opps = [_make_opp("opp-d", apify_researched_at=recent_ts)]
    with patch("opportunity_os.apify_client.is_available", return_value=True), \
         patch("opportunity_os.apify_client.fetch_linkedin_jobs", return_value=10) as mock_li, \
         patch("opportunity_os.apify_client.fetch_g2_reviews", return_value={}) as mock_g2:
        _run_step_117_only(opps, dry_run=False)
    mock_li.assert_not_called()
    mock_g2.assert_not_called()
