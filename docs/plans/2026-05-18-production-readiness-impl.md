# Production Readiness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Pain OS and Distribution OS produce real research data, wire that data into the scoring engine, add CI, and bring daily_run.py under the 800-line limit.

**Architecture:** Three phases. Phase 1 adds real execution functions to `pain_intelligence.py` and `distribution_intelligence.py` and wires them into `daily_run.py` steps 10-11. Phase 2 adds two new scoring dimensions that consume Phase 1 output. Phase 3 adds GitHub Actions CI and splits `daily_run.py` below the 800-line hard limit.

**Tech Stack:** Python 3.11+, `anthropic` SDK (already installed), pytest, GitHub Actions

---

## CONTEXT FOR EXECUTOR

The project lives at `src/opportunity_os/`. Run all commands from the repo root.
Run tests with: `uv run pytest tests/ -v`
The `anthropic` SDK is installed. The Anthropic API key is in `.env` as `ANTHROPIC_API_KEY=...`.
Model constant already defined in `distribution_intelligence.py`: `MODEL = "claude-haiku-4-5-20251001"` — use same in pain module.

### Why each existing step is broken

- `run_pain_intelligence()` (`pain_intelligence.py:275`) returns a template dict. Never calls any API. All 79 opps have `pain_validation_score = None`.
- `run_distribution_executor()` (`distribution_intelligence.py:416`) exists and calls Claude, but depends on `tavily_client` which is NOT installed — it silently returns `{}` on every call.
- `daily_run.py` step 10 calls `run_pain_intelligence()` (the template builder). It never calls the executor.
- `daily_run.py` step 11 calls `run_distribution_intelligence()` (also a template builder). `run_distribution_executor()` is never called from the pipeline.

---

## Phase 1 — Execute Real Research

---

### Task 1: Add `execute_pain_research()` to `pain_intelligence.py`

**Files:**
- Modify: `src/opportunity_os/pain_intelligence.py` (append after line 338)
- Create: `tests/test_pain_intelligence.py`

**Step 1: Write the failing test**

Create `tests/test_pain_intelligence.py`:

```python
"""Tests for pain_intelligence.py — build_pain_queries, execute_pain_research."""
import pytest
from unittest.mock import MagicMock, patch
from opportunity_os.pain_intelligence import (
    build_pain_queries,
    execute_pain_research,
    is_pain_validated,
    pain_score_label,
)


# ─── build_pain_queries ───────────────────────────────────────────────────────

def test_build_pain_queries_returns_list():
    opp = {"vertical": "fintech", "geography": "venezuela"}
    result = build_pain_queries(opp)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_build_pain_queries_uses_wedge_category():
    opp = {"venezuela_wedge_category": "payments_and_collections"}
    result = build_pain_queries(opp)
    assert any("USDT" in q or "cobrar" in q or "pago" in q for q in result)


def test_build_pain_queries_deduplicates():
    opp = {
        "venezuela_wedge_category": "payments_and_collections",
        "vertical": "payments",
        "geography": "venezuela",
    }
    result = build_pain_queries(opp)
    assert len(result) == len(set(result)), "queries must be deduplicated"


# ─── execute_pain_research ────────────────────────────────────────────────────

def _make_mock_client(json_text: str):
    """Return a mock Anthropic client that returns json_text in its response."""
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = json_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def test_execute_pain_research_returns_dict_on_success():
    json_text = '{"pain_validation_score": 8.0, "exact_customer_phrases": ["no puedo cobrar"], "pain_evidence_sources": ["reddit r/vzla"], "workarounds_found": ["USDT P2P"]}'
    client = _make_mock_client(json_text)
    opp = {"id": "t1", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=client)
    assert result.get("pain_validation_score") == 8.0
    assert "pain_researched_at" in result


def test_execute_pain_research_no_api_key_returns_empty():
    """When no API key and no client passed, return empty dict gracefully."""
    opp = {"id": "t2", "name": "Test", "geography": "global", "vertical": "saas"}
    with patch.dict("os.environ", {}, clear=True):
        with patch("opportunity_os.pain_intelligence._load_api_key", return_value=None):
            result = execute_pain_research(opp)
    assert result == {}


def test_execute_pain_research_skips_if_researched_recently():
    """Skip if pain_researched_at is within the last 7 days."""
    from datetime import date
    opp = {
        "id": "t3",
        "name": "Test",
        "geography": "global",
        "pain_researched_at": date.today().isoformat(),
    }
    result = execute_pain_research(opp, client=MagicMock())
    assert result == {}


def test_execute_pain_research_graceful_on_api_error():
    """API exception must return empty dict, not raise."""
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("network error")
    opp = {"id": "t4", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=mock_client)
    assert result == {}


def test_execute_pain_research_handles_bad_json():
    """Malformed JSON from the model must return empty dict."""
    client = _make_mock_client("not valid json at all")
    opp = {"id": "t5", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_pain_research(opp, client=client)
    assert result == {}


def test_execute_pain_research_does_not_mutate_input():
    json_text = '{"pain_validation_score": 7.0, "exact_customer_phrases": [], "pain_evidence_sources": [], "workarounds_found": []}'
    client = _make_mock_client(json_text)
    opp = {"id": "t6", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    keys_before = set(opp.keys())
    execute_pain_research(opp, client=client)
    assert set(opp.keys()) == keys_before, "must not mutate input"


# ─── is_pain_validated ────────────────────────────────────────────────────────

def test_is_pain_validated_true_for_score_7():
    assert is_pain_validated({"pain_validation_score": 7.0}) is True


def test_is_pain_validated_false_for_score_6():
    assert is_pain_validated({"pain_validation_score": 6.9}) is False


def test_is_pain_validated_false_for_none():
    assert is_pain_validated({}) is False


# ─── pain_score_label ─────────────────────────────────────────────────────────

def test_pain_score_label_critical():
    assert "critical" in pain_score_label(9.5)


def test_pain_score_label_unscored():
    assert pain_score_label(None) == "unscored"
```

