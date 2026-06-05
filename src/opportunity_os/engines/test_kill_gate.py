"""Unit tests for kill_gate.evaluate_kill_gate and format_kill_report."""
from opportunity_os.engines.kill_gate import evaluate_kill_gate, KILL_THRESHOLD, format_kill_report


def _all_pass() -> dict:
    return {f"KG-0{i}": True for i in range(1, 8)}


def test_all_pass_clears_gate():
    result = evaluate_kill_gate(_all_pass())
    assert result.kill_decision is False
    assert result.passed_count == 7
    assert result.failed_count == 0


def test_two_failures_trigger_kill():
    answers = {**_all_pass(), "KG-02": False, "KG-05": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True
    assert result.failed_count == 2
    assert sorted(result.failed_criteria) == ["KG-02", "KG-05"]


def test_one_failure_clears_with_warning():
    answers = {**_all_pass(), "KG-04": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is False
    assert result.failed_count == 1
    assert "KG-04" in result.failed_criteria


def test_all_fail_triggers_kill():
    answers = {f"KG-0{i}": False for i in range(1, 8)}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True
    assert result.failed_count == 7


def test_unknown_criterion_ids_are_ignored():
    answers = {"KG-99": False, "KG-01": True, "KG-02": False, "KG-03": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True  # KG-02 + KG-03 = 2 failures
    assert "KG-99" not in result.failed_criteria


def test_empty_answers_clears_gate():
    result = evaluate_kill_gate({})
    assert result.kill_decision is False
    assert result.passed_count == 0
    assert result.failed_count == 0


def test_kill_reason_contains_failed_criterion_ids():
    answers = {**_all_pass(), "KG-01": False, "KG-03": False}
    result = evaluate_kill_gate(answers)
    assert "KG-01" in result.kill_reason
    assert "KG-03" in result.kill_reason


def test_format_kill_report_contains_decision_label():
    answers = {**_all_pass(), "KG-02": False, "KG-06": False}
    result = evaluate_kill_gate(answers)
    report = format_kill_report(result)
    assert "KILLED" in report
    assert "KG-02" in report
    assert "KG-06" in report


def test_format_kill_report_cleared_label():
    result = evaluate_kill_gate(_all_pass())
    report = format_kill_report(result)
    assert "CLEARED" in report


def test_kill_threshold_is_two():
    assert KILL_THRESHOLD == 2
