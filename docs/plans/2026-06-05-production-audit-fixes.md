# Daily Opportunity OS — Production Audit Fix Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix every critical bug and quality issue found in the full codebase audit — 4 batches, lowest-risk first, tests green throughout.

**Architecture:** Surgical edits to existing files. No new abstractions. TDD where possible. One atomic commit per task.

**Tech Stack:** Python 3.11+, uv, pytest, Pydantic v2, Click, JSONL storage

---

## BATCH 1 — CRITICAL DATA-LOSS BUGS

### Task 1: Fix research executor results silently discarded (enrichment.py step 11.5)

**Files:**
- Modify: `src/opportunity_os/pipelines/enrichment.py` (lines 162-178)
- Test: `src/opportunity_os/pipelines/test_enrichment_apify.py` (add test)

**Problem:** `run_research_executor(opp)` result is never used. Every daily run burns API tokens on research and discards all results silently.

**Step 1: Fix enrichment.py step 11.5**

Replace the entire step 11.5 block (lines 162-178) with:
```python
    # Step 11.5: Research Executor — top 3 ONLY (API cost ~$0.08-0.15/opp)
    # Never increase this limit without checking Anthropic billing first.
    top_3_research = [o for o in all_opps_sorted[:3] if not o.get("research_executed_at")]
    logger.info("Step 11.5: Running Research Executor on top 3 new opportunities (%d unresearched)...", len(top_3_research))
    if dry_run:
        logger.info("  [dry-run] Skipping research executor (API cost ~$0.08-0.15/opp)")
    else:
        try:
            from opportunity_os.research_executor import run_research_executor
            researched_map: dict = {}
            for i, opp in enumerate(top_3_research, 1):
                logger.info("  Researching %d/%d: %s", i, len(top_3_research), opp.get("name", "unknown")[:50])
                enriched = run_research_executor(opp)
                if enriched and enriched.get("id"):
                    researched_map[enriched["id"]] = enriched
            # Merge results back into all_opps_sorted (was: results silently discarded)
            if researched_map:
                all_opps_sorted = [
                    researched_map.get(o.get("id"), o) for o in all_opps_sorted
                ]
                logger.info("  Research executor merged %d enriched records", len(researched_map))
        except ImportError as e:
            logger.warning("Research executor not available: %s", e)
        except Exception as e:
            log_failure("research_executor", e)
```

**Step 2: Write the test**
```python
# Add to src/opportunity_os/pipelines/test_enrichment_apify.py
def test_research_executor_results_merged_back():
    """Step 11.5 must merge enriched results back into all_opps_sorted."""
    from unittest.mock import patch
    opp = {
        "id": "opp_test_merge_001",
        "name": "Test Merge Opp",
        "geography": "global",
        "vertical": "saas",
        "final_score": 8.5,
        "kill_decision": False,
    }
    fake_enriched = {**opp, "pain_validation_score": 7.5, "research_executed_at": "2026-06-01"}

    with patch("opportunity_os.research_executor.run_research_executor", return_value=fake_enriched), \
         patch("opportunity_os.engines.benchmark_engine.run_benchmark", return_value={}), \
         patch("opportunity_os.pain_intelligence.run_pain_intelligence", return_value={}), \
         patch("opportunity_os.pain_intelligence.execute_pain_research", return_value={}), \
         patch("opportunity_os.distribution_intelligence.run_distribution_intelligence", return_value={}), \
         patch("opportunity_os.distribution_intelligence.execute_distribution_research", return_value={}), \
         patch("opportunity_os.free_research.research_opportunity_free", return_value={"free_research_at": "2026-06-01"}), \
         patch("opportunity_os.apify_client.is_available", return_value=False):
        from opportunity_os.pipelines.enrichment import run_enrichment_steps
        result_opps, _ = run_enrichment_steps([opp], dry_run=False)

    found = next((o for o in result_opps if o.get("id") == "opp_test_merge_001"), None)
    assert found is not None
    assert found.get("pain_validation_score") == 7.5, "research_executor results must be merged"
```

**Step 3: Run test**
Run: `uv run pytest src/opportunity_os/pipelines/test_enrichment_apify.py -v`
Expected: all PASS

**Step 4: Commit**
```bash
git add src/opportunity_os/pipelines/enrichment.py src/opportunity_os/pipelines/test_enrichment_apify.py
git commit -m "fix(enrichment): merge run_research_executor results back into all_opps_sorted"
```