**Step 2: Run tests to verify they fail**

```
uv run pytest tests/test_pain_intelligence.py -v
```
Expected: FAIL — `ImportError: cannot import name 'execute_pain_research'`

**Step 3: Add `execute_pain_research()` to `pain_intelligence.py`**

After the existing module-level constants, add the `MODEL` constant and a `_load_api_key` helper. Then append `execute_pain_research()` at the end of the file after `pain_score_label()`:

First, add at the top of the file (after existing imports, before PAIN_CATEGORY_QUERIES):
```python
import json
import logging
import os
import re
from datetime import date, datetime

MODEL = "claude-haiku-4-5-20251001"

logger = logging.getLogger(__name__)
```

Note: `from __future__ import annotations`, `from datetime import date`, and `from typing import Optional` are already present. Add `import json`, `import logging`, `import os`, `import re`, `from datetime import datetime` (keep existing `date` import).

Then append this function at the end of the file:

```python
# ─── Pain Research Executor ───────────────────────────────────────────────────

def _load_api_key() -> Optional[str]:
    """Load ANTHROPIC_API_KEY from .env file."""
    from pathlib import Path
    for parent in list(Path(__file__).resolve().parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
            break
    return None


def execute_pain_research(opp: dict, client=None) -> dict:
    """
    Execute real pain research via Anthropic API with web search.

    Calls Claude to search for evidence of customer pain matching this opportunity.
    Returns dict with pain fields populated, or {} on any failure (never raises).

    Args:
        opp: opportunity dict (not mutated)
        client: optional pre-built anthropic.Anthropic client (for testing)

    Returns populated fields:
        - pain_validation_score: float 0-10
        - exact_customer_phrases: list[str]
        - pain_evidence_sources: list[str]
        - workarounds_found: list[str]
        - pain_researched_at: str (ISO date)
    """
    # Skip guard: do not re-research within 7 days
    last_researched = opp.get("pain_researched_at")
    if last_researched:
        try:
            days_ago = (date.today() - date.fromisoformat(str(last_researched)[:10])).days
            if days_ago < 7:
                return {}
        except (ValueError, TypeError):
            pass

    # Resolve client
    if client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_api_key()
        if not api_key:
            return {}
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        except Exception:
            return {}

    queries = build_pain_queries(opp)
    geo = opp.get("geography", "global")
    geo_label = "Venezuela" if geo == "venezuela" else geo.upper()
    problem = (opp.get("problem_statement") or "")[:200]
    query_list = "\n".join(f"- {q}" for q in queries[:4])

    prompt = f"""Research customer pain validation for this business opportunity.

Name: {opp.get("name", "")}
Geography: {geo_label}
Vertical: {opp.get("vertical", "")}
Problem: {problem}

Search for real evidence of this pain using these queries (search in Spanish where relevant):
{query_list}

Score the pain severity based on evidence found (volume of complaints, failed workarounds, daily urgency).

Return ONLY this JSON object — no prose, no markdown fences:
{{
  "pain_validation_score": <float 0-10>,
  "exact_customer_phrases": [<up to 3 real complaint phrases found verbatim>],
  "pain_evidence_sources": [<source platform or URL descriptions where evidence was found>],
  "workarounds_found": [<what people do today to solve this pain>]
}}"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        logger.warning("Pain research API call failed for '%s': %s", opp.get("name"), e)
        return {}

    # Extract text content (model may return tool_use + text blocks)
    raw = ""
    for block in (response.content or []):
        if hasattr(block, "type") and block.type == "text":
            raw = block.text.strip()
            break

    if not raw:
        return {}

    # Strip markdown fences if model wrapped the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    try:
        data = json.loads(match.group())
    except (json.JSONDecodeError, ValueError):
        logger.warning("Pain research returned invalid JSON for '%s'", opp.get("name"))
        return {}

    result: dict = {"pain_researched_at": date.today().isoformat()}

    score_val = data.get("pain_validation_score")
    if score_val is not None:
        try:
            result["pain_validation_score"] = round(float(score_val), 2)
        except (ValueError, TypeError):
            pass

    for list_field in ("exact_customer_phrases", "pain_evidence_sources", "workarounds_found"):
        val = data.get(list_field)
        if isinstance(val, list):
            result[list_field] = [str(x)[:200] for x in val[:3] if x]

    return result
```

