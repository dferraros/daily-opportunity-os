"""Tests for storage._make_id determinism and dedup_check behavior."""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

from opportunity_os.storage import dedupe_check, _make_id


# ── _make_id determinism ──────────────────────────────────────────────────────

def test_make_id_is_deterministic_across_processes():
    """_make_id must produce the same ID regardless of PYTHONHASHSEED."""
    script = (
        "from opportunity_os.storage import _make_id; "
        "o = {'name': 'Venezuelan Payment Collection App', 'geography': 'venezuela'}; "
        "print(_make_id(o))"
    )
    env_base = dict(os.environ)
    results = set()
    for seed in ["0", "1", "42"]:
        env = {**env_base, "PYTHONHASHSEED": seed}
        r = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, env=env,
        )
        assert r.returncode == 0, f"Script failed with seed {seed}: {r.stderr}"
        results.add(r.stdout.strip())

    assert len(results) == 1, (
        f"_make_id is not deterministic across PYTHONHASHSEED values: {results}"
    )


def test_make_id_format():
    """_make_id output must match opp_{date}_{geo3}_{4digit} pattern."""
    import re
    opp = {"name": "Test Opp", "geography": "venezuela"}
    opp_id = _make_id(opp)
    assert re.match(r"opp_\d{8}_[a-z]{2,3}_\d{4}$", opp_id), f"Unexpected ID format: {opp_id}"


def test_make_id_different_names_different_ids():
    """Different names must (almost always) produce different hash suffixes."""
    id1 = _make_id({"name": "PayVE", "geography": "venezuela"})
    id2 = _make_id({"name": "InvoiceBot LATAM", "geography": "venezuela"})
    # Same date + same geo, but different name hash
    assert id1 != id2


# ── dedupe_check ──────────────────────────────────────────────────────────────

def _write_opp(path: str, opp: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(opp) + "\n")


def test_dedupe_returns_none_when_no_match(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {"id": "opp_001", "name": "Other Opp", "geography": "global",
                   "first_seen": datetime.now().isoformat()})
    assert dedupe_check("My Opp", "venezuela", path=p) is None


def test_dedupe_finds_exact_match_within_7_days(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {
        "id": "opp_001",
        "name": "My Opp",
        "geography": "venezuela",
        "first_seen": datetime.now().isoformat(),
    })
    assert dedupe_check("My Opp", "venezuela", path=p) == "opp_001"


def test_dedupe_ignores_old_records(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    old_date = (datetime.now() - timedelta(days=10)).isoformat()
    _write_opp(p, {"id": "opp_old", "name": "My Opp", "geography": "venezuela",
                   "first_seen": old_date})
    assert dedupe_check("My Opp", "venezuela", path=p, days=7) is None


def test_dedupe_case_insensitive(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {"id": "opp_001", "name": "MY OPP", "geography": "VENEZUELA",
                   "first_seen": datetime.now().isoformat()})
    assert dedupe_check("my opp", "venezuela", path=p) == "opp_001"


def test_dedupe_geo_mismatch_returns_none(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {"id": "opp_001", "name": "My Opp", "geography": "global",
                   "first_seen": datetime.now().isoformat()})
    assert dedupe_check("My Opp", "venezuela", path=p) is None


def test_dedupe_missing_file_returns_none(tmp_path):
    p = str(tmp_path / "nonexistent.jsonl")
    assert dedupe_check("My Opp", "venezuela", path=p) is None
