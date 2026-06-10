"""Tests for geo_lens.py — WTP adjustments, payment rail context, Venezuela wedge bonuses."""
import pytest
from opportunity_os.geo_lens import apply_geo_adjustments, get_payment_rail_context, is_venezuela_wedge


# ─── apply_geo_adjustments ────────────────────────────────────────────────────

def test_venezuela_adds_wtp_pricing_estimate():
    opp = {"id": "x", "name": "t", "geography": "venezuela", "willingness_to_pay": 6}
    result = apply_geo_adjustments(opp)
    assert "wtp_pricing_estimate" in result
    assert result["wtp_pricing_estimate"] < 6  # multiplier < 1.0


def test_venezuela_adds_payment_rail_context():
    opp = {"id": "x", "name": "t", "geography": "venezuela"}
    result = apply_geo_adjustments(opp)
    assert "payment_rail_context" in result
    assert isinstance(result["payment_rail_context"], dict)


def test_venezuela_sets_latam_asymmetry_bucket():
    opp = {"id": "x", "name": "t", "geography": "venezuela"}
    result = apply_geo_adjustments(opp)
    assert result.get("bucket") == "latam_asymmetry"


def test_venezuela_does_not_overwrite_existing_bucket():
    opp = {"id": "x", "name": "t", "geography": "venezuela", "bucket": "fast_cash"}
    result = apply_geo_adjustments(opp)
    assert result.get("bucket") == "fast_cash"


def test_venezuela_wedge_match_boosts_regional_fit():
    opp = {
        "id": "x", "name": "t",
        "geography": "venezuela",
        "venezuela_wedge_category": "smb_software_informal_operators",
        "regional_fit": 5.0,
    }
    result = apply_geo_adjustments(opp)
    assert result.get("venezuela_wedge_match") is True
    assert result.get("regional_fit", 0) > 5.0


def test_venezuela_no_wedge_match_does_not_boost():
    opp = {
        "id": "x", "name": "t",
        "geography": "venezuela",
        "venezuela_wedge_category": None,
        "regional_fit": 5.0,
        "vertical": "nonexistent_vertical_xyz",
    }
    result = apply_geo_adjustments(opp)
    assert result.get("venezuela_wedge_match") is False
    assert result.get("regional_fit") == 5.0


def test_latam_adds_wtp_pricing_estimate():
    opp = {"id": "x", "name": "t", "geography": "latam", "willingness_to_pay": 7}
    result = apply_geo_adjustments(opp)
    assert "wtp_pricing_estimate" in result
    assert result["wtp_pricing_estimate"] < 7


def test_latam_does_not_set_bucket():
    opp = {"id": "x", "name": "t", "geography": "latam"}
    result = apply_geo_adjustments(opp)
    assert "bucket" not in result


def test_global_geo_no_adjustments():
    opp = {"id": "x", "name": "t", "geography": "global", "willingness_to_pay": 6}
    result = apply_geo_adjustments(opp)
    assert "wtp_pricing_estimate" not in result
    assert "payment_rail_context" not in result


def test_does_not_mutate_input():
    opp = {"id": "x", "name": "t", "geography": "venezuela", "willingness_to_pay": 6}
    original_keys = set(opp.keys())
    apply_geo_adjustments(opp)
    assert set(opp.keys()) == original_keys


# ─── get_payment_rail_context ─────────────────────────────────────────────────

def test_venezuela_payment_rail_has_zelle():
    ctx = get_payment_rail_context("venezuela")
    primary = ctx.get("primary_rail", "")
    secondary = ctx.get("secondary_rail", "")
    assert "Zelle" in primary or "Zelle" in secondary


def test_payment_rail_returns_dict():
    ctx = get_payment_rail_context("colombia")
    assert isinstance(ctx, dict)
    assert "primary_rail" in ctx


def test_unknown_geo_returns_default_rail():
    ctx = get_payment_rail_context("unknown_country_xyz")
    assert "primary_rail" in ctx


# ─── is_venezuela_wedge ───────────────────────────────────────────────────────

def test_known_wedge_category_returns_true():
    assert is_venezuela_wedge("smb_software_informal_operators") is True


def test_unknown_category_returns_false():
    assert is_venezuela_wedge("definitely_not_a_wedge_category") is False


def test_empty_category_returns_false():
    assert is_venezuela_wedge("") is False
