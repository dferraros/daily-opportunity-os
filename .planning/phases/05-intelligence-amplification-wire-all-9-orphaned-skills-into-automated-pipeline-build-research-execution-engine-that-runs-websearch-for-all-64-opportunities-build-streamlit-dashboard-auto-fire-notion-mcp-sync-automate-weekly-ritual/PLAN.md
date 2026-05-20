# Phase 05: Intelligence Amplification — PLAN

---
phase: 05-intelligence-amplification
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/opportunity_os/research_executor.py
  - scripts/run_research_backfill.py
autonomous: true
requirements: [INTEL-01, INTEL-02]

must_haves:
  truths:
    - "All 64 opportunities have pain_validation_score populated (not None)"
    - "All 64 opportunities have exact_customer_phrases populated (not empty list)"
    - "All 64 opportunities have distribution_validated field populated"
    - "research_executed_at timestamp exists on researched opportunities"
    - "Backfill script skips opps that already have research_executed_at"
    - "Pipeline steps 10-11 call research_executor after pain/distribution templates built"
  artifacts:
    - path: "src/opportunity_os/research_executor.py"
      provides: "Web search execution for pain + distribution research"
      exports: ["run_research_executor"]
    - path: "scripts/run_research_backfill.py"
      provides: "Backfill all 64 existing opportunities with real research"
      exports: []
  key_links:
    - from: "src/opportunity_os/pipelines/daily_run.py"
      to: "src/opportunity_os/research_executor.py"
      via: "import run_research_executor; call after Steps 10+11"
      pattern: "run_research_executor\\(opp\\)"
    - from: "scripts/run_research_backfill.py"
      to: "src/opportunity_os/research_executor.py"
      via: "direct import + loop over all opportunities"
      pattern: "run_research_executor"
---

## Wave 1A — Research Executor (parallel with 1C dashboard)

### Task 1: Create research_executor.py

**File:** `src/opportunity_os/research_executor.py`

**Action:**

Create this module from scratch following the exact pattern in `ai_scorer.py` (same `_load_env_key()` + `_find_project_root()` helpers, same `try/except` graceful fallback). The module uses Anthropic's `web_search_20250305` tool to fire real web searches and populate null pain + distribution fields.

