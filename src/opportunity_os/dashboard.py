"""
Opportunity OS — Streamlit Dashboard
Single-file, 5-tab dashboard for the Daily Opportunity OS.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Opportunity OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Paths ───────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ─── Data Loaders ────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_opportunities():
    path = PROJECT_ROOT / "data" / "opportunities" / "opportunities.jsonl"
    opps = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        opps.append(json.loads(line))
                    except Exception:
                        pass
    return opps


@st.cache_data(ttl=60)
def load_automation_runs():
    path = PROJECT_ROOT / "data" / "automation_runs.jsonl"
    runs = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        runs.append(json.loads(line))
                    except Exception:
                        pass
    return runs


@st.cache_data(ttl=60)
def load_machine_metrics():
    path = PROJECT_ROOT / "data" / "machine_metrics.jsonl"
    metrics = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        metrics.append(json.loads(line))
                    except Exception:
                        pass
    return metrics


@st.cache_data(ttl=60)
def load_pipeline_failures():
    path = PROJECT_ROOT / "data" / "pipeline_failures.jsonl"
    failures = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        failures.append(json.loads(line))
                    except Exception:
                        pass
    return failures


@st.cache_data(ttl=60)
def load_weekly_quotas():
    import yaml
    path = PROJECT_ROOT / "config" / "weekly_quotas.yaml"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_last_run_ts(runs):
    """Return ISO string of last completed run, or None."""
    completed = [r for r in runs if r.get("status") == "completed"]
    if not completed:
        return None
    last = max(completed, key=lambda r: r.get("date", ""))
    return last.get("date")


def fmt_ts(ts_str):
    if not ts_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts_str


def score_bucket(score):
    if score is None:
        return "unknown"
    score = float(score)
    if score < 2:
        return "< 2"
    elif score < 3:
        return "2-3"
    elif score < 4:
        return "3-4"
    elif score < 5:
        return "4-5"
    elif score < 6:
        return "5-6"
    elif score < 7:
        return "6-7"
    elif score < 8:
        return "7-8"
    elif score < 9:
        return "8-9"
    else:
        return "9-10"


SCORE_BUCKET_ORDER = ["< 2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10"]

LANE_COLORS = {
    "now": "#22c55e",
    "soon": "#3b82f6",
    "strategic": "#a855f7",
    "no": "#ef4444",
}

GEO_LABELS = {
    "global": "Global",
    "latam": "LATAM",
    "venezuela": "Venezuela",
    "spain": "Spain",
    "us": "US",
    "other": "Other",
}

DIMENSION_FIELDS = [
    "pain_severity", "market_size", "timing_tailwind",
    "monetization_clarity", "speed_to_mvp", "capital_efficiency",
    "distribution_accessibility", "competition_intensity", "defensibility",
    "regional_fit", "founder_fit", "ai_leverage",
    "operational_simplicity", "regulatory_simplicity",
]

SCORE_FIELD = "final_score"


def apply_filters(opps, geo_filter, score_min, score_max):
    """Apply sidebar filters."""
    result = opps
    if geo_filter and geo_filter != "All":
        geo_key = geo_filter.lower()
        result = [o for o in result if (o.get("geography") or "").lower() == geo_key]
    result = [
        o for o in result
        if score_min <= float(o.get(SCORE_FIELD) or 0) <= score_max
    ]
    return result


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar(runs):
    with st.sidebar:
        st.title("Opportunity OS")

        # Last run
        last_ts = get_last_run_ts(runs)
        st.caption(f"Last run: **{fmt_ts(last_ts)}**")
        st.divider()

        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
        if auto_refresh:
            st.caption("Refreshing every 30s...")
            import time
            time.sleep(30)
            st.rerun()

        # Run pipeline button
        st.subheader("Pipeline")
        if st.button("▶ Run daily pipeline", use_container_width=True):
            with st.spinner("Running pipeline…"):
                try:
                    result = subprocess.run(
                        ["uv", "run", "--no-sync", "python", "-m", "opportunity_os.main", "daily"],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    if result.returncode == 0:
                        st.success("Pipeline completed successfully.")
                        st.cache_data.clear()
                    else:
                        st.error(f"Pipeline failed (exit {result.returncode})")
                        if result.stderr:
                            st.code(result.stderr[-2000:], language="text")
                except subprocess.TimeoutExpired:
                    st.error("Pipeline timed out after 5 minutes.")
                except Exception as e:
                    st.error(f"Could not run pipeline: {e}")

        st.divider()

        # Geography filter
        st.subheader("Filters")
        geo_options = ["All", "Global", "LATAM", "Venezuela", "Spain", "US", "Other"]
        geo_filter = st.selectbox("Geography", geo_options, index=0)

        # Score range
        score_range = st.slider(
            "Score range",
            min_value=0.0,
            max_value=10.0,
            value=(0.0, 10.0),
            step=0.1,
        )

        st.divider()
        st.caption("Built with Streamlit · Opportunity OS v1")

    return geo_filter, score_range


# ─── Tab 1: Command Center ────────────────────────────────────────────────────

def tab_command_center(opps, filtered_opps, quotas):
    st.header("Command Center")

    active_opps = [o for o in filtered_opps if not o.get("kill_decision", False)]
    killed_opps = [o for o in filtered_opps if o.get("kill_decision", False)]
    ve_opps = [o for o in active_opps if (o.get("geography") or "").lower() == "venezuela"]

    scores = [float(o.get(SCORE_FIELD) or 0) for o in active_opps]
    top_score = max(scores) if scores else 0.0

    # Interview quota
    weekly_quotas = quotas.get("weekly_quotas", {})
    interview_target = weekly_quotas.get("validations_run", {}).get("target", 2)
    # Load interview count from machine_metrics or interviews file
    metrics_list = load_machine_metrics()
    recent_validations = 0
    if metrics_list:
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        for m in metrics_list:
            if m.get("date", "") >= week_ago:
                recent_validations += m.get("validations_run", 0) or m.get("opportunities_validated_pass", 0)

    # ── KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Opportunities", len(active_opps))
    with c2:
        st.metric("Top Score", f"{top_score:.2f}")
    with c3:
        st.metric("VE Opportunities", len(ve_opps))
    with c4:
        quota_label = f"{recent_validations} / {interview_target}"
        delta_color = "normal" if recent_validations > 0 else "inverse"
        st.metric(
            "Validation Quota (7d)",
            quota_label,
            delta="On track" if recent_validations >= interview_target else "Behind",
            delta_color=delta_color,
        )

    st.divider()

    # ── Top 10 table
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.subheader("Top 10 Opportunities")
        if not active_opps:
            st.info("No opportunities match current filters.")
        else:
            sorted_opps = sorted(active_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)
            top10 = sorted_opps[:10]
            rows = []
            for rank, o in enumerate(top10, 1):
                rows.append({
                    "Rank": rank,
                    "Name": o.get("name", "—"),
                    "Geography": GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—")),
                    "Score": round(float(o.get(SCORE_FIELD) or 0), 2),
                    "Raw Score": round(float(o.get("attractiveness_score") or 0), 2),
                    "Lane": (o.get("portfolio_lane") or "—").capitalize(),
                    "Stage": (o.get("stage") or "—").capitalize(),
                })

            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.NumberColumn(format="%.2f"),
                    "Raw Score": st.column_config.NumberColumn(format="%.2f"),
                },
            )

    with col_right:
        st.subheader("Score Distribution")
        if not active_opps:
            st.info("No data.")
        else:
            from collections import Counter
            bucket_counts = Counter(score_bucket(o.get(SCORE_FIELD)) for o in active_opps)
            bucket_data = {b: bucket_counts.get(b, 0) for b in SCORE_BUCKET_ORDER}

            fig = go.Figure(
                go.Bar(
                    x=list(bucket_data.keys()),
                    y=list(bucket_data.values()),
                    marker_color="#4C8BFF",
                    text=list(bucket_data.values()),
                    textposition="outside",
                )
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#fafafa",
                margin=dict(l=10, r=10, t=10, b=30),
                xaxis_title="Score bucket",
                yaxis_title="Count",
                height=320,
                showlegend=False,
            )
            fig.update_xaxes(tickfont_color="#fafafa", gridcolor="#333")
            fig.update_yaxes(tickfont_color="#fafafa", gridcolor="#333")
            st.plotly_chart(fig, use_container_width=True)


# ─── Tab 2: All Opportunities ─────────────────────────────────────────────────

def tab_all_opportunities(opps, geo_filter, score_range):
    import pandas as pd

    st.header("All Opportunities")

    # Local filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("Search name or problem statement", placeholder="e.g. fintech, venezuela, SaaS…")
    with col2:
        all_geos = sorted(set(o.get("geography", "unknown") for o in opps))
        geo_multi = st.multiselect(
            "Geography",
            options=all_geos,
            default=[],
            placeholder="All geographies",
        )
    with col3:
        lane_options = ["now", "soon", "strategic", "no"]
        lane_multi = st.multiselect(
            "Portfolio lane",
            options=lane_options,
            default=[],
            placeholder="All lanes",
        )

    # Apply filters
    filtered = opps
    # Apply sidebar geo + score
    if geo_filter and geo_filter != "All":
        filtered = [o for o in filtered if (o.get("geography") or "").lower() == geo_filter.lower()]
    filtered = [o for o in filtered if score_range[0] <= float(o.get(SCORE_FIELD) or 0) <= score_range[1]]

    # Apply local filters
    if search:
        s = search.lower()
        filtered = [
            o for o in filtered
            if s in (o.get("name") or "").lower() or s in (o.get("problem_statement") or "").lower()
        ]
    if geo_multi:
        filtered = [o for o in filtered if o.get("geography") in geo_multi]
    if lane_multi:
        filtered = [o for o in filtered if o.get("portfolio_lane") in lane_multi]

    # Sort by score
    filtered = sorted(filtered, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)

    st.caption(f"Showing {len(filtered)} of {len(opps)} opportunities")

    if not filtered:
        st.info("No opportunities match the current filters.")
        return

    for o in filtered:
        score = float(o.get(SCORE_FIELD) or 0)
        lane = o.get("portfolio_lane") or "—"
        geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
        lane_color = LANE_COLORS.get(lane, "#888")

        label = f"**{o.get('name', '—')}** · {geo} · Score: `{score:.2f}` · Lane: `{lane}` · Stage: `{o.get('stage', '—')}`"

        with st.expander(label, expanded=False):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**Problem Statement**  \n{o.get('problem_statement', '—')}")
                st.markdown(f"**Target Customer**  \n{o.get('target_customer', '—')}")
                if o.get("path_to_first_revenue"):
                    st.markdown(f"**Path to First Revenue**  \n{o.get('path_to_first_revenue')}")
            with c2:
                st.markdown("**Dimension Scores**")
                dim_data = {
                    field.replace("_", " ").title(): o.get(field)
                    for field in DIMENSION_FIELDS
                    if o.get(field) is not None
                }
                if dim_data:
                    rows_dim = [{"Dimension": k, "Score": v} for k, v in dim_data.items()]
                    df_dim = pd.DataFrame(rows_dim)
                    st.dataframe(df_dim, use_container_width=True, hide_index=True)

            # Kill info
            if o.get("kill_decision"):
                st.error(f"KILLED — {', '.join(o.get('kill_reasons', [])) or 'No reason logged'}")
            elif o.get("kill_reasons"):
                st.warning(f"Kill signals: {', '.join(o.get('kill_reasons', []))}")

            # Scores summary
            st.markdown(
                f"**Attractiveness:** {o.get('attractiveness_score', '—')} · "
                f"**Executability:** {o.get('executability_score', '—')} · "
                f"**Strategic Value:** {o.get('strategic_value_score', '—')}"
            )

            if o.get("ai_scored_at"):
                st.caption(f"AI scored: {o.get('ai_scored_at')} · Venezuela lens: {'Yes' if o.get('venezuela_lens_applied') else 'No'}")


# ─── Tab 3: Pipeline Health ────────────────────────────────────────────────────

def tab_pipeline_health():
    import pandas as pd
    from collections import Counter

    st.header("Pipeline Health")

    runs = load_automation_runs()
    metrics_list = load_machine_metrics()
    failures = load_pipeline_failures()

    col1, col2 = st.columns(2)

    # ── Last 10 automation runs
    with col1:
        st.subheader("Last 10 Automation Runs")
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
                icon = "✅" if status == "completed" and exit_code == 0 else ("🔴" if exit_code and exit_code != 0 else "🔵")
                rows.append({
                    "": icon,
                    "Timestamp": ts,
                    "Status": status.capitalize(),
                    "Exit": exit_code if exit_code is not None else "—",
                    "Trigger": trigger,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Pipeline failures
    with col2:
        st.subheader("Pipeline Failures by Step")
        if not failures:
            st.success("No pipeline failures logged.")
        else:
            step_counts = Counter(f.get("step", "unknown") for f in failures)
            df_fail = pd.DataFrame(
                [{"Step": k, "Count": v} for k, v in step_counts.most_common()],
            )
            st.dataframe(df_fail, use_container_width=True, hide_index=True)

    st.divider()

    # ── Machine metrics table
    st.subheader("Machine Metrics History")
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # ── Score history chart (opps with multi-point history)
    st.subheader("Score History (Opportunities with Tracked History)")
    all_opps = load_opportunities()
    opps_with_history = [o for o in all_opps if o.get("score_history") and len(o["score_history"]) > 1]

    if not opps_with_history:
        st.info("No multi-point score history yet. History accumulates as the daily pipeline runs.")
    else:
        fig = go.Figure()
        for o in opps_with_history[:15]:  # limit to 15 lines for readability
            history = o["score_history"]
            dates = [h.get("date", "") for h in history]
            scores = [h.get("score", 0) for h in history]
            fig.add_trace(go.Scatter(
                x=dates,
                y=scores,
                mode="lines+markers",
                name=o.get("name", o.get("id", "—"))[:30],
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
        st.plotly_chart(fig, use_container_width=True)


# ─── Tab 4: Venezuela Focus ────────────────────────────────────────────────────

def tab_venezuela_focus(opps):
    import pandas as pd
    from collections import Counter

    st.header("Venezuela Focus")

    ve_opps = [o for o in opps if (o.get("geography") or "").lower() == "venezuela"]
    ve_opps_sorted = sorted(ve_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)

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

    # ── Wedge category breakdown
    with col1:
        st.subheader("Wedge Category Breakdown")
        wedge_counts = Counter(
            o.get("venezuela_wedge_category") or "unclassified"
            for o in ve_opps
        )
        df_wedge = pd.DataFrame(
            [{"Category": k, "Count": v} for k, v in wedge_counts.most_common()]
        )
        fig = go.Figure(
            go.Bar(
                y=df_wedge["Category"],
                x=df_wedge["Count"],
                orientation="h",
                marker_color="#f59e0b",
                text=df_wedge["Count"],
                textposition="outside",
            )
        )
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
        st.plotly_chart(fig, use_container_width=True)

    # ── Lane breakdown
    with col2:
        st.subheader("Lane Distribution")
        lane_counts = Counter(o.get("portfolio_lane") or "unknown" for o in ve_opps)
        labels = list(lane_counts.keys())
        values = list(lane_counts.values())
        colors = [LANE_COLORS.get(l, "#888") for l in labels]
        fig2 = go.Figure(
            go.Pie(
                labels=[l.capitalize() for l in labels],
                values=values,
                marker_colors=colors,
                hole=0.45,
                textinfo="label+percent",
            )
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#fafafa",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── VE opportunities table
    st.subheader("Venezuela Opportunities — Ranked")
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

    # ── Expandable detail per VE opp
    st.subheader("Detail")
    for o in ve_opps_sorted:
        score = float(o.get(SCORE_FIELD) or 0)
        with st.expander(f"{o.get('name', '—')} — {score:.2f}", expanded=False):
            st.markdown(f"**Problem:** {o.get('problem_statement', '—')}")
            st.markdown(f"**Target customer:** {o.get('target_customer', '—')}")
            if o.get("path_to_first_revenue"):
                st.markdown(f"**Path to first revenue:** {o.get('path_to_first_revenue')}")
            if o.get("trigger_signal"):
                st.markdown(f"**Trigger signal:** {o.get('trigger_signal')}")


# ─── Tab 5: Weekly Ritual ─────────────────────────────────────────────────────

def tab_weekly_ritual(opps, quotas):
    from datetime import datetime, timedelta
    import pandas as pd

    st.header("Weekly Ritual")

    active = [o for o in opps if not o.get("kill_decision", False)]
    sorted_opps = sorted(active, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)

    weekly_q = quotas.get("weekly_quotas", {})
    validation_target = weekly_q.get("validations_run", {}).get("target", 2)
    metrics_list = load_machine_metrics()

    # Count validations this week
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    validations_done = 0
    for m in metrics_list:
        if m.get("date", "") >= week_ago:
            validations_done += int(m.get("opportunities_validated_pass", 0) or 0)

    # ── Interview quota indicator
    quota_met = validations_done >= validation_target
    if quota_met:
        st.success(f"Validation quota met: {validations_done} / {validation_target} this week")
    else:
        st.error(f"Validation quota BEHIND: {validations_done} / {validation_target} this week — run validation-runner on top opps")

    st.divider()

    col1, col2 = st.columns(2)

    # ── Rising signals
    with col1:
        st.subheader("Rising Signals (score delta >= 0.5 in 7 days)")
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        rising = []
        for o in active:
            history = o.get("score_history") or []
            if len(history) >= 2:
                recent = [h for h in history if h.get("date", "") >= seven_days_ago]
                if recent:
                    delta = sum(h.get("delta", 0) for h in recent)
                    if delta >= 0.5:
                        rising.append((o, delta))
        rising.sort(key=lambda x: x[1], reverse=True)

        if not rising:
            st.info("No rising signals this week. All score_history entries are backfill (delta = 0).")
        else:
            for o, delta in rising[:10]:
                st.markdown(
                    f"- **{o.get('name', '—')}** — +{delta:.2f} · Score: `{float(o.get(SCORE_FIELD) or 0):.2f}`"
                )

    # ── Top 3 to validate
    with col2:
        st.subheader("Top 3 to Validate")
        not_in_validation = [
            o for o in sorted_opps
            if o.get("stage") not in ("validation", "validated", "killed")
        ]
        if not not_in_validation:
            st.info("All high-score opportunities are already in validation.")
        else:
            for o in not_in_validation[:3]:
                score = float(o.get(SCORE_FIELD) or 0)
                geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
                st.markdown(
                    f"- **{o.get('name', '—')}** — Score: `{score:.2f}` · {geo} · Lane: `{o.get('portfolio_lane', '—')}`"
                )
                if o.get("path_to_first_revenue"):
                    st.caption(f"  Path: {o.get('path_to_first_revenue')[:120]}…")

    st.divider()

    col3, col4 = st.columns(2)

    # ── Candidates to kill
    with col3:
        st.subheader("Candidates to Kill (score < 4.0)")
        kill_candidates = [
            o for o in active
            if float(o.get(SCORE_FIELD) or 0) < 4.0
        ]
        kill_candidates.sort(key=lambda o: float(o.get(SCORE_FIELD) or 0))

        if not kill_candidates:
            st.success("No low-score opportunities to kill.")
        else:
            for o in kill_candidates[:5]:
                score = float(o.get(SCORE_FIELD) or 0)
                st.markdown(
                    f"- **{o.get('name', '—')}** — Score: `{score:.2f}` · Stage: `{o.get('stage', '—')}`"
                )

    # ── Conviction area
    with col4:
        st.subheader("This Week's Conviction Area")
        # Use top VE opp name or top overall
        ve_opps = [o for o in sorted_opps if (o.get("geography") or "") == "venezuela"]
        if ve_opps:
            top_ve = ve_opps[0]
            conviction = (
                f"**Venezuela — {top_ve.get('name', '—')}**\n\n"
                f"{top_ve.get('problem_statement', '')[:200]}"
            )
            st.info(conviction)
        elif sorted_opps:
            top = sorted_opps[0]
            conviction = (
                f"**{GEO_LABELS.get(top.get('geography',''), top.get('geography',''))} — {top.get('name','—')}**\n\n"
                f"{top.get('problem_statement','')[:200]}"
            )
            st.info(conviction)
        else:
            st.info("No opportunities loaded yet.")

    st.divider()

    # ── Weekly summary stats
    st.subheader("Weekly Pipeline Summary (last 7 days)")
    if not metrics_list:
        st.info("No machine metrics yet.")
    else:
        recent_metrics = [m for m in metrics_list if m.get("date", "") >= week_ago]
        if not recent_metrics:
            st.info("No metrics recorded in the last 7 days.")
        else:
            totals = {
                "Signals ingested": sum(m.get("signals_ingested", 0) for m in recent_metrics),
                "Opportunities scored": sum(m.get("opportunities_scored", 0) for m in recent_metrics),
                "Killed": sum(m.get("opportunities_killed", 0) for m in recent_metrics),
                "Promoted to validation": sum(m.get("opportunities_promoted_to_validation", 0) for m in recent_metrics),
                "Validated (pass)": sum(m.get("opportunities_validated_pass", 0) for m in recent_metrics),
                "Deep dives": sum(m.get("deep_dives_produced", 0) for m in recent_metrics),
            }
            targets = {
                "Signals ingested": weekly_q.get("signals_ingested", {}).get("target", 40),
                "Opportunities scored": weekly_q.get("structured_opportunities", {}).get("target", 10),
                "Deep dives": weekly_q.get("deep_dives_produced", {}).get("target", 3),
                "Promoted to validation": weekly_q.get("validations_run", {}).get("target", 2),
            }

            cols = st.columns(len(totals))
            for col, (label, value) in zip(cols, totals.items()):
                target = targets.get(label)
                if target:
                    delta = value - target
                    col.metric(label, value, delta=f"{delta:+d} vs target", delta_color="normal" if delta >= 0 else "inverse")
                else:
                    col.metric(label, value)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    # Load data
    all_opps = load_opportunities()
    runs = load_automation_runs()
    quotas = load_weekly_quotas()

    # Sidebar (returns active filters)
    geo_filter, score_range = render_sidebar(runs)

    # Apply sidebar filters for tabs that need them
    filtered_opps = apply_filters(all_opps, geo_filter, score_range[0], score_range[1])

    # Tabs
    tabs = st.tabs([
        "Command Center",
        "All Opportunities",
        "Pipeline Health",
        "Venezuela Focus",
        "Weekly Ritual",
    ])

    with tabs[0]:
        tab_command_center(all_opps, filtered_opps, quotas)

    with tabs[1]:
        tab_all_opportunities(all_opps, geo_filter, score_range)

    with tabs[2]:
        tab_pipeline_health()

    with tabs[3]:
        # Venezuela tab uses sidebar score filter but ignores geo filter (always shows VE)
        ve_filtered = [
            o for o in all_opps
            if (o.get("geography") or "").lower() == "venezuela"
            and score_range[0] <= float(o.get(SCORE_FIELD) or 0) <= score_range[1]
        ]
        tab_venezuela_focus(ve_filtered if (geo_filter == "All" or geo_filter.lower() == "venezuela") else ve_filtered)

    with tabs[4]:
        tab_weekly_ritual(all_opps, quotas)


if __name__ == "__main__" or True:
    main()