**Step 4: Run tests**

```
uv run pytest tests/test_pain_intelligence.py -v
```
Expected: All tests PASS.

**Step 5: Commit**

```bash
git add src/opportunity_os/pain_intelligence.py tests/test_pain_intelligence.py
git commit -m "feat(pain-os): add execute_pain_research() with Anthropic web search + tests"
```

---

### Task 2: Wire pain executor into `daily_run.py` step 10

**Files:**
- Modify: `src/opportunity_os/pipelines/daily_run.py` (~line 447-460 in `_step_enrich_and_rank`)

**Step 1: Locate the exact lines to change**

In `_step_enrich_and_rank()`, find the "Step 10: Customer Pain OS" block (around line 447):

```python
    # Step 10: Customer Pain OS
    logger.info("Step 10: Running Customer Pain OS on top 20 opportunities...")
    top_20 = all_opps_sorted[:20]
    try:
        from opportunity_os.pain_intelligence import run_pain_intelligence
        for i, opp in enumerate(top_20):
            pain_result = run_pain_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in pain_result.items() if not k.startswith("_")}}
            logger.info("  Pain queries built for: %s (%d queries)",
                        opp.get("name", "unknown"), len(pain_result.get("_pain_queries", [])))
    except ImportError as e:
        logger.warning("Pain intelligence module not available: %s", e)
    except Exception as e:
        log_failure("pain_os", e)
```

**Step 2: Replace with version that calls the executor on top 5**

Replace the entire Step 10 block with:

```python
    # Step 10: Customer Pain OS
    logger.info("Step 10: Running Customer Pain OS on top 20 opportunities...")
    top_20 = all_opps_sorted[:20]
    try:
        from opportunity_os.pain_intelligence import run_pain_intelligence, execute_pain_research
        for i, opp in enumerate(top_20):
            pain_result = run_pain_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in pain_result.items() if not k.startswith("_")}}
        logger.info("  Pain templates built for %d opportunities", len(top_20))

        # Execute real research on top 5 only (API cost ~$0.15/opp)
        if not dry_run:
            top_5 = top_20[:5]
            researched_count = 0
            for i, opp in enumerate(top_5):
                research_result = execute_pain_research(opp)
                if research_result:
                    top_20[i] = {**top_20[i], **research_result}
                    researched_count += 1
                    logger.info("  Pain researched: %s (score: %s)",
                                opp.get("name", "unknown")[:40],
                                research_result.get("pain_validation_score"))
            logger.info("  Pain research executed for %d/5 opportunities", researched_count)
    except ImportError as e:
        logger.warning("Pain intelligence module not available: %s", e)
    except Exception as e:
        log_failure("pain_os", e)
```

**Step 3: Run the full test suite**

```
uv run pytest tests/ -v
```
Expected: All existing tests PASS (no regressions). `test_pain_intelligence.py` PASS.

