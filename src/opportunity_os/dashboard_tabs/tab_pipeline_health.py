"""Tab 3: Pipeline Health — automation runs, failure counts, metrics history, score trends."""

from collections import Counter

import plotly.graph_objects as go
import streamlit as st

from .components import fmt_ts, section_header, subsection
from .data import (
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