---

### Task 2: Fix Step 12 — save ALL enriched opps, not just top_20

**Files:**
- Modify: `src/opportunity_os/pipelines/daily_run.py` (inside `_step_validate_and_sync`, ~line 493)

**Problem:** `enriched_ids = {o["id"]: o for o in top_20}` — only 20 records. Opps 21-N lose their TAM, scoring, geo adjustments, and benchmark data every run.

**Step 1: Fix daily_run.py**

In `_step_validate_and_sync`, find the Step 12 block and change the enriched_ids line:
```python
    # BEFORE (bug — only saves top_20):
    enriched_ids = {o["id"]: o for o in top_20 if o.get("id")}

    # AFTER (fix — saves all enriched opps from all_opps_sorted):
    enriched_ids = {o["id"]: o for o in all_opps_sorted if o.get("id")}
```

Also update the log message:
```python
    logger.info("  Saved %d enriched records (all_opps_sorted, not just top_20)", len(all_opps_sorted))
```

**Step 2: Run tests**
Run: `uv run pytest src/opportunity_os/ -q`
Expected: 53+ passed

**Step 3: Commit**
```bash
git add src/opportunity_os/pipelines/daily_run.py
git commit -m "fix(pipeline): Step 12 must save all_opps_sorted not just top_20"
```

---

### Task 3: Fix dict mutation via .pop() in main.py research command

**Files:**
- Modify: `src/opportunity_os/main.py` (line 100)
- Test: new `src/opportunity_os/test_main_immutability.py`

**Problem:** `opp.pop("research_executed_at", None)` mutates the dict returned from storage, violating the immutability rule.

**Step 1: Write the test**
```python
# src/opportunity_os/test_main_immutability.py
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
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest src/opportunity_os/test_main_immutability.py -v`
Expected: FAIL

**Step 3: Fix main.py**

Replace line 100 (`opp.pop("research_executed_at", None)`) with:
```python
    # Force re-run: create a clean copy without the research timestamp
    # Never mutate the dict returned from storage
    opp = {k: v for k, v in opp.items() if k != "research_executed_at"}
```

**Step 4: Run tests**
Run: `uv run pytest src/opportunity_os/test_main_immutability.py src/opportunity_os/ -q`
Expected: all PASS

**Step 5: Commit**
```bash
git add src/opportunity_os/main.py src/opportunity_os/test_main_immutability.py
git commit -m "fix(main): replace opp.pop() with immutable dict copy in research command"
```

---

## BATCH 2 — SCORING CORRECTNESS

### Task 4: Fix "now" lane — derive from speed_to_mvp when time_to_mvp absent

**Files:**
- Modify: `src/opportunity_os/filters.py`
- Test: new `src/opportunity_os/test_filters_lane.py`

**Problem:** `assign_from_dict` requires `time_to_mvp` (never auto-populated) for "now" lane. Result: every opportunity defaults to "soon", the "now" lane is always empty.

**Step 1: Create test file**
```python
# src/opportunity_os/test_filters_lane.py
from opportunity_os.filters import PortfolioLaneAssigner

def test_now_lane_uses_speed_to_mvp_as_fallback():
    """fast_cash + path_to_first_revenue + speed_to_mvp >= 7 => now, even without time_to_mvp."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp to 10 local businesses",
        "speed_to_mvp": 8,
        # time_to_mvp intentionally absent
    }
    assert assigner.assign_from_dict(opp) == "now"

def test_now_lane_requires_speed_to_mvp_at_least_7():
    """speed_to_mvp < 7 should not qualify for now lane without explicit time_to_mvp."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp",
        "speed_to_mvp": 5,
    }
    assert assigner.assign_from_dict(opp) == "soon"

def test_now_lane_explicit_time_to_mvp_still_works():
    """Existing behavior preserved when time_to_mvp is explicitly set."""
    assigner = PortfolioLaneAssigner()
    opp = {
        "kill_decision": False,
        "bucket": "fast_cash",
        "path_to_first_revenue": "Sell via WhatsApp",
        "time_to_mvp": "2 weeks",
    }
    assert assigner.assign_from_dict(opp) == "now"

def test_strategic_lane():
    assigner = PortfolioLaneAssigner()
    opp = {"kill_decision": False, "bucket": "venture_scale", "tam": 500_000_000}
    assert assigner.assign_from_dict(opp) == "strategic"

def test_kill_decision_always_no():
    assigner = PortfolioLaneAssigner()
    assert assigner.assign_from_dict({"kill_decision": True, "bucket": "fast_cash"}) == "no"

def test_soon_fallback_for_all_others():
    assigner = PortfolioLaneAssigner()
    opp = {"kill_decision": False, "bucket": "latam_asymmetry"}
    assert assigner.assign_from_dict(opp) == "soon"
```