**Step 4: Commit**

```bash
git add src/opportunity_os/pipelines/daily_run.py
git commit -m "feat(pain-os): wire execute_pain_research into daily_run step 10 (top 5, dry-run safe)"
```

---

### Task 3: Add `execute_distribution_research()` to `distribution_intelligence.py` + tests

**Context:** `run_distribution_executor()` already exists at line 416 of `distribution_intelligence.py` but depends on `tavily_client` which is NOT installed. It always silently returns `{}`. Replace with a direct Anthropic API call (same pattern as pain executor).

**Files:**
- Modify: `src/opportunity_os/distribution_intelligence.py` (add new function near line 519, before `_load_api_key`)
- Create: `tests/test_distribution_intelligence.py`

**Step 1: Write the failing test**

Create `tests/test_distribution_intelligence.py`:

```python
"""Tests for distribution_intelligence.py — execute_distribution_research."""
import pytest
from unittest.mock import MagicMock, patch
from opportunity_os.distribution_intelligence import (
    build_distribution_queries,
    get_recommended_channels,
    execute_distribution_research,
    is_distribution_validated,
    distribution_ease_label,
)


# ─── build_distribution_queries ──────────────────────────────────────────────

def test_build_distribution_queries_returns_list():
    opp = {"geography": "venezuela", "vertical": "fintech"}
    result = build_distribution_queries(opp)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_get_recommended_channels_for_venezuela():
    opp = {"geography": "venezuela", "vertical": "fintech"}
    channels = get_recommended_channels(opp)
    assert len(channels) >= 1
    assert any("whatsapp" in c.lower() or "WhatsApp" in c for c in channels)


# ─── execute_distribution_research ───────────────────────────────────────────

def _make_mock_client(json_text: str):
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = json_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def test_execute_distribution_research_returns_dict_on_success():
    json_text = '{"distribution_validated": true, "top_distribution_channels": ["WhatsApp"], "estimated_cac_logic": "~$12 CAC via WhatsApp", "first_10_customer_path": "Outreach to 50 VE SMBs", "trust_mechanism_latam": "WhatsApp referral"}'
    client = _make_mock_client(json_text)
    opp = {"id": "d1", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=client)
    assert result.get("distribution_validated") is True
    assert "distribution_researched_at" in result


def test_execute_distribution_research_no_api_key_returns_empty():
    opp = {"id": "d2", "name": "Test", "geography": "global", "vertical": "saas"}
    with patch.dict("os.environ", {}, clear=True):
        with patch("opportunity_os.distribution_intelligence._load_api_key", return_value=None):
            result = execute_distribution_research(opp)
    assert result == {}


def test_execute_distribution_research_skips_if_researched_recently():
    from datetime import date
    opp = {
        "id": "d3",
        "name": "Test",
        "geography": "global",
        "distribution_researched_at": date.today().isoformat(),
    }
    result = execute_distribution_research(opp, client=MagicMock())
    assert result == {}


def test_execute_distribution_research_graceful_on_api_error():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("timeout")
    opp = {"id": "d4", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=mock_client)
    assert result == {}


def test_execute_distribution_research_handles_bad_json():
    client = _make_mock_client("not json")
    opp = {"id": "d5", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    result = execute_distribution_research(opp, client=client)
    assert result == {}


def test_execute_distribution_research_does_not_mutate_input():
    json_text = '{"distribution_validated": true, "top_distribution_channels": [], "estimated_cac_logic": "n/a", "first_10_customer_path": "n/a", "trust_mechanism_latam": "referral"}'
    client = _make_mock_client(json_text)
    opp = {"id": "d6", "name": "Test", "geography": "venezuela", "vertical": "fintech"}
    keys_before = set(opp.keys())
    execute_distribution_research(opp, client=client)
    assert set(opp.keys()) == keys_before


# ─── convenience helpers ──────────────────────────────────────────────────────

def test_is_distribution_validated_true():
    assert is_distribution_validated({"distribution_validated": True}) is True


def test_is_distribution_validated_false_for_none():
    assert is_distribution_validated({}) is False


def test_distribution_ease_label_unscored():
    assert distribution_ease_label(None) == "unscored"


def test_distribution_ease_label_clear():
    assert "clear" in distribution_ease_label(9.5)
```

**Step 2: Run to verify failure**

