"""Verify the 4 new data-backed scoring fields exist and default to None."""
from opportunity_os.models import Opportunity


def test_new_fields_exist_and_default_to_none():
    """All 4 new fields must be present and default to None when not supplied."""
    opp = Opportunity.empty(name="test")

    assert opp.job_posting_count is None
    assert opp.competitor_negative_review_rate is None
    assert opp.news_signal_count is None
    assert opp.competitor_pricing_data is None


def test_new_fields_accept_values():
    opp = Opportunity(
        name="test",
        geography="global",
        vertical="fintech",
        target_customer="SMBs",
        problem_statement="TBD",
        trigger_signal="TBD",
        job_posting_count=25,
        competitor_negative_review_rate=0.45,
        news_signal_count=12,
        competitor_pricing_data=[{"price_usd": 99.0}],
    )
    assert opp.job_posting_count == 25
    assert abs(opp.competitor_negative_review_rate - 0.45) < 0.001
    assert opp.news_signal_count == 12
    assert isinstance(opp.competitor_pricing_data, list)


# ─── Pipeline-written fields declared on the model (2026-06-10 audit) ─────────

def test_pipeline_written_fields_are_declared():
    """Pydantic's default extra='ignore' silently DROPS undeclared fields on any
    dict -> Opportunity -> dict round-trip. Every field a pipeline step writes
    must therefore be declared. These 19 were found in live data without a
    model declaration during the 2026-06-10 audit, plus 5 conviction bridge fields."""
    pipeline_fields = [
        "market_momentum_score", "competitor_weakness_score", "pain_signal_count",
        "distribution_quality", "thesis_fit_score", "willingness_to_pay_raw",
        "benchmark_fit_score", "benchmark_archetype_description", "analog_benchmarks",
        "sam_usd_estimate", "som_usd_estimate", "tam_rationale", "whitespace",
        "deep_dive_status", "kill_date", "pain_validated_date",
        "distribution_validated_date", "validation_start_date", "validation_deadline",
        "scoring_incomplete",
        "kickoff_at", "build_mode", "outcome", "outcome_note", "outcome_at",
        # 2026-06-12: evidence coverage (calibration) + kill-thesis (Wave 2.1)
        "evidence_coverage", "low_evidence_flag",
        "kill_thesis", "kill_thesis_strength", "kill_thesis_evidence", "kill_thesis_at",
        # 2026-06-12: competitor intelligence (G2 retool)
        "competitor_complaint_themes", "competitor_signal_basis", "competitor_research_at",
        # 2026-06-12: deep-dive Sonnet synthesis (Wave 2.2)
        "synthesis_bull_case", "synthesis_key_risks", "synthesis_recommendation",
        "synthesis_rationale",
    ]
    missing = [f for f in pipeline_fields if f not in Opportunity.model_fields]
    assert not missing, f"Pipeline-written fields missing from model: {missing}"


def test_round_trip_preserves_kill_thesis_and_evidence_fields():
    """The 2026-06-12 fields must survive a dict -> model -> dict round-trip."""
    opp = Opportunity.empty(name="Kill Thesis RT")
    record = {
        **opp.model_dump(),
        "evidence_coverage": 0.33,
        "low_evidence_flag": True,
        "kill_thesis": "Market is too small after the kill-gate filter.",
        "kill_thesis_strength": 8,
        "kill_thesis_evidence": ["postmortem cite", "TAM cite"],
        "kill_thesis_at": "2026-06-12T10:00:00",
    }
    restored = Opportunity.model_validate(record).model_dump()
    assert restored["evidence_coverage"] == 0.33
    assert restored["low_evidence_flag"] is True
    assert restored["kill_thesis_strength"] == 8
    assert restored["kill_thesis_evidence"] == ["postmortem cite", "TAM cite"]


def test_round_trip_preserves_pipeline_fields():
    """Round-tripping a dict through the model must not drop enrichment data."""
    opp = Opportunity.empty(name="Round Trip")
    record = {**opp.model_dump(), "market_momentum_score": 7.5, "pain_signal_count": 6}
    restored = Opportunity.model_validate(record).model_dump()
    assert restored["market_momentum_score"] == 7.5
    assert restored["pain_signal_count"] == 6