**Step 2: Run tests to verify they fail**
Run: `uv run pytest src/opportunity_os/test_filters_lane.py -v`
Expected: test_now_lane_uses_speed_to_mvp_as_fallback FAIL

**Step 3: Fix filters.py**

Replace `assign_from_dict`:
```python
    def assign_from_dict(self, opp_dict: dict) -> str:
        """
        Compute portfolio lane for a raw dict.

        Rules (priority order):
        1. "no"         — kill_decision is True
        2. "now"        — bucket is fast_cash AND path_to_first_revenue is non-empty
                          AND (time_to_mvp is set OR speed_to_mvp >= 7)
        3. "strategic"  — bucket is venture_scale AND tam >= STRATEGIC_TAM_THRESHOLD
        4. "soon"       — all surviving opportunities not matched above
        """
        if opp_dict.get("kill_decision"):
            return "no"

        bucket = opp_dict.get("bucket", "")
        path_to_rev = opp_dict.get("path_to_first_revenue")

        has_revenue_path = (
            path_to_rev is not None
            and str(path_to_rev).strip()
            and str(path_to_rev).strip().upper() != "TBD"
        )

        # time_to_mvp explicit OR speed_to_mvp >= 7 (never auto-populated, so use scoring fallback)
        time_to_mvp = opp_dict.get("time_to_mvp")
        has_mvp_signal = (
            (time_to_mvp is not None and str(time_to_mvp).strip())
            or int(opp_dict.get("speed_to_mvp") or 0) >= 7
        )

        if bucket == "fast_cash" and has_revenue_path and has_mvp_signal:
            return "now"

        tam = opp_dict.get("tam") or opp_dict.get("tam_usd_estimate")
        if bucket == "venture_scale" and tam is not None:
            try:
                if float(tam) >= self.STRATEGIC_TAM_THRESHOLD:
                    return "strategic"
            except (TypeError, ValueError):
                pass

        return "soon"
```

**Step 4: Run all tests**
Run: `uv run pytest src/opportunity_os/test_filters_lane.py src/opportunity_os/ -q`
Expected: all PASS

**Step 5: Commit**
```bash
git add src/opportunity_os/filters.py src/opportunity_os/test_filters_lane.py
git commit -m "fix(filters): derive now-lane from speed_to_mvp>=7 when time_to_mvp absent"
```

---

### Task 5: Fix _make_id — use hashlib instead of hash() for deterministic IDs

**Files:**
- Modify: `src/opportunity_os/storage.py` (function `_make_id`, lines 58-63)
- Test: new `src/opportunity_os/test_storage_deterministic.py`

**Problem:** Python's `hash()` is randomized per process (PYTHONHASHSEED). Two pipeline runs produce different IDs for the same opportunity name, potentially creating duplicate JSONL records.

**Step 1: Write the test**
```python
# src/opportunity_os/test_storage_deterministic.py
import subprocess
import sys
import os

def test_make_id_is_deterministic_across_processes():
    """_make_id must produce the same ID regardless of PYTHONHASHSEED."""
    script = (
        "from opportunity_os.storage import _make_id; "
        "o = {'name': 'Test Opp Venezuela Payments', 'geography': 'venezuela'}; "
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
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest src/opportunity_os/test_storage_deterministic.py -v`
Expected: FAIL (multiple different IDs for different seeds)

**Step 3: Fix storage.py**

Add `import hashlib` to the imports at top of `storage.py`, then replace `_make_id`:
```python
import hashlib

def _make_id(opp: dict) -> str:
    """Generate opp_{date}_{geo}_{hash4} id from opportunity dict.
    Uses hashlib.md5 for deterministic output regardless of PYTHONHASHSEED.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    geo = (opp.get("geography") or "xx")[:3].lower().replace(" ", "")
    name = opp.get("name", "")
    name_hash = int(
        hashlib.md5(name.encode("utf-8"), usedforsecurity=False).hexdigest(), 16
    ) % 10000
    return f"opp_{date_str}_{geo}_{name_hash:04d}"
```