```
uv run pytest tests/test_distribution_intelligence.py -v
```
Expected: FAIL — `ImportError: cannot import name 'execute_distribution_research'`

**Step 3: Add `execute_distribution_research()` to `distribution_intelligence.py`**

Insert the following function BEFORE the `_load_api_key()` function (before line 519):

```python
def execute_distribution_research(opp: dict, client=None) -> dict:
    """
    Execute real distribution research via Anthropic API with web search.

    Calls Claude to validate distribution channels for this opportunity.
    Returns dict with distribution fields populated, or {} on any failure (never raises).

    Args:
        opp: opportunity dict (not mutated)
        client: optional pre-built anthropic.Anthropic client (for testing)

    Returns populated fields:
        - distribution_validated: bool
        - top_distribution_channels: list[str]
        - estimated_cac_logic: str
        - first_10_customer_path: str
        - trust_mechanism_latam: str
        - distribution_researched_at: str (ISO date)
    """
    from datetime import date as _date

    # Skip guard: do not re-research within 7 days
    last_researched = opp.get("distribution_researched_at")
    if last_researched:
        try:
            days_ago = (_date.today() - _date.fromisoformat(str(last_researched)[:10])).days
            if days_ago < 7:
                return {}
        except (ValueError, TypeError):
            pass

    # Resolve client
    if client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_api_key()
        if not api_key:
            return {}
        try:
            import anthropic as _anthropic
            client = _anthropic.Anthropic(api_key=api_key)
        except Exception:
            return {}

    template = run_distribution_intelligence(opp)
    queries = template.get("_distribution_queries") or []
    geo = opp.get("geography", "latam")
    geo_label = "Venezuela" if geo == "venezuela" else geo.upper()
    channels = template.get("_recommended_channels", [])
    channel_str = ", ".join(channels[:3]) if channels else "WhatsApp, direct sales"
    query_list = "\n".join(f"- {q}" for q in queries[:3])

    prompt = f"""Research distribution channels for this business opportunity in {geo_label}.

Name: {opp.get("name", "")}
Vertical: {opp.get("vertical", "")}
Target customer: {opp.get("target_customer", "")}
Recommended channels to validate: {channel_str}

Search for evidence of whether these channels work in {geo_label} for similar products:
{query_list}

Return ONLY this JSON object — no prose, no markdown fences:
{{
  "distribution_validated": <true if research confirms at least 1 viable channel, else false>,
  "top_distribution_channels": [<up to 3 channels confirmed by evidence>],
  "estimated_cac_logic": "<primary channel + realistic CAC estimate, 1 sentence>",
  "first_10_customer_path": "<concrete step-by-step path to first 10 customers in {geo_label}, 2-3 sentences>",
  "trust_mechanism_latam": "<primary trust signal needed to convert first buyer in {geo_label}>"
}}"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "Distribution research API call failed for '%s': %s", opp.get("name"), e
        )
        return {}

    raw = ""
    for block in (response.content or []):
        if hasattr(block, "type") and block.type == "text":
            raw = block.text.strip()
            break

    if not raw:
        return {}

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    try:
        data = json.loads(match.group())
    except (json.JSONDecodeError, ValueError):
        return {}

    from datetime import date as _date2
    result: dict = {"distribution_researched_at": _date2.today().isoformat()}

    validated_val = data.get("distribution_validated")
    if validated_val is not None:
        result["distribution_validated"] = bool(validated_val)

    for str_field in ("estimated_cac_logic", "first_10_customer_path", "trust_mechanism_latam"):
        val = data.get(str_field)
        if val is not None:
            result[str_field] = str(val)[:400]

    channels_out = data.get("top_distribution_channels")
    if isinstance(channels_out, list):
        result["top_distribution_channels"] = [str(x)[:100] for x in channels_out[:3] if x]

    return result
```

**Step 4: Run tests**

```
uv run pytest tests/test_distribution_intelligence.py -v
```
Expected: All tests PASS.

**Step 5: Commit**

```bash
git add src/opportunity_os/distribution_intelligence.py tests/test_distribution_intelligence.py
git commit -m "feat(distribution-os): add execute_distribution_research() with Anthropic web search + tests"
```

---

### Task 4: Wire distribution executor into `daily_run.py` step 11

**Files:**
- Modify: `src/opportunity_os/pipelines/daily_run.py` (~line 462-475 in `_step_enrich_and_rank`)

**Step 1: Locate the Step 11 block**

