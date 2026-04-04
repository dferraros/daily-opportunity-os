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

# ─── Custom CSS — Intelligence Terminal Aesthetic ─────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #060A10;
    --card: #0D1420;
    --amber: #F59E0B;
    --cyan: #22D3EE;
    --green: #10B981;
    --red: #EF4444;
    --muted: #4B5563;
    --text: #C9D1D9;
    --text-dim: #6B7280;
}

.stApp {
    background: var(--bg) !important;
    background-image:
        linear-gradient(rgba(245,158,11,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(245,158,11,0.03) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em !important;
    color: #F8FAFC !important;
}

/* Tab nav */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(245,158,11,0.2) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    padding: 12px 20px !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border-left: 3px solid var(--amber) !important;
    border-radius: 4px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 28px !important;
    color: #F8FAFC !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(245,158,11,0.15) !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(245,158,11,0.08) !important;
    color: var(--amber) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* Expanders */
[data-testid="stExpander"] {
    border: none !important;
    border-left: 3px solid rgba(245,158,11,0.3) !important;
    background: var(--card) !important;
    border-radius: 0 4px 4px 0 !important;
    margin-bottom: 6px !important;
}
[data-testid="stExpander"]:hover {
    border-left-color: var(--amber) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080C16 !important;
    border-right: 1px solid rgba(245,158,11,0.1) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    color: var(--amber) !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(245,158,11,0.2) !important;
    border-color: var(--amber) !important;
}

/* Select, slider */
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div {
    background: var(--card) !important;
    border-color: rgba(245,158,11,0.2) !important;
}

/* Divider */
hr {
    border-color: rgba(245,158,11,0.1) !important;
}

/* Alert boxes */
[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.1) !important;
    border-color: #10B981 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stError"] {
    background: rgba(239,68,68,0.1) !important;
    border-color: #EF4444 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stInfo"] {
    background: rgba(34,211,238,0.07) !important;
    border-color: #22D3EE !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(245,158,11,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--amber); }

/* Caption */
[data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    color: var(--text-dim) !important;
}

/* Text input */
[data-testid="stTextInput"] input {
    background: var(--card) !important;
    border-color: rgba(245,158,11,0.2) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px #F59E0B; }
    50% { opacity: 0.4; box-shadow: 0 0 3px #F59E0B; }
}
</style>
"""

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


def hero_card(o: dict, rank: int) -> str:
    """Render a top-opportunity hero card as HTML."""
    score = float(o.get(SCORE_FIELD) or 0)
    lane = o.get("portfolio_lane") or "—"
    geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
    name = o.get("name", "—")
    problem = (o.get("problem_statement") or "")[:180]
    tam = o.get("tam_usd_estimate") or o.get("tam")
    tam_str = f"${float(tam)/1e6:.0f}M" if tam else "—"
    bucket = (o.get("bucket") or "—").replace("_", " ").upper()
    archetype = (o.get("benchmark_archetype") or "—").replace("_", " ").title()
    wedge = o.get("daniels_wedge_score")

    lane_color = LANE_COLORS.get(lane, "#888")
    score_color = "#22D3EE" if score >= 9 else "#F59E0B" if score >= 7 else "#6B7280"

    rank_labels = {1: "01", 2: "02", 3: "03"}
    rank_str = rank_labels.get(rank, f"{rank:02d}")

    return f"""
<div style="background:#0D1420;border:1px solid rgba(245,158,11,0.12);border-left:3px solid {lane_color};
     border-radius:6px;padding:20px 24px;margin-bottom:12px;position:relative;overflow:hidden">
  <div style="position:absolute;top:16px;right:20px;
       font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;
       color:{score_color};line-height:1">{score:.1f}</div>
  <div style="position:absolute;top:20px;right:22px;margin-top:40px;
       font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B7280;letter-spacing:1px">/10</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#6B7280;
       letter-spacing:3px;text-transform:uppercase;margin-bottom:6px">#{rank_str} · {geo}</div>
  <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:600;
       color:#F8FAFC;margin-bottom:10px;max-width:75%">{name}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#9CA3AF;
       line-height:1.6;margin-bottom:14px;max-width:80%">{problem}</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B7280">
      TAM <span style="color:#F59E0B">{tam_str}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B7280">
      LANE <span style="color:{lane_color}">{lane.upper()}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B7280">
      BUCKET <span style="color:#C9D1D9">{bucket}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B7280">
      ARCHETYPE <span style="color:#C9D1D9">{archetype}</span>
    </span>
    {f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280">WEDGES <span style="color:#22D3EE">{wedge}/6</span></span>' if wedge is not None else ''}
  </div>
</div>"""


def radar_chart(o: dict):
    """Return a Plotly radar chart for the opportunity's 8 key dimensions."""
    dims = [
        ("Pain", "pain_severity"),
        ("Market", "market_size"),
        ("WTP", "willingness_to_pay"),
        ("Speed", "speed_to_mvp"),
        ("Capital", "capital_efficiency"),
        ("Distribution", "distribution_accessibility"),
        ("Regional Fit", "regional_fit"),
        ("Founder Fit", "founder_fit"),
    ]
    labels = [d[0] for d in dims]
    values = [float(o.get(d[1]) or 5) for d in dims]
    # Close the polygon
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(245,158,11,0.12)",
        line=dict(color="#F59E0B", width=1.5),
        mode="lines+markers",
        marker=dict(color="#F59E0B", size=5),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 10],
                tickfont=dict(size=8, color="#6B7280"),
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.08)",
            ),
            angularaxis=dict(
                tickfont=dict(size=9, color="#9CA3AF", family="JetBrains Mono"),
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.08)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=260,
        showlegend=False,
    )
    return fig


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


