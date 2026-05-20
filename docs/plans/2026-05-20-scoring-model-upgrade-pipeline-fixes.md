# Scoring Model Upgrade + Pipeline Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 3 P0 bugs and 3 P1 improvements that leave the scoring model silently broken — a YAML modifier that's never read, scores that go stale after free research, and noise signals that slip through the kill gate.

**Architecture:** All changes are additive and None-safe. New scoring fields follow the existing `score_layer()` skip-if-None pattern. The noise gate is a pure predicate function. Re-scoring after free research is a 3-line addition in the enrichment loop. No schema migrations needed.

**Tech Stack:** Python 3.11, pytest, PyYAML, `{**opp, ...}` immutable dict pattern throughout.

---

## Priority Reference

| ID | File | Change | Risk |
|----|------|--------|------|
| P0-1 | `scoring_engine.py` | Apply `non_obviousness_high` modifier (dead config) | Low |
| P0-2 | `enrichment.py` | Re-score after free research updates `pain_signal_count` | Low |
| P0-3 | `signal_harvester.py` | `_is_noise_signal()` gate blocks raw social posts | Low |
| P1-1 | `scoring_engine.py` + `scoring_weights.yaml` | 3 VC fields: `gross_margin_potential`, `network_effect_strength`, `switching_cost_score` | Low |
| P1-2 | `scoring_engine.py` | `pain_signal_count` → `pain_validation_score` fallback | Low |
| P1-3 | `opportunities.jsonl` | Clear `free_research_at` on reframed opp `opp_20260520_ven_1d8d479c` | None |

---

### Task 1: P0-1 — Apply non_obviousness_high modifier

**Problem:** `config/scoring_weights.yaml` defines `non_obviousness_high: +0.5` under `modifiers`. The `apply_modifiers()` function in `scoring_engine.py` never reads it. Opps with `non_obviousness_score >= 6` receive no bonus.

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py` — `apply_modifiers()` function (~line 192)
- Test: `tests/test_scoring_engine.py`

**Step 1: Write the failing tests**

Add to `tests/test_scoring_engine.py`:

```python
# ─── non_obviousness_high modifier ───────────────────────────────────────────

def test_non_obviousness_high_applies_bonus(base_opp):
    """non_obviousness_score >= 6 must add +0.5 to final_score."""
    below = score_opportunity({**base_opp, "non_obviousness_score": 5.0})
    above = score_opportunity({**base_opp, "non_obviousness_score": 7.0})
    assert above["final_score"] > below["final_score"]


def test_non_obviousness_below_threshold_no_bonus(base_opp):
    """non_obviousness_score < 6 must not change the score vs. field absent."""
    without_field = score_opportunity(base_opp)
    with_low = score_opportunity({**base_opp, "non_obviousness_score": 4.9})
    assert with_low["final_score"] == pytest.approx(without_field["final_score"])


def test_non_obviousness_absent_no_bonus(base_opp):
    """No non_obviousness_score field must not crash or add bonus."""
    result = score_opportunity(base_opp)
    assert "final_score" in result
    assert result["final_score"] <= 10.0
```

**Step 2: Run to verify they fail**

```
uv run pytest tests/test_scoring_engine.py -k "non_obviousness" -v
```
Expected: FAIL — `above["final_score"] > below["final_score"]` will be False (no bonus applied).

**Step 3: Implement — add 4 lines to `apply_modifiers()`**

In `src/opportunity_os/engines/scoring_engine.py`, locate `apply_modifiers()`. After the `daniels_wedge_low` block, add:

```python
    # Non-obviousness bonus
    non_obviousness = opp.get("non_obviousness_score")
    if non_obviousness is not None and float(non_obviousness) >= 6.0:
        adjusted += float(mods.get("non_obviousness_high", 0.5))
```

**Step 4: Run to verify they pass**

```
uv run pytest tests/test_scoring_engine.py -k "non_obviousness" -v
```
Expected: 3 PASS

**Step 5: Run full test suite to confirm no regressions**

```
uv run pytest tests/test_scoring_engine.py -v
```
Expected: all existing tests still pass.

**Step 6: Commit**

```bash
git add src/opportunity_os/engines/scoring_engine.py tests/test_scoring_engine.py
git commit -m "fix(scoring): apply non_obviousness_high modifier that was dead config"
```

---

### Task 2: P1-2 — pain_signal_count → pain_validation_score fallback

Do this before Task P1-1 (adding VC fields) because it affects the attractiveness layer, and we want tests to validate it in isolation first.

**Problem:** `free_research.py` populates `pain_signal_count` for all live opps (10–20+ signals found). But `pain_validation_score` stays None for opps that haven't had paid research. The attractiveness layer therefore misses a cheap signal that's already in the record.

**Formula:** `if pain_validation_score is None and pain_signal_count >= 3: pain_validation_score = min(6.0, 4.0 + pain_signal_count * 0.3)`

This caps at 6.0 (lower than the paid research range of 7–9) to ensure paid research still wins when it runs.

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py` — add `_apply_pain_signal_fallback()` and call from `score_opportunity()`
- Test: `tests/test_scoring_engine.py`

