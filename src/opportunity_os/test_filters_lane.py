"""Unit tests for PortfolioLaneAssigner."""
from opportunity_os.filters import PortfolioLaneAssigner


def test_now_lane_uses_speed_to_mvp_as_fallback():
    """fast_cash + path_to_first_revenue + speed_to_mvp >= 7 => now, even without time_to_mvp."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp to 10 local businesses",
        "speed_to_mvp": 8,
        # time_to_mvp intentionally absent
    }
    assert assigner.assign_from_dict(opp) == "now"


def test_now_lane_requires_speed_to_mvp_at_least_7():
    """speed_to_mvp < 7 does not qualify for now lane without explicit time_to_mvp."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp",
        "speed_to_mvp": 5,
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_now_lane_explicit_time_to_mvp_still_works():
    """Existing behavior preserved when time_to_mvp is explicitly set."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp",
        "time_to_mvp": "2 weeks",
    }
    assert assigner.assign_from_dict(opp) == "now"


def test_strategic_lane():
    assigner = PortfolioLaneAssigner()
    opp = {"kill_decision": False, "bucket": "venture_scale", "tam": 500_000_000}
    assert assigner.assign_from_dict(opp) == "strategic"


def test_kill_decision_always_no():
    assigner = PortfolioLaneAssigner()
    assert assigner.assign_from_dict({"kill_decision": True, "bucket": "fast_cash"}) == "no"


def test_soon_fallback_for_all_others():
    assigner = PortfolioLaneAssigner()
    opp = {"kill_decision": False, "bucket": "latam_asymmetry"}
    assert assigner.assign_from_dict(opp) == "soon"


def test_tbd_path_does_not_qualify_for_now():
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "TBD",
        "speed_to_mvp": 9,
    }
    assert assigner.assign_from_dict(opp) == "soon"


def test_no_path_does_not_qualify_for_now():
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "speed_to_mvp": 9,
    }
    assert assigner.assign_from_dict(opp) == "soon"
