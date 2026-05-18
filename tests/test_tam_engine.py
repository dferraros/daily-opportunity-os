"""Tests for engines/tam_engine.py — 4 TAM methods, geo adjustments, pipeline adapter."""
import pytest
from opportunity_os.engines.tam_engine import (
    tam_bottom_up,
    tam_top_down,
    tam_proxy,
    tam_competitor_revenue,
    estimate_tam,
    estimate_tam_from_opp,
    format_tam_usd,
    GEO_TAM_MULTIPLIERS,
)


# ─── tam_bottom_up ────────────────────────────────────────────────────────────

def test_bottom_up_returns_required_keys():
    result = tam_bottom_up(10_000, 500.0)
    for key in ("method", "tam_usd", "sam_usd", "som_usd", "assumptions"):
        assert key in result


def test_bottom_up_method_label():
    result = tam_bottom_up(10_000, 500.0)
    assert result["method"] == "bottom_up"


def test_bottom_up_sam_is_30_pct_of_tam():
    result = tam_bottom_up(100_000, 100.0)
    assert pytest.approx(result["sam_usd"]) == result["tam_usd"] * 0.30


def test_bottom_up_som_uses_conversion_rate():
    result = tam_bottom_up(100_000, 100.0, conversion_rate=0.05)
    assert pytest.approx(result["som_usd"]) == result["sam_usd"] * 0.05


def test_bottom_up_geo_multiplier_scales_tam():
    base = tam_bottom_up(100_000, 100.0, geography_multiplier=1.0)
    scaled = tam_bottom_up(100_000, 100.0, geography_multiplier=0.008)
    assert pytest.approx(scaled["tam_usd"]) == base["tam_usd"] * 0.008


# ─── tam_top_down ─────────────────────────────────────────────────────────────

def test_top_down_returns_required_keys():
    result = tam_top_down(1_000_000_000, 0.15)
    for key in ("method", "tam_usd", "sam_usd", "som_usd", "assumptions"):
        assert key in result


def test_top_down_method_label():
    result = tam_top_down(1_000_000_000, 0.15)
    assert result["method"] == "top_down"


def test_top_down_sam_uses_addressable_pct():
    result = tam_top_down(1_000_000_000, 0.20)
    assert pytest.approx(result["sam_usd"]) == result["tam_usd"] * 0.20


def test_top_down_invalid_addressable_pct_raises():
    with pytest.raises(ValueError):
        tam_top_down(1_000_000_000, 1.5)


def test_top_down_invalid_som_pct_raises():
    with pytest.raises(ValueError):
        tam_top_down(1_000_000_000, 0.15, som_pct=2.0)


# ─── tam_proxy ────────────────────────────────────────────────────────────────

def test_proxy_returns_required_keys():
    result = tam_proxy(500_000_000, "colombia", "venezuela", 0.15)
    for key in ("method", "tam_usd", "sam_usd", "som_usd", "assumptions"):
        assert key in result


def test_proxy_scales_by_size_ratio():
    result = tam_proxy(1_000_000_000, "latam", "venezuela", 0.10)
    assert pytest.approx(result["tam_usd"]) == 100_000_000.0


def test_proxy_negative_size_ratio_raises():
    with pytest.raises(ValueError):
        tam_proxy(500_000_000, "global", "venezuela", -0.1)


def test_proxy_zero_size_ratio_raises():
    with pytest.raises(ValueError):
        tam_proxy(500_000_000, "global", "venezuela", 0.0)


# ─── tam_competitor_revenue ───────────────────────────────────────────────────

def test_competitor_revenue_returns_required_keys():
    result = tam_competitor_revenue(10_000_000, 0.05)
    for key in ("method", "tam_usd", "sam_usd", "som_usd", "assumptions"):
        assert key in result


def test_competitor_revenue_back_calculates_market():
    result = tam_competitor_revenue(10_000_000, 0.10)
    assert pytest.approx(result["tam_usd"]) == 100_000_000.0


def test_competitor_revenue_zero_share_raises():
    with pytest.raises(ValueError):
        tam_competitor_revenue(10_000_000, 0.0)


def test_competitor_revenue_over_100_pct_raises():
    with pytest.raises(ValueError):
        tam_competitor_revenue(10_000_000, 1.5)


# ─── estimate_tam (router) ────────────────────────────────────────────────────

def test_estimate_tam_routes_bottom_up():
    result = estimate_tam("bottom_up", geography="global",
                          target_customers=10_000, annual_price_usd=500.0)
    assert result["method"] == "bottom_up"
    assert "geography" in result
    assert "confidence" in result
    assert "notes" in result


