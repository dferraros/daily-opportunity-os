"""Tab 1: Command Center — live KPIs, top-3 hero cards, ranking table, geo/lane charts."""

from collections import Counter
from datetime import datetime, timedelta

import plotly.graph_objects as go
import streamlit as st

from .components import (
    GEO_LABELS,
    LANE_COLORS,
    SCORE_FIELD,
    hero_card,
    metric_card,
    section_header,
    subsection,
)
from .data import load_machine_metrics


def tab_command_center(opps, filtered_opps, quotas):
    import pandas as pd

    st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:8px 0 20px 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:24px">
  <div style="width:7px;height:7px;background:#22C55E;border-radius:50%;box-shadow:0 0 0 2px rgba(34,197,94,0.2)"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#52525B;letter-spacing:0.05em">Live · {today}</span>
</div>
""".format(today=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
    st.markdown(section_header("Command Center"), unsafe_allow_html=True)

    active_opps = [o for o in filtered_opps if not o.get("kill_decision", False)]
    ve_opps = [o for o in active_opps if (o.get("geography") or "").lower() == "venezuela"]

    scores = [float(o.get(SCORE_FIELD) or 0) for o in active_opps]
    top_score = max(scores) if scores else 0.0

    weekly_quotas = quotas.get("weekly_quotas", {})
    interview_target = weekly_quotas.get("validations_run", {}).get("target", 2)
    metrics_list = load_machine_metrics()
    recent_validations = 0
    if metrics_list:
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        for m in metrics_list:
            if m.get("date", "") >= week_ago:
                recent_validations += m.get("validations_run", 0) or m.get("opportunities_validated_pass", 0)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Total Opportunities", len(active_opps)), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Top Score", f"{top_score:.2f}", accent="#3B82F6"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("VE Opportunities", len(ve_opps), accent="#22C55E"), unsafe_allow_html=True)
    with c4:
        delta_ok = recent_validations >= interview_target
        st.markdown(metric_card(
            "Validation Quota (7d)",
            f"{recent_validations} / {interview_target}",
            delta_text="ON TRACK" if delta_ok else "BEHIND TARGET",
            delta_ok=delta_ok,
        ), unsafe_allow_html=True)

    st.divider()

    # ── Top 3 hero cards ──────────────────────────────────────────────────────
    sorted_opps = sorted(active_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)
    if active_opps:
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;'
            'letter-spacing:3px;text-transform:uppercase;margin-bottom:12px">Top Opportunities</div>',
            unsafe_allow_html=True,
        )
        for rank, o in enumerate(sorted_opps[:3], 1):
            st.markdown(hero_card(o, rank), unsafe_allow_html=True)

    st.divider()

    # ── Table + charts ────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown(subsection("Full Ranking"), unsafe_allow_html=True)
        if not active_opps:
            st.info("No opportunities match current filters.")
        else:
            top10 = sorted_opps[:10]
            rows = []
            for rank, o in enumerate(top10, 1):
                tam = o.get("tam_usd_estimate") or o.get("tam")
                try:
                    tam_str = f"${float(tam)/1e6:.0f}M" if tam else "—"
                except (TypeError, ValueError):
                    tam_str = str(tam) if tam else "—"
                first_seen_raw = o.get("first_seen") or ""
                discovered_str = str(first_seen_raw)[:10] if first_seen_raw else "—"
                rows.append({
                    "#": rank,
                    "Name": (o.get("name", "—") or "—")[:40],
                    "Geo": GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—")),
                    "Score": round(float(o.get(SCORE_FIELD) or 0), 2),
                    "TAM": tam_str,
                    "Lane": (o.get("portfolio_lane") or "—").capitalize(),
                    "Wedge": str(o.get("daniels_wedge_score") or "—"),
                    "Discovered": discovered_str,
                })
            df = pd.DataFrame(rows)
            st.dataframe(
                df, width="stretch", hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=10, format="%.1f"),
                },
            )

    with col_right:
        if not active_opps:
            st.info("No data.")
        else:
            # Geo donut
            geo_counts = Counter(GEO_LABELS.get(o.get("geography", ""), "Other") for o in active_opps)
            geo_colors = ["#3B82F6", "#22C55E", "#F59E0B", "#A855F7", "#EF4444", "#71717A"]
            fig_geo = go.Figure(go.Pie(
                labels=list(geo_counts.keys()),
                values=list(geo_counts.values()),
                hole=0.6,
                marker=dict(colors=geo_colors[:len(geo_counts)]),
                textfont=dict(family="JetBrains Mono", size=10),
            ))
            fig_geo.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=24, b=0), height=200,
                showlegend=True,
                legend=dict(font=dict(size=9, color="#9CA3AF", family="JetBrains Mono"),
                            orientation="v", x=1.0),
                annotations=[dict(text="GEO", x=0.5, y=0.5, showarrow=False,
                                  font=dict(size=11, color="#6B7280", family="JetBrains Mono"))],
            )
            st.plotly_chart(fig_geo, width="stretch", key="cmd_geo_donut")

            # Lane horizontal bars
            lane_order = ["now", "soon", "strategic", "no"]
            lane_counts = Counter(o.get("portfolio_lane") or "—" for o in active_opps)
            lane_vals = [lane_counts.get(l, 0) for l in lane_order]
            lane_clrs = [LANE_COLORS.get(l, "#888") for l in lane_order]
            fig_lane = go.Figure(go.Bar(
                y=[l.upper() for l in lane_order],
                x=lane_vals,
                orientation="h",
                marker_color=lane_clrs,
                text=lane_vals,
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color="#9CA3AF"),
            ))
            fig_lane.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#9CA3AF",
                margin=dict(l=0, r=30, t=8, b=0), height=160,
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(family="JetBrains Mono", size=10)),
            )
            st.plotly_chart(fig_lane, width="stretch", key="cmd_lane_bars")
