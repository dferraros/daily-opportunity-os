"""Minimum-signal promotion gate (standing rule 2026-07-22b, wired 2026-08-04)."""

from opportunity_os.validation_engine import evaluate_minimum_signal_gate


def test_no_signals_fails_gate():
    out = evaluate_minimum_signal_gate({})
    assert out["validation_gate_passed"] is False
    assert "NOT MET" in out["validation_gate_evidence"]


def test_none_values_are_zero_not_benefit_of_doubt():
    out = evaluate_minimum_signal_gate({
        "paid_pilots_count": None, "signed_lois_count": None,
        "data_sharing_companies_count": None, "anchor_client_funded": None,
    })
    assert out["validation_gate_passed"] is False


def test_three_paid_pilots_pass():
    out = evaluate_minimum_signal_gate({"paid_pilots_count": 3})
    assert out["validation_gate_passed"] is True
    assert "paid pilots" in out["validation_gate_evidence"]


def test_two_pilots_do_not_pass():
    assert evaluate_minimum_signal_gate({"paid_pilots_count": 2})["validation_gate_passed"] is False


def test_five_lois_pass():
    assert evaluate_minimum_signal_gate({"signed_lois_count": 5})["validation_gate_passed"] is True


def test_ten_data_sharing_companies_pass():
    assert evaluate_minimum_signal_gate({"data_sharing_companies_count": 10})["validation_gate_passed"] is True


def test_anchor_client_passes_alone():
    out = evaluate_minimum_signal_gate({"anchor_client_funded": True})
    assert out["validation_gate_passed"] is True
    assert "anchor client" in out["validation_gate_evidence"]


def test_multiple_criteria_all_cited():
    out = evaluate_minimum_signal_gate({"paid_pilots_count": 4, "anchor_client_funded": True})
    ev = out["validation_gate_evidence"]
    assert "paid pilots" in ev and "anchor client" in ev