def test_estimate_tam_applies_geo_multiplier():
    global_result = estimate_tam("bottom_up", geography="global",
                                 target_customers=10_000, annual_price_usd=500.0)
    ve_result = estimate_tam("bottom_up", geography="venezuela",
                             target_customers=10_000, annual_price_usd=500.0)
    expected_ratio = GEO_TAM_MULTIPLIERS["venezuela"]
    assert pytest.approx(ve_result["tam_usd"]) == global_result["tam_usd"] * expected_ratio


def test_estimate_tam_unknown_method_raises():
    with pytest.raises(ValueError, match="Unknown method"):
        estimate_tam("magic_method", geography="global", total_market_usd=1e9)


def test_estimate_tam_top_down_adds_note():
    result = estimate_tam("top_down", geography="global",
                          total_market_usd=1_000_000_000, addressable_pct=0.15)
    assert any("top-down" in n.lower() or "overestimates" in n.lower() for n in result["notes"])


def test_estimate_tam_unknown_geo_adds_note():
    result = estimate_tam("bottom_up", geography="narnia",
                          target_customers=1_000, annual_price_usd=100.0)
    assert any("narnia" in n.lower() or "not in lookup" in n.lower() for n in result["notes"])


def test_estimate_tam_confidence_bottom_up_is_high():
    result = estimate_tam("bottom_up", geography="global",
                          target_customers=1_000, annual_price_usd=100.0)
    assert result["confidence"] == "high"


def test_estimate_tam_confidence_top_down_is_low():
    result = estimate_tam("top_down", geography="global",
                          total_market_usd=1e9, addressable_pct=0.10)
    assert result["confidence"] == "low"


# ─── estimate_tam_from_opp ────────────────────────────────────────────────────

def test_estimate_tam_from_opp_returns_float_for_tam():
    """C-01 regression: tam must be float, not formatted string."""
    opp = {"geography": "global", "tam_target_customers": 10_000, "tam_annual_price_usd": 500.0}
    result = estimate_tam_from_opp(opp)
    assert isinstance(result["tam"], float)


def test_estimate_tam_from_opp_returns_string_for_tam_display():
    opp = {"geography": "global", "tam_target_customers": 10_000, "tam_annual_price_usd": 500.0}
    result = estimate_tam_from_opp(opp)
    assert isinstance(result["tam_display"], str)
    assert "$" in result["tam_display"]


def test_estimate_tam_from_opp_uses_bottom_up_when_customers_and_price_set():
    opp = {"geography": "global", "tam_target_customers": 10_000, "tam_annual_price_usd": 500.0}
    result = estimate_tam_from_opp(opp)
    assert result["tam_method"] == "bottom_up"


def test_estimate_tam_from_opp_falls_back_to_top_down():
    opp = {"geography": "global", "tam_total_market_usd": 1_000_000_000}
    result = estimate_tam_from_opp(opp)
    assert result["tam_method"] == "top_down"


def test_estimate_tam_from_opp_proxy_fallback_no_inputs():
    opp = {"geography": "venezuela"}
    result = estimate_tam_from_opp(opp)
    assert result["tam_method"] == "proxy"
    assert result["tam"] is not None


def test_estimate_tam_from_opp_returns_all_keys():
    opp = {"geography": "global"}
    result = estimate_tam_from_opp(opp)
    for key in ("tam", "tam_display", "tam_usd_estimate", "sam_usd", "som_usd",
                "tam_method", "tam_confidence", "tam_notes"):
        assert key in result


def test_estimate_tam_from_opp_venezuela_geo_reduces_tam():
    global_opp = {"geography": "global", "tam_target_customers": 10_000, "tam_annual_price_usd": 500.0}
    ve_opp = {"geography": "venezuela", "tam_target_customers": 10_000, "tam_annual_price_usd": 500.0}
    global_result = estimate_tam_from_opp(global_opp)
    ve_result = estimate_tam_from_opp(ve_opp)
    assert ve_result["tam"] < global_result["tam"]


# ─── format_tam_usd ───────────────────────────────────────────────────────────

def test_format_tam_billions():
    assert format_tam_usd(5_000_000_000) == "$5.0B"


def test_format_tam_millions():
    assert format_tam_usd(80_000_000) == "$80.0M"


def test_format_tam_thousands():
    assert format_tam_usd(450_000) == "$450K"


def test_format_tam_small():
    assert format_tam_usd(500) == "$500"


def test_format_tam_none_returns_unknown():
    assert format_tam_usd(None) == "Unknown"
