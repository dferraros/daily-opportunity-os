"""
Tests for engines/calibration_engine.py -- the quantitative outcome-calibration loop.

Rubric criteria covered (docs/plans/2026-06-12-scoring-calibration-goal.md):
CAL-02 discrimination, CAL-03 Brier skill, CAL-04 dimension effects,
CAL-05 damped never-auto-applied proposals.
"""
import copy

from opportunity_os.engines.calibration_engine import (
    MAX_WEIGHT_CHANGE,
    MIN_RESOLVED,
    REFIT_MIN_RESOLVED,
    VERDICT_DISCRIMINATIVE,
    VERDICT_INSUFFICIENT,
    VERDICT_INVERTED,
    brier_report,
    calibration_summary,
    dimension_effects,
    dimension_redundancy,
    discrimination_report,
    outcomes_from_opportunity_stamps,
    propose_weight_adjustments,
    resolve_outcomes,
)


def make_outcome(score, outcome, criteria=None):
    return {
        "opp_id": f"opp_{score}_{outcome}",
        "outcome": outcome,
        "final_score": score,
        "scoring_criteria": criteria or {},
    }


def graded_outcomes():
    """12 resolved outcomes where success rate rises with score (terciles: 0 / .5 / 1)."""
    lows = [make_outcome(s, "validated_failed") for s in (2.0, 2.5, 3.0, 3.5)]
    mids = [make_outcome(5.0, "validated_failed"), make_outcome(5.5, "validated_failed"),
            make_outcome(6.0, "validated_passed"), make_outcome(6.5, "validated_passed")]
    highs = [make_outcome(s, "built_launched") for s in (8.0, 8.5, 9.0, 9.5)]
    return lows + mids + highs


class TestResolveOutcomes:
    def test_excludes_unresolved_and_scoreless(self):
        outcomes = [
            make_outcome(8.0, "validated_passed"),
            make_outcome(7.0, "watching"),
            make_outcome(6.0, "pivoted"),
            make_outcome(None, "validated_failed"),
        ]
        resolved = resolve_outcomes(outcomes)
        assert len(resolved) == 1
        assert resolved[0]["success"] == 1

    def test_failure_outcomes_marked_zero(self):
        resolved = resolve_outcomes([make_outcome(3.0, "killed_wrong_score")])
        assert resolved[0]["success"] == 0

    def test_input_not_mutated(self):
        outcomes = [make_outcome(8.0, "validated_passed")]
        snapshot = copy.deepcopy(outcomes)
        resolve_outcomes(outcomes)
        assert outcomes == snapshot


class TestDiscrimination:
    def test_insufficient_below_min_resolved(self):
        outcomes = [make_outcome(8.0, "validated_passed")] * (MIN_RESOLVED - 1)
        report = discrimination_report(outcomes)
        assert report["verdict"] == VERDICT_INSUFFICIENT
        assert report["resolved_count"] == MIN_RESOLVED - 1

    def test_graded_outcomes_are_discriminative(self):
        report = discrimination_report(graded_outcomes())
        assert report["verdict"] == VERDICT_DISCRIMINATIVE
        assert report["n_buckets"] == 3  # 12 resolved < quintile threshold
        rates = [b["success_rate"] for b in report["buckets"]]
        assert rates == sorted(rates)

    def test_inverted_when_low_scores_succeed(self):
        flipped = [
            make_outcome(s, "validated_passed") for s in (2.0, 2.5, 3.0, 3.5)
        ] + [
            make_outcome(s, "validated_failed") for s in (8.0, 8.5, 9.0, 9.5)
        ]
        assert discrimination_report(flipped)["verdict"] == VERDICT_INVERTED

    def test_quintiles_at_fifteen_resolved(self):
        outcomes = [make_outcome(1 + i * 0.5, "validated_failed" if i < 10 else "validated_passed")
                    for i in range(20)]
        assert discrimination_report(outcomes)["n_buckets"] == 5

    def test_low_n_warning_set(self):
        assert discrimination_report(graded_outcomes())["low_n_warning"] is True


