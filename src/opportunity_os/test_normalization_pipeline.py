"""Tests for normalization.py — field aliases, geo normalization, infer_bucket, normalize_signal."""
import pytest
from opportunity_os.normalization import (
    normalize_field_names,
    normalize_geography,
    infer_bucket,
    infer_missing_fields,
    fill_defaults,
    normalize_signal,
    FIELD_ALIASES,
    GEO_NORMALIZER,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _minimal_signal(**overrides) -> dict:
    """Minimal raw dict that normalize_signal can turn into a valid Opportunity."""
    base = {
        "name": "Test Signal",
        "geography": "global",
        "vertical": "fintech",
        "raw_text": "Businesses lose $500/month to manual reconciliation.",
    }
    base.update(overrides)
    return base


# ─── normalize_field_names ────────────────────────────────────────────────────

def test_field_alias_title_to_name():
    result = normalize_field_names({"title": "My Opp", "geography": "global"})
    assert result.get("name") == "My Opp"
    assert "title" not in result


def test_field_alias_geo_to_geography():
    result = normalize_field_names({"geo": "venezuela"})
    assert result.get("geography") == "venezuela"
    assert "geo" not in result


def test_field_alias_pain_to_pain_severity():
    result = normalize_field_names({"pain": 8})
    assert result.get("pain_severity") == 8


def test_field_alias_competition_to_competition_intensity():
    result = normalize_field_names({"competition": 3})
    assert result.get("competition_intensity") == 3


def test_field_alias_mvp_time_to_speed_to_mvp():
    result = normalize_field_names({"mvp_time": 6})
    assert result.get("speed_to_mvp") == 6


def test_field_alias_revenue_path_to_path_to_first_revenue():
    result = normalize_field_names({"revenue_path": "Direct outbound"})
    assert result.get("path_to_first_revenue") == "Direct outbound"


def test_keys_lowercased_and_spaces_replaced():
    result = normalize_field_names({"Market Size": 7, "TAM USD": 1_000_000})
    assert "market_size" in result
    assert "tam_usd" in result or "market_size" in result


def test_string_values_stripped():
    result = normalize_field_names({"name": "  My Opp  "})
    assert result["name"] == "My Opp"


def test_non_alias_key_passes_through():
    result = normalize_field_names({"vertical": "saas"})
    assert result["vertical"] == "saas"


# ─── normalize_geography ─────────────────────────────────────────────────────

def test_ve_normalizes_to_venezuela():
    result = normalize_geography({"geography": "ve"})
    assert result["geography"] == "venezuela"


def test_vzla_normalizes_to_venezuela():
    result = normalize_geography({"geography": "vzla"})
    assert result["geography"] == "venezuela"


def test_ven_normalizes_to_venezuela():
    result = normalize_geography({"geography": "ven"})
    assert result["geography"] == "venezuela"


def test_co_normalizes_to_latam():
    """Colombia abbreviations roll up to 'latam' — the valid Opportunity geo value."""
    result = normalize_geography({"geography": "co"})
    assert result["geography"] == "latam"


def test_mx_normalizes_to_latam():
    """Mexico abbreviations roll up to 'latam' — the valid Opportunity geo value."""
    result = normalize_geography({"geography": "mx"})
    assert result["geography"] == "latam"


def test_latin_america_normalizes_to_latam():
    result = normalize_geography({"geography": "latin america"})
    assert result["geography"] == "latam"


def test_unknown_geo_falls_back_to_global():
    result = normalize_geography({"geography": "mars"})
    assert result["geography"] == "global"


def test_already_valid_geo_unchanged():
    result = normalize_geography({"geography": "spain"})
    assert result["geography"] == "spain"


def test_missing_geography_falls_back_to_global():
    result = normalize_geography({})
    assert result["geography"] == "global"


def test_normalize_geography_does_not_mutate_input():
    raw = {"geography": "ve"}
    _ = normalize_geography(raw)
    assert raw["geography"] == "ve"


# ─── infer_bucket ────────────────────────────────────────────────────────────

def test_venezuela_geo_gives_latam_asymmetry():
    result = infer_bucket({"geography": "venezuela", "vertical": "fintech"})
    assert result["bucket"] == "latam_asymmetry"


def test_latam_geo_gives_latam_asymmetry():
    result = infer_bucket({"geography": "latam", "vertical": "saas"})
    assert result["bucket"] == "latam_asymmetry"


def test_colombia_geo_gives_latam_asymmetry():
    result = infer_bucket({"geography": "colombia", "vertical": "saas"})
    assert result["bucket"] == "latam_asymmetry"


def test_large_tam_global_gives_venture_scale():
    result = infer_bucket({"geography": "global", "vertical": "saas", "tam": 200_000_000})
    assert result["bucket"] == "venture_scale"


def test_platform_text_gives_venture_scale():
    result = infer_bucket({
        "geography": "global",
        "vertical": "saas",
        "name": "A platform for connecting buyers",
        "problem_statement": "",
        "description": "",
        "raw_notes": "",
    })
    assert result["bucket"] == "venture_scale"


def test_consulting_text_gives_fast_cash():
    result = infer_bucket({
        "geography": "global",
        "vertical": "services",
        "name": "Done-for-you consulting",
        "problem_statement": "",
        "description": "",
        "raw_notes": "",
    })
    assert result["bucket"] == "fast_cash"


def test_existing_bucket_not_overridden():
    raw = {"geography": "venezuela", "bucket": "fast_cash"}
    result = infer_bucket(raw)
    assert result["bucket"] == "fast_cash"


def test_venezuela_geo_beats_large_tam_for_bucket():
    """Geography check runs before TAM check — VE + large TAM → latam_asymmetry."""
    result = infer_bucket({
        "geography": "venezuela",
        "vertical": "fintech",
        "tam": 500_000_000,
    })
    assert result["bucket"] == "latam_asymmetry"


def test_infer_bucket_does_not_mutate_input():
    raw = {"geography": "global", "vertical": "saas", "tam": 200_000_000}
    _ = infer_bucket(raw)
    assert "bucket" not in raw


# ─── infer_missing_fields ────────────────────────────────────────────────────

def test_problem_statement_inferred_from_raw_text():
    raw = {"raw_text": "Businesses need faster payments."}
    result = infer_missing_fields(raw)
    assert result["problem_statement"] == "Businesses need faster payments."


def test_trigger_signal_inferred_from_raw_text():
    raw = {"raw_text": "Urgent demand for X in Venezuela."}
    result = infer_missing_fields(raw)
    assert "trigger_signal" in result
    assert len(result["trigger_signal"]) > 0


def test_target_customer_inferred_from_vertical_and_geo():
    raw = {"vertical": "fintech", "geography": "venezuela"}
    result = infer_missing_fields(raw)
    assert "Venezuelan" in result["target_customer"]
    assert "Fintech" in result["target_customer"]


def test_existing_problem_statement_not_overwritten():
    raw = {"problem_statement": "Explicit statement.", "raw_text": "Should not override."}
    result = infer_missing_fields(raw)
    assert result["problem_statement"] == "Explicit statement."


# ─── normalize_signal (full pipeline) ────────────────────────────────────────

def test_normalize_signal_returns_opportunity_on_valid_input():
    opp, errors = normalize_signal(_minimal_signal())
    assert opp is not None
    assert errors == []


def test_normalize_signal_returns_none_on_missing_name():
    raw = {"geography": "global", "vertical": "fintech", "raw_text": "Pain."}
    opp, errors = normalize_signal(raw)
    assert opp is None
    assert len(errors) > 0


def test_normalize_signal_resolves_geo_alias_end_to_end():
    raw = _minimal_signal(geo="vzla")
    opp, errors = normalize_signal(raw)
    assert opp is not None
    assert opp.geography == "venezuela"


def test_normalize_signal_resolves_field_alias_end_to_end():
    raw = _minimal_signal()
    raw.pop("name", None)
    raw["title"] = "My Pipeline Opp"
    opp, errors = normalize_signal(raw)
    assert opp is not None
    assert opp.name == "My Pipeline Opp"


def test_normalize_signal_auto_generates_id():
    opp, _ = normalize_signal(_minimal_signal())
    assert opp is not None
    assert opp.id.startswith("opp_")


def test_normalize_signal_sets_stage_to_scout():
    opp, _ = normalize_signal(_minimal_signal())
    assert opp is not None
    assert opp.stage == "scout"


def test_normalize_signal_sets_kill_decision_false():
    opp, _ = normalize_signal(_minimal_signal())
    assert opp is not None
    assert opp.kill_decision is False


def test_normalize_signal_infers_bucket_from_geography():
    raw = _minimal_signal(geography="venezuela")
    opp, _ = normalize_signal(raw)
    assert opp is not None
    assert opp.bucket == "latam_asymmetry"


def test_normalize_signal_does_not_mutate_input():
    raw = _minimal_signal()
    keys_before = set(raw.keys())
    normalize_signal(raw)
    assert set(raw.keys()) == keys_before, "normalize_signal mutated caller dict"


def test_normalize_signal_invalid_geo_falls_back_gracefully():
    """Unknown geo → global → valid Opportunity, no error."""
    raw = _minimal_signal(geography="moon")
    opp, errors = normalize_signal(raw)
    assert opp is not None
    assert opp.geography == "global"
