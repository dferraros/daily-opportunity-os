# Dashboard Fixes + Signal Visibility Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 4 accuracy/navigation bugs in the Streamlit dashboard and add signal run visibility to the Pipeline Health tab.

**Architecture:** All changes are confined to 5 existing files. No new files, no new dependencies, no schema changes. The signal visibility section reads already-written `.jsonl` files from `data/raw/` — it never re-runs the harvester.

**Tech Stack:** Python, Streamlit, Plotly, `signal_harvester.py` (internal module)

---

## Task 1: Fix subprocess result key bug

**Files:**
- Modify: `src/opportunity_os/dashboard_tabs/tab_deep_dive.py:473,485,488-489`

The subprocess outputs for Validation and Research are cached in session state using
`selected_idx` (an integer position). If the opportunity list re-sorts, a stale cache
entry silently shows the wrong output. Fix: use `opp_id` (stable string) as the key.

**Step 1: Open the file and locate the three occurrences**

Open `src/opportunity_os/dashboard_tabs/tab_deep_dive.py`.

Find line 473 (inside `if run_val:` block):
```python
st.session_state[f"super_val_{selected_idx}"] = (ok, out)
```

Find line 485 (inside `if run_res:` block):
```python
st.session_state[f"super_res_{selected_idx}"] = (ok, out)
```

Find lines 488-489 (the display loop):
```python
for sess_key, label in [
    (f"super_val_{selected_idx}", "Validation"),
    (f"super_res_{selected_idx}", "Research"),
]:
```

**Step 2: Replace all three occurrences**

Line 473 — change to:
```python
st.session_state[f"super_val_{opp_id}"] = (ok, out)
```

Line 485 — change to:
```python
st.session_state[f"super_res_{opp_id}"] = (ok, out)
```

Lines 488-489 — change to:
```python
for sess_key, label in [
    (f"super_val_{opp_id}", "Validation"),
    (f"super_res_{opp_id}", "Research"),
]:
```

**Step 3: Verify no other `selected_idx` session state keys exist**

Run:
```
grep -n "selected_idx" src/opportunity_os/dashboard_tabs/tab_deep_dive.py
```
Expected: only the `st.selectbox(..., key="super_deep_dive_selector")` line and the
`o = active_opps[selected_idx]` assignment. No more session state keys.

**Step 4: Commit**
```bash
git add src/opportunity_os/dashboard_tabs/tab_deep_dive.py
git commit -m "fix(dashboard): key subprocess results by opp_id not selected_idx"
```

---

## Task 2: Fix Kill Gate label

**Files:**
- Modify: `src/opportunity_os/dashboard_tabs/tab_deep_dive.py:531`

The label `"MVP in 2–6 weeks?"` implies a time estimate but the code checks
`speed_to_mvp >= 6` (a numeric 0–10 score). This misleads anyone reading the gate.

**Step 1: Find the line**

In `tab_deep_dive.py`, find the `_KILL_QS` list (around line 524). It looks like:
```python
("MVP in 2–6 weeks?",     (
    o.get("speed_to_mvp") is not None
    and float(o.get("speed_to_mvp") or 0) >= 6
)),
```

**Step 2: Change the label string only**

```python
("Speed to MVP score ≥ 6",     (
    o.get("speed_to_mvp") is not None
    and float(o.get("speed_to_mvp") or 0) >= 6
)),
```

**Step 3: Verify the dashboard renders the new label**

Run `uv run streamlit run src/opportunity_os/dashboard.py`, open the Deep Dive tab,
scroll to KILL GATE. The fifth row should now read "Speed to MVP score ≥ 6".

**Step 4: Commit**
```bash
git add src/opportunity_os/dashboard_tabs/tab_deep_dive.py
git commit -m "fix(dashboard): correct Kill Gate label to match actual score check"
```

---

## Task 3: Fix SAM/SOM honesty in TAM funnel chart

**Files:**
- Modify: `src/opportunity_os/dashboard_tabs/components.py:287-319`

`tam_funnel_chart()` silently fabricates SAM as `tam * 0.12` and SOM as `_sam * 0.18`
when those fields are absent. Labels show real-looking dollar values with no indication
they are estimated. Fix: add `(est.)` suffix and reduce opacity for fabricated values.

**Step 1: Locate the full function**

In `components.py`, find `def tam_funnel_chart(tam: float, sam: float | None, som: float | None):` (around line 287).