**Step 4: Run tests**
Run: `uv run pytest src/opportunity_os/test_storage_deterministic.py src/opportunity_os/ -q`
Expected: all PASS

**Step 5: Commit**
```bash
git add src/opportunity_os/storage.py src/opportunity_os/test_storage_deterministic.py
git commit -m "fix(storage): replace hash() with hashlib.md5 in _make_id for deterministic IDs"
```

---

### Task 6: Fix stats command — guard first_seen.startswith() against datetime objects

**Files:**
- Modify: `src/opportunity_os/main.py` (line 164)

**Problem:** `o.get("first_seen", "").startswith(today)` throws AttributeError when `first_seen` is stored as a datetime object (Pydantic model_dump output).

**Step 1: Fix main.py line 164**

```python
    # Before (bug — AttributeError if first_seen is datetime):
    today_opps = [o for o in all_opps if o.get("first_seen", "").startswith(today)]

    # After (safe — cast to str first):
    today_opps = [o for o in all_opps if str(o.get("first_seen") or "").startswith(today)]
```

**Step 2: Run tests**
Run: `uv run pytest src/opportunity_os/ -q`
Expected: all PASS

**Step 3: Commit**
```bash
git add src/opportunity_os/main.py
git commit -m "fix(stats): guard first_seen.startswith() against datetime objects"
```

---

## BATCH 3 — CODE QUALITY

### Task 7: Fix __import__ anti-pattern + isolate pytest testpaths

**Files:**
- Modify: `src/opportunity_os/free_research.py` (line 447)
- Modify: `pyproject.toml` (add [tool.pytest.ini_options])

**Step 1: Fix free_research.py**

Add `from datetime import datetime` to the imports at the top of `free_research.py` (after the existing imports block).

Replace line 447:
```python
    # Before (anti-pattern):
    result["free_research_at"] = __import__("datetime").datetime.now().isoformat()

    # After (clean):
    result["free_research_at"] = datetime.now().isoformat()
```

**Step 2: Fix pyproject.toml — add testpaths**

Add this section to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["src/opportunity_os"]
```

**Step 3: Verify pytest now only collects opportunity_os tests**
Run: `uv run pytest --collect-only -q 2>&1 | head -20`
Expected: only opportunity_os test files listed, zero "pytest_asyncio" errors

Run: `uv run pytest -q`
Expected: 53+ passed, 0 collection errors

**Step 4: Commit**
```bash
git add src/opportunity_os/free_research.py pyproject.toml
git commit -m "fix(quality): replace __import__ anti-pattern; add pytest testpaths config"
```

---

### Task 8: Fix score_opportunity dict mutation

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py` (end of `score_opportunity`, lines 399-430)

**Problem:** `opp["attractiveness_score"] = ...` mutates the shallow copy. Should return a new dict via spread.

**Step 1: Fix scoring_engine.py**

Replace the final block of `score_opportunity` (from `# --- Layer 1` to `return opp`):

```python
    # --- Layer 1: Attractiveness ---
    attractiveness = score_layer(opp, ATTRACTIVENESS_FIELDS, weights)

    # --- Layer 2: Executability ---
    executability = score_layer(opp, EXECUTABILITY_FIELDS, weights)

    # --- Venezuela wedge bonus: applied to regional_fit before Layer 3 ---
    opp = apply_venezuela_wedge_bonus(opp, weights)

    # --- Layer 3: Strategic Value ---
    strategic = score_layer(opp, STRATEGIC_VALUE_FIELDS, weights)

    # --- Composite: 50% attractiveness + 30% executability + 20% strategic ---
    composite = (
        0.50 * attractiveness +
        0.30 * executability +
        0.20 * strategic
    )

    # --- Modifiers ---
    composite = apply_modifiers(composite, opp, weights)

    # --- Caps ---
    composite = apply_caps(composite, opp, weights)

    return {
        **opp,
        "attractiveness_score": round(attractiveness, 4),
        "executability_score": round(executability, 4),
        "strategic_value_score": round(strategic, 4),
        "final_score": round(max(0.0, min(10.0, composite)), 4),
    }
```

