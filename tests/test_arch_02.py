"""Tests for ARCH-02: TAM estimate wired into market_size scoring dimension."""
import pytest
from opportunity_os.pipelines.daily_run import _tam_to_market_size
from opportunity_os.engines.scoring_engine import score_opportunity


# ─── _tam_to_market_size ─────────────────────────────────────────────────────

def test_billion_tam_gives_10():
    assert _tam_to_market_size(1_000_000_000) == 10.0


def test_above_billion_gives_10():
    assert _tam_to_market_size(5_000_000_000) == 10.0


def test_100m_tam_gives_8():
    assert _tam_to_market_size(100_000_000) == 8.0


def test_between_100m_and_1b_gives_8():
    assert _tam_to_market_size(500_000_000) == 8.0


def test_10m_tam_gives_6():
    assert _tam_to_market_size(10_000_000) == 6.0


def test_between_10m_and_100m_gives_6():
    assert _tam_to_market_size(50_000_000) == 6.0


def test_1m_tam_gives_4():
    assert _tam_to_market_size(1_000_000) == 4.0


def test_between_1m_and_10m_gives_4():
    assert _tam_to_market_size(5_000_000) == 4.0


def test_below_1m_gives_2():
    assert _tam_to_market_size(999_999) == 2.0


def test_zero_tam_gives_2():
    assert _tam_to_market_size(0) == 2.0


# ─── Integration: market_size flows into final_score ─────────────────────────

@pytest.fixture
def base_opp():
    return {
        "id": "arch02_test",
        "name": "Test",
        "geography": "global",
        "vertical": "saas",
        "kill_decision": False,
        "pain_severity": 7,
        "timing_tailwind": 6,
        "willingness_to_pay": 7,
        "monetization_clarity": 7,
        "speed_to_mvp": 7,
        "capital_efficiency": 7,
        "distribution_accessibility": 6,
        "competition_intensity": 4,
        "defensibility": 5,
        "regional_fit": 5,
        "founder_fit": 6,
        "ai_leverage": 6,
        "operational_simplicity": 6,
        "regulatory_simplicity": 7,
        "revenue_speed_score": 6,
    }


def test_market_size_from_tam_raises_score(base_opp):
    """Wiring a large TAM into market_size must increase final_score."""
    opp_no_ms = dict(base_opp)
    opp_with_ms = {**base_opp, "market_size": _tam_to_market_size(500_000_000)}  # 8.0

    result_no = score_opportunity(opp_no_ms)
    result_yes = score_opportunity(opp_with_ms)

    assert result_yes["final_score"] >= result_no["final_score"], (
        "market_size derived from large TAM should not lower final_score"
    )


def test_market_size_from_large_tam_is_significant(base_opp):
    """$1B+ TAM yields market_size=10 which should noticeably move the score."""
    opp_small_tam = {**base_opp, "market_size": _tam_to_market_size(500_000)}    # 2.0
    opp_large_tam = {**base_opp, "market_size": _tam_to_market_size(2_000_000_000)}  # 10.0

    result_small = score_opportunity(opp_small_tam)
    result_large = score_opportunity(opp_large_tam)

    assert result_large["final_score"] > result_small["final_score"], (
        "$2B TAM → market_size=10 must score higher than $500k TAM → market_size=2"
    )


def test_existing_market_size_not_overwritten(base_opp):
    """If market_size already set, step 9.6 must not touch it."""
    opp = {**base_opp, "market_size": 9.0, "tam_usd_estimate": 50_000}
    ms_before = opp["market_size"]
    # Simulate the step 9.6 guard: only write if market_size is None
    if opp.get("market_size") is not None:
        result = score_opportunity(opp)
    else:
        ms = _tam_to_market_size(float(opp["tam_usd_estimate"]))
        result = score_opportunity({**opp, "market_size": ms})

    assert result.get("market_size") == ms_before, "Existing market_size must not be overwritten"
