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