This removes the three `opp[...] = ...` direct assignments and `opp["final_score"] = ...` at the end.

**Step 2: Run tests**
Run: `uv run pytest src/opportunity_os/ -q`
Expected: 53+ passed

**Step 3: Commit**
```bash
git add src/opportunity_os/engines/scoring_engine.py
git commit -m "fix(scoring): eliminate direct dict mutation in score_opportunity; use spread return"
```

---

## BATCH 4 — TEST COVERAGE

### Task 9: Add kill gate + normalization + storage tests

**Files:**
- Create: `src/opportunity_os/engines/test_kill_gate.py`
- Create: `src/opportunity_os/test_normalization.py`
- Create: `src/opportunity_os/test_storage_dedup.py`

**Step 1: Create src/opportunity_os/engines/test_kill_gate.py**
```python
"""Unit tests for kill_gate.evaluate_kill_gate."""
from opportunity_os.engines.kill_gate import evaluate_kill_gate, KILL_THRESHOLD, format_kill_report


def _all_pass():
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
    assert "KG-04" in result.kill_reason


def test_all_fail_triggers_kill():
    answers = {f"KG-0{i}": False for i in range(1, 8)}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True
    assert result.failed_count == 7


def test_unknown_criterion_ids_ignored():
    answers = {"KG-99": False, "KG-01": True, "KG-02": False, "KG-03": False}
    result = evaluate_kill_gate(answers)
    assert result.kill_decision is True  # KG-02 + KG-03 = 2
    assert "KG-99" not in result.failed_criteria


def test_empty_answers_clears_gate():
    result = evaluate_kill_gate({})
    assert result.kill_decision is False
    assert result.passed_count == 0
    assert result.failed_count == 0


def test_kill_reason_contains_failed_ids():
    answers = {**_all_pass(), "KG-01": False, "KG-03": False}
    result = evaluate_kill_gate(answers)
    assert "KG-01" in result.kill_reason
    assert "KG-03" in result.kill_reason


def test_format_kill_report_contains_decision():
    answers = {**_all_pass(), "KG-02": False, "KG-06": False}
    result = evaluate_kill_gate(answers)
    report = format_kill_report(result)
    assert "KILLED" in report
    assert "KG-02" in report
    assert "KG-06" in report
```

**Step 2: Create src/opportunity_os/test_normalization.py**
```python
"""Unit tests for normalization pipeline."""
from opportunity_os.normalization import (
    normalize_geography,
    _is_noise_signal,
    normalize_field_names,
    infer_bucket,
    normalize_signal,
    FIELD_ALIASES,
)


def test_normalize_geography_ve_variants():
    for raw_geo in ["ve", "vzla", "ven", "VE", "VZla"]:
        result = normalize_geography({"geography": raw_geo})
        assert result["geography"] == "venezuela", f"Failed for geo: {raw_geo!r}"


def test_normalize_geography_latam_variants():
    for raw_geo in ["colombia", "co", "Mexico", "mx", "argentina", "ar", "brazil", "br"]:
        result = normalize_geography({"geography": raw_geo})
        assert result["geography"] == "latam", f"Failed for geo: {raw_geo!r}"


def test_normalize_geography_spain():
    assert normalize_geography({"geography": "es"})["geography"] == "spain"
    assert normalize_geography({"geography": "spain"})["geography"] == "spain"


def test_normalize_geography_unknown_defaults_to_global():
    result = normalize_geography({"geography": "neptune"})
    assert result["geography"] == "global"


def test_noise_signal_hn_ask():
    assert _is_noise_signal("Ask HN: What tools do you use for X?") is True


def test_noise_signal_funding_news():
    assert _is_noise_signal("Stripe raised $600M in Series G") is True
    assert _is_noise_signal("Who is hiring — June 2026") is True


def test_noise_signal_legitimate_opportunity():
    assert _is_noise_signal("WhatsApp invoice automation for Venezuelan SMBs") is False
    assert _is_noise_signal("USDT payment collection for Venezuelan freelancers") is False


def test_field_alias_tam_usd_estimate_maps_to_tam():
    result = normalize_field_names({"tam_usd_estimate": 5_000_000})
    assert "tam" in result, "tam_usd_estimate should alias to tam"


def test_field_alias_title_maps_to_name():
    result = normalize_field_names({"title": "My Opportunity"})
    assert result["name"] == "My Opportunity"


def test_infer_bucket_ve_always_latam_asymmetry():
    raw = {"geography": "venezuela", "name": "Test", "vertical": "saas"}
    result = infer_bucket(raw)
    assert result["bucket"] == "latam_asymmetry"


def test_infer_bucket_large_tam_is_venture_scale():
    raw = {"geography": "global", "name": "Test", "vertical": "saas", "tam": 500_000_000}
    result = infer_bucket(raw)
    assert result["bucket"] == "venture_scale"


def test_normalize_signal_end_to_end_ve():
    raw = {
        "title": "Payment collection app for Venezuelan SMBs",
        "geo": "ve",
        "market": "fintech",
        "description": "Helps small businesses collect payments via USDT and Zelle",
    }
    opp, errors = normalize_signal(raw)
    assert opp is not None, f"Normalization failed: {errors}"
    assert opp.geography == "venezuela"
    assert opp.vertical == "fintech"
    assert opp.bucket == "latam_asymmetry"


def test_normalize_signal_rejects_hn_noise():
    raw = {"name": "Ask HN: Is there a tool for X?", "geography": "global"}
    opp, errors = normalize_signal(raw)
    assert opp is None
    assert any("Rejected" in e for e in errors)
```

