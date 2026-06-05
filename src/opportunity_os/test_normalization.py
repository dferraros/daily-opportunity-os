"""Unit tests for the normalization pipeline."""
from opportunity_os.normalization import (
    normalize_geography,
    _is_noise_signal,
    normalize_field_names,
    infer_bucket,
    normalize_signal,
    FIELD_ALIASES,
)


# ── Geography normalizer ──────────────────────────────────────────────────────

def test_normalize_geography_ve_variants():
    for raw_geo in ["ve", "vzla", "ven", "VE", "VZla"]:
        result = normalize_geography({"geography": raw_geo})
        assert result["geography"] == "venezuela", f"Failed for geo: {raw_geo!r}"


def test_normalize_geography_latam_variants():
    for raw_geo in ["colombia", "co", "Mexico", "mx", "argentina", "ar", "brazil", "br"]:
        result = normalize_geography({"geography": raw_geo})
        assert result["geography"] == "latam", f"Failed for geo: {raw_geo!r}"


def test_normalize_geography_spain():
    assert normalize_geography({"geography": "es"})["geography"] == "spain"
    assert normalize_geography({"geography": "Spain"})["geography"] == "spain"


def test_normalize_geography_unknown_defaults_to_global():
    result = normalize_geography({"geography": "neptune"})
    assert result["geography"] == "global"


def test_normalize_geography_explicit_global():
    result = normalize_geography({"geography": "global"})
    assert result["geography"] == "global"


# ── Noise signal filter ───────────────────────────────────────────────────────

def test_noise_signal_hn_ask():
    assert _is_noise_signal("Ask HN: What tools do you use for X?") is True


def test_noise_signal_show_hn():
    assert _is_noise_signal("Show HN: I built a thing") is True


def test_noise_signal_funding_news():
    assert _is_noise_signal("Stripe raised $600M in Series G") is True


def test_noise_signal_hn_hiring():
    assert _is_noise_signal("Who is hiring — June 2026") is True


def test_noise_signal_acquisition():
    assert _is_noise_signal("Google acquired by Microsoft") is True


def test_noise_signal_legitimate_opportunity():
    assert _is_noise_signal("WhatsApp invoice automation for Venezuelan SMBs") is False
    assert _is_noise_signal("USDT payment collection for Venezuelan freelancers") is False
    assert _is_noise_signal("B2B SaaS for SMB inventory management") is False


# ── Field aliases ─────────────────────────────────────────────────────────────

def test_field_alias_tam_usd_estimate_maps_to_tam():
    result = normalize_field_names({"tam_usd_estimate": 5_000_000})
    assert "tam" in result, "tam_usd_estimate should alias to tam"


def test_field_alias_title_maps_to_name():
    result = normalize_field_names({"title": "My Opportunity"})
    assert result.get("name") == "My Opportunity"


def test_field_alias_geo_maps_to_geography():
    result = normalize_field_names({"geo": "venezuela"})
    assert result.get("geography") == "venezuela"


def test_field_alias_market_maps_to_vertical():
    result = normalize_field_names({"market": "fintech"})
    assert result.get("vertical") == "fintech"


# ── Bucket inference ──────────────────────────────────────────────────────────

def test_infer_bucket_ve_always_latam_asymmetry():
    raw = {"geography": "venezuela", "name": "Test", "vertical": "saas"}
    result = infer_bucket(raw)
    assert result["bucket"] == "latam_asymmetry"


def test_infer_bucket_large_tam_is_venture_scale():
    raw = {"geography": "global", "name": "Test", "vertical": "saas", "tam": 500_000_000}
    result = infer_bucket(raw)
    assert result["bucket"] == "venture_scale"


def test_infer_bucket_service_language_is_fast_cash():
    raw = {
        "geography": "global",
        "name": "Done-for-you consulting",
        "vertical": "consulting",
        "problem_statement": "Productized service for SMBs",
    }
    result = infer_bucket(raw)
    assert result["bucket"] == "fast_cash"


def test_infer_bucket_existing_value_not_overwritten():
    raw = {"geography": "global", "name": "Test", "vertical": "saas", "bucket": "venture_scale"}
    result = infer_bucket(raw)
    assert result["bucket"] == "venture_scale"


# ── End-to-end normalize_signal ───────────────────────────────────────────────

def test_normalize_signal_end_to_end_ve():
    raw = {
        "title": "Payment collection app for Venezuelan SMBs",
        "geo": "ve",
        "market": "fintech",
        "description": "Helps small businesses collect payments via USDT and Zelle",
    }
    opp, errors = normalize_signal(raw)
    assert opp is not None, f"Normalization failed: {errors}"
    assert opp.geography == "venezuela"
    assert opp.vertical == "fintech"
    assert opp.bucket == "latam_asymmetry"


def test_normalize_signal_rejects_hn_noise():
    raw = {"name": "Ask HN: Is there a tool for X?", "geography": "global"}
    opp, errors = normalize_signal(raw)
    assert opp is None
    assert any("Rejected" in e for e in errors)


def test_normalize_signal_fills_missing_target_customer():
    raw = {
        "name": "Invoice automation tool",
        "geo": "ve",
        "market": "saas",
        "description": "Helps Venezuelan SMBs with invoicing",
    }
    opp, errors = normalize_signal(raw)
    assert opp is not None, f"Normalization failed: {errors}"
    assert opp.target_customer  # must be inferred, not blank


def test_normalize_signal_invalid_geography_falls_to_global():
    raw = {
        "name": "Some opportunity",
        "geography": "atlantis",
        "vertical": "saas",
        "description": "Description here",
    }
    opp, errors = normalize_signal(raw)
    assert opp is not None, f"Should not fail on unknown geo: {errors}"
    assert opp.geography == "global"