```python
"""
Research Executor — fires real Anthropic web_search_20250305 calls to validate
pain and distribution fields for each opportunity.

Follows ai_scorer.py patterns exactly:
- _load_env_key() and _find_project_root() helpers
- Falls back gracefully (returns opp unchanged) if API unavailable or call fails
- Writes research_executed_at timestamp on success

Input: opp dict already enriched by pain_intelligence + distribution_intelligence
  (must have _pain_queries and _recommended_channels fields from those modules)

Output: opp dict with these fields populated:
  Pain fields:
    - pain_validation_score (float 0-10)
    - exact_customer_phrases (list[str], max 3, in Spanish)
    - pain_evidence_sources (list[str], source descriptions/URLs)
    - workarounds_found (list[str])
  Distribution fields:
    - distribution_validated (bool)
    - top_distribution_channels (list[str], max 3)
    - estimated_cac_logic (str, e.g. "WhatsApp cold ~$12 CAC")
    - first_10_customer_path (str, step-by-step)
    - trust_mechanism_latam (str, primary trust signal)
  Plus:
    - research_executed_at (str, ISO datetime)
"""

import json
import os
import re
import time
from datetime import datetime
from typing import Optional

MODEL = "claude-haiku-4-5-20251001"
MAX_SEARCH_USES = 3


def run_research_executor(opp: dict) -> dict:
    """
    Execute web research for pain + distribution validation on one opportunity.
    Returns opp dict with populated research fields (or unchanged if API unavailable).
    """
    if opp.get("research_executed_at"):
        return opp  # Skip already-researched opps

    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_env_key()
    if not api_key:
        print(f"  [research_executor] No API key — skipping: {opp.get('name', '?')[:50]}")
        return opp

    name = opp.get("name", "unknown")

    try:
        pain_result = _execute_pain_research(opp, api_key)
        opp.update(pain_result)
    except Exception as exc:
        print(f"  [research_executor] Pain research failed ({type(exc).__name__}: {exc}) for: {name[:40]}")

    try:
        dist_result = _execute_distribution_research(opp, api_key)
        opp.update(dist_result)
    except Exception as exc:
        print(f"  [research_executor] Distribution research failed ({type(exc).__name__}: {exc}) for: {name[:40]}")

    opp["research_executed_at"] = datetime.now().isoformat()
    print(f"  [research_executor] Research complete: {name[:50]}")
    return opp


def _execute_pain_research(opp: dict, api_key: str) -> dict:
    """
    Use web_search_20250305 to validate pain signals.
    Queries come from _pain_queries built by pain_intelligence.py.
    Returns dict with pain validation fields.
    """
    import anthropic

    queries = opp.get("_pain_queries") or []
    if not queries:
        from opportunity_os.pain_intelligence import build_pain_queries
        queries = build_pain_queries(opp)

    name = opp.get("name", "")
    problem = opp.get("problem_statement", "") or opp.get("description", "")
    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()

    # Use top 3 queries to stay within MAX_SEARCH_USES
    search_queries = queries[:3]
    query_list = "\n".join(f"- {q}" for q in search_queries)

    prompt = f"""Research pain validation for this business opportunity:

Opportunity: {name}
Problem: {problem}
Geography: {geo_label}

Execute web searches using these queries to find real evidence:
{query_list}

After searching, return ONLY this JSON (no prose, no markdown, no code block):
{{
  "pain_validation_score": <float 0-10, where 10=daily urgent pain with failed workarounds>,
  "exact_customer_phrases": [<up to 3 exact Spanish complaint phrases found>, ...],
  "pain_evidence_sources": [<up to 3 source descriptions or URLs>, ...],
  "workarounds_found": [<what people actually do today to solve this>, ...]
}}

Score guide: 9-10=emergency daily pain, 7-8=frequent recurring pain, 5-6=moderate annoyance, 3-4=nice-to-have, 1-2=assumed pain not confirmed.
Return null values if no evidence found for a field."""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCH_USES,
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text blocks from potentially mixed content (text + tool_use + tool_result)
    text_blocks = [b.text for b in response.content if hasattr(b, "text") and b.type == "text"]
    raw = " ".join(text_blocks).strip()

    # Strip markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Find JSON object in response
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    data = json.loads(match.group())
    result = {}

    score = data.get("pain_validation_score")
    if score is not None:
        try:
            result["pain_validation_score"] = max(0.0, min(10.0, float(score)))
        except (ValueError, TypeError):
            pass

    phrases = data.get("exact_customer_phrases")
    if isinstance(phrases, list):
        result["exact_customer_phrases"] = [str(p)[:200] for p in phrases[:3] if p]

    sources = data.get("pain_evidence_sources")
    if isinstance(sources, list):
        result["pain_evidence_sources"] = [str(s)[:300] for s in sources[:3] if s]

    workarounds = data.get("workarounds_found")
    if isinstance(workarounds, list):
        result["workarounds_found"] = [str(w)[:200] for w in workarounds if w]

    return result


def _execute_distribution_research(opp: dict, api_key: str) -> dict:
    """
    Use web_search_20250305 to validate distribution channels and CAC.
    Queries come from _distribution_queries built by distribution_intelligence.py.
    Returns dict with distribution validation fields.
    """
    import anthropic

    from opportunity_os.distribution_intelligence import (
        build_distribution_queries,
        get_recommended_channels,
        CAC_BENCHMARKS_BY_CHANNEL,
    )

    queries = opp.get("_distribution_queries") or build_distribution_queries(opp)
    recommended = opp.get("_recommended_channels") or get_recommended_channels(opp)
    search_queries = queries[:3]
    query_list = "\n".join(f"- {q}" for q in search_queries)

    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()
    name = opp.get("name", "")

    # Build CAC benchmark context for the prompt
    benchmark_lines = []
    for ch in recommended:
        bm = CAC_BENCHMARKS_BY_CHANNEL.get(ch, {})
        if bm:
            benchmark_lines.append(f"- {ch}: CPL=${bm.get('cpl_usd','?')}, conv={bm.get('conversion_rate','?')}, CAC~${bm.get('approx_cac_usd','?')}")
    benchmark_ctx = "\n".join(benchmark_lines) if benchmark_lines else "No benchmarks available"

    prompt = f"""Research distribution channels and customer acquisition for this opportunity:

Opportunity: {name}
Geography: {geo_label}
Candidate channels: {', '.join(recommended)}

Internal CAC benchmarks:
{benchmark_ctx}

Execute web searches using these queries to find real distribution evidence:
{query_list}

After searching, return ONLY this JSON (no prose, no markdown, no code block):
{{
  "distribution_validated": <true if at least one clear path to first 10 customers confirmed, else false>,
  "top_distribution_channels": [<top 3 channels, most effective first>],
  "estimated_cac_logic": "<one sentence: channel name + CPL + conversion rate + ~$X CAC>",
  "first_10_customer_path": "<step-by-step: how to find and close first 10 customers in {geo_label}>",
  "trust_mechanism_latam": "<primary trust signal that makes {geo_label} buyers pay>"
}}"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCH_USES,
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [b.text for b in response.content if hasattr(b, "text") and b.type == "text"]
    raw = " ".join(text_blocks).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    data = json.loads(match.group())
    result = {}

    validated = data.get("distribution_validated")
    if validated is not None:
        result["distribution_validated"] = bool(validated)

    channels = data.get("top_distribution_channels")
    if isinstance(channels, list):
        result["top_distribution_channels"] = [str(c)[:100] for c in channels[:3] if c]

    cac_logic = data.get("estimated_cac_logic")
    if cac_logic:
        result["estimated_cac_logic"] = str(cac_logic)[:300]

    path = data.get("first_10_customer_path")
    if path:
        result["first_10_customer_path"] = str(path)[:500]

    trust = data.get("trust_mechanism_latam")
    if trust:
        result["trust_mechanism_latam"] = str(trust)[:300]

    result["distribution_validated_date"] = datetime.now().strftime("%Y-%m-%d")
    return result


def _load_env_key() -> Optional[str]:
    """Try to read ANTHROPIC_API_KEY from .env file in project root."""
    root = _find_project_root()
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return key or None
    return None


def _find_project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && PYTHONPATH=src uv run python -c "from opportunity_os.research_executor import run_research_executor; print('import OK')"
```

**Done:** Module imports cleanly. `run_research_executor(opp)` returns opp dict unchanged when no API key (graceful fallback confirmed).

---

### Task 2: Create scripts/run_research_backfill.py

**File:** `scripts/run_research_backfill.py`

**Action:**

Follow `scripts/run_ai_backfill.py` structure exactly: argparse with `--dry-run` and `--force`, `sys.path.insert` for local imports, `load_dotenv`, loop with `time.sleep(1)` between opps (1s, slower than ai_backfill to stay within rate limits on web_search).