**Step 1: Write the failing tests**

Add to `tests/test_scoring_engine.py`:

```python
# ─── pain_signal_count fallback ───────────────────────────────────────────────

def test_pain_signal_count_fallback_raises_score(base_opp):
    """pain_signal_count >= 3 with no paid research must raise score vs. no count."""
    no_signals = score_opportunity({**base_opp, "pain_validation_score": None, "pain_signal_count": 0})
    with_signals = score_opportunity({**base_opp, "pain_validation_score": None, "pain_signal_count": 5})
    assert with_signals["final_score"] > no_signals["final_score"]


def test_pain_signal_count_below_threshold_no_effect(base_opp):
    """pain_signal_count < 3 must not set pain_validation_score fallback."""
    no_signals = score_opportunity({**base_opp, "pain_validation_score": None, "pain_signal_count": 0})
    two_signals = score_opportunity({**base_opp, "pain_validation_score": None, "pain_signal_count": 2})
    assert two_signals["final_score"] == pytest.approx(no_signals["final_score"])


def test_pain_signal_count_fallback_capped_at_6(base_opp):
    """Fallback score must be capped at 6.0 — paid research (7-9) must always win."""
    # 100 signals → 4.0 + 100*0.3 = 34.0 → capped at 6.0
    many_signals = score_opportunity({**base_opp, "pain_validation_score": None, "pain_signal_count": 100})
    paid_research = score_opportunity({**base_opp, "pain_validation_score": 7.0})
    assert paid_research["final_score"] > many_signals["final_score"]


def test_pain_signal_count_fallback_does_not_override_existing(base_opp):
    """Existing pain_validation_score must not be touched by the fallback."""
    with_existing = score_opportunity({**base_opp, "pain_validation_score": 9.0, "pain_signal_count": 5})
    without_count = score_opportunity({**base_opp, "pain_validation_score": 9.0})
    assert with_existing["final_score"] == pytest.approx(without_count["final_score"])
```

**Step 2: Run to verify they fail**

```
uv run pytest tests/test_scoring_engine.py -k "pain_signal_count" -v
```
Expected: FAIL — fallback not implemented yet, `with_signals` will equal `no_signals`.

**Step 3: Implement `_apply_pain_signal_fallback()`**

Add this function to `scoring_engine.py` before `score_opportunity()`:

```python
def _apply_pain_signal_fallback(opp: dict) -> dict:
    """Derive a pain_validation_score proxy from pain_signal_count when paid research is absent.

    Formula: min(6.0, 4.0 + pain_signal_count * 0.3)
    Capped at 6.0 so paid research results (typically 7-9) always dominate.
    Only fires when pain_validation_score is None and pain_signal_count >= 3.
    """
    if opp.get("pain_validation_score") is not None:
        return opp
    count = opp.get("pain_signal_count")
    if count is None or int(count) < 3:
        return opp
    fallback = min(6.0, 4.0 + int(count) * 0.3)
    return {**opp, "pain_validation_score": round(fallback, 2)}
```

Then in `score_opportunity()`, call it as the first step after the shallow copy:

```python
def score_opportunity(opp_dict: dict) -> dict:
    opp = dict(opp_dict)  # shallow copy
    opp = _derive_distribution_quality(opp)
    opp = _apply_pain_signal_fallback(opp)   # ← add this line
    ...
```

**Step 4: Run tests**

```
uv run pytest tests/test_scoring_engine.py -k "pain_signal_count" -v
```
Expected: 4 PASS

**Step 5: Full suite**

```
uv run pytest tests/test_scoring_engine.py -v
```
Expected: all pass.

**Step 6: Commit**

```bash
git add src/opportunity_os/engines/scoring_engine.py tests/test_scoring_engine.py
git commit -m "feat(scoring): add pain_signal_count fallback for pain_validation_score"
```

---

### Task 3: P1-1 — Add 3 VC scoring fields

**Problem:** The strategic value layer lacks moat-quality signals that every VC uses internally. `gross_margin_potential`, `network_effect_strength`, and `switching_cost_score` are universally used at YC, First Round, and Sequoia to evaluate business model durability. All three are currently absent.

