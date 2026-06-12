"""Suite-wide test isolation.

Tests that exercise exception paths trigger pipeline_monitor.log_failure(),
which appends to the LIVE data/pipeline_failures.jsonl. Redirect it to tmp
for every test so the suite never writes to runtime data files.
"""

import pytest


@pytest.fixture(autouse=True)
def _isolate_pipeline_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opportunity_os.pipeline_monitor._failures_path",
        lambda: str(tmp_path / "pipeline_failures.jsonl"),
    )


@pytest.fixture(autouse=True)
def _isolate_outcome_tracking(tmp_path, monkeypatch):
    """The bridge `outcome` command snapshots into outcome_tracking.jsonl via
    record_outcome(); without this redirect, CLI tests pollute the LIVE
    calibration data (8 opp_test_w1 records leaked on 2026-06-12)."""
    monkeypatch.setattr(
        "opportunity_os.outcome_tracking._outcome_file",
        lambda: str(tmp_path / "outcome_tracking.jsonl"),
    )


@pytest.fixture(autouse=True)
def _skip_dotenv(monkeypatch):
    """Never load real API keys from .env during tests — CLI tests invoke
    cli(), which bootstraps the project .env; real keys leaking into
    os.environ could turn mocked tests into live API calls."""
    monkeypatch.setenv("OPP_OS_SKIP_DOTENV", "1")