def metric_card(label, value, delta_text=None, delta_ok=True, accent="#F59E0B"):
    """Render a styled metric card as HTML for the intelligence terminal UI."""
    delta_html = ""
    if delta_text:
        color = "#10B981" if delta_ok else "#EF4444"
        delta_html = (
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:{color};margin-top:4px">{delta_text}</div>'
        )
    return (
        f'<div style="background:#0D1420;border-left:3px solid {accent};'
        f'border-radius:4px;padding:16px 20px;margin:4px 0">'
        f'<div style="font-family:Syne,sans-serif;font-size:11px;color:#6B7280;'
        f'text-transform:uppercase;letter-spacing:2px;margin-bottom:8px">{label}</div>'
        f'<div style="font-family:JetBrains Mono,monospace;font-size:28px;'
        f'font-weight:500;color:#F8FAFC">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )


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
                        ["uv", "run", "--no-sync", "opp-os", "daily"],
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
    st.markdown("""
<div style="display:flex;align-items:center;gap:16px;padding:8px 0 24px 0;border-bottom:1px solid rgba(245,158,11,0.2);margin-bottom:24px">
  <div style="width:10px;height:10px;background:#F59E0B;border-radius:50%;box-shadow:0 0 8px #F59E0B;animation:pulse 2s infinite"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#F59E0B;letter-spacing:3px;text-transform:uppercase">OPPORTUNITY OS v1 &middot; LIVE &middot; {today}</span>
</div>
""".format(today=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
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
        st.markdown(metric_card("Total Opportunities", len(active_opps)), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Top Score", f"{top_score:.2f}", accent="#22D3EE"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("VE Opportunities", len(ve_opps), accent="#F59E0B"), unsafe_allow_html=True)
    with c4:
        delta_ok = recent_validations >= interview_target
        st.markdown(metric_card(
            "Validation Quota (7d)",
            f"{recent_validations} / {interview_target}",
            delta_text="ON TRACK" if delta_ok else "BEHIND TARGET",
            delta_ok=delta_ok,
        ), unsafe_allow_html=True)

    st.divider()

    # ── Top 3 hero cards
    if active_opps:
        sorted_opps = sorted(active_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;'
            'letter-spacing:3px;text-transform:uppercase;margin-bottom:12px">Top Opportunities</div>',
            unsafe_allow_html=True,
        )
        for rank, o in enumerate(sorted_opps[:3], 1):
            st.markdown(hero_card(o, rank), unsafe_allow_html=True)

    st.divider()

    # ── Table + charts
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("Full Ranking")
        if not active_opps:
            st.info("No opportunities match current filters.")
        else:
            import pandas as pd
            top10 = sorted_opps[:10]
            rows = []
            for rank, o in enumerate(top10, 1):
                tam = o.get("tam_usd_estimate") or o.get("tam")
                tam_str = f"${float(tam)/1e6:.0f}M" if tam else "—"
                rows.append({
                    "#": rank,
                    "Name": (o.get("name", "—") or "—")[:40],
                    "Geo": GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—")),
                    "Score": round(float(o.get(SCORE_FIELD) or 0), 2),
                    "TAM": tam_str,
                    "Lane": (o.get("portfolio_lane") or "—").capitalize(),
                    "Wedge": str(o.get("daniels_wedge_score") or "—"),
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
            from collections import Counter

            # Geo donut
            geo_counts = Counter(GEO_LABELS.get(o.get("geography", ""), "Other") for o in active_opps)
            geo_colors = ["#F59E0B", "#22D3EE", "#10B981", "#A855F7", "#EF4444", "#6B7280"]
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
            st.plotly_chart(fig_geo, width="stretch")

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
            st.plotly_chart(fig_lane, width="stretch")


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
                    st.markdown(f"**Path to First Revenue**  \n{str(o.get('path_to_first_revenue'))}")
                if o.get("first_10_customer_path"):
                    st.markdown(f"**First 10 Customers**  \n{str(o.get('first_10_customer_path'))[:300]}")
                if o.get("exact_customer_phrases"):
                    phrases = o.get("exact_customer_phrases")
                    if isinstance(phrases, list):
                        st.markdown("**Customer Language**")
                        for p in phrases[:3]:
                            st.markdown(f"> *{p}*")

                # TAM section
                tam = o.get("tam_usd_estimate") or o.get("tam")
                sam = o.get("sam_usd_estimate")
                som = o.get("som_usd_estimate")
                if tam:
                    tam_str = f"${float(tam)/1e6:.0f}M"
                    sam_str = f"${float(sam)/1e6:.0f}M" if sam else "—"
                    som_str = f"${float(som)/1e6:.0f}M" if som else "—"
                    st.markdown(f"**TAM / SAM / SOM:** {tam_str} / {sam_str} / {som_str}")
                    if o.get("tam_rationale"):
                        st.caption(str(o.get("tam_rationale"))[:200])

            with c2:
                # Intelligence scores
                st.markdown("**Intelligence**")
                intel = {
                    "Thesis Fit": o.get("thesis_fit_score"),
                    "Daniel Wedges": f"{o.get('daniels_wedge_score')}/6" if o.get('daniels_wedge_score') is not None else None,
                    "Archetype": (o.get("benchmark_archetype") or "").replace("_", " ").title() or None,
                    "Bucket": (o.get("bucket") or "").replace("_", " ").title() or None,
                    "VE Wedge": (o.get("venezuela_wedge_category") or "").replace("_", " ").title() or None,
                }
                for k, v in intel.items():
                    if v is not None:
                        st.caption(f"{k}: **{v}**")

                has_dims = any(o.get(f) for f in DIMENSION_FIELDS)
                if has_dims:
                    st.plotly_chart(radar_chart(o), width="stretch")

            # Distribution channels
            channels = o.get("top_distribution_channels")
            if channels:
                if isinstance(channels, list):
                    st.caption("Distribution: " + " · ".join(str(c) for c in channels[:3]))
                else:
                    st.caption(f"Distribution: {str(channels)[:150]}")

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
                    "Exit": str(exit_code) if exit_code is not None else "—",
                    "Trigger": trigger,
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

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
            st.dataframe(df_fail, width="stretch", hide_index=True)

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
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

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
        st.plotly_chart(fig, width="stretch")


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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig2, width="stretch")

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
        width="stretch",
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
                    st.caption(f"  Path: {str(o.get('path_to_first_revenue'))[:120]}…")

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


# ─── Tab 6: Deep Dive (On-Demand Validation + Research) ──────────────────────

def _run_subprocess(cmd: list, label: str) -> tuple[bool, str]:
    """Run a subprocess command, return (success, output_text)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )
        output = (result.stdout or "") + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"{label} timed out after 5 minutes."
    except Exception as e:
        return False, f"Could not run {label}: {e}"


def _load_validation_report(opp_id: str) -> str | None:
    """Find the most recent validation markdown for this opp_id."""
    val_dir = PROJECT_ROOT / "reports" / "validation"
    if not val_dir.exists():
        return None
    # Find files matching the opp_id (may have date prefix)
    matches = sorted(val_dir.glob(f"*{opp_id[:20]}*-validation.md"), reverse=True)
    if not matches:
        # Fall back: any file containing the opp_id
        matches = sorted(val_dir.glob("*-validation.md"), reverse=True)
        matches = [m for m in matches if opp_id[:16] in m.name]
    if matches:
        try:
            return matches[0].read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def tab_deep_dive(opps: list):
    st.header("Deep Dive")
    st.caption("Select an opportunity and run automated validation + research expansion on-demand.")

    active_opps = [o for o in opps if not o.get("kill_decision", False)]
    if not active_opps:
        st.info("No opportunities loaded. Run the daily pipeline first.")
        return

    sorted_opps = sorted(active_opps, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True)

    # ── Opportunity selector
    opp_labels = [
        f"[{float(o.get(SCORE_FIELD) or 0):.1f}] {o.get('name', '—')[:60]}  ·  {(o.get('geography') or '').upper()}"
        for o in sorted_opps
    ]
    selected_idx = st.selectbox(
        "Select opportunity",
        options=range(len(sorted_opps)),
        format_func=lambda i: opp_labels[i],
        index=0,
        key="deep_dive_selector",
    )

    o = sorted_opps[selected_idx]
    opp_id = o.get("id", "")
    opp_name = o.get("name", "—")

    # ── Selected opportunity summary card
    st.markdown(hero_card(o, selected_idx + 1), unsafe_allow_html=True)

    col_val, col_res = st.columns(2)

    # ── Run Validation button
    with col_val:
        stage = o.get("stage") or "scout"
        stage_color = {"validation": "#F59E0B", "validated": "#10B981", "killed": "#EF4444"}.get(stage, "#6B7280")
        st.markdown(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:{stage_color}">Current stage: {stage.upper()}</span>',
            unsafe_allow_html=True,
        )

        run_val = st.button(
            "▶ Run Validation Package",
            key="btn_run_validation",
            use_container_width=True,
            help="Runs the full 8-section validation package for this opportunity",
        )

        if run_val:
            if not opp_id:
                st.error("Opportunity has no ID — cannot run validation.")
            else:
                with st.spinner(f"Running validation for: {opp_name[:40]}…"):
                    ok, out = _run_subprocess(
                        ["uv", "run", "--no-sync", "opp-os", "validate", opp_id],
                        "Validation",
                    )
                    st.session_state[f"val_result_{selected_idx}"] = (ok, out)
                    st.cache_data.clear()

        # Show validation result / existing report
        if f"val_result_{selected_idx}" in st.session_state:
            ok, out = st.session_state[f"val_result_{selected_idx}"]
            if ok:
                st.success("Validation completed.")
            else:
                st.warning("Validation run had errors — see output below.")
            with st.expander("▸ Run output", expanded=False):
                st.code(out[-3000:], language="text")

        # Show existing validation report
        val_md = _load_validation_report(opp_id)
        if val_md:
            with st.expander("▸ Latest validation report", expanded=True):
                st.markdown(val_md[:6000])
        else:
            st.caption("No validation report found. Run validation above to generate one.")

    # ── Expand Research button
    with col_res:
        research_fields = ["pain_validation_score", "exact_customer_phrases", "first_10_customer_path", "distribution_validated"]
        has_research = any(o.get(f) for f in research_fields)
        res_label = "✓ Research enriched" if has_research else "○ No research yet"
        res_color = "#10B981" if has_research else "#6B7280"
        st.markdown(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:{res_color}">{res_label}</span>',
            unsafe_allow_html=True,
        )

        run_res = st.button(
            "▶ Expand Research (Pain + Distribution)",
            key="btn_run_research",
            use_container_width=True,
            help="Runs combined pain + distribution research (1 API call, 1 web search)",
        )

        if run_res:
            if not opp_id:
                st.error("Opportunity has no ID.")
            else:
                with st.spinner(f"Running research for: {opp_name[:40]}…"):
                    ok, out = _run_subprocess(
                        ["uv", "run", "--no-sync", "opp-os", "research", opp_id],
                        "Research",
                    )
                    st.session_state[f"res_result_{selected_idx}"] = (ok, out)
                    st.cache_data.clear()

        if f"res_result_{selected_idx}" in st.session_state:
            ok, out = st.session_state[f"res_result_{selected_idx}"]
            if ok:
                st.success("Research complete — reload to see updated fields.")
            else:
                st.warning("Research had errors.")
            with st.expander("▸ Run output", expanded=False):
                st.code(out[-3000:], language="text")

        # Show current research data inline
        if has_research:
            with st.expander("▸ Current research data", expanded=True):
                pvs = o.get("pain_validation_score")
                if pvs is not None:
                    st.metric("Pain Validation Score", f"{float(pvs):.1f} / 10")

                phrases = o.get("exact_customer_phrases")
                if phrases:
                    st.markdown("**Customer phrases:**")
                    for p in (phrases if isinstance(phrases, list) else [phrases])[:3]:
                        st.markdown(f"> *{p}*")

                workarounds = o.get("workarounds_found")
                if workarounds:
                    st.markdown("**Current workarounds:**")
                    for w in (workarounds if isinstance(workarounds, list) else [workarounds])[:3]:
                        st.markdown(f"- {w}")

                dist_ok = o.get("distribution_validated")
                if dist_ok is not None:
                    st.markdown(f"**Distribution validated:** {'Yes' if dist_ok else 'No'}")

                channels = o.get("top_distribution_channels")
                if channels:
                    ch_list = channels if isinstance(channels, list) else [channels]
                    st.markdown("**Top channels:** " + " · ".join(str(c) for c in ch_list[:3]))

                cac = o.get("estimated_cac_logic")
                if cac:
                    st.caption(f"CAC logic: {cac}")

                path10 = o.get("first_10_customer_path")
                if path10:
                    st.markdown(f"**First 10 customers:** {str(path10)[:300]}")

                trust = o.get("trust_mechanism_latam")
                if trust:
                    st.caption(f"Trust mechanism: {trust}")
        else:
            st.caption("No research data yet. Run 'Expand Research' above.")

    st.divider()

    # ── Radar chart + full field dump
    col_chart, col_fields = st.columns([1, 1])
    with col_chart:
        has_dims = any(o.get(f) for f in DIMENSION_FIELDS)
        if has_dims:
            st.markdown("**Dimension Radar**")
            st.plotly_chart(radar_chart(o), width="stretch")

    with col_fields:
        st.markdown("**All Scored Fields**")
        scored = {
            k: v for k, v in o.items()
            if isinstance(v, (int, float)) and k not in ("id",) and v is not None
        }
        for k, v in sorted(scored.items()):
            st.caption(f"{k.replace('_', ' ').title()}: **{v}**")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    # Inject intelligence terminal CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
        "Deep Dive",
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

    with tabs[5]:
        tab_deep_dive(all_opps)


if __name__ == "__main__" or True:
    main()