**Files:**
- Modify: `src/opportunity_os/engines/scoring_engine.py` — `STRATEGIC_VALUE_FIELDS`, `DEFAULT_WEIGHTS`
- Modify: `config/scoring_weights.yaml` — `weights` section
- Test: `tests/test_scoring_engine.py`

**Step 1: Write the failing tests**

Add to `tests/test_scoring_engine.py`:

```python
# ─── VC moat fields ───────────────────────────────────────────────────────────

def test_gross_margin_potential_raises_score(base_opp):
    low = score_opportunity({**base_opp, "gross_margin_potential": 2.0})
    high = score_opportunity({**base_opp, "gross_margin_potential": 9.0})
    assert high["final_score"] > low["final_score"]


def test_network_effect_strength_raises_score(base_opp):
    low = score_opportunity({**base_opp, "network_effect_strength": 2.0})
    high = score_opportunity({**base_opp, "network_effect_strength": 9.0})
    assert high["final_score"] > low["final_score"]


def test_switching_cost_score_raises_score(base_opp):
    low = score_opportunity({**base_opp, "switching_cost_score": 2.0})
    high = score_opportunity({**base_opp, "switching_cost_score": 9.0})
    assert high["final_score"] > low["final_score"]


def test_vc_fields_absent_no_penalty(base_opp):
    """New VC fields absent must not change score vs. baseline — None-safe."""
    baseline = score_opportunity(base_opp)
    with_none = score_opportunity({
        **base_opp,
        "gross_margin_potential": None,
        "network_effect_strength": None,
        "switching_cost_score": None,
    })
    assert baseline["final_score"] == pytest.approx(with_none["final_score"])
```

**Step 2: Run to verify they fail**

```
uv run pytest tests/test_scoring_engine.py -k "gross_margin or network_effect or switching_cost or vc_fields" -v
```
Expected: FAIL — fields not in `STRATEGIC_VALUE_FIELDS`, weight is 0, so high=low always.

**Step 3: Add fields to `STRATEGIC_VALUE_FIELDS` and `DEFAULT_WEIGHTS`**

In `scoring_engine.py`:

```python
STRATEGIC_VALUE_FIELDS = [
    "competition_intensity",   # inverted
    "defensibility",
    "regional_fit",
    "founder_fit",
    "ai_leverage",
    "operational_simplicity",
    "regulatory_simplicity",
    "revenue_speed_score",
    "gross_margin_potential",   # new: SaaS=9, services=3, hardware=4
    "network_effect_strength",  # new: marketplace/social=9, single-player=2
    "switching_cost_score",     # new: data lock-in=9, commodity=2
]
```

In `DEFAULT_WEIGHTS` dict, add:

```python
"gross_margin_potential": 0.06,
"network_effect_strength": 0.05,
"switching_cost_score": 0.05,
```

**Step 4: Update `config/scoring_weights.yaml`**

Add under `weights:`:

```yaml
  gross_margin_potential: 0.06   # SaaS/software=9, services=4, hardware=3
  network_effect_strength: 0.05  # marketplace=9, single-player=2; strong moat signal
  switching_cost_score: 0.05     # data lock-in=9, commodity tools=2; retention predictor
```

**Step 5: Run tests**

```
uv run pytest tests/test_scoring_engine.py -k "gross_margin or network_effect or switching_cost or vc_fields" -v
```
Expected: 4 PASS

**Step 6: Full suite**

```
uv run pytest tests/test_scoring_engine.py -v
```
Expected: all pass.

**Step 7: Commit**

```bash
git add src/opportunity_os/engines/scoring_engine.py config/scoring_weights.yaml tests/test_scoring_engine.py
git commit -m "feat(scoring): add gross_margin_potential, network_effect_strength, switching_cost_score (VC moat fields)"
```

---

### Task 4: P0-3 — Noise quality gate in signal harvester

**Problem:** Raw Reddit posts and HN questions enter the pipeline and pass the kill gate because the AI scorer generates plausible financial fields for any text (e.g., "anyone knows a good barber in Caracas?" → `pain_validation_score: 8.5`). The harvester has a length check (`len(name) < 15`) but no semantic noise filter.

**Files:**
- Modify: `src/opportunity_os/pipelines/signal_harvester.py` — add `_is_noise_signal()` and call from `harvest_signals()`
- Test: `tests/test_signal_harvester.py` (create new file)

**Step 1: Write the failing tests**

Create `tests/test_signal_harvester.py`:

