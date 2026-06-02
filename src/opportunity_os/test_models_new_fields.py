"""Verify the 4 new data-backed scoring fields exist and default to None."""
from opportunity_os.models import Opportunity


def test_new_fields_exist_and_default_to_none():
    """All 4 new fields must be present and default to None when not supplied."""
    opp = Opportunity.empty(name="test")

    assert opp.job_posting_count is None
    assert opp.competitor_negative_review_rate is None
    assert opp.news_signal_count is None
    assert opp.competitor_pricing_data is None


def test_new_fields_accept_values():
    opp = Opportunity(
        name="test",
        geography="global",
        vertical="fintech",
        target_customer="SMBs",
        problem_statement="TBD",
        trigger_signal="TBD",
        job_posting_count=25,
        competitor_negative_review_rate=0.45,
        news_signal_count=12,
        competitor_pricing_data=[{"price_usd": 99.0}],
    )
    assert opp.job_posting_count == 25
    assert abs(opp.competitor_negative_review_rate - 0.45) < 0.001
    assert opp.news_signal_count == 12
    assert isinstance(opp.competitor_pricing_data, list)
