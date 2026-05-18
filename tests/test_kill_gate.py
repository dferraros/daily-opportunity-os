"""Tests for engines/kill_gate.py — binary kill gate evaluation."""
import pytest
from opportunity_os.engines.kill_gate import evaluate_kill_gate, KILL_CRITERIA


ALL_PASS = {f"KG-0{i}" if i < 10 else f"KG-{i}": True for i in range(1, 8)}
ALL_FAIL = {k: False for k in ALL_PASS}


# ─── evaluate_kill_gate ───────────────────────────────────────────────────────

def test_all_pass_clears_gate():
    result = evaluate_kill_gate(ALL_PASS)
    assert result.kill_decision is False
    assert result.failed_count == 0


def test_all_fail_triggers_kill():
    result = evaluate_kill_gate(ALL_FAIL)
    assert result.kill_decision is True
    assert result.failed_count == 7


def test_one_fail_clears_gate():
    answers = {**ALL_PASS, "KG-02": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is False
    assert result.failed_count == 1
    assert "KG-02" in result.failed_criteria


def test_two_fails_triggers_kill():
    answers = {**ALL_PASS, "KG-01": False, "KG-05": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True
    assert result.failed_count == 2
    assert "KG-01" in result.failed_criteria
    assert "KG-05" in result.failed_criteria


def test_failed_criteria_are_sorted():
    answers = {**ALL_PASS, "KG-07": False, "KG-02": False}
    result = evaluate_kill_gate(answers)
    assert result.failed_criteria == sorted(result.failed_criteria)


def test_unknown_criterion_ids_are_ignored():
    answers = {**ALL_PASS, "INVALID-99": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is False


def test_empty_answers_returns_zero_counts():
    result = evaluate_kill_gate({})
    assert result.passed_count == 0
    assert result.failed_count == 0
    assert result.kill_decision is False


def test_kill_reason_present_when_killed():
    answers = {**ALL_PASS, "KG-01": False, "KG-06": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True
    assert len(result.kill_reason) > 0


def test_kill_criteria_has_7_items():
    assert len(KILL_CRITERIA) == 7


@pytest.mark.parametrize("criterion", ["KG-01", "KG-02", "KG-03", "KG-04", "KG-05", "KG-06", "KG-07"])
def test_each_criterion_is_individually_evaluable(criterion):
    answers = {criterion: False}
    result = evaluate_kill_gate(answers)
    assert result.failed_count == 1
    assert criterion in result.failed_criteria
    assert result.kill_decision is False  # single fail never triggers kill