**Step 2: Replace the entire function body**

Replace the current function with:
```python
def tam_funnel_chart(tam: float, sam: float | None, som: float | None):
    """TAM -> SAM -> SOM bar chart. Estimated values shown at reduced opacity with (est.) label."""
    is_sam_estimated = sam is None
    is_som_estimated = som is None

    _sam = sam if sam is not None else tam * 0.12
    _som = som if som is not None else _sam * 0.18

    def fmt(v: float, estimated: bool) -> str:
        if v >= 1e9:
            base = f"${v/1e9:.1f}B"
        elif v >= 1e6:
            base = f"${v/1e6:.0f}M"
        else:
            base = f"${v/1e3:.0f}K"
        return f"{base} (est.)" if estimated else base

    labels = ["TAM", "SAM", "SOM"]
    values = [tam, _sam, _som]
    estimated_flags = [False, is_sam_estimated, is_som_estimated]
    colors = [
        "rgba(59,130,246,0.85)",
        "rgba(34,197,94,0.35)" if is_sam_estimated else "rgba(34,197,94,0.6)",
        "rgba(245,158,11,0.25)" if is_som_estimated else "rgba(245,158,11,0.55)",
    ]
    texts = [fmt(v, est) for v, est in zip(values, estimated_flags)]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=texts,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="JetBrains Mono", size=12, color="#F8FAFC"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=8, b=0),
        height=150,
        showlegend=False,
        xaxis=dict(tickfont=dict(family="JetBrains Mono", size=10, color="#9CA3AF"), showgrid=False),
        yaxis=dict(visible=False),
    )
    return fig, (is_sam_estimated or is_som_estimated)
```

Note: the function now returns a **tuple** `(fig, has_estimated)`. This is a breaking change
to callers — fix them in the next step.

**Step 3: Fix the two callers**

Search for all calls to `tam_funnel_chart`:
```
grep -rn "tam_funnel_chart" src/
```

There are two callers: `tab_deep_dive.py` and `tab_all_opportunities.py` (via components import).
Actually `tab_all_opportunities.py` doesn't call it — only `tab_deep_dive.py` does.

In `tab_deep_dive.py`, find the call (around line 248):
```python
st.plotly_chart(
    tam_funnel_chart(tam_raw, sam_raw, som_raw),
```

Replace with:
```python
_funnel_fig, _has_est = tam_funnel_chart(tam_raw, sam_raw, som_raw)
st.plotly_chart(
    _funnel_fig,
```

Then immediately after the `st.plotly_chart(...)` call for the funnel, add:
```python
if _has_est:
    st.caption("(est.) = modeled at 12% TAM / 18% SAM — not field-validated")
```

**Step 4: Verify**

Run `uv run streamlit run src/opportunity_os/dashboard.py`, open Deep Dive tab,
select an opportunity. If it has no SAM/SOM fields:
- SAM bar should be visibly dimmer than TAM
- SAM label should read e.g. `$12M (est.)`
- Caption `(est.) = modeled...` should appear below the chart

If the opp has real SAM/SOM values: no `(est.)` suffix, full opacity bars.

**Step 5: Commit**
```bash
git add src/opportunity_os/dashboard_tabs/components.py src/opportunity_os/dashboard_tabs/tab_deep_dive.py
git commit -m "fix(dashboard): mark estimated SAM/SOM with (est.) label and reduced opacity"
```

---

## Task 4: Fix cross-tab navigation hint

**Files:**
- Modify: `src/opportunity_os/dashboard_tabs/tab_all_opportunities.py:187-205`

The current hint disappears on the next rerun because `active_tab_hint` is set but there
is no guarantee the expander that set it is still expanded. Fix: remove the `active_tab_hint`
flag entirely — show the hint solely based on whether `deep_dive_opp_name` is set in session
state and matches this opp. The Deep Dive tab already deletes this key when the user navigates
there, so the hint naturally disappears once the user arrives.

**Step 1: Find the navigation block**

In `tab_all_opportunities.py`, find lines 187-205:
```python
# Cross-tab deep dive navigation
st.markdown("---")
btn_col, hint_col = st.columns([1, 3])
with btn_col:
    if st.button(
        "📊 → Super Deep Dive",
        key=f"goto_dd_{opp_idx}",
        use_container_width=True,
    ):
        st.session_state["deep_dive_opp_name"] = o.get("name")
        st.session_state["active_tab_hint"] = True
with hint_col:
    if (
        st.session_state.get("active_tab_hint")
        and st.session_state.get("deep_dive_opp_name") == o.get("name")
    ):
        st.info(
            "↑ Switch to the **Deep Dive** tab above to see the full intelligence brief."
        )
```