**Step 3: Create src/opportunity_os/test_storage_dedup.py**
```python
"""Unit tests for storage dedup_check."""
import os
import tempfile
import json
from datetime import datetime, timedelta

from opportunity_os.storage import dedupe_check, append_opportunity


def _write_opp(path: str, opp: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(opp) + "\n")


def test_dedupe_returns_none_when_no_match(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {"id": "opp_001", "name": "Other Opp", "geography": "global",
                   "first_seen": datetime.now().isoformat()})
    result = dedupe_check("My Opp", "venezuela", path=p)
    assert result is None


def test_dedupe_finds_exact_match_within_7_days(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {
        "id": "opp_001",
        "name": "My Opp",
        "geography": "venezuela",
        "first_seen": datetime.now().isoformat(),
    })
    result = dedupe_check("My Opp", "venezuela", path=p)
    assert result == "opp_001"


def test_dedupe_ignores_old_records(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    old_date = (datetime.now() - timedelta(days=10)).isoformat()
    _write_opp(p, {
        "id": "opp_old",
        "name": "My Opp",
        "geography": "venezuela",
        "first_seen": old_date,
    })
    result = dedupe_check("My Opp", "venezuela", path=p, days=7)
    assert result is None


def test_dedupe_case_insensitive(tmp_path):
    p = str(tmp_path / "opps.jsonl")
    _write_opp(p, {
        "id": "opp_001",
        "name": "MY OPP",
        "geography": "VENEZUELA",
        "first_seen": datetime.now().isoformat(),
    })
    result = dedupe_check("my opp", "venezuela", path=p)
    assert result == "opp_001"
```

**Step 4: Run all new tests**
Run: `uv run pytest src/opportunity_os/engines/test_kill_gate.py src/opportunity_os/test_normalization.py src/opportunity_os/test_storage_dedup.py -v`
Expected: all PASS (these are pure logic tests)

**Step 5: Commit**
```bash
git add src/opportunity_os/engines/test_kill_gate.py \
        src/opportunity_os/test_normalization.py \
        src/opportunity_os/test_storage_dedup.py
git commit -m "test(coverage): add kill gate, normalization, and storage dedup tests"
```

---

### Task 10: Final verification + push

**Step 1: Run full test suite**
Run: `uv run pytest -v --tb=short`
Expected: 70+ tests, all PASS

**Step 2: Verify rescore dry-run still works**
Run: `uv run opp-os rescore-all --dry-run`
Expected: score delta table printed, "No files written."

**Step 3: Push to remote**
```bash
git log --oneline origin/master..HEAD
git push origin master
```

---

## Summary

| Batch | Tasks | Critical Impact |
|-------|-------|----------------|
| 1 — Data Loss | 3 | API spend wasted; opps lose enrichment every run; storage mutation |
| 2 — Scoring | 3 | "now" lane never fires; IDs non-deterministic; stats crashes |
| 3 — Quality | 2 | __import__ anti-pattern; pytest collects 19 unrelated project tests |
| 4 — Tests | 2 | Kill gate, normalization, storage dedup all untested |