Find the "Step 11: Distribution OS" block (around line 462):

```python
    # Step 11: Distribution OS
    logger.info("Step 11: Running Distribution OS on top 20 opportunities...")
    try:
        from opportunity_os.distribution_intelligence import run_distribution_intelligence
        for i, opp in enumerate(top_20):
            dist_result = run_distribution_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in dist_result.items() if not k.startswith("_")}}
            channels = dist_result.get("_recommended_channels", [])
            logger.info("  Distribution mapped for: %s -> top channel: %s",
                        opp.get("name", "unknown"), channels[0] if channels else "unknown")
    except ImportError as e:
        logger.warning("Distribution intelligence module not available: %s", e)
    except Exception as e:
        log_failure("distribution_os", e)
```

**Step 2: Replace with version that calls the executor on top 5**

Replace with:

```python
    # Step 11: Distribution OS
    logger.info("Step 11: Running Distribution OS on top 20 opportunities...")
    try:
        from opportunity_os.distribution_intelligence import (
            run_distribution_intelligence,
            execute_distribution_research,
        )
        for i, opp in enumerate(top_20):
            dist_result = run_distribution_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in dist_result.items() if not k.startswith("_")}}
        logger.info("  Distribution templates built for %d opportunities", len(top_20))

        # Execute real research on top 5 only (API cost ~$0.15/opp)
        if not dry_run:
            researched_count = 0
            for i, opp in enumerate(top_20[:5]):
                research_result = execute_distribution_research(opp)
                if research_result:
                    top_20[i] = {**top_20[i], **research_result}
                    researched_count += 1
                    logger.info("  Distribution researched: %s (validated: %s)",
                                opp.get("name", "unknown")[:40],
                                research_result.get("distribution_validated"))
            logger.info("  Distribution research executed for %d/5 opportunities", researched_count)
    except ImportError as e:
        logger.warning("Distribution intelligence module not available: %s", e)
    except Exception as e:
        log_failure("distribution_os", e)
```

**Step 3: Run full test suite**

```
uv run pytest tests/ -v
```
Expected: All tests PASS.

**Step 4: Commit**

```bash
git add src/opportunity_os/pipelines/daily_run.py
git commit -m "feat(distribution-os): wire execute_distribution_research into daily_run step 11 (top 5, dry-run safe)"
```

---

## Phase 2 — Wire into Scoring

---

### Task 5: Add `pain_validation_score` as scoring dimension

**Context:** `score_layer()` in `scoring_engine.py` uses a weighted average of non-None fields. Adding a new field with weight 0.08 is fully backward-compatible: when `pain_validation_score` is `None`, it is skipped; when present, it influences the attractiveness_score. No existing test will break.

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py`
- Modify: `config/scoring_weights.yaml`
- Modify: `tests/test_scoring_engine.py` (append new tests at the end)

**Step 1: Write failing tests**

Append to `tests/test_scoring_engine.py`:

```python
# ─── pain_validation_score dimension ─────────────────────────────────────────

def test_pain_validation_score_absent_does_not_change_result(base_opp):
    """opp without pain_validation_score must score identically to current behavior."""
    result_without = score_opportunity(base_opp)
    opp_with_none = {**base_opp, "pain_validation_score": None}
    result_with_none = score_opportunity(opp_with_none)
    assert result_without["final_score"] == result_with_none["final_score"]


def test_high_pain_score_raises_attractiveness(base_opp):
    """pain_validation_score=9 must raise attractiveness_score vs no pain score."""
    result_no_pain = score_opportunity(base_opp)
    result_high_pain = score_opportunity({**base_opp, "pain_validation_score": 9.0})
    assert result_high_pain["attractiveness_score"] >= result_no_pain["attractiveness_score"]


def test_high_pain_raises_final_score(base_opp):
    """pain_validation_score=9 must raise final_score vs pain_validation_score=2."""
    result_low = score_opportunity({**base_opp, "pain_validation_score": 2.0})
    result_high = score_opportunity({**base_opp, "pain_validation_score": 9.0})
    assert result_high["final_score"] > result_low["final_score"]


# ─── distribution_quality dimension ──────────────────────────────────────────

def test_distribution_validated_true_raises_executability(base_opp):
    """distribution_validated=True must raise executability_score vs False."""
    result_false = score_opportunity({**base_opp, "distribution_validated": False})
    result_true = score_opportunity({**base_opp, "distribution_validated": True})
    assert result_true["executability_score"] >= result_false["executability_score"]