**Step 2: Replace with the cleaner version**

```python
# Cross-tab deep dive navigation
st.markdown("---")
btn_col, hint_col = st.columns([1, 3])
with btn_col:
    if st.button(
        "📊 → Super Deep Dive",
        key=f"goto_dd_{opp_idx}",
        use_container_width=True,
    ):
        st.session_state["deep_dive_opp_name"] = o.get("name")
with hint_col:
    if st.session_state.get("deep_dive_opp_name") == o.get("name"):
        st.info(
            "✓ Ready in **Deep Dive** tab — click the tab above to view the full brief for this opportunity."
        )
```

Changes made:
- Removed the `active_tab_hint` write entirely (was redundant)
- Hint condition is now just `deep_dive_opp_name == this opp's name`
- Hint text is more actionable ("Ready in Deep Dive tab")

**Step 3: Verify**

Run the dashboard. In All Opportunities, expand any opp and click "Super Deep Dive".
- The hint should appear immediately and stay visible on subsequent reruns
- Switch to Deep Dive tab — the hint should no longer appear in All Opps after the Deep Dive
  tab renders (because `tab_deep_dive.py` deletes the session state key)

**Step 4: Commit**
```bash
git add src/opportunity_os/dashboard_tabs/tab_all_opportunities.py
git commit -m "fix(dashboard): make cross-tab navigation hint persistent until Deep Dive loads"
```

---

## Task 5: Expose quality_score as public + add Pipeline Health signal section

**Files:**
- Modify: `src/opportunity_os/pipelines/signal_harvester.py:140`
- Modify: `src/opportunity_os/dashboard_tabs/tab_pipeline_health.py`

### Part A: Make quality_score importable

**Step 1: Rename the function**

In `signal_harvester.py` line 140, change:
```python
def _quality_score(signal: dict) -> float:
```
to:
```python
def quality_score(signal: dict) -> float:
```

**Step 2: Update the internal call site**

In `signal_harvester.py`, find line ~388 inside `harvest_signals()`:
```python
scored = sorted(
    [(s, _quality_score(s)) for s in all_raw],
```
Change to:
```python
scored = sorted(
    [(s, quality_score(s)) for s in all_raw],
```

**Step 3: Verify no other `_quality_score` references**
```
grep -n "_quality_score" src/opportunity_os/pipelines/signal_harvester.py
```
Expected: 0 results.

### Part B: Add signal run section to Pipeline Health tab

**Step 4: Add the imports at the top of `tab_pipeline_health.py`**

At the top of `tab_pipeline_health.py`, after the existing imports, add:
```python
import json
from datetime import date as _date
from pathlib import Path

from opportunity_os.pipelines.signal_harvester import quality_score
from .data import PROJECT_ROOT
```

**Step 5: Add the signal run section at the bottom of `tab_pipeline_health()`**

At the very end of `tab_pipeline_health()` (after the score history chart block, replacing
the bare `return` after `st.info(...)`), add:

