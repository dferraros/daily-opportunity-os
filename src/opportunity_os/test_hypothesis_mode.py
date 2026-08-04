"""
Hypothesis-mode tests. Every API boundary (Anthropic, Tavily, kill thesis,
revenue evidence, storage) is monkeypatched -- no live calls, no live writes.
"""

import json

import pytest

from opportunity_os import hypothesis_mode, hypothesis_neighbors
from opportunity_os.models import Opportunity


IDEA = (
    "A reconciliation tool for Venezuelan distributors that receive payments via "
    "pago movil, Zelle, USDT and cash, who currently match payments to invoices "
    "in spreadsheets and lose money on unidentified deposits."
)

INTAKE_JSON = {
    "name": "VE Multi-Rail Reconciliation",
    "geography": "venezuela",
    "vertical": "fintech",
    "problem_statement": (
        "A distributor loses cash visibility because pago movil, Zelle, USDT and "
        "cash do not share one reference, currently solved via spreadsheets."
    ),
    "target_customer": "Distributor CFO / collections lead",
    "monetization_model": "SaaS subscription + setup fee",
    "direct_competitors": ["Galac", "eFactory"],
}

NEIGHBORS_JSON = [
    {"name": "Restaurant-group close", "axis": "customer", "thesis": "t1",
     "entry_rung": "ops_platform", "geography": "venezuela",
     "why_it_might_beat_original": "simpler ICP", "two_sided_check": None},
    {"name": "Konecto Reconciliation module", "axis": "absorb_into_asset",
     "thesis": "t2", "entry_rung": "ops_platform", "geography": "venezuela",
     "why_it_might_beat_original": "shared core",
     "two_sided_check": {"icp_match": "partial", "roadmap_conflict": "low",
                         "cannibalization_risk": "low"}},
]


def _fake_model_json(responses):
    """Return a call_model_json fake that pops canned responses in order."""
    queue = list(responses)

    def fake(system, user, model=None, max_tokens=1500):
        return queue.pop(0) if queue else None
    return fake


@pytest.fixture
def with_api_key(monkeypatch):
    monkeypatch.setattr(hypothesis_neighbors, "_get_api_key", lambda: "test-key")


# ── intake ───────────────────────────────────────────────────────────────────

class TestIntake:
    def test_fails_fast_without_key(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors, "_get_api_key", lambda: None)
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            hypothesis_mode.intake_hypothesis(IDEA)

    def test_empty_idea_rejected(self, with_api_key):
        with pytest.raises(ValueError, match="empty"):
            hypothesis_mode.intake_hypothesis("   ")

    def test_structures_and_stamps(self, with_api_key, monkeypatch):
        monkeypatch.setattr(hypothesis_mode, "call_model_json",
                            _fake_model_json([INTAKE_JSON]))
        opp = hypothesis_mode.intake_hypothesis(IDEA)
        assert opp["source"] == "hypothesis"
        assert opp["stage"] == "hypothesis"
        assert opp["hypothesis_at"]
        assert opp["geography"] == "venezuela"
        assert Opportunity.model_validate(opp)  # round-trips the model

    def test_unusable_model_output_raises(self, with_api_key, monkeypatch):
        monkeypatch.setattr(hypothesis_mode, "call_model_json",
                            _fake_model_json([{"nope": True}]))
        with pytest.raises(ValueError, match="no usable structure"):
            hypothesis_mode.intake_hypothesis(IDEA)

    def test_bad_geography_coerced_to_other(self, with_api_key, monkeypatch):
        monkeypatch.setattr(hypothesis_mode, "call_model_json",
                            _fake_model_json([{**INTAKE_JSON, "geography": "mars"}]))
        opp = hypothesis_mode.intake_hypothesis(IDEA)
        assert opp["geography"] == "other"


# ── neighborhood ─────────────────────────────────────────────────────────────