```python
"""Tests for signal_harvester.py noise gate."""
import pytest
from opportunity_os.pipelines.signal_harvester import _is_noise_signal


def _make_signal(name: str, description: str = "some description about a market") -> dict:
    return {
        "name": name,
        "description": description,
        "geography": "venezuela",
        "vertical": "fintech",
        "source_url": "https://reddit.com/r/vzla/abc",
        "raw_notes": "Reddit r/vzla.",
        "harvested_at": "2026-05-20",
    }


def test_noise_gate_blocks_first_person_post():
    assert _is_noise_signal(_make_signal("I need help finding a bank that works in Venezuela")) is True


def test_noise_gate_blocks_question_post():
    assert _is_noise_signal(_make_signal("Does anyone know how to transfer money in Venezuela")) is True


def test_noise_gate_blocks_short_name():
    assert _is_noise_signal(_make_signal("help with money")) is True  # 3 words


def test_noise_gate_allows_valid_opportunity():
    signal = _make_signal(
        "Venezuelan fintech startup raises seed round for remittance corridor",
        "A Caracas-based startup has raised $1.2M to build remittance infrastructure.",
    )
    assert _is_noise_signal(signal) is False


def test_noise_gate_allows_market_signal():
    signal = _make_signal(
        "LATAM payment infrastructure gap leaves SMBs without banking access",
        "Small businesses across Latin America cannot access credit or payment rails.",
    )
    assert _is_noise_signal(signal) is False


def test_noise_gate_case_insensitive():
    assert _is_noise_signal(_make_signal("MY PROBLEM with banking in Venezuela")) is True
```

**Step 2: Run to verify they fail**

```
uv run pytest tests/test_signal_harvester.py -v
```
Expected: ImportError or AttributeError — `_is_noise_signal` does not exist yet.

**Step 3: Implement `_is_noise_signal()`**

In `signal_harvester.py`, add after the `QUALITY_KEYWORDS` constant block:

```python
# Prefixes that indicate a personal social post, not a market opportunity
NOISE_PREFIXES = (
    "i ", "i'", "my ", "me ", "we ", "our ",
    "how do i", "how can i", "how to ",
    "does anyone", "anyone know", "anyone here",
    "is there a", "is there any",
    "what is ", "what are ", "what's ",
    "where can", "where do",
    "help with", "need help",
    "can anyone", "can someone",
    "looking for ", "trying to ",
)

MIN_OPPORTUNITY_WORDS = 5
```

Then add the function after `quality_score()`:

```python
def _is_noise_signal(signal: dict) -> bool:
    """Return True if this signal looks like a raw social post, not a real opportunity.

    Blocks: first-person questions, personal help requests, names under 5 words.
    Allowed: market observations, startup news, funding signals, problem statements.
    """
    name = (signal.get("name") or "").strip().lower()
    if len(name.split()) < MIN_OPPORTUNITY_WORDS:
        return True
    if any(name.startswith(prefix) for prefix in NOISE_PREFIXES):
        return True
    return False
```

Then in `harvest_signals()`, add the gate in the acceptance loop, after the `len(name) < 15` check:

```python
        if len(name) < 15:
            continue
        if _is_noise_signal(signal):   # ← add this
            continue
        if _is_duplicate(name, seen_names):
            continue
```

**Step 4: Run tests**

```
uv run pytest tests/test_signal_harvester.py -v
```
Expected: 6 PASS

**Step 5: Commit**

```bash
git add src/opportunity_os/pipelines/signal_harvester.py tests/test_signal_harvester.py
git commit -m "fix(harvester): add noise_quality_gate to block raw social posts before kill gate"
```

---

### Task 5: P0-2 — Re-score after free research

**Problem:** Step 11.6 in `enrichment.py` runs free research and updates `pain_signal_count` in the sorted opp list. But `score_opportunity()` is never called after the update. The enriched data is stored but never flows into the score. The opp's `final_score` is stale from before enrichment ran.

**Files:**
- Modify: `src/opportunity_os/pipelines/enrichment.py` — Step 11.6 loop, lines ~113-121

**Note:** No unit test is added here — `enrichment.py` imports are complex and the behavior is covered end-to-end by `rescore_all.py --dry-run`. Manual verification is the appropriate gate.

**Step 1: Make the change — add 3 lines after the update**

In `enrichment.py`, Step 11.6, after the `all_opps_sorted[i] = {**opp, **updates}` line:

Before:
```python
        for i, opp in enumerate(all_opps_sorted[:20]):
            if not opp.get("free_research_at"):
                updates = research_opportunity_free(opp)
                if updates:
                    all_opps_sorted[i] = {**opp, **updates}
                    free_researched += 1
                time.sleep(0.5)
```