def test_distribution_validated_none_backward_compatible(base_opp):
    """opp without distribution_validated must score identically to current behavior."""
    result_without = score_opportunity(base_opp)
    result_with_none = score_opportunity({**base_opp, "distribution_validated": None})
    assert result_without["final_score"] == result_with_none["final_score"]
```

**Step 2: Run to verify failure**

```
uv run pytest tests/test_scoring_engine.py -v -k "pain_validation or distribution_validated"
```
Expected: FAIL — tests pass vacuously (no assertion failures because fields are ignored) OR fail because new tests not yet added. Actually they will PASS vacuously since the score doesn't change. These tests will fail once we add the dimension and the assertions become meaningful. Let's add the dimension first and then validate.

**Step 3: Add `pain_validation_score` to `ATTRACTIVENESS_FIELDS` and `DEFAULT_WEIGHTS`**

In `scoring_engine.py`:

1. Add `"pain_validation_score"` to `ATTRACTIVENESS_FIELDS` list:
```python
ATTRACTIVENESS_FIELDS = [
    "market_size",
    "timing_tailwind",
    "pain_severity",
    "willingness_to_pay",
    "monetization_clarity",
    "pain_validation_score",   # add this line
]
```

2. Add `"pain_validation_score": 0.08` to `DEFAULT_WEIGHTS["weights"]`:
```python
DEFAULT_WEIGHTS = {
    "weights": {
        "market_size": 0.10,
        "timing_tailwind": 0.08,
        "pain_severity": 0.10,
        "willingness_to_pay": 0.08,
        "monetization_clarity": 0.08,
        "pain_validation_score": 0.08,    # add this line
        ...
    },
```

**Step 4: Add `distribution_quality` derived from `distribution_validated`**

Add a preprocessing helper function in `scoring_engine.py` BEFORE `score_opportunity()`:

```python
def _derive_distribution_quality(opp: dict) -> dict:
    """Derive numeric distribution_quality from distribution_validated bool.

    True  -> 8.0  (validated channel found)
    False -> 3.0  (research found no viable channel)
    None  -> skip (absent = no change to executability)

    Returns new dict with distribution_quality added (does not mutate input).
    """
    validated = opp.get("distribution_validated")
    if validated is None:
        return opp
    quality = 8.0 if bool(validated) else 3.0
    return {**opp, "distribution_quality": quality}
```

Then add `"distribution_quality"` to `EXECUTABILITY_FIELDS`:
```python
EXECUTABILITY_FIELDS = [
    "speed_to_mvp",
    "capital_efficiency",
    "distribution_accessibility",
    "distribution_quality",     # add this line
]
```

Add weight to `DEFAULT_WEIGHTS`:
```python
"distribution_quality": 0.07,    # add this line
```

Finally, call `_derive_distribution_quality` at the start of `score_opportunity()`, right after the shallow copy:
```python
def score_opportunity(opp_dict: dict) -> dict:
    opp = dict(opp_dict)  # shallow copy
    opp = _derive_distribution_quality(opp)   # add this line
    ...
```

**Step 5: Update `config/scoring_weights.yaml`**

Add the two new fields to the weights section:
```yaml
  pain_validation_score: 0.08   # populated by execute_pain_research(); None = skipped
  distribution_quality: 0.07    # derived from distribution_validated bool; None = skipped
```

**Step 6: Run tests**

```
uv run pytest tests/test_scoring_engine.py -v
```
Expected: All tests PASS including the new ones.

**Step 7: Run full suite**

```
uv run pytest tests/ -v
```
Expected: All tests PASS.

**Step 8: Commit**

```bash
git add src/opportunity_os/engines/scoring_engine.py config/scoring_weights.yaml tests/test_scoring_engine.py
git commit -m "feat(scoring): add pain_validation_score + distribution_quality as scoring dimensions (backward-compatible)"
```

---

## Phase 3 — Visibility + Safety Net

---

### Task 6: Add GitHub Actions CI

**Files:**
- Create: `.github/workflows/tests.yml`

**Step 1: Create the workflow file**

Create `.github/workflows/tests.yml`:

```yaml
name: tests

on:
  push:
    branches:
      - "feat/**"
      - "main"
  pull_request:
    branches:
      - "feat/**"
      - "main"

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest tests/ -v --tb=short
```

**Step 2: Verify the file is syntactically correct**

```
uv run pytest tests/ -v --tb=short
```
Expected: All tests PASS (confirms the command in CI is correct).

**Step 3: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: add GitHub Actions test workflow on push to feat/** and main"
```

---

### Task 7: Split `daily_run.py` below 800 lines

**Context:** `daily_run.py` is 824 lines. The `_step_enrich_and_rank()` function (line ~426) contains all of steps 9.7–11.8 (~250 lines). Extract it into `src/opportunity_os/pipelines/enrichment.py`.

**Files:**
- Create: `src/opportunity_os/pipelines/enrichment.py`
- Modify: `src/opportunity_os/pipelines/daily_run.py`

**Step 1: Verify the current line count**

```
uv run python -c "print(sum(1 for _ in open('src/opportunity_os/pipelines/daily_run.py')))"
```
Expected: 824

**Step 2: Create `enrichment.py` with extracted function**

Create `src/opportunity_os/pipelines/enrichment.py`. Copy the entire `_step_enrich_and_rank()` function from `daily_run.py` into this new file:

```python
"""
Enrichment step for the daily run pipeline.

Extracted from daily_run.py to keep that file under the 800-line hard limit.
Contains: step 9.7 (benchmark mapping), step 10 (pain OS), step 11 (distribution OS),
step 11.5 (research executor), step 11.6 (free research), step 11.8 (pain library).
"""

import logging
import os
from opportunity_os.pipeline_monitor import log_failure

logger = logging.getLogger(__name__)


def run_enrichment_steps(all_opps_sorted: list, dry_run: bool) -> tuple:
    """Steps 9.7–11.8: benchmark mapping, pain/distribution OS, research, pain library.

    Renamed from _step_enrich_and_rank in daily_run.py.
    Returns (all_opps_sorted, top_20) — both may be enriched in place.
    """
    # [PASTE THE FULL BODY OF _step_enrich_and_rank HERE]
```

Note: Copy the complete function body from `daily_run.py` lines ~426-~600 verbatim. The only change is:
- Function renamed from `_step_enrich_and_rank` to `run_enrichment_steps`
- Module-level imports at top of new file

**Step 3: Update `daily_run.py` to import and call from enrichment.py**

In `daily_run.py`:
1. Delete the entire `_step_enrich_and_rank()` function body
2. Add the import at the top of the function or module:
```python
from opportunity_os.pipelines.enrichment import run_enrichment_steps
```
3. Replace the call site in the pipeline (where `_step_enrich_and_rank` was called):
```python
# was: all_opps_sorted, top_20 = _step_enrich_and_rank(all_opps_sorted, dry_run)
all_opps_sorted, top_20 = run_enrichment_steps(all_opps_sorted, dry_run)
```

**Step 4: Verify line count**

```
uv run python -c "print(sum(1 for _ in open('src/opportunity_os/pipelines/daily_run.py')))"
```
Expected: < 800

**Step 5: Run full test suite**

```
uv run pytest tests/ -v
```
Expected: All tests PASS.

**Step 6: Commit**

```bash
git add src/opportunity_os/pipelines/enrichment.py src/opportunity_os/pipelines/daily_run.py
git commit -m "refactor(daily-run): extract enrichment steps into pipelines/enrichment.py (daily_run.py < 800 lines)"
```

---

## Verification Checklist

After all tasks complete:

```bash
# 1. All tests pass
uv run pytest tests/ -v

# 2. daily_run.py under 800 lines
python -c "c=sum(1 for _ in open('src/opportunity_os/pipelines/daily_run.py')); print(c, 'lines —', 'OK' if c < 800 else 'OVER LIMIT')"

# 3. New test files exist
ls tests/test_pain_intelligence.py tests/test_distribution_intelligence.py

# 4. Pain executor is importable and correct
python -c "from opportunity_os.pain_intelligence import execute_pain_research; print('OK')"

# 5. Distribution executor is importable
python -c "from opportunity_os.distribution_intelligence import execute_distribution_research; print('OK')"

# 6. Scoring dimensions registered
python -c "from opportunity_os.engines.scoring_engine import ATTRACTIVENESS_FIELDS, EXECUTABILITY_FIELDS; assert 'pain_validation_score' in ATTRACTIVENESS_FIELDS; assert 'distribution_quality' in EXECUTABILITY_FIELDS; print('OK')"
```

All 6 must print `OK` before this plan is considered complete.