class TestNeighborhood:
    def test_parses_and_caps(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json",
                            _fake_model_json([NEIGHBORS_JSON * 4]))  # 8 items
        out = hypothesis_neighbors.generate_neighborhood(INTAKE_JSON)
        assert 0 < len(out) <= hypothesis_neighbors.MAX_NEIGHBORS
        assert all(n["name"] and n["axis"] for n in out)

    def test_absorb_axis_carries_two_sided_check(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json",
                            _fake_model_json([NEIGHBORS_JSON]))
        out = hypothesis_neighbors.generate_neighborhood(INTAKE_JSON)
        absorb = [n for n in out if n["axis"] == "absorb_into_asset"]
        assert absorb and absorb[0]["two_sided_check"]["icp_match"] == "partial"

    def test_model_failure_returns_empty_not_invented(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json",
                            _fake_model_json([None]))
        assert hypothesis_neighbors.generate_neighborhood(INTAKE_JSON) == []

    def test_fenced_json_parses(self):
        raw = "```json\n" + json.dumps(NEIGHBORS_JSON) + "\n```"
        assert hypothesis_neighbors._parse_json_block(raw) == NEIGHBORS_JSON


# ── feasibility ──────────────────────────────────────────────────────────────

class TestFeasibility:
    def test_skipped_for_non_regulated(self):
        out = hypothesis_neighbors.run_feasibility_interrogation(
            {"name": "x", "vertical": "edtech", "geography": "latam"})
        assert out == {"feasibility_skipped": "non-regulated vertical"}

    def test_unverified_answer_forces_legal_flag(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors.tavily_client, "is_available", lambda: True)
        monkeypatch.setattr(hypothesis_neighbors.tavily_client, "search_with_content",
                            lambda q, max_results=2: [{"url": "https://e.com", "content": "evidence"}])
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json", _fake_model_json([{
            "answers": {q: ("unverified" if q == "q3_license_needed" else "ok")
                        for q in hypothesis_neighbors.FEASIBILITY_QUESTIONS},
            "legal_flags": ["SUDEBAN perimeter unclear"],
            "any_unverified_legal_assumption": False,  # model lies; code must override
        }]))
        out = hypothesis_neighbors.run_feasibility_interrogation(INTAKE_JSON)
        assert out["legal_opinion_required"] is True

    def test_no_search_evidence_forces_legal_flag(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors.tavily_client, "is_available", lambda: False)
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json", _fake_model_json([{
            "answers": {q: "fine" for q in hypothesis_neighbors.FEASIBILITY_QUESTIONS},
            "legal_flags": [],
            "any_unverified_legal_assumption": False,
        }]))
        out = hypothesis_neighbors.run_feasibility_interrogation(INTAKE_JSON)
        assert out["legal_opinion_required"] is True

    def test_synthesis_failure_is_conservative(self, monkeypatch):
        monkeypatch.setattr(hypothesis_neighbors.tavily_client, "is_available", lambda: False)
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json", _fake_model_json([None]))
        out = hypothesis_neighbors.run_feasibility_interrogation(INTAKE_JSON)
        assert out["legal_opinion_required"] is True
        assert out["feasibility_answers"] == {}


# ── verdict enforcement ──────────────────────────────────────────────────────

class TestVerdictEnforcement:
    def _verdict(self, monkeypatch, opp_extra, model_verdict="build"):
        monkeypatch.setattr(hypothesis_mode, "call_model_json", _fake_model_json([{
            "verdict": model_verdict, "rationale": "looks great",
            "best_neighbor": None, "key_unknowns": [],
        }]))
        opp = {**INTAKE_JSON, "final_score": 8.0, **opp_extra}
        return hypothesis_mode._synthesize_verdict(opp, [])

    def test_legal_opinion_blocks_build(self, monkeypatch):
        v = self._verdict(monkeypatch, {"legal_opinion_required": True})
        assert v["verdict"] == "validate"
        assert "LEGAL OPINION REQUIRED" in v["rationale"]

    def test_strong_kill_thesis_blocks_build(self, monkeypatch):
        v = self._verdict(monkeypatch, {"kill_thesis_strength": 8})
        assert v["verdict"] == "validate"
        assert "kill thesis strength 8" in v["rationale"]

    def test_clean_build_passes(self, monkeypatch):
        v = self._verdict(monkeypatch, {"kill_thesis_strength": 3})
        assert v["verdict"] == "build"

    def test_unknown_verdict_sanitized(self, monkeypatch):
        v = self._verdict(monkeypatch, {}, model_verdict="moonshot")
        assert v["verdict"] == "validate"

    def test_synthesis_failure_never_builds(self, monkeypatch):
        monkeypatch.setattr(hypothesis_mode, "call_model_json", _fake_model_json([None]))
        v = hypothesis_mode._synthesize_verdict({**INTAKE_JSON}, [])
        assert v["verdict"] == "validate"