```python
st.divider()
st.markdown(subsection("Today's Signal Run"), unsafe_allow_html=True)

_default_date = _date.today().isoformat()
_selected_date = st.date_input(
    "Signal file date",
    value=_date.today(),
    key="ph_signal_date",
).isoformat()

_raw_dir = PROJECT_ROOT / "data" / "raw"
_signal_file = _raw_dir / f"{_selected_date}-signals.jsonl"

if not _signal_file.exists():
    st.info(
        f"No signal file for {_selected_date}. "
        f"Run `opp-os harvest` or `opp-os daily` to generate one."
    )
    return

# Load raw signals
_raw_signals: list[dict] = []
try:
    with open(_signal_file, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line:
                try:
                    _raw_signals.append(json.loads(_line))
                except json.JSONDecodeError:
                    pass
except OSError as _exc:
    st.error(f"Could not read signal file: {_exc}")
    return

if not _raw_signals:
    st.info("Signal file exists but is empty.")
    return

# Score and classify each signal
_MIN_QUALITY = 0.30
_MIN_NAME_LEN = 15

def _signal_status(sig: dict) -> tuple[str, str]:
    """Return (status_label, reason) for display."""
    if len(sig.get("name", "")) < _MIN_NAME_LEN:
        return "Filtered", "Name too short"
    q = quality_score(sig)
    if q < _MIN_QUALITY:
        return "Filtered", f"Quality {q:.2f} < {_MIN_QUALITY}"
    return "Passed", ""

def _source_chip(sig: dict) -> str:
    notes = sig.get("raw_notes", "").lower()
    if "hn story" in notes or "hacker news" in notes:
        return "HN Story"
    if "ask hn" in notes:
        return "HN Ask"
    if "reddit" in notes:
        return "Reddit"
    if "serper" in notes:
        return "Serper"
    return "Unknown"

def _quality_badge(q: float) -> str:
    if q >= 0.65:
        color = "#22C55E"
        label = "HIGH"
    elif q >= 0.30:
        color = "#F59E0B"
        label = "MED"
    else:
        color = "#EF4444"
        label = "LOW"
    return (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:9px;'
        f'color:{color};font-weight:600;border:1px solid {color};'
        f'border-radius:3px;padding:1px 5px">{label} {q:.2f}</span>'
    )

_statuses = [_signal_status(s) for s in _raw_signals]
_passed = sum(1 for st_label, _ in _statuses if st_label == "Passed")
_filtered = len(_raw_signals) - _passed

st.caption(
    f"{len(_raw_signals)} signals ingested  ·  "
    f"{_passed} passed filter  ·  "
    f"{_filtered} dropped"
)

for _i, (_sig, (_st_label, _reason)) in enumerate(zip(_raw_signals, _statuses)):
    _q = quality_score(_sig)
    _name = _sig.get("name", "—")[:60]
    _geo = _sig.get("geography", "?").upper()
    _vert = _sig.get("vertical", "?")
    _src = _source_chip(_sig)
    _status_color = "#22C55E" if _st_label == "Passed" else "#52525B"
    _status_str = (
        f'<span style="color:{_status_color};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;font-weight:600">{_st_label}</span>'
        + (f' <span style="color:#52525B;font-size:9px">— {_reason}</span>' if _reason else "")
    )

    with st.expander(
        f"[{_geo}/{_vert}] {_name}",
        expanded=False,
    ):
        col_meta, col_badge = st.columns([3, 1])
        with col_meta:
            st.markdown(_status_str, unsafe_allow_html=True)
            st.caption(f"Source: {_src}")
            if _sig.get("source_url"):
                st.caption(f"URL: {_sig['source_url'][:100]}")
            if _sig.get("description"):
                st.caption(_sig["description"][:200])
            if _sig.get("raw_notes"):
                st.caption(f"Notes: {_sig['raw_notes'][:120]}")
        with col_badge:
            st.markdown(_quality_badge(_q), unsafe_allow_html=True)
```

**Step 6: Verify the section renders**

Run `uv run streamlit run src/opportunity_os/dashboard.py`. Navigate to Pipeline Health.
Scroll to the bottom — "Today's Signal Run" section should appear.

- If `data/raw/YYYY-MM-DD-signals.jsonl` exists for today: signals listed with badges
- If no file: grey info box with instructions to run `opp-os harvest`
- Change the date picker to a past date that has a signals file — table should update

**Step 7: Commit**
```bash
git add src/opportunity_os/pipelines/signal_harvester.py
git add src/opportunity_os/dashboard_tabs/tab_pipeline_health.py
git commit -m "feat(dashboard): add signal run visibility section to Pipeline Health tab"
```

---

## Final verification

After all 5 tasks:

1. **Subprocess key fix**: Run validation on Deep Dive tab, note the opp name, then change
   selected opp and back — output should only show for the correct opp.

2. **Kill Gate label**: Open Deep Dive → KILL GATE section. Fifth row reads
   "Speed to MVP score ≥ 6".

3. **SAM/SOM**: Select an opp with no `sam_usd_estimate` field. TAM bar is full opacity,
   SAM/SOM bars are dimmer, labels show `(est.)`, caption appears.

4. **Cross-tab nav**: In All Opps, click "Super Deep Dive". Hint persists across reruns.
   Switch to Deep Dive tab — hint clears from All Opps on next visit.

5. **Signal run**: Pipeline Health → scroll to bottom → "Today's Signal Run" section
   shows signals with quality badges.

Run the full daily pipeline as a smoke test:
```bash
uv run opp-os daily --dry-run
```
Expected: exits 0, no import errors.
