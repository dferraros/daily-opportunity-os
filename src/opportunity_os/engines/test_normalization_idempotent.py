"""Tests for Wave 3.2: portfolio normalization must be a pure function of the
raw scores -- re-running it (or partially rescoring) must not shift anything."""

from opportunity_os.engines.scoring_engine import (
    normalize_portfolio_scores,
    score_opportunity,
)


def _pool():
    return [
        {"id": "a", "raw_final_score": 5.0, "final_score": 5.0, "kill_decision": False},
        {"id": "b", "raw_final_score": 6.2, "final_score": 6.2, "kill_decision": False},
        {"id": "c", "raw_final_score": 7.4, "final_score": 7.4, "kill_decision": False},
        {"id": "d", "raw_final_score": 8.1, "final_score": 8.1, "kill_decision": False},
    ]


def _finals(opps):
    return {o["id"]: o["final_score"] for o in opps}


def test_score_opportunity_stamps_raw_final_score():
    """The raw composite must be persisted at scoring time so normalization
    always has a true-raw input."""
    result = score_opportunity({"id": "x", "name": "x", "pain_severity": 7,
                                "market_size": 6, "kill_decision": False})
    assert result["raw_final_score"] == result["final_score"]


def test_normalization_is_idempotent():
    once = normalize_portfolio_scores(_pool())
    twice = normalize_portfolio_scores(once)
    assert _finals(once) == _finals(twice)


def test_normalization_reads_raw_not_inflated_final():
    """A previously-normalized (inflated) final_score must not leak into the
    input pool -- this is the mixed-pool bug that shifted ~75/80 scores on
    every partial rescore."""
    clean = normalize_portfolio_scores(_pool())

    inflated = _pool()
    inflated[0] = {**inflated[0], "final_score": 9.5}  # stale normalized value
    from_inflated = normalize_portfolio_scores(inflated)

    assert _finals(clean) == _finals(from_inflated)


def test_partial_rescore_does_not_shift_untouched_opps():
    """Simulate free-research: normalize the pool, freshly rescore ONE opp
    (raw unchanged), renormalize the mixed list -- untouched opps must keep
    their exact scores."""
    first_pass = normalize_portfolio_scores(_pool())

    # "Rescore" opp b: fresh raw composite replaces its normalized final_score
    mixed = [
        {**o, "final_score": o["raw_final_score"]} if o["id"] == "b" else o
        for o in first_pass
    ]
    second_pass = normalize_portfolio_scores(mixed)

    assert _finals(first_pass) == _finals(second_pass)


def test_legacy_records_without_raw_still_normalize():
    legacy = [
        {"id": "a", "final_score": 5.0, "kill_decision": False},
        {"id": "b", "final_score": 7.0, "kill_decision": False},
        {"id": "c", "final_score": 9.0, "kill_decision": False},
    ]
    result = normalize_portfolio_scores(legacy)
    scores = [o["final_score"] for o in result]
    assert min(scores) >= 2.0 and max(scores) <= 9.5
    # raw is stamped on the way through so the NEXT run is idempotent
    assert all(o.get("raw_final_score") is not None for o in result)