# ── full run ─────────────────────────────────────────────────────────────────

class TestRunHypothesis:
    @pytest.fixture
    def wired(self, monkeypatch, tmp_path, with_api_key):
        # intake -> neighborhood handled per-module; downstream engines faked
        monkeypatch.setattr(hypothesis_mode, "call_model_json", _fake_model_json([
            INTAKE_JSON,                                            # intake
            [{"name": "Restaurant-group close", "mini_score": 7,
              "reason": "simpler"}],                                # mini-scores
            {"verdict": "validate", "rationale": "needs interviews",
             "best_neighbor": "Restaurant-group close",
             "key_unknowns": ["data export legality"]},             # verdict
        ]))
        monkeypatch.setattr(hypothesis_neighbors, "call_model_json",
                            _fake_model_json([NEIGHBORS_JSON]))
        monkeypatch.setattr(hypothesis_neighbors.tavily_client, "is_available", lambda: False)

        import opportunity_os.kill_thesis as kt
        monkeypatch.setattr(kt, "run_kill_thesis_pass",
                            lambda opp, force=False: {**opp, "kill_thesis": "incumbents ship it",
                                                      "kill_thesis_strength": 5,
                                                      "kill_thesis_at": "2026-08-04T00:00:00"})
        import opportunity_os.revenue_evidence as rev
        monkeypatch.setattr(rev, "run_revenue_evidence",
                            lambda opp, force=False: {**opp, "competitor_pricing_model": "SaaS $30/mo"})
        import opportunity_os.ai_scorer as ai
        monkeypatch.setattr(ai, "score_dimensions_with_ai", lambda opp: {**opp, "pain_severity": 8})
        import opportunity_os.storage as st
        saved = {}
        monkeypatch.setattr(st, "append_opportunity",
                            lambda opp, path=None: saved.update(opp) or "opp_test_hyp")
        return {"tmp": tmp_path, "saved": saved}

    def test_happy_path(self, wired):
        result = hypothesis_mode.run_hypothesis(IDEA, out_dir=str(wired["tmp"]))
        assert result["verdict"] == "validate"
        assert result["best_neighbor"] == "Restaurant-group close"
        # report written with all sections
        report = open(result["report_path"], encoding="utf-8").read()
        for section in ("## Verdict", "## Kill Thesis", "## Feasibility",
                        "## Neighborhood Map", "## Revenue Evidence",
                        "## Questions That Cannot Yet Be Answered"):
            assert section in report, section
        # feasibility ran (fintech) and, lacking evidence, requires legal opinion
        assert "[LEGAL OPINION REQUIRED]" in report
        # validate verdict -> build package written
        assert result["build_paths"], "validate verdict must produce build package"
        # record persisted with verdict fields
        assert wired["saved"]["hypothesis_verdict"] == "validate"
        assert wired["saved"]["neighborhood"]

    def test_neighbors_carry_mini_scores(self, wired):
        result = hypothesis_mode.run_hypothesis(IDEA, out_dir=str(wired["tmp"]))
        scored = [n for n in result["opp"]["neighborhood"] if n.get("mini_score")]
        assert scored and scored[0]["mini_score"] == 7.0

    def test_hypothesis_fields_round_trip_model(self, wired):
        result = hypothesis_mode.run_hypothesis(IDEA, out_dir=str(wired["tmp"]))
        dumped = Opportunity.model_validate(result["opp"]).model_dump()
        assert dumped["hypothesis_verdict"] == "validate"
        assert dumped["neighborhood"]
        assert dumped["legal_opinion_required"] is True
