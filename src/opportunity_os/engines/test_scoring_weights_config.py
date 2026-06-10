"""Tests for T1.3: scoring_weights.yaml is the single source of truth;
fallback is equal-weight and loud, never a stale tuned copy."""

import logging

from opportunity_os.engines.scoring_engine import (
    _ALL_SCORED_FIELDS,
    DEFAULT_WEIGHTS,
    load_weights,
)


def test_yaml_contains_every_scored_field():
    """Each field in the three scoring layers must have a weight in the YAML —
    a missing field silently contributes nothing (this happened to the two
    data-backed sub-scores for weeks)."""
    weights = load_weights()["weights"]
    missing = [f for f in _ALL_SCORED_FIELDS if f not in weights]
    assert missing == [], f"scoring_weights.yaml missing: {missing}"


def test_yaml_data_backed_weights_present():
    weights = load_weights()["weights"]
    assert weights["market_momentum_score"] == 0.06
    assert weights["competitor_weakness_score"] == 0.06


def test_fallback_is_equal_weight():
    """The fallback must not be a tuned copy that can drift from the YAML."""
    values = set(DEFAULT_WEIGHTS["weights"].values())
    assert values == {1.0}
    assert set(DEFAULT_WEIGHTS["weights"]) == set(_ALL_SCORED_FIELDS)


def test_missing_yaml_falls_back_loudly(tmp_path, caplog):
    with caplog.at_level(logging.ERROR, logger="opportunity_os.engines.scoring_engine"):
        result = load_weights(config_path=str(tmp_path / "does_not_exist.yaml"))

    assert result == DEFAULT_WEIGHTS
    assert any("NOT calibrated" in r.message for r in caplog.records)


def test_malformed_yaml_falls_back_loudly(tmp_path, caplog):
    bad = tmp_path / "bad.yaml"
    bad.write_text("thresholds:\n  auto_validation: 7.0\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR, logger="opportunity_os.engines.scoring_engine"):
        result = load_weights(config_path=str(bad))

    assert result == DEFAULT_WEIGHTS
    assert any("NOT calibrated" in r.message for r in caplog.records)


def test_yaml_weights_used_as_is_not_merged(tmp_path, caplog):
    """Tuned 0.05-scale YAML weights must never be mixed with the 1.0-scale
    fallback — a merge would let fallback values dominate any field the YAML
    omits. Omitted fields warn and contribute nothing instead."""
    partial = tmp_path / "partial.yaml"
    partial.write_text("weights:\n  market_size: 0.5\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="opportunity_os.engines.scoring_engine"):
        result = load_weights(config_path=str(partial))

    assert result["weights"] == {"market_size": 0.5}
    assert any("will not contribute" in r.message for r in caplog.records)