class TestBrier:
    def test_perfect_predictions_give_skill_one(self):
        outcomes = [make_outcome(10.0, "validated_passed")] * 3 + \
                   [make_outcome(0.0, "validated_failed")] * 3
        report = brier_report(outcomes)
        assert report["brier"] == 0.0
        assert report["skill"] == 1.0

    def test_base_rate_predictions_give_zero_skill(self):
        outcomes = [make_outcome(5.0, "validated_passed")] * 4 + \
                   [make_outcome(5.0, "validated_failed")] * 4
        report = brier_report(outcomes)
        assert report["base_rate"] == 0.5
        assert abs(report["skill"]) < 1e-9

    def test_insufficient_below_min(self):
        report = brier_report([make_outcome(8.0, "validated_passed")])
        assert report["verdict"] == VERDICT_INSUFFICIENT


class TestDimensionEffects:
    def test_positive_effect_when_successes_score_higher(self):
        outcomes = [make_outcome(8.0, "validated_passed", {"pain_severity": 9.0}) for _ in range(3)] + \
                   [make_outcome(3.0, "validated_failed", {"pain_severity": 5.0}) for _ in range(3)]
        effects = dimension_effects(outcomes, ["pain_severity"])
        assert len(effects) == 1
        assert effects[0]["effect"] == 0.4
        assert effects[0]["n_success"] == 3

    def test_min_per_side_guard_skips_thin_dimensions(self):
        outcomes = [make_outcome(8.0, "validated_passed", {"founder_fit": 9.0}) for _ in range(3)] + \
                   [make_outcome(3.0, "validated_failed", {"founder_fit": 4.0}) for _ in range(2)]
        assert dimension_effects(outcomes, ["founder_fit"]) == []

    def test_sorted_by_absolute_effect(self):
        crit_s = {"a": 9.0, "b": 6.0}
        crit_f = {"a": 5.0, "b": 5.5}
        outcomes = [make_outcome(8.0, "validated_passed", crit_s) for _ in range(3)] + \
                   [make_outcome(3.0, "validated_failed", crit_f) for _ in range(3)]
        effects = dimension_effects(outcomes, ["b", "a"])
        assert effects[0]["dimension"] == "a"


class TestWeightProposal:
    def test_damping_cap_respected(self):
        effects = [{"dimension": "pain_severity", "avg_success": 9.0, "avg_failure": 1.0,
                    "effect": 0.8, "n_success": 5, "n_failure": 5}]
        weights = {"pain_severity": 0.10, "market_size": 0.10}
        proposal = propose_weight_adjustments(effects, weights)
        nudged = proposal["adjusted_dimensions"]["pain_severity"]
        # effect saturates the cap: raw nudge is exactly +20% before renormalization
        assert nudged["proposed"] <= round(0.10 * (1 + MAX_WEIGHT_CHANGE), 4)

    def test_total_weight_preserved(self):
        effects = [{"dimension": "pain_severity", "avg_success": 9.0, "avg_failure": 5.0,
                    "effect": 0.4, "n_success": 4, "n_failure": 4}]
        weights = {"pain_severity": 0.10, "market_size": 0.10, "founder_fit": 0.05}
        proposal = propose_weight_adjustments(effects, weights)
        assert abs(proposal["total_weight_preserved"] - 0.25) < 0.001

    def test_small_effects_and_unknown_dims_ignored(self):
        effects = [
            {"dimension": "market_size", "avg_success": 7.1, "avg_failure": 7.0,
             "effect": 0.01, "n_success": 4, "n_failure": 4},
            {"dimension": "not_a_weight", "avg_success": 9.0, "avg_failure": 2.0,
             "effect": 0.7, "n_success": 4, "n_failure": 4},
        ]
        proposal = propose_weight_adjustments(effects, {"market_size": 0.10})
        assert proposal["adjusted_dimensions"] == {}

    def test_never_auto_applied(self):
        proposal = propose_weight_adjustments([], {"market_size": 0.10})
        assert proposal["auto_apply"] is False


