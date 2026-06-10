"""Tests for enrichment merge-back: results from steps 9.7/10/11 must appear in
the returned all_opps_sorted list (which daily_run step 12 persists), and paid
research must respect the 30-day skip guard."""

from datetime import datetime, timedelta, timezone

import pytest

from opportunity_os.pipelines.enrichment import run_enrichment_steps


def _make_opp(i: int, **extra) -> dict:
    return {
        "id": f"opp_test_{i:03d}",
        "name": f"Test Opp {i}",
        "geography": "latam",
        "vertical": "smb_software",
        "final_score": 9.0 - i * 0.1,
        "kill_decision": False,
        # Skip guards for steps 11.5 / 11.6 so the test isolates steps 9.7/10/11
        "research_executed_at": "2026-06-01",
        "free_research_at": "2026-06-01",
        **extra,
    }


@pytest.fixture
def patched_research(monkeypatch):
    """Mock every external enrichment source; count paid-research calls."""
    calls = {"pain": 0, "dist": 0}

    monkeypatch.setattr(
        "opportunity_os.engines.benchmark_engine.run_benchmark",
        lambda opp: {"benchmark_archetype": "vertical_saas"},
    )
    monkeypatch.setattr(
        "opportunity_os.pain_intelligence.run_pain_intelligence",
        lambda opp: {"pain_template_built": True},
    )

    def fake_pain_research(opp):
        calls["pain"] += 1
        return {"pain_validation_score": 8.0, "exact_customer_phrases": ["it hurts"]}

    monkeypatch.setattr(
        "opportunity_os.pain_intelligence.execute_pain_research", fake_pain_research
    )
    monkeypatch.setattr(
        "opportunity_os.distribution_intelligence.run_distribution_intelligence",
        lambda opp: {},
    )

    def fake_dist_research(opp):
        calls["dist"] += 1
        return {"distribution_validated": True}

    monkeypatch.setattr(
        "opportunity_os.distribution_intelligence.execute_distribution_research",
        fake_dist_research,
    )
    monkeypatch.setattr("opportunity_os.apify_client.is_available", lambda: False)
    monkeypatch.setattr(
        "opportunity_os.pain_library.upsert_pain_cluster", lambda opp: False
    )
    return calls


def test_enrichment_results_present_in_returned_list(patched_research):
    """Pain/distribution/benchmark results must land in all_opps_sorted —
    the list daily_run step 12 persists. Slice-copy enrichment loses them."""
    opps = [_make_opp(i) for i in range(6)]

    result, top_20 = run_enrichment_steps(opps, dry_run=False)

    top_5 = result[:5]
    assert all(o.get("pain_validation_score") == 8.0 for o in top_5)
    assert all(o.get("distribution_validated") is True for o in top_5)
    assert all(o.get("benchmark_archetype") == "vertical_saas" for o in result[:6])
    # Skip-guard timestamps must persist or research re-runs (and re-bills) daily
    assert all(o.get("pain_researched_at") for o in top_5)
    assert all(o.get("distribution_researched_at") for o in top_5)
    # Returned top_20 must reflect the same enriched records
    assert top_20[0].get("pain_validation_score") == 8.0


def test_recent_research_is_skipped(patched_research):
    """Opps researched within 30 days must not trigger paid calls again."""
    fresh = datetime.now(timezone.utc).isoformat()
    opps = [
        _make_opp(i, pain_researched_at=fresh, distribution_researched_at=fresh)
        for i in range(6)
    ]

    run_enrichment_steps(opps, dry_run=False)

    assert patched_research["pain"] == 0
    assert patched_research["dist"] == 0


def test_stale_research_is_rerun(patched_research):
    """Research older than 30 days is eligible again (30-day TTL, not once-ever)."""
    stale = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    opps = [_make_opp(i, pain_researched_at=stale) for i in range(6)]

    run_enrichment_steps(opps, dry_run=False)

    assert patched_research["pain"] == 5


def test_failed_research_not_stamped(patched_research, monkeypatch):
    """Empty research result (API failure) must NOT stamp the timestamp,
    so the next run retries instead of skipping for 30 days."""
    monkeypatch.setattr(
        "opportunity_os.pain_intelligence.execute_pain_research", lambda opp: {}
    )
    opps = [_make_opp(i) for i in range(6)]

    result, _ = run_enrichment_steps(opps, dry_run=False)

    assert all(not o.get("pain_researched_at") for o in result[:5])


def test_input_list_not_mutated(patched_research):
    """run_enrichment_steps must not mutate the caller's dicts in place."""
    opps = [_make_opp(i) for i in range(6)]
    before = {o["id"]: dict(o) for o in opps}

    run_enrichment_steps(opps, dry_run=False)

    for opp in opps:
        assert opp == before[opp["id"]], f"input dict mutated: {opp['id']}"
