"""Tab 3: Pipeline Health — automation runs, failure counts, metrics history, score trends."""

import json
import os
from collections import Counter
from datetime import date as _date
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from opportunity_os.pipelines.signal_harvester import quality_score
from .components import fmt_ts, section_header, subsection
from .data import (
    PROJECT_ROOT,
    load_automation_runs,
    load_machine_metrics,
    load_opportunities,
    load_pipeline_failures,
)


def tab_pipeline_health():
    import pandas as pd

    st.markdown(section_header("Pipeline Health"), unsafe_allow_html=True)

    runs = load_automation_runs()
    metrics_list = load_machine_metrics()
    failures = load_pipeline_failures()

    col1, col2 = st.columns(2)

    # ── Last 10 automation runs ────────────────────────────────────────────────
    with col1:
        st.markdown(subsection("Last 10 Automation Runs"), unsafe_allow_html=True)
        if not runs:
            st.info("No automation runs recorded.")
        else:
            last10 = runs[-10:][::-1]
            rows = []
            for r in last10:
                status = r.get("status", "—")
                exit_code = r.get("exit_code")
                ts = fmt_ts(r.get("date"))
                trigger = r.get("trigger", "manual")
                if status == "completed" and exit_code == 0:
                    icon = "✅"
                elif exit_code and exit_code != 0:
                    icon = "🔴"
                else:
                    icon = "🔵"
                rows.append({
                    "": icon,
                    "Timestamp": ts,
                    "Status": status.capitalize(),
                    "Exit": str(exit_code) if exit_code is not None else "—",
                    "Trigger": trigger,
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    # ── Pipeline failures by step ──────────────────────────────────────────────
    with col2:
        st.markdown(subsection("Pipeline Failures by Step"), unsafe_allow_html=True)
        if not failures:
            st.success("No pipeline failures logged.")
        else:
            step_counts = Counter(f.get("step", "unknown") for f in failures)
            df_fail = pd.DataFrame(
                [{"Step": k, "Count": v} for k, v in step_counts.most_common()],
            )
            st.dataframe(df_fail, width="stretch", hide_index=True)

    st.divider()

    # ── Machine metrics history ────────────────────────────────────────────────
    st.markdown(subsection("Machine Metrics History"), unsafe_allow_html=True)
    if not metrics_list:
        st.info("No machine metrics recorded.")
    else:
        rows = []
        for m in reversed(metrics_list):
            rows.append({
                "Date": m.get("date", "—"),
                "Signals": m.get("signals_ingested", 0),
                "Scored": m.get("opportunities_scored", 0),
                "Killed": m.get("opportunities_killed", 0),
                "Promoted": m.get("opportunities_promoted_to_validation", 0),
                "Val Pass": m.get("opportunities_validated_pass", 0),
                "Val Fail": m.get("opportunities_validated_fail", 0),
                "Deep Dives": m.get("deep_dives_produced", 0),
                "Top Category": m.get("top_category_this_run", "—"),
                "Top Geo": m.get("top_geo_this_run", "—"),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.divider()

    # ── Score history chart ────────────────────────────────────────────────────
    st.markdown(subsection("Score History"), unsafe_allow_html=True)
    all_opps = load_opportunities()
    opps_with_history = [
        o for o in all_opps
        if o.get("score_history") and len(o["score_history"]) > 1
    ]

    if not opps_with_history:
        st.info("No multi-point score history yet. History accumulates as the daily pipeline runs.")
        return

    fig = go.Figure()
    for o in opps_with_history[:15]:  # limit to 15 lines for readability
        history = o["score_history"]
        dates = [h.get("date", "") for h in history]
        scores = [h.get("score", 0) for h in history]
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers",
            name=(o.get("name") or o.get("id") or "—")[:30],
            line=dict(width=1.5),
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fafafa",
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Date",
        yaxis_title="Score",
        height=350,
        legend=dict(font=dict(size=9)),
    )
    fig.update_xaxes(gridcolor="#333")
    fig.update_yaxes(gridcolor="#333")
    st.plotly_chart(fig, width="stretch", key="pipeline_score_hist")

    st.divider()
    st.markdown(subsection("Today's Signal Run"), unsafe_allow_html=True)

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
        if "ask hn" in notes:
            return "HN Ask"
        if "hn story" in notes or "hacker news" in notes:
            return "HN Story"
        if "reddit" in notes:
            return "Reddit"
        if "serper" in notes:
            return "Serper"
        return "Unknown"

    def _quality_badge(q: float) -> str:
        if q >= 0.65:
            color, label = "#22C55E", "HIGH"
        elif q >= 0.30:
            color, label = "#F59E0B", "MED"
        else:
            color, label = "#EF4444", "LOW"
        return (
            f'<span style="font-family:JetBrains Mono,monospace;font-size:9px;'
            f'color:{color};font-weight:600;border:1px solid {color};'
            f'border-radius:3px;padding:1px 5px">{label} {q:.2f}</span>'
        )

    _statuses = [_signal_status(s) for s in _raw_signals]
    _n_passed = sum(1 for status_label, _ in _statuses if status_label == "Passed")
    _n_filtered = len(_raw_signals) - _n_passed

    st.caption(
        f"{len(_raw_signals)} signals ingested  ·  "
        f"{_n_passed} passed filter  ·  "
        f"{_n_filtered} dropped"
    )

    for _sig, (_st_label, _reason) in zip(_raw_signals, _statuses):
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

        with st.expander(f"[{_geo}/{_vert}] {_name}", expanded=False):
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

    st.divider()
    _render_backup_section()


# ── Backup & Recovery section ─────────────────────────────────────────────────

def _render_backup_section():
    """Show available snapshots and allow one-click restore from the dashboard."""
    import pandas as pd
    from .components import subsection

    st.markdown(subsection("Backup & Recovery"), unsafe_allow_html=True)

    try:
        from opportunity_os.backup import create_backup, list_backups, restore_backup
    except ImportError:
        st.error("backup module not found — run `pip install -e .` to reinstall.")
        return

    backups = list_backups()

    col_info, col_snap = st.columns([3, 1])
    with col_info:
        if backups:
            newest = backups[0]
            st.caption(
                f"{len(backups)} snapshot(s) available  ·  "
                f"Newest: **{newest['filename']}**  ·  "
                f"{newest['record_count']} records"
            )
        else:
            st.caption("No snapshots yet. Click **Create Snapshot** to make one.")

    with col_snap:
        if st.button("Create Snapshot", key="ph_create_backup"):
            result = create_backup("dashboard")
            if result:
                st.success(f"Saved {result['record_count']} records → {result['filename']}")
            else:
                st.warning("Snapshot skipped: opportunities store is empty or missing.")
            st.rerun()

    if not backups:
        st.info("Snapshots are created automatically before each `opp-os daily` run.")
        return

    # Table of available backups
    rows = []
    for b in backups:
        size_kb = b["size_bytes"] // 1024
        rows.append({
            "Timestamp": b["timestamp"].replace("-", " ", 3).replace("-", ":"),
            "Label": b["label"],
            "Records": b["record_count"],
            "Size (KB)": size_kb,
            "Filename": b["filename"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    # Restore selector
    st.markdown("**Restore from snapshot:**")
    filenames = [b["filename"] for b in backups]
    selected = st.selectbox(
        "Select snapshot to restore",
        options=filenames,
        format_func=lambda f: f,
        key="ph_restore_select",
        label_visibility="collapsed",
    )

    selected_meta = next((b for b in backups if b["filename"] == selected), None)
    if selected_meta:
        st.caption(
            f"This will overwrite opportunities.jsonl with **{selected_meta['record_count']} records** "
            f"from {selected_meta['timestamp']}."
        )

    confirmed = st.checkbox(
        "I understand this will overwrite the current opportunities store.",
        key="ph_restore_confirm",
    )

    if st.button("Restore Selected Snapshot", key="ph_restore_btn", disabled=not confirmed):
        result = restore_backup(selected)
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])
