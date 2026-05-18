"""Tests for filters.py — PortfolioLaneAssigner lane assignment."""
import pytest
from opportunity_os.filters import PortfolioLaneAssigner


@pytest.fixture
def assigner():
    return PortfolioLaneAssigner()


# ─── Kill gate → "no" ────────────────────────────────────────────────────────

def test_killed_opp_returns_no(assigner):
    opp = {"kill_decision": True, "bucket": "fast_cash",
           "path_to_first_revenue": "Direct sales", "time_to_mvp": "2 weeks"}
    assert assigner.assign_from_dict(opp) == "no"


def test_kill_gate_takes_priority_over_now_lane(assigner):
    """kill_decision overrides every other signal."""
    opp = {
        "kill_decision": True,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Outbound to 50 shops",
        "time_to_mvp": "3 weeks",
    }
    assert assigner.assign_from_dict(opp) == "no"


# ─── fast_cash → "now" ───────────────────────────────────────────────────────

def test_fast_cash_with_path_and_mvp_returns_now(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "WhatsApp cold outreach to 30 businesses",
        "time_to_mvp": "2 weeks",
    }
    assert assigner.assign_from_dict(opp) == "now"


def test_fast_cash_tbd_path_returns_soon(assigner):
    """TBD path_to_first_revenue must not qualify as 'now'."""
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "TBD",
        "time_to_mvp": "2 weeks",
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_fast_cash_tbd_case_insensitive(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "tbd",
        "time_to_mvp": "2 weeks",
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_fast_cash_missing_path_returns_soon(assigner):
    opp = {"kill_decision": False, "bucket": "fast_cash", "time_to_mvp": "2 weeks"}
    assert assigner.assign_from_dict(opp) == "soon"


def test_fast_cash_missing_mvp_returns_soon(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Outbound to 50 shops",
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_fast_cash_empty_path_returns_soon(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "   ",
        "time_to_mvp": "3 weeks",
    }
    assert assigner.assign_from_dict(opp) == "soon"


# ─── venture_scale → "strategic" ─────────────────────────────────────────────

def test_venture_scale_large_tam_returns_strategic(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "venture_scale",
        "tam": 500_000_000,
    }
    assert assigner.assign_from_dict(opp) == "strategic"


def test_venture_scale_exact_threshold_returns_strategic(assigner):
    """TAM == STRATEGIC_TAM_THRESHOLD (100M) must qualify."""
    opp = {
        "kill_decision": False,
        "bucket": "venture_scale",
        "tam": 100_000_000,
    }
    assert assigner.assign_from_dict(opp) == "strategic"


def test_venture_scale_below_threshold_returns_soon(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "venture_scale",
        "tam": 99_999_999,
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_venture_scale_tam_from_usd_estimate_field(assigner):
    """tam_usd_estimate field is the secondary TAM source."""
    opp = {
        "kill_decision": False,
        "bucket": "venture_scale",
        "tam_usd_estimate": 200_000_000,
    }
    assert assigner.assign_from_dict(opp) == "strategic"


def test_venture_scale_non_numeric_tam_returns_soon(assigner):
    opp = {
        "kill_decision": False,
        "bucket": "venture_scale",
        "tam": "large",
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_venture_scale_missing_tam_returns_soon(assigner):
    opp = {"kill_decision": False, "bucket": "venture_scale"}
    assert assigner.assign_from_dict(opp) == "soon"


# ─── "soon" catch-all ────────────────────────────────────────────────────────

def test_latam_asymmetry_bucket_returns_soon(assigner):
    opp = {"kill_decision": False, "bucket": "latam_asymmetry"}
    assert assigner.assign_from_dict(opp) == "soon"


def test_no_bucket_returns_soon(assigner):
    opp = {"kill_decision": False}
    assert assigner.assign_from_dict(opp) == "soon"


def test_false_kill_decision_does_not_return_no(assigner):
    opp = {"kill_decision": False, "bucket": "latam_asymmetry"}
    assert assigner.assign_from_dict(opp) != "no"