```python
"""
Research Backfill — runs pain_intelligence + distribution_intelligence template builders
then fires real web searches via research_executor for all 64 opportunities.

Usage:
    cd .worktrees/daily-opportunity-os
    PYTHONPATH=src uv run python scripts/run_research_backfill.py

Flags:
    --dry-run   Print what would be researched without writing anything
    --force     Re-research ALL opps, even those with research_executed_at
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
_repo_root = Path(__file__).parent.parent
load_dotenv(dotenv_path=_repo_root / ".env", override=True)

from opportunity_os.storage import read_all_opportunities, update_opportunity
from opportunity_os.pain_intelligence import run_pain_intelligence
from opportunity_os.distribution_intelligence import run_distribution_intelligence
from opportunity_os.research_executor import run_research_executor


def main():
    parser = argparse.ArgumentParser(description="Research backfill for all opportunities")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-run even if research_executed_at exists")
    args = parser.parse_args()

    opps = read_all_opportunities()
    total = len(opps)

    if args.force:
        targets = opps
        print(f"FORCE mode: researching all {total} opportunities")
    else:
        targets = [o for o in opps if not o.get("research_executed_at")]
        print(f"Found {len(targets)} unresearched opportunities (of {total} total)")

    if not targets:
        print("Nothing to backfill. All opportunities already have research_executed_at.")
        print("Use --force to re-research everything.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Would research:")
        for o in targets:
            pain_status = "pain_validated" if o.get("pain_validation_score") else "pain_null"
            dist_status = "dist_validated" if o.get("distribution_validated") else "dist_null"
            print(f"  - {o.get('name', '?')[:55]} [{o.get('geography','?')}] {pain_status} {dist_status}")
        return

    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check your .env file.")
        sys.exit(1)

    print(f"\nStarting research backfill for {len(targets)} opportunities...\n")
    succeeded = 0
    failed = 0
    fields_populated = {"pain_validation_score": 0, "exact_customer_phrases": 0,
                        "distribution_validated": 0, "first_10_customer_path": 0}

    for i, opp in enumerate(targets, 1):
        name = opp.get("name", "?")[:55]
        print(f"[{i}/{len(targets)}] {name}...")

        # Build query templates (fast — no API calls)
        pain_template = run_pain_intelligence(opp)
        opp["_pain_queries"] = pain_template.get("_pain_queries", [])

        dist_template = run_distribution_intelligence(opp)
        opp["_recommended_channels"] = dist_template.get("_recommended_channels", [])
        opp["_distribution_queries"] = dist_template.get("_distribution_queries", [])

        # Fire real web searches
        if args.force:
            opp.pop("research_executed_at", None)

        researched = run_research_executor(opp)

        if researched.get("research_executed_at"):
            # Track which fields got populated
            for field in fields_populated:
                val = researched.get(field)
                if val is not None and val != [] and val is not False:
                    fields_populated[field] += 1

            # Strip internal _ fields before saving
            save_opp = {k: v for k, v in researched.items() if not k.startswith("_")}
            update_opportunity(save_opp["id"], save_opp)
            succeeded += 1
        else:
            failed += 1
            print(f"  [FAIL] No research_executed_at — API call likely failed")

        # Rate limit: 1s between opps (web_search is heavier than text-only calls)
        if i < len(targets):
            time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Research backfill complete: {succeeded} succeeded, {failed} failed")
    print(f"\nFields populated:")
    for field, count in fields_populated.items():
        pct = round(count / max(succeeded, 1) * 100)
        print(f"  {field}: {count}/{succeeded} ({pct}%)")


if __name__ == "__main__":
    main()
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && PYTHONPATH=src uv run python scripts/run_research_backfill.py --dry-run
```

**Done:** Dry-run prints all opportunities with their current pain/dist status. No writes. No API calls.

---

### Task 3: Wire research_executor into daily_run.py Steps 10-11

**File:** `src/opportunity_os/pipelines/daily_run.py`

**Action:**

In the existing `run_daily()` function, after Step 11 (distribution intelligence) finishes its loop over `top_5`, add Step 11.5 that calls `run_research_executor` on each opp in `top_5`. This goes AFTER the distribution loop ends (after line ~177) and BEFORE Step 12 (save enriched records).

Find the block:
```python
    # ─── Step 11: Distribution OS — map distribution reality for top 5 ───
```

After the entire Step 11 try/except block ends, insert:

```python
    # ─── Step 11.5: Research Executor — fire real web searches on top 5 ───
    print("Step 11.5: Running Research Executor (web search) on top 5 opportunities...")
    try:
        from opportunity_os.research_executor import run_research_executor
        import time as _time
        for opp in top_5:
            if not opp.get("research_executed_at"):
                run_research_executor(opp)
                _time.sleep(1)
        researched_count = sum(1 for o in top_5 if o.get("research_executed_at"))
        print(f"  Research complete: {researched_count}/{len(top_5)} opps researched")
    except ImportError as e:
        print(f"WARNING  Research executor not available: {e}")
    except Exception as e:
        print(f"WARNING  Research executor error (non-blocking): {e}")
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && PYTHONPATH=src uv run python -c "from opportunity_os.pipelines.daily_run import run_daily; print('import OK')"
```

**Done:** `daily_run.py` imports cleanly. Step 11.5 block present in source. `grep "Step 11.5"` returns the new block.

---

## Wave 1C — Streamlit Dashboard (parallel with 1A)

---
phase: 05-intelligence-amplification
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - dashboard.py
  - pyproject.toml
autonomous: true
requirements: [INTEL-03]

must_haves:
  truths:
    - "Dashboard runs on port 8502 without errors"
    - "Sidebar filters (geography, bucket, lane, score) all work"
    - "Ranked table shows all non-killed opportunities sorted by final_score"
    - "Clicking a row opens 5-tab detail view"
    - "Research tab shows pain_validation_score + exact_customer_phrases"
    - "Scores tab renders 16 dimension scores as horizontal bar chart"
    - "Top metrics row shows correct counts"
  artifacts:
    - path: "dashboard.py"
      provides: "Streamlit dashboard reading opportunities.jsonl live"
      min_lines: 200
    - path: "pyproject.toml"
      provides: "streamlit and plotly added to project.dependencies"
      contains: "streamlit"
  key_links:
    - from: "dashboard.py"
      to: "data/opportunities/opportunities.jsonl"
      via: "open() + json.loads() on each line — no caching"
      pattern: "opportunities.jsonl"