class TestCalibrationSummary:
    def test_insufficient_path_proposes_nothing(self):
        summary = calibration_summary([], {"market_size": 0.10}, ["market_size"])
        assert summary["discrimination"]["verdict"] == VERDICT_INSUFFICIENT
        assert summary["weight_proposal"]["proposed_weights"] == {}

    def test_hold_weights_below_refit_threshold(self):
        summary = calibration_summary(graded_outcomes(), {"market_size": 0.10}, ["market_size"])
        assert "HOLD_WEIGHTS_VALIDATE_ONLY" in summary["weight_proposal"]["recommendation"]

    def test_review_and_apply_at_refit_threshold(self):
        outcomes = [make_outcome(8.0 + (i % 3) * 0.5, "validated_passed") for i in range(15)] + \
                   [make_outcome(2.0 + (i % 3) * 0.5, "validated_failed") for i in range(15)]
        assert len(resolve_outcomes(outcomes)) >= REFIT_MIN_RESOLVED
        summary = calibration_summary(outcomes, {"market_size": 0.10}, ["market_size"])
        assert summary["weight_proposal"]["recommendation"] == "REVIEW_AND_APPLY"

    def test_outcomes_not_mutated(self):
        outcomes = graded_outcomes()
        snapshot = copy.deepcopy(outcomes)
        calibration_summary(outcomes, {"market_size": 0.10}, ["market_size"])
        assert outcomes == snapshot


class TestDimensionRedundancy:
    def test_perfectly_correlated_pair_flagged(self):
        opps = [{"defensibility": float(i), "switching_cost_score": float(i)} for i in range(1, 13)]
        flagged = dimension_redundancy(opps, ["defensibility", "switching_cost_score"])
        assert len(flagged) == 1
        assert flagged[0]["spearman"] == 1.0

    def test_uncorrelated_pair_not_flagged(self):
        values = [(1, 7), (2, 3), (3, 9), (4, 1), (5, 8), (6, 2),
                  (7, 10), (8, 4), (9, 6), (10, 5), (11, 12), (12, 11)]
        opps = [{"a": float(x), "b": float(y)} for x, y in values]
        assert dimension_redundancy(opps, ["a", "b"]) == []

    def test_min_pairs_guard(self):
        opps = [{"a": float(i), "b": float(i)} for i in range(5)]
        assert dimension_redundancy(opps, ["a", "b"]) == []

    def test_killed_opps_excluded(self):
        opps = [{"a": float(i), "b": float(i), "kill_decision": True} for i in range(1, 13)]
        assert dimension_redundancy(opps, ["a", "b"]) == []


class TestBridgeStampAdapter:
    def test_statuses_map_to_calibration_outcomes(self):
        opps = [
            {"id": "o1", "outcome": "validated", "final_score": 8.0},
            {"id": "o2", "outcome": "shipped", "final_score": 7.0},
            {"id": "o3", "outcome": "revenue", "final_score": 9.0},
        ]
        derived = outcomes_from_opportunity_stamps(opps, ["pain_severity"])
        assert [d["outcome"] for d in derived] == \
            ["validated_passed", "built_launched", "built_launched"]
        assert all(d["derived_from"] == "bridge_stamp" for d in derived)

    def test_zero_scored_kills_skipped(self):
        # kill cap zeroes final_score on rescore -- a 0.0 "prediction" for every
        # failure would fake perfect discrimination, so these records are unusable
        opps = [
            {"id": "o1", "outcome": "killed", "final_score": 0.0, "kill_decision": True},
            {"id": "o2", "outcome": "killed", "final_score": 6.5, "kill_decision": True},
        ]
        derived = outcomes_from_opportunity_stamps(opps, ["pain_severity"])
        assert [d["opp_id"] for d in derived] == ["o2"]
        assert derived[0]["outcome"] == "validated_failed"

    def test_unstamped_and_scoreless_skipped(self):
        opps = [
            {"id": "o1", "final_score": 8.0},
            {"id": "o2", "outcome": "validated", "final_score": None},
            {"id": "o3", "outcome": "watching_something_else", "final_score": 8.0},
        ]
        assert outcomes_from_opportunity_stamps(opps, ["pain_severity"]) == []

    def test_criteria_snapshot_taken(self):
        opps = [{"id": "o1", "outcome": "validated", "final_score": 8.0, "pain_severity": 9.0}]
        derived = outcomes_from_opportunity_stamps(opps, ["pain_severity", "market_size"])
        assert derived[0]["scoring_criteria"] == {"pain_severity": 9.0, "market_size": None}