After:
```python
        for i, opp in enumerate(all_opps_sorted[:20]):
            if not opp.get("free_research_at"):
                updates = research_opportunity_free(opp)
                if updates:
                    enriched = {**opp, **updates}
                    if not enriched.get("kill_decision"):
                        enriched = score_opportunity(enriched)
                        enriched = apply_geo_adjustments(enriched)
                    all_opps_sorted[i] = enriched
                    free_researched += 1
                time.sleep(0.5)
```

Also add the missing imports at the top of the enrichment step (inside the try block or as module-level imports):

The imports for `score_opportunity` and `apply_geo_adjustments` need to be added. Since this is inside a `try` block, add them at the top of the Step 11.6 block:

```python
    try:
        from opportunity_os.free_research import research_opportunity_free
        from opportunity_os.engines.scoring_engine import score_opportunity
        from opportunity_os.geo_lens import apply_geo_adjustments
        ...
```

**Step 2: Verify manually**

```
uv run python scripts/rescore_all.py --dry-run
```
Expected: runs without error, score summary shows correct values.

**Step 3: Commit**

```bash
git add src/opportunity_os/pipelines/enrichment.py
git commit -m "fix(enrichment): re-score opp after free research updates pain_signal_count"
```

---

### Task 6: P1-3 — Clear free_research_at on reframed opp

**Problem:** Opp `opp_20260520_ven_1d8d479c` was reframed from a generic Venezuela signal to "Investment Account Access Platform for Venezuelan Retail Investors". The `free_research_at` field is stamped from the old content. Clearing it causes the backfill script to re-run free research with the new framing on the next run.

**Files:**
- Modify: `data/opportunities/opportunities.jsonl` — update one record in place

**Step 1: Apply the patch**

Run from the project root:

```bash
uv run python - <<'EOF'
import json, os
from pathlib import Path

TARGET_ID = "opp_20260520_ven_1d8d479c"
path = Path("data/opportunities/opportunities.jsonl")
records = []
found = False

with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("id") == TARGET_ID:
            rec = {**rec, "free_research_at": None}
            found = True
        records.append(rec)

if not found:
    print(f"ERROR: {TARGET_ID} not found")
else:
    tmp = path.with_suffix(".p13.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")
    os.replace(str(tmp), str(path))
    print(f"Cleared free_research_at on {TARGET_ID}")
EOF
```

**Step 2: Verify**

```bash
uv run python -c "
import json
from pathlib import Path
path = Path('data/opportunities/opportunities.jsonl')
for line in path.read_text().splitlines():
    r = json.loads(line)
    if r.get('id') == 'opp_20260520_ven_1d8d479c':
        print('free_research_at:', r.get('free_research_at'))
        break
"
```
Expected: `free_research_at: None`

**Step 3: Commit**

```bash
git add data/opportunities/opportunities.jsonl
git commit -m "data: clear free_research_at on reframed Venezuela investment opp for re-research"
```

---

### Task 7: Post-execution — rescore_all dry run + backfill

Run these after all 6 tasks complete to validate the full pipeline.

**Step 1: Dry-run rescore to verify no regressions**

```
uv run python scripts/rescore_all.py --dry-run
```

Expected output includes:
- Records: 78+ live opps
- Score distribution shows some 8+ entries (VC fields + non_obviousness bonus now active)
- No "Newly SURVIVED" — manual_kill records still protected
- No Python errors

**Step 2: Run actual rescore**

```
uv run python scripts/rescore_all.py
```

**Step 3: Trigger free research backfill for reframed opp**

```
uv run python scripts/run_free_research_backfill.py --dry-run
```

Verify it picks up `opp_20260520_ven_1d8d479c` in the "Missing free_research_at" count.

If dry-run looks good:

```
uv run python scripts/run_free_research_backfill.py
```

**Step 4: Final commit**

```bash
git add data/opportunities/opportunities.jsonl
git commit -m "data: post-rescore after scoring model upgrade"
```

---

## Execution Order

Run tasks in this order — each is independent except Task 7 (depends on all others):

```
Task 1 (P0-1 non_obviousness) → commit
Task 2 (P1-2 pain_signal_count fallback) → commit
Task 3 (P1-1 VC fields) → commit
Task 4 (P0-3 noise gate) → commit
Task 5 (P0-2 re-score after enrichment) → commit
Task 6 (P1-3 clear free_research_at) → commit
Task 7 (rescore + backfill) → commit
```

Tasks 1-6 can be batched as 2 parallel groups if using subagent-driven execution:
- **Group A** (scoring_engine.py only): Task 1, Task 2, Task 3
- **Group B** (other files): Task 4, Task 5, Task 6
