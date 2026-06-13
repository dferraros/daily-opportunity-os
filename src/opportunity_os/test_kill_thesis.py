"""
Tests for the kill-thesis adversarial pass (Wave 2.1) and its scoring cap.

Covers: inverted query construction, skeptic-response parsing, the never-fabricate
graceful-fail contract, and apply_caps honoring kill_thesis_strength.
"""
import copy

import pytest

from opportunity_os import kill_thesis
from opportunity_os.engines.scoring_engine import (
    KILL_THESIS_CAP_THRESHOLD,
    apply_caps,
)


WEIGHTS = {"caps": {"kill_decision_true": 0.0, "decision_filter_2_failed": 5.0,
                    "kill_thesis_strong": 5.0}}


def base_opp(**over):
    opp = {"name": "Test Opp", "vertical": "fintech", "geography": "venezuela",
           "bucket": "payments", "final_score": 8.0}
    opp.update(over)
    return opp


class TestBuildInvertedQueries:
    def test_produces_failure_oriented_queries(self):
        qs = kill_thesis.build_inverted_queries(base_opp())
        assert qs
        assert all(any(w in q.lower() for w in ("fail", "shutdown", "too small", "refuse"))
                   for q in qs)

    def test_dedupes_and_skips_missing_fields(self):
        qs = kill_thesis.build_inverted_queries(
            {"name": "X", "vertical": "", "geography": "", "bucket": ""}
        )
        assert qs == []  # nothing buildable without vertical/bucket

    def test_no_duplicate_queries(self):
        qs = kill_thesis.build_inverted_queries(base_opp())
        assert len(qs) == len(set(qs))


class TestParseThesisResponse:
    def test_valid_json_parsed(self):
        raw = ('{"kill_thesis": "Market too small", "kill_thesis_strength": 8, '
               '"kill_thesis_evidence": ["cite1", "cite2"]}')
        result = kill_thesis._parse_thesis_response(raw)
        assert result["kill_thesis_strength"] == 8
        assert result["kill_thesis"] == "Market too small"
        assert result["kill_thesis_evidence"] == ["cite1", "cite2"]

    def test_strength_clamped_to_range(self):
        raw = '{"kill_thesis": "x", "kill_thesis_strength": 47}'
        assert kill_thesis._parse_thesis_response(raw)["kill_thesis_strength"] == 10
        raw_lo = '{"kill_thesis": "x", "kill_thesis_strength": -3}'
        assert kill_thesis._parse_thesis_response(raw_lo)["kill_thesis_strength"] == 1

    def test_markdown_fenced_json_parsed(self):
        raw = '```json\n{"kill_thesis": "y", "kill_thesis_strength": 6}\n```'
        assert kill_thesis._parse_thesis_response(raw)["kill_thesis_strength"] == 6

    def test_missing_fields_returns_none(self):
        assert kill_thesis._parse_thesis_response('{"kill_thesis_strength": 8}') is None
        assert kill_thesis._parse_thesis_response('{"kill_thesis": "x"}') is None

    def test_malformed_returns_none(self):
        assert kill_thesis._parse_thesis_response("not json at all") is None
        assert kill_thesis._parse_thesis_response('{"kill_thesis": "x", "kill_thesis_strength": "high"}') is None

    def test_non_list_evidence_coerced(self):
        raw = '{"kill_thesis": "x", "kill_thesis_strength": 5, "kill_thesis_evidence": "single"}'
        assert kill_thesis._parse_thesis_response(raw)["kill_thesis_evidence"] == ["single"]


class TestRunKillThesisPassGracefulFail:
    def test_unchanged_when_tavily_unavailable(self, monkeypatch):
        monkeypatch.setattr(kill_thesis.tavily_client, "is_available", lambda: False)
        opp = base_opp()
        assert kill_thesis.run_kill_thesis_pass(opp) == opp

    def test_unchanged_when_search_empty(self, monkeypatch):
        monkeypatch.setattr(kill_thesis.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(kill_thesis.tavily_client, "search_multi",
                            lambda q, max_results_per_query=3: "")
        opp = base_opp()
        assert kill_thesis.run_kill_thesis_pass(opp) == opp

    def test_unchanged_when_synthesis_fails(self, monkeypatch):
        monkeypatch.setattr(kill_thesis.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(kill_thesis.tavily_client, "search_multi",
                            lambda q, max_results_per_query=3: "some failure evidence")
        monkeypatch.setattr(kill_thesis, "generate_kill_thesis", lambda opp, digest: None)
        opp = base_opp()
        assert kill_thesis.run_kill_thesis_pass(opp) == opp

    def test_fresh_within_ttl_skipped(self, monkeypatch):
        called = {"searched": False}
        def _mark(*a, **k):
            called["searched"] = True
            return "evidence"
        monkeypatch.setattr(kill_thesis.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(kill_thesis.tavily_client, "search_multi", _mark)
        opp = base_opp(kill_thesis_at="2026-06-12T09:00:00")
        # freshness is measured against now(); a same-day stamp is within 30d TTL
        monkeypatch.setattr(kill_thesis, "_is_fresh", lambda o: True)
        kill_thesis.run_kill_thesis_pass(opp)
        assert called["searched"] is False

    def test_stamps_thesis_on_success(self, monkeypatch):
        monkeypatch.setattr(kill_thesis.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(kill_thesis.tavily_client, "search_multi",
                            lambda q, max_results_per_query=3: "evidence digest")
        monkeypatch.setattr(kill_thesis, "generate_kill_thesis",
                            lambda opp, digest: {"kill_thesis": "doomed",
                                                 "kill_thesis_strength": 9,
                                                 "kill_thesis_evidence": ["c"]})
        opp = base_opp()
        result = kill_thesis.run_kill_thesis_pass(opp)
        assert result["kill_thesis_strength"] == 9
        assert result["kill_thesis_at"]
        assert opp.get("kill_thesis_at") is None  # input not mutated


class TestKillThesisCap:
    def test_strong_thesis_caps_score(self):
        opp = base_opp(kill_thesis_strength=KILL_THESIS_CAP_THRESHOLD)
        assert apply_caps(8.5, opp, WEIGHTS) == 5.0

    def test_weak_thesis_does_not_cap(self):
        opp = base_opp(kill_thesis_strength=KILL_THESIS_CAP_THRESHOLD - 1)
        assert apply_caps(8.5, opp, WEIGHTS) == 8.5

    def test_no_thesis_does_not_cap(self):
        assert apply_caps(8.5, base_opp(), WEIGHTS) == 8.5

    def test_kill_decision_overrides_thesis(self):
        opp = base_opp(kill_decision=True, kill_thesis_strength=9)
        assert apply_caps(8.5, opp, WEIGHTS) == 0.0

    def test_cap_does_not_raise_low_scores(self):
        opp = base_opp(kill_thesis_strength=9)
        assert apply_caps(3.0, opp, WEIGHTS) == 3.0  # min(), never lifts

    def test_non_numeric_strength_skipped(self):
        opp = base_opp(kill_thesis_strength="high")
        assert apply_caps(8.5, opp, WEIGHTS) == 8.5  # guarded, no crash

    def test_combines_with_decision_filter_cap(self):
        opp = base_opp(kill_thesis_strength=8, decision_filters_failed=2)
        assert apply_caps(9.0, opp, WEIGHTS) == 5.0  # capped once, not stacked
