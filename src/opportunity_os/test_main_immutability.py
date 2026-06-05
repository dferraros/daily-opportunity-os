"""Test that CLI commands do not mutate dicts returned from storage."""
from unittest.mock import patch


def test_research_command_does_not_mutate_storage_dict():
    """research CLI command must not mutate the dict returned from get_opportunity_by_id."""
    original = {
        "id": "opp_test_001",
        "name": "Test Opp",
        "geography": "global",
        "research_executed_at": "2026-01-01T00:00:00",
    }
    snapshot = dict(original)
    fake_enriched = {**original, "pain_validation_score": 7.0, "research_executed_at": "2026-06-01"}

    with patch("opportunity_os.storage.get_opportunity_by_id", return_value=original), \
         patch("opportunity_os.storage.update_opportunity", return_value=True), \
         patch("opportunity_os.research_executor.run_research_executor", return_value=fake_enriched):
        from click.testing import CliRunner
        from opportunity_os.main import cli
        runner = CliRunner()
        runner.invoke(cli, ["research", "opp_test_001"])

    assert original == snapshot, f"get_opportunity_by_id result was mutated: {original}"
