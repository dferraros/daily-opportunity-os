"""Tests for data-backed score normalization in scoring_engine."""
from opportunity_os.engines.scoring_engine import _normalize_data_backed_scores


def test_job_count_none_returns_empty():
    result = _normalize_data_backed_scores({"job_posting_count": None})
    assert "market_momentum_score" not in result


def test_job_count_zero_treated_as_no_signal():
    """apify_client.fetch_linkedin_jobs returns 0 on failure, so 0 must be
    indistinguishable from 'no data' -- never scored as zero momentum."""
    result = _normalize_data_backed_scores({"job_posting_count": 0})
    assert "market_momentum_score" not in result


def test_job_count_50_gives_10():
    result = _normalize_data_backed_scores({"job_posting_count": 50})
    assert result["market_momentum_score"] == 10.0


def test_job_count_25_gives_5():
    result = _normalize_data_backed_scores({"job_posting_count": 25})
    assert result["market_momentum_score"] == 5.0


def test_job_count_over_50_capped_at_10():
    result = _normalize_data_backed_scores({"job_posting_count": 200})
    assert result["market_momentum_score"] == 10.0


def test_neg_rate_none_returns_empty():
    result = _normalize_data_backed_scores({"competitor_negative_review_rate": None})
    assert "competitor_weakness_score" not in result


def test_neg_rate_zero_gives_5():
    result = _normalize_data_backed_scores({"competitor_negative_review_rate": 0.0})
    assert abs(result["competitor_weakness_score"] - 5.0) < 0.01


def test_neg_rate_08_gives_10():
    result = _normalize_data_backed_scores({"competitor_negative_review_rate": 0.8})
    assert abs(result["competitor_weakness_score"] - 10.0) < 0.01


def test_neg_rate_over_08_capped_at_10():
    result = _normalize_data_backed_scores({"competitor_negative_review_rate": 1.0})
    assert result["competitor_weakness_score"] == 10.0


def test_neg_rate_negative_clamped_to_neutral():
    """Negative neg_review_rate from bad API data should clamp to 5.0 (neutral), not below."""
    opp = {"competitor_negative_review_rate": -0.5}
    result = _normalize_data_backed_scores(opp)
    assert result["competitor_weakness_score"] == 5.0, (
        f"Expected 5.0 (neutral) for negative neg_rate, got {result['competitor_weakness_score']}"
    )