---

### Task 1: Add streamlit and plotly to pyproject.toml

**File:** `pyproject.toml`

**Action:**

Read current pyproject.toml. Under `[project]` → `dependencies`, append `"streamlit>=1.32"` and `"plotly>=5.0"` to the list. Then run `uv sync` to install.

The current dependencies list is:
```toml
dependencies = [
    "pydantic>=2.0",
    "click>=8.0",
    "jinja2>=3.0",
    "pyyaml>=6.0",
    "python-dateutil>=2.8",
    "rich>=13.0",
]
```

Add the two new entries so it becomes:
```toml
dependencies = [
    "pydantic>=2.0",
    "click>=8.0",
    "jinja2>=3.0",
    "pyyaml>=6.0",
    "python-dateutil>=2.8",
    "rich>=13.0",
    "streamlit>=1.32",
    "plotly>=5.0",
]
```

Then run:
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && uv sync
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && uv run python -c "import streamlit; import plotly; print('deps OK')"
```

**Done:** Both `import streamlit` and `import plotly` succeed.

---

### Task 2: Create dashboard.py

**File:** `dashboard.py` (project root, same level as pyproject.toml)

**Action:**

Create the full Streamlit dashboard. Read `data/opportunities/opportunities.jsonl` live on every render — no `st.cache_data` (file changes frequently). The detail view uses `st.session_state` to track the selected opportunity ID.

```python
"""
Opportunity OS Dashboard — Streamlit interface for all 64+ opportunities.

Run: streamlit run dashboard.py --server.port 8502
"""

import json
import os
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

