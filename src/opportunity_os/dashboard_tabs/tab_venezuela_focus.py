"""Tab 4: Venezuela Focus — VE-only KPIs, wedge breakdown, lane pie, ranked table."""

from collections import Counter

import plotly.graph_objects as go
import streamlit as st

from .components import LANE_COLORS, SCORE_FIELD, section_header, subsection


def tab_venezuela_focus(opps):
    import pandas as pd

    st.markdown(section_header("Venezuela Focus"), unsafe_allow_html=True)

    ve_opps = [o for o in opps if (o.get("geography") or "").lower() == "venezuela"]
    ve_opps_sorted = sorted(
        ve_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True
    )

    # KPI row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("VE Opportunities", len(ve_opps))
    with c2:
        avg_score = (
            sum(float(o.get(SCORE_FIELD) or 0) for o in ve_opps) / len(ve_opps)
            if ve_opps else 0.0
        )
        st.metric("Avg VE Score", f"{avg_score:.2f}")
    with c3:
        lens_applied = sum(1 for o in ve_opps if o.get("venezuela_lens_applied"))
        st.metric("Lens Applied", f"{lens_applied} / {len(ve_opps)}")

    st.divider()

    if not ve_opps:
        st.info("No Venezuela opportunities match current filters.")
        return

    col1, col2 = st.columns([1, 1])

    # ── Wedge category breakdown ───────────────────────────────────────────────
    with col1:
        st.markdown(subsection("Wedge Category Breakdown"), unsafe_allow_html=True)
        wedge_counts = Counter(
            o.get("venezuela_wedge_category") or "unclassified"
            for o in ve_opps
        )
        df_wedge = pd.DataFrame(
            [{"Category": k, "Count": v} for k, v in wedge_counts.most_common()]
        )
        fig = go.Figure(go.Bar(
            y=df_wedge["Category"],
            x=df_wedge["Count"],
            orientation="h",
            marker_color="#f59e0b",
            text=df_wedge["Count"],
            textposition="outside",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fafafa",
            margin=dict(l=10, r=30, t=10, b=30),
            height=max(250, len(wedge_counts) * 40),
            showlegend=False,
        )
        fig.update_xaxes(gridcolor="#333")
        fig.update_yaxes(gridcolor="#333")
        st.plotly_chart(fig, use_container_width=True, key="ve_wedge_bar")

    # ── Lane breakdown ─────────────────────────────────────────────────────────
    with col2:
        st.markdown(subsection("Lane Distribution"), unsafe_allow_html=True)
        lane_counts = Counter(o.get("portfolio_lane") or "unknown" for o in ve_opps)
        labels = list(lane_counts.keys())
        values = list(lane_counts.values())
        colors = [LANE_COLORS.get(l, "#888") for l in labels]
        fig2 = go.Figure(go.Pie(
            labels=[l.capitalize() for l in labels],
            values=values,
            marker_colors=colors,
            hole=0.45,
            textinfo="label+percent",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#fafafa",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, key="ve_lane_pie")

    st.divider()

    # ── VE opportunities ranked table ──────────────────────────────────────────
    st.markdown(subsection("Venezuela Opportunities — Ranked"), unsafe_allow_html=True)
    rows = []
    for o in ve_opps_sorted:
        rows.append({
            "Name": o.get("name", "—"),
            "Score": round(float(o.get(SCORE_FIELD) or 0), 2),
            "Lane": (o.get("portfolio_lane") or "—").capitalize(),
            "Stage": (o.get("stage") or "—").capitalize(),
            "Wedge": o.get("venezuela_wedge_category") or "unclassified",
            "Lens": "Yes" if o.get("venezuela_lens_applied") else "No",
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    # ── Expandable detail per VE opp ──────────────────────────────────────────
    st.markdown(subsection("Detail"), unsafe_allow_html=True)
    for o in ve_opps_sorted:
        score = float(o.get(SCORE_FIELD) or 0)
        with st.expander(f"{o.get('name', '—')} — {score:.2f}", expanded=False):
            st.markdown(f"**Problem:** {o.get('problem_statement', '—')}")
            st.markdown(f"**Target customer:** {o.get('target_customer', '—')}")
            if o.get("path_to_first_revenue"):
                st.markdown(f"**Path to first revenue:** {o.get('path_to_first_revenue')}")
            if o.get("trigger_signal"):
                st.markdown(f"**Trigger signal:** {o.get('trigger_signal')}")
