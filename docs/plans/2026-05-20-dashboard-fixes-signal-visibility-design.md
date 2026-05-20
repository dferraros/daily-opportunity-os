# Dashboard Fixes + Signal Visibility Design

**Date:** 2026-05-20
**Scope:** Fix 4 accuracy/navigation bugs, add signal run visibility to Pipeline Health tab.
**Out of scope:** Inline actions (promote/kill/research from dashboard) — that is Phase 2.

---

## Goal

Make the dashboard trustworthy and informative. Four bugs currently cause silent wrong data
or broken UX. Signal visibility closes the loop between the harvester and the scored list.

---

## Architecture

All changes are confined to:
- `src/opportunity_os/dashboard_tabs/components.py` — SAM/SOM honesty fix
- `src/opportunity_os/dashboard_tabs/tab_deep_dive.py` — subprocess key bug + Kill Gate label
- `src/opportunity_os/dashboard_tabs/tab_all_opportunities.py` — cross-tab navigation fix
- `src/opportunity_os/dashboard_tabs/tab_pipeline_health.py` — signal run section
- `src/opportunity_os/pipelines/signal_harvester.py` — expose `quality_score()` as public

No new files. No schema changes. No new dependencies.

---

## Section 1: The 4 Accuracy Fixes

### Fix 1 — Cross-tab navigation (tab_all_opportunities.py)

**Current:** "Super Deep Dive" button sets `st.session_state["deep_dive_opp_name"]` and shows
a tooltip asking the user to manually click the Deep Dive tab. Tab switching is not automatic.

**Fix:** Keep the session state write. Replace the tooltip with a persistent, styled
`st.info()` banner that survives across reruns (do not delete it on the next rerender).
Add a `st.page_link()`-style markdown anchor pointing the user clearly to the tab.
The banner stays visible until the user selects a different opportunity.

This is the pragmatic fix within Streamlit's constraints (no programmatic tab switch in
Streamlit < 1.44 without multi-page mode). The UX message becomes unambiguous rather than
disappearing on rerun.

### Fix 2 — Subprocess result key bug (tab_deep_dive.py)

**Current:** Deep dive / research / validation subprocess outputs are cached in session
state keyed by `selected_idx` (integer position in the sorted list). If the list order
changes (e.g. after a new score run), cached results silently show for the wrong opp.

**Fix:** Key all subprocess result caches by `opp_id` (stable string field). Change every
`st.session_state[f"some_key_{selected_idx}"]` to `st.session_state[f"some_key_{opp_id}"]`
throughout `tab_deep_dive.py`.

### Fix 3 — SAM/SOM honesty (components.py)

**Current:** `tam_funnel_chart()` silently computes `_sam = sam if sam else tam * 0.12`
and `_som = som if som else _sam * 0.18`. Bar labels show dollar values with no indication
they are estimated.

**Fix:**
- Add `is_sam_estimated = sam is None` and `is_som_estimated = som is None` booleans.
- When estimated: append `" (est.)"` to the bar text label.
- When estimated: render bar at 50% opacity (add `opacity=0.5` per bar via marker config).
- When real: full opacity, no suffix.
- Add a `st.caption("(est.) = modeled at 12% / 18% of parent tier")` footnote below
  the chart when any estimated value is shown.

### Fix 4 — Kill Gate label (tab_deep_dive.py)

**Current:** Kill Gate criterion label reads `"MVP in 2-6 weeks?"` but the code checks
`speed_to_mvp >= 6` (a numeric score, not a time estimate).

**Fix:** Change label to `"Speed to MVP score ≥ 6"`. One string change.

---

## Section 2: Signal Visibility in Pipeline Health Tab

### What it shows

A new collapsible section at the bottom of `tab_pipeline_health.py`:
**"Today's Signal Run"** with a date picker (default: today).

Reads `data/raw/YYYY-MM-DD-signals.jsonl`. If no file exists for the selected date,
shows a grey info box: "No signal file for {date}. Run `opp-os harvest` or `opp-os daily`."

**Signal table columns:**
| Column | Value |
|---|---|
| Name | Truncated to 60 chars |
| Geo / Vertical | Classified values from harvester |
| Quality | Badge: green (≥ 0.65), amber (0.30–0.64), red (< 0.30) |
| Source | Chip: HN Story / HN Ask / Reddit / Serper |
| Status | "Passed" (green) or "Filtered" (grey, with reason) |

Expandable row shows: full name, source URL, raw_notes, description snippet (200 chars).

**Summary line above table:**
`{n} signals ingested · {passed} passed filter · {filtered} dropped`

### Quality score exposure

`signal_harvester.py`: rename `_quality_score` → `quality_score` (remove leading underscore)
to make it importable by the dashboard without triggering linter warnings about private access.

### Filter status logic

A signal is "Filtered" if:
- `quality_score(signal) < min_quality` (default 0.30) — reason: "Below quality threshold"
- Name is a duplicate of an existing opp — reason: "Duplicate"
- Name length < 15 chars — reason: "Too short"

The dashboard re-runs this same logic on the raw signals to assign status.
It does NOT re-run the harvester; it reads the already-written `.jsonl` file.

---

## Files to Touch

| File | Change |
|---|---|
| `components.py` | `tam_funnel_chart()`: estimated flag, opacity, label suffix, caption |
| `tab_deep_dive.py` | Subprocess keys: `selected_idx` → `opp_id`; Kill Gate label |
| `tab_all_opportunities.py` | Navigation hint: persistent banner, no auto-delete |
| `tab_pipeline_health.py` | New "Today's Signal Run" section |
| `signal_harvester.py` | `_quality_score` → `quality_score` (public) |

---

## Testing

- Run `uv run streamlit run src/opportunity_os/dashboard.py` after each fix
- For Fix 2: select an opp, run a subprocess, then change the sort order and verify result
  still shows for the correct opp
- For Fix 3: open an opp with no SAM/SOM fields and verify `(est.)` appears
- For Section 2: run `opp-os harvest --dry-run` then check Pipeline Health tab shows signal file
- No new pytest tests required (dashboard is Streamlit UI, not unit-testable in isolation)