# ─── Path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
OPPS_FILE = ROOT / "data" / "opportunities" / "opportunities.jsonl"

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Opportunity OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Data loader (no cache — reads fresh each render) ────────────────────────
def load_opportunities() -> list[dict]:
    if not OPPS_FILE.exists():
        return []
    opps = []
    with open(OPPS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    opps.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return opps


# ─── Dimension list (mirrors ai_scorer.py) ───────────────────────────────────
DIMENSIONS = [
    "pain_severity", "market_size", "timing_tailwind", "willingness_to_pay",
    "monetization_clarity", "speed_to_mvp", "capital_efficiency",
    "distribution_accessibility", "competition_intensity", "defensibility",
    "regional_fit", "founder_fit", "ai_leverage", "operational_simplicity",
    "regulatory_simplicity", "revenue_speed_score",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _safe_float(val, default=0.0) -> float:
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def _score_color(score: float) -> str:
    if score >= 7.5:
        return "#22c55e"  # green
    if score >= 5.5:
        return "#f59e0b"  # amber
    return "#ef4444"      # red


def render_scores_radar(opp: dict):
    """Plotly radar chart for the 16 dimension scores."""
    values = [_safe_float(opp.get(d), 5) for d in DIMENSIONS]
    labels = [d.replace("_", " ").title() for d in DIMENSIONS]

    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],  # close the loop
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(99, 102, 241, 0.2)",
        line=dict(color="#6366f1", width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        height=350,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_scores_bars(opp: dict):
    """Horizontal bar chart for all 16 dimension scores with _reason tooltips."""
    dims = DIMENSIONS
    scores = [_safe_float(opp.get(d), 0) for d in dims]
    labels = [d.replace("_", " ").title() for d in dims]
    colors = [_score_color(s) for s in scores]
    reasons = [opp.get(f"{d}_reason", "") or "" for d in dims]

    fig = go.Figure(go.Bar(
        x=scores,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        hovertext=[f"{l}: {s:.1f}<br>{r}" for l, s, r in zip(labels, scores, reasons)],
        hoverinfo="text",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 11], showgrid=True, gridcolor="#e5e7eb"),
        yaxis=dict(autorange="reversed"),
        height=480,
        margin=dict(l=200, r=60, t=10, b=30),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show reasons below chart
    st.markdown("**Dimension Reasoning:**")
    for d in dims:
        reason = opp.get(f"{d}_reason", "")
        if reason:
            st.caption(f"**{d.replace('_', ' ').title()}**: {reason}")


def render_detail(opp: dict):
    """Render 5-tab detail view for a selected opportunity."""
    score = _safe_float(opp.get("final_score"))
    geo = opp.get("geography", "?")
    lane = opp.get("portfolio_lane", "?")
    bucket = opp.get("bucket", "?")

    st.markdown(f"## {opp.get('name', 'Unnamed')}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score", f"{score:.2f}", delta=None)
    col2.metric("Lane", lane.upper())
    col3.metric("Geo", geo.upper())
    col4.metric("Bucket", bucket)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Scores", "Research", "Validation", "Economics"]
    )

    with tab1:
        st.markdown("**Problem Statement**")
        st.write(opp.get("problem_statement") or "_No problem statement_")

        kill = opp.get("kill_decision")
        if kill:
            st.error(f"KILLED: {opp.get('kill_reason', 'No reason logged')}")
        else:
            st.success("Active — not killed")

        st.markdown("**Why Now**")
        why_now = opp.get("why_now") or opp.get("timing_tailwind_reason") or "_Not set_"
        st.write(why_now)

        st.markdown("**Path to First Revenue**")
        pfr = opp.get("path_to_first_revenue") or opp.get("monetization_clarity_reason") or "_Not set_"
        st.write(pfr)

        render_scores_radar(opp)

    with tab2:
        render_scores_bars(opp)

    with tab3:
        st.markdown("### Pain Validation")
        pain_score = opp.get("pain_validation_score")
        if pain_score is not None:
            st.metric("Pain Validation Score", f"{_safe_float(pain_score):.1f} / 10")
        else:
            st.warning("Pain research not yet executed (run `scripts/run_research_backfill.py`)")

        phrases = opp.get("exact_customer_phrases") or []
        if phrases:
            st.markdown("**Exact Customer Phrases**")
            for p in phrases:
                st.markdown(f"> {p}")
        else:
            st.caption("No customer phrases yet")

        sources = opp.get("pain_evidence_sources") or []
        if sources:
            st.markdown("**Evidence Sources**")
            for s in sources:
                st.caption(s)

        workarounds = opp.get("workarounds_found") or []
        if workarounds:
            st.markdown("**Current Workarounds**")
            for w in workarounds:
                st.markdown(f"- {w}")

        st.divider()
        st.markdown("### Distribution Research")
        dist_validated = opp.get("distribution_validated")
        if dist_validated is True:
            st.success("Distribution validated")
        elif dist_validated is False:
            st.error("Distribution NOT validated")
        else:
            st.warning("Distribution research not yet executed")

        first_10 = opp.get("first_10_customer_path")
        if first_10:
            st.markdown("**First 10 Customer Path**")
            st.write(first_10)

        cac_logic = opp.get("estimated_cac_logic")
        if cac_logic:
            st.markdown("**Estimated CAC Logic**")
            st.write(cac_logic)

        trust = opp.get("trust_mechanism_latam")
        if trust:
            st.markdown("**Trust Mechanism (LATAM)**")
            st.write(trust)

    with tab4:
        stage = opp.get("stage", "scout")
        status = opp.get("validation_status", "")
        st.metric("Stage", stage)
        if status:
            st.metric("Validation Status", status)

        notes = opp.get("validation_notes") or ""
        if notes:
            st.markdown("**Validation Notes**")
            st.write(notes)

        report = opp.get("validation_report") or ""
        if report:
            st.markdown("**Validation Report**")
            st.markdown(report)
        else:
            st.caption("No validation report yet")

    with tab5:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("TAM (USD)", f"${opp.get('tam', 0):,.0f}" if opp.get("tam") else "N/A")
        col_b.metric("SAM (USD)", f"${opp.get('sam', 0):,.0f}" if opp.get("sam") else "N/A")
        col_c.metric("SOM (USD)", f"${opp.get('som', 0):,.0f}" if opp.get("som") else "N/A")

        tam_method = opp.get("tam_method") or ""
        if tam_method:
            st.caption(f"TAM method: {tam_method}")

        archetype = opp.get("benchmark_archetype") or ""
        if archetype:
            st.markdown("**Benchmark Archetype**")
            st.write(archetype)

        competitors = opp.get("competitors_found") or []
        if competitors:
            st.markdown("**Competitors Found**")
            if isinstance(competitors, list):
                for c in competitors:
                    st.markdown(f"- {c}")
            else:
                st.write(competitors)

        whitespace = opp.get("whitespace_note") or ""
        if whitespace:
            st.markdown("**Whitespace Note**")
            st.write(whitespace)


# ─── Main app ─────────────────────────────────────────────────────────────────
def main():
    # Initialize session state
    if "selected_opp_id" not in st.session_state:
        st.session_state.selected_opp_id = None

    all_opps = load_opportunities()

    # ─── Sidebar filters ──────────────────────────────────────────────────────
    st.sidebar.title("Opportunity OS")
    st.sidebar.caption(f"Loaded {len(all_opps)} opportunities")

    geos = sorted(set(o.get("geography", "global") for o in all_opps))
    lanes = sorted(set(o.get("portfolio_lane", "") for o in all_opps if o.get("portfolio_lane")))
    buckets = sorted(set(o.get("bucket", "") for o in all_opps if o.get("bucket")))

    sel_geo = st.sidebar.multiselect("Geography", geos, default=geos)
    sel_lane = st.sidebar.multiselect("Portfolio Lane", lanes, default=lanes)
    sel_bucket = st.sidebar.multiselect("Bucket", buckets, default=buckets)

    score_min, score_max = st.sidebar.slider("Score Range", 0.0, 10.0, (0.0, 10.0), 0.1)

    show_killed = st.sidebar.checkbox("Show killed opportunities", value=False)

    # ─── Apply filters ────────────────────────────────────────────────────────
    filtered = [
        o for o in all_opps
        if o.get("geography", "global") in sel_geo
        and (not o.get("portfolio_lane") or o.get("portfolio_lane") in sel_lane)
        and (not o.get("bucket") or o.get("bucket") in sel_bucket)
        and score_min <= _safe_float(o.get("final_score")) <= score_max
        and (show_killed or not o.get("kill_decision"))
    ]
    filtered.sort(key=lambda x: _safe_float(x.get("final_score")), reverse=True)

    # ─── Top metrics row ──────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Opps", len(filtered))
    avg_score = sum(_safe_float(o.get("final_score")) for o in filtered) / max(len(filtered), 1)
    m2.metric("Avg Score", f"{avg_score:.2f}")
    ve_count = sum(1 for o in filtered if o.get("geography") == "venezuela")
    m3.metric("Venezuela", ve_count)
    validated_count = sum(1 for o in filtered if o.get("stage") in ("validation", "build"))
    m4.metric("In Validation", validated_count)
    now_count = sum(1 for o in filtered if o.get("portfolio_lane") == "now")
    m5.metric("Now Lane", now_count)

    st.divider()

    # ─── If an opp is selected, show detail view ──────────────────────────────
    if st.session_state.selected_opp_id:
        selected = next(
            (o for o in all_opps if o.get("id") == st.session_state.selected_opp_id),
            None
        )
        if selected:
            if st.button("Back to list"):
                st.session_state.selected_opp_id = None
                st.rerun()
            else:
                render_detail(selected)
                return

    # ─── Main ranked table ────────────────────────────────────────────────────
    st.subheader(f"Ranked Opportunities ({len(filtered)} shown)")

    if not filtered:
        st.info("No opportunities match the current filters.")
        return

    # Table header
    hcols = st.columns([0.5, 3, 0.8, 0.8, 1, 1, 0.8])
    hcols[0].markdown("**#**")
    hcols[1].markdown("**Name**")
    hcols[2].markdown("**Score**")
    hcols[3].markdown("**Geo**")
    hcols[4].markdown("**Lane**")
    hcols[5].markdown("**Bucket**")
    hcols[6].markdown("**Stage**")

    for rank, opp in enumerate(filtered, 1):
        score = _safe_float(opp.get("final_score"))
        cols = st.columns([0.5, 3, 0.8, 0.8, 1, 1, 0.8])
        cols[0].write(str(rank))

        # Clickable name button
        opp_name = opp.get("name", "Unnamed")[:55]
        if cols[1].button(opp_name, key=f"opp_{opp.get('id', rank)}"):
            st.session_state.selected_opp_id = opp.get("id")
            st.rerun()

        score_str = f"{score:.2f}"
        cols[2].markdown(
            f"<span style='color:{_score_color(score)};font-weight:bold'>{score_str}</span>",
            unsafe_allow_html=True
        )
        cols[3].write(opp.get("geography", "?")[:3].upper())
        cols[4].write(opp.get("portfolio_lane", "?"))
        cols[5].write(opp.get("bucket", "?"))
        cols[6].write(opp.get("stage", "scout"))


if __name__ == "__main__":
    main()
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && uv run python -c "import dashboard; print('parse OK')"
```

Manual verify: `streamlit run dashboard.py --server.port 8502` — opens in browser, shows ranked table, clicking a row opens detail view.

**Done:** `dashboard.py` parses without errors. Streamlit launches on port 8502. Top metrics row shows counts. Sidebar filters reduce the table. Clicking any row opens 5-tab detail.

---

## Wave 2 — Pipeline Wiring + Notion Sync (runs after Wave 1 completes)

---
phase: 05-intelligence-amplification
plan: 03
type: execute
wave: 2
depends_on: [plan-01]
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
autonomous: true
requirements: [INTEL-04, INTEL-05]

must_haves:
  truths:
    - "daily_run.py Step 10.5 calls tam_engine.estimate_tam() on all scored_opps"
    - "daily_run.py Step 10.7 calls benchmark_engine.run_benchmark() on top 10"
    - "TAM fields (tam, tam_method, sam, som) are written to opportunity records"
    - "benchmark fields (benchmark_archetype, competitors_found) written to top 10"
  artifacts:
    - path: "src/opportunity_os/pipelines/daily_run.py"
      provides: "TAM + benchmark wired as Steps 10.5 and 10.7"
      contains: "Step 10.5"
  key_links:
    - from: "src/opportunity_os/pipelines/daily_run.py"
      to: "src/opportunity_os/engines/tam_engine.py"
      via: "import estimate_tam; call on scored_opps list"
      pattern: "estimate_tam"
    - from: "src/opportunity_os/pipelines/daily_run.py"
      to: "src/opportunity_os/engines/benchmark_engine.py"
      via: "import run_benchmark; call on all_opps_sorted[:10]"
      pattern: "run_benchmark"
---

### Task 1: Wire TAM engine as Step 10.5 in daily_run.py

**File:** `src/opportunity_os/pipelines/daily_run.py`

**Action:**

Read the current daily_run.py. Find the comment `# Step 9: Rank scored opportunities`. Insert Step 10.5 AFTER the sort block (`all_opps_sorted = sorted(...)`) and BEFORE the existing `# ─── Step 10: Customer Pain OS` comment.

```python
    # ─── Step 10.5: TAM Engine — estimate market size for all scored opps ────
    print("Step 10.5: Running TAM engine on all scored opportunities...")
    try:
        from opportunity_os.engines.tam_engine import estimate_tam
        for opp in all_opps_sorted:
            if not opp.get("tam"):
                tam_result = estimate_tam(opp)
                if tam_result:
                    opp["tam"] = tam_result.get("tam_usd")
                    opp["sam"] = tam_result.get("sam_usd")
                    opp["som"] = tam_result.get("som_usd")
                    opp["tam_method"] = tam_result.get("method")
        tam_populated = sum(1 for o in all_opps_sorted if o.get("tam"))
        print(f"  TAM populated: {tam_populated}/{len(all_opps_sorted)} opps")
    except ImportError as e:
        print(f"WARNING  TAM engine not available: {e}")
    except Exception as e:
        print(f"WARNING  TAM engine error (non-blocking): {e}")
```

Then find the existing `# ─── Step 12: Save enriched records back to JSONL ───` comment (Step 12). Insert Step 10.7 BEFORE Step 12 but AFTER Step 11.5 (the research executor block added in plan-01).

```python
    # ─── Step 10.7: Benchmark Engine — map archetypes for top 10 ─────────────
    print("Step 10.7: Running Benchmark engine on top 10 opportunities...")
    try:
        from opportunity_os.engines.benchmark_engine import run_benchmark
        top_10 = all_opps_sorted[:10]
        for opp in top_10:
            if not opp.get("benchmark_archetype"):
                bench_result = run_benchmark(opp)
                if bench_result:
                    opp["benchmark_archetype"] = bench_result.get("archetype")
                    opp["competitors_found"] = bench_result.get("competitors_found", [])
                    opp["whitespace_note"] = bench_result.get("whitespace_note")
        bench_populated = sum(1 for o in top_10 if o.get("benchmark_archetype"))
        print(f"  Benchmark populated: {bench_populated}/{len(top_10)} top opps")
    except ImportError as e:
        print(f"WARNING  Benchmark engine not available: {e}")
    except Exception as e:
        print(f"WARNING  Benchmark engine error (non-blocking): {e}")
```

**Verify:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && PYTHONPATH=src uv run python -c "from opportunity_os.pipelines.daily_run import run_daily; print('import OK')" && grep -n "Step 10.5\|Step 10.7" src/opportunity_os/pipelines/daily_run.py
```

**Done:** Both Step 10.5 and Step 10.7 blocks appear in daily_run.py grep output. Module imports cleanly.

---

### Task 2: Create scripts/notion_push.py + scripts/run_weekly_ritual.sh

**Files:**
- `scripts/notion_push.py`
- `scripts/run_weekly_ritual.sh`

**Action for notion_push.py:**

This script reads the daily notion-sync JSON and prints clear, actionable instructions for Claude Code to fire MCP calls. It does NOT fire MCP calls itself — it generates a step-by-step execution guide. This is the correct architecture: Python generates the payload, Claude Code reads it and fires the MCP tool calls.

```python
"""
Notion Push — reads the daily sync JSON and prints MCP execution instructions.

This script does NOT call MCP tools directly. It prints the payload in a format
that Claude Code can read and execute via notion MCP tools.

Usage:
    uv run python scripts/notion_push.py
    uv run python scripts/notion_push.py --date 2025-01-15
    uv run python scripts/notion_push.py --list   (show available sync files)
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Print Notion sync instructions from daily payload")
    parser.add_argument("--date", default=None, help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--list", action="store_true", help="List available sync JSON files")
    args = parser.parse_args()

    sync_dir = ROOT / "reports" / "daily"

    if args.list:
        files = sorted(sync_dir.glob("*-notion-sync.json"), reverse=True)
        if not files:
            print("No sync files found in reports/daily/")
            return
        print("Available Notion sync files:")
        for f in files[:10]:
            data = json.loads(f.read_text(encoding="utf-8"))
            n_opps = len(data.get("upsert_opps", []))
            print(f"  {f.name} — {n_opps} opps to upsert")
        return

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    sync_file = sync_dir / f"{date_str}-notion-sync.json"

    if not sync_file.exists():
        print(f"ERROR: No sync file found: {sync_file}")
        print(f"Run a daily pipeline first: opp-os run-daily")
        sys.exit(1)

    payload = json.loads(sync_file.read_text(encoding="utf-8"))
    opps = payload.get("upsert_opps", [])
    stats = payload.get("run_stats", {})

    print(f"\n{'='*60}")
    print(f"NOTION SYNC READY — {date_str}")
    print(f"{'='*60}")
    print(f"Opportunities to upsert: {len(opps)}")
    print(f"Run stats: {json.dumps(stats, indent=2)}")
    print(f"\nSync file: {sync_file}")
    print(f"\n{'='*60}")
    print("CLAUDE CODE INSTRUCTIONS:")
    print("="*60)
    print(f"""
To sync to Notion, execute these MCP calls:

1. For each opportunity in the payload, search Notion for existing page:
   notion-search: query=<opportunity_id>

2. If page exists: notion-update-page with the properties from upsert_opps[i]
   If page not found: notion-create-pages in database {payload.get('metadata', {}).get('opportunity_db_id', 'ad158a23-902c-4fed-9503-a8cffab29754')}

3. After all opps synced, update the Daily Scout Feed page:
   Page ID: {payload.get('metadata', {}).get('daily_feed_page_id', 'a27f4787-07d0-4a07-a6c4-e39dc3f0e75a')}

Payload path for reference:
  {sync_file}
""")

    print("\nTop 5 opportunities in this sync:")
    for i, opp in enumerate(opps[:5], 1):
        score = opp.get("properties", {}).get("Score", {}).get("number", "?")
        name = opp.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "?")
        print(f"  {i}. {name[:50]} — score: {score}")

    print(f"\nFull payload has {len(opps)} entries. Read {sync_file} for complete data.")
    print("\nAfter syncing, daily_run.py already prints 'NOTION SYNC READY' — this script provides the detail.")


if __name__ == "__main__":
    main()
```

**Action for run_weekly_ritual.sh:**

```bash
#!/usr/bin/env bash
# Weekly Ritual — Friday outputs
# Usage: bash scripts/run_weekly_ritual.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=============================="
echo "OPPORTUNITY OS — Weekly Ritual"
echo "=============================="
echo ""
echo "Generating weekly review outputs..."
echo ""

# Generate weekly report via CLI
PYTHONPATH=src uv run python -m opportunity_os.main weekly-review 2>/dev/null || \
    PYTHONPATH=src uv run opp-os weekly-review 2>/dev/null || \
    echo "WARNING: weekly-review CLI not available — run manually in Claude Code session"

echo ""
echo "=============================="
echo "RITUAL CHECKLIST (every Friday)"
echo "=============================="
echo ""
echo "1. Top 3 opportunities to move to validation:"
echo "   -> Run: opp-os weekly-review --output reports/weekly/"
echo ""
echo "2. Top 3 opportunities to discard:"
echo "   -> Check opportunities with score < 4.0 and no recent activity"
echo ""
echo "3. Top 3 rising signals (score increased this week):"
echo "   -> Compare current scores vs last week's JSONL backup"
echo ""
echo "4. 1 conviction area to double down on for 30 days:"
echo "   -> Review top 5 by portfolio_lane='now' in dashboard"
echo ""
echo "Dashboard: streamlit run dashboard.py --server.port 8502"
echo "Notion sync: uv run python scripts/notion_push.py"
echo ""
echo "Ritual complete."
```

**Verify notion_push.py:**
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && PYTHONPATH=src uv run python scripts/notion_push.py --list
```

**Verify run_weekly_ritual.sh:**
```bash
bash "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os/scripts/run_weekly_ritual.sh"
```

**Done:** `notion_push.py --list` runs without error (prints "No sync files found" if none exist). `run_weekly_ritual.sh` prints checklist without crashing.

---

## Wave 3 — Integration Test + Commit

---
phase: 05-intelligence-amplification
plan: 04
type: execute
wave: 3
depends_on: [plan-01, plan-02, plan-03]
files_modified: []
autonomous: false
requirements: [INTEL-01, INTEL-02, INTEL-03, INTEL-04, INTEL-05]

must_haves:
  truths:
    - "All new imports resolve cleanly in a single Python process"
    - "Dashboard parses and loads without errors"
    - "Backfill dry-run lists all unresearched opportunities"
    - "Steps 10.5, 11.5, 10.7 all present in daily_run.py"
    - "All new files committed under feat/daily-opportunity-os branch"
  artifacts:
    - path: "src/opportunity_os/research_executor.py"
      provides: "research executor module"
    - path: "scripts/run_research_backfill.py"
      provides: "backfill script"
    - path: "dashboard.py"
      provides: "streamlit dashboard"
    - path: "scripts/notion_push.py"
      provides: "notion push instructions script"
    - path: "scripts/run_weekly_ritual.sh"
      provides: "weekly ritual runner"
  key_links:
    - from: "daily_run.py"
      to: "research_executor.py"
      via: "Step 11.5 import"
      pattern: "Step 11.5"
    - from: "daily_run.py"
      to: "tam_engine.py"
      via: "Step 10.5 import"
      pattern: "Step 10.5"
---

### Task 1: Integration smoke test

**Action:**

Run the following checks in sequence. All must pass before committing.

```bash
# Check 1: All new modules import cleanly
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && \
PYTHONPATH=src uv run python -c "
from opportunity_os.research_executor import run_research_executor
from opportunity_os.pipelines.daily_run import run_daily
import dashboard
print('ALL IMPORTS OK')
"

# Check 2: Backfill dry-run runs without error
PYTHONPATH=src uv run python scripts/run_research_backfill.py --dry-run

# Check 3: Notion push --list runs without error
PYTHONPATH=src uv run python scripts/notion_push.py --list

# Check 4: New step hooks present in daily_run.py
grep -n "Step 10.5\|Step 10.7\|Step 11.5" src/opportunity_os/pipelines/daily_run.py

# Check 5: streamlit + plotly installed
uv run python -c "import streamlit; import plotly; print('deps OK')"
```

All checks must return without errors. If any fail, fix before proceeding to commit.

**Verify:**
All 5 checks print their success message.

**Done:** All checks pass. Zero import errors. Step hooks present. Deps installed.

---

### Task 2: Commit all Phase 05 files

**Action:**

This is a `checkpoint:human-verify` — run the dashboard manually before committing.

1. Start dashboard: `streamlit run dashboard.py --server.port 8502`
2. Confirm in browser:
   - Top metrics row shows correct counts
   - Sidebar filters work (try filtering by geo=venezuela)
   - Ranked table shows opportunities sorted by score
   - Clicking a row opens detail view with 5 tabs
   - Research tab shows "Pain research not yet executed" message (expected — backfill not run yet)
3. Stop dashboard (Ctrl+C)

Then commit:
```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os" && \
git add \
  src/opportunity_os/research_executor.py \
  scripts/run_research_backfill.py \
  dashboard.py \
  scripts/notion_push.py \
  scripts/run_weekly_ritual.sh \
  src/opportunity_os/pipelines/daily_run.py \
  pyproject.toml && \
git commit -m "feat(05-intelligence): wire research executor, dashboard, TAM+benchmark pipeline, notion push"
```

**Done:** Git commit succeeds on `feat/daily-opportunity-os` branch. All 7 files staged and committed.

---

## Execution Summary

```
Wave 1 (run in parallel):
  Plan 01 — Research Executor (05A)
    Task 1: src/opportunity_os/research_executor.py  (new file)
    Task 2: scripts/run_research_backfill.py         (new file)
    Task 3: daily_run.py Step 11.5 insertion         (edit)

  Plan 02 — Streamlit Dashboard (05C)
    Task 1: pyproject.toml — add streamlit + plotly  (edit)
    Task 2: dashboard.py                             (new file)

Wave 2 (after Wave 1):
  Plan 03 — Pipeline Wiring + Notion (05B + 05D)
    Task 1: daily_run.py Steps 10.5 + 10.7           (edit)
    Task 2: scripts/notion_push.py                   (new file)
            scripts/run_weekly_ritual.sh             (new file)

Wave 3 (after Wave 2):
  Plan 04 — Integration Test + Commit (checkpoint)
    Task 1: smoke tests (all imports, dry-runs, grep checks)
    Task 2: human verify dashboard, then git commit
```

## After Phase 05 — Next Steps

1. **Run backfill** (first real research on all 64 opportunities):
   ```
   PYTHONPATH=src uv run python scripts/run_research_backfill.py
   ```
   Takes ~64 seconds (1s sleep between opps). Will populate pain + distribution fields.

2. **View results** in dashboard:
   ```
   streamlit run dashboard.py --server.port 8502
   ```
   Research tab per opportunity will now show real evidence.

3. **Weekly ritual** (every Friday):
   ```
   bash scripts/run_weekly_ritual.sh
   ```

4. **Notion sync** (after any daily run):
   ```
   uv run python scripts/notion_push.py
   ```
   Then in Claude Code session, read the sync file and fire MCP calls.
