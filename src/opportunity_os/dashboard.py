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
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — Intelligence Terminal Aesthetic ─────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #09090B;
    --surface: #18181B;
    --surface-2: #27272A;
    --border: rgba(255,255,255,0.06);
    --border-strong: rgba(255,255,255,0.10);
    --blue: #3B82F6;
    --blue-dim: rgba(59,130,246,0.10);
    --green: #22C55E;
    --red: #EF4444;
    --amber: #F59E0B;
    --text: #F4F4F5;
    --text-muted: #A1A1AA;
    --text-dim: #52525B;
}

/* ── Hide Streamlit chrome ── */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    color: var(--text-muted) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
}

/* ── App shell ── */
.stApp {
    background: var(--bg) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.025em !important;
    color: var(--text) !important;
}

/* Apply font only to actual text elements, not Streamlit internals */
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stText, .stCaption,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stExpander"] summary p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Expander icon spans must NEVER get font overridden — the icon glyph only exists
   in Streamlit's internal icon font; overriding renders the raw text "_arrowRight" */
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] details > summary > span:first-child {
    font-family: inherit !important;
    font-size: inherit !important;
}

/* ── Tab nav ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em !important;
    text-transform: none !important;
    color: var(--text-dim) !important;
    padding: 10px 20px !important;
    background: transparent !important;
    border: none !important;
    transition: color 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-muted) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--blue) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--blue) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
}
[data-testid="metric-container"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 500 !important;
    color: var(--text) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stDataFrame"] th {
    background: var(--surface-2) !important;
    color: var(--text-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-strong) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
    margin-bottom: 6px !important;
    transition: border-color 0.15s ease !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-strong) !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    padding: 12px 16px !important;
}
/* Only the label text paragraph gets our custom font */
[data-testid="stExpander"] summary p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0C0C0E !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stWidgetLabel > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: var(--blue-dim) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    color: var(--blue) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 9px 0 !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.18) !important;
    border-color: var(--blue) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--blue) !important;
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: var(--text-dim) !important;
    font-size: 10px !important;
}

/* ── Global inputs ── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--surface) !important;
    border-color: var(--border-strong) !important;
}

[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

/* ── Alerts ── */
hr { border-color: var(--border) !important; }

[data-testid="stSuccess"] {
    background: rgba(34,197,94,0.07) !important;
    border-color: rgba(34,197,94,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stError"] {
    background: rgba(239,68,68,0.07) !important;
    border-color: rgba(239,68,68,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stInfo"] {
    background: var(--blue-dim) !important;
    border-color: rgba(59,130,246,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stWarning"] {
    background: rgba(245,158,11,0.07) !important;
    border-color: rgba(245,158,11,0.3) !important;
    border-radius: 6px !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-dim) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface-2); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }

/* ── Main content ── */
.stMainBlockContainer, [data-testid="stMainBlockContainer"],
section[data-testid="stMain"] > div:first-child {
    padding-top: 0px !important;
    padding-left: 32px !important;
    padding-right: 32px !important;
}

/* Small top clearance for the toolbar */
.stApp > section[data-testid="stMain"] {
    padding-top: 10px !important;
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
    score_color = "#3B82F6" if score >= 9 else "#F59E0B" if score >= 7 else "#71717A"

    rank_labels = {1: "01", 2: "02", 3: "03"}
    rank_str = rank_labels.get(rank, f"{rank:02d}")

    return f"""
<div style="background:#18181B;border:1px solid rgba(255,255,255,0.06);border-left:3px solid {lane_color};
     border-radius:8px;padding:20px 24px;margin-bottom:10px;position:relative;overflow:hidden">
  <div style="position:absolute;top:16px;right:20px;
       font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:600;
       color:{score_color};line-height:1">{score:.1f}</div>
  <div style="position:absolute;top:20px;right:22px;margin-top:40px;
       font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;letter-spacing:1px">/10</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;
       letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px">#{rank_str} · {geo}</div>
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:600;
       color:#F4F4F5;margin-bottom:8px;max-width:75%;letter-spacing:-0.01em">{name}</div>
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#A1A1AA;
       line-height:1.6;margin-bottom:14px;max-width:80%">{problem}</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
      TAM <span style="color:#3B82F6">{tam_str}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
      LANE <span style="color:{lane_color}">{lane.upper()}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
      BUCKET <span style="color:#A1A1AA">{bucket}</span>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
      ARCHETYPE <span style="color:#A1A1AA">{archetype}</span>
    </span>
    {f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">WEDGES <span style="color:#3B82F6">{wedge}/6</span></span>' if wedge is not None else ''}
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
        fillcolor="rgba(59,130,246,0.10)",
        line=dict(color="#3B82F6", width=1.5),
        mode="lines+markers",
        marker=dict(color="#3B82F6", size=4),
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


def score_gauge(value: float, title: str, max_val: float = 10.0):
    """Plotly gauge chart for a score value (pain, timing, etc)."""
    color = "#3B82F6" if value >= 8 else "#F59E0B" if value >= 6 else "#EF4444" if value < 4 else "#71717A"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"font": {"family": "JetBrains Mono", "color": color, "size": 24}, "suffix": "/10"},
        gauge={
            "axis": {
                "range": [0, max_val],
                "tickfont": {"size": 8, "color": "#52525B", "family": "JetBrains Mono"},
                "tickcolor": "#52525B",
            },
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 4], "color": "rgba(239,68,68,0.07)"},
                {"range": [4, 7], "color": "rgba(245,158,11,0.06)"},
                {"range": [7, 10], "color": "rgba(59,130,246,0.07)"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.8, "value": value},
        },
        title={"text": title, "font": {"family": "JetBrains Mono", "size": 9, "color": "#4B5563"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=5),
        height=160,
    )
    return fig


def tam_funnel_chart(tam: float, sam: float | None, som: float | None):
    """TAM → SAM → SOM bar chart."""
    def fmt(v):
        if v >= 1e9:
            return f"${v/1e9:.1f}B"
        if v >= 1e6:
            return f"${v/1e6:.0f}M"
        return f"${v/1e3:.0f}K"

    _sam = sam if sam else tam * 0.12
    _som = som if som else _sam * 0.18
    labels = ["TAM", "SAM", "SOM"]
    values = [tam, _sam, _som]
    colors = ["rgba(59,130,246,0.85)", "rgba(34,197,94,0.6)", "rgba(245,158,11,0.55)"]
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[fmt(v) for v in values],
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
    return fig


def score_breakdown_chart(o: dict):
    """Horizontal bars for each scored dimension."""
    dims = [
        ("Pain", "pain_severity"),
        ("Market Size", "market_size"),
        ("Timing", "timing_tailwind"),
        ("WTP", "willingness_to_pay"),
        ("Monetization", "monetization_clarity"),
        ("Speed to MVP", "speed_to_mvp"),
        ("Capital Eff.", "capital_efficiency"),
        ("Distribution", "distribution_accessibility"),
        ("Competition", "competition_intensity"),
        ("Defensibility", "defensibility"),
        ("Regional Fit", "regional_fit"),
        ("Founder Fit", "founder_fit"),
    ]
    labels, values = [], []
    for label, field in dims:
        v = o.get(field)
        if v is not None:
            labels.append(label)
            values.append(float(v))
    if not labels:
        return None
    colors = [
        "#3B82F6" if v >= 8 else "#F59E0B" if v >= 6 else "#EF4444" if v < 4 else "#71717A"
        for v in values
    ]
    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v:.0f}" for v in values],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color="#9CA3AF"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=36, t=4, b=4),
        height=max(200, len(labels) * 26),
        showlegend=False,
        xaxis=dict(range=[0, 11], visible=False),
        yaxis=dict(
            tickfont=dict(family="JetBrains Mono", size=10, color="#9CA3AF"),
            autorange="reversed",
            gridcolor="rgba(255,255,255,0.04)",
        ),
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


def metric_card(label, value, delta_text=None, delta_ok=True, accent="#3B82F6"):
    """Render a styled metric card as HTML."""
    delta_html = ""
    if delta_text:
        color = "#22C55E" if delta_ok else "#EF4444"
        delta_html = (
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:{color};margin-top:4px">{delta_text}</div>'
        )
    return (
        f'<div style="background:#18181B;border:1px solid rgba(255,255,255,0.06);'
        f'border-top:2px solid {accent};'
        f'border-radius:8px;padding:16px 20px;margin:4px 0">'
        f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B;'
        f'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px">{label}</div>'
        f'<div style="font-family:JetBrains Mono,monospace;font-size:26px;'
        f'font-weight:500;color:#F4F4F5">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )


def section_header(title: str, subtitle: str = "") -> str:
    """Render a styled section header."""
    sub = (
        f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:13px;'
        f'color:#71717A;margin-top:4px">{subtitle}</div>'
        if subtitle else ""
    )
    return (
        f'<div style="margin:0 0 20px 0;padding-bottom:16px;'
        f'border-bottom:1px solid rgba(255,255,255,0.06)">'
        f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:18px;'
        f'font-weight:600;letter-spacing:-0.025em;color:#F4F4F5;margin-bottom:4px">'
        f'{title}</div>'
        f'{sub}'
        f'</div>'
    )


def subsection(title: str) -> str:
    """Render a styled subsection label."""
    return (
        f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;'
        f'color:#52525B;letter-spacing:0.07em;text-transform:uppercase;'
        f'margin:20px 0 10px 0;padding-left:10px;'
        f'border-left:2px solid rgba(59,130,246,0.4)">{title}</div>'
    )


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar(runs):
    with st.sidebar:
        last_ts = get_last_run_ts(runs)

        # Header block
        st.markdown(f"""
<div style="padding:20px 16px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;font-weight:700;
       color:#F4F4F5;letter-spacing:-0.01em;margin-bottom:4px">
    Opportunity OS
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;
       letter-spacing:0.04em">
    {fmt_ts(last_ts)}
  </div>
</div>
""", unsafe_allow_html=True)

        # Actions section
        st.markdown('<div style="padding:0 4px;font-family:JetBrains Mono,monospace;font-size:8px;color:#1F2937;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">ACTIONS</div>', unsafe_allow_html=True)

        if st.button("▶  Run Daily Pipeline"):
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
                        st.success("Pipeline complete.")
                        st.cache_data.clear()
                    else:
                        st.error(f"Pipeline failed (exit {result.returncode})")
                        if result.stderr:
                            st.code(result.stderr[-2000:], language="text")
                except subprocess.TimeoutExpired:
                    st.error("Timed out after 5 min.")
                except Exception as e:
                    st.error(f"Error: {e}")

        auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
        if auto_refresh:
            # Non-blocking: browser-level page reload every 30s
            st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

        # Filters section
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:0 4px;font-family:JetBrains Mono,monospace;font-size:10px;color:#3F3F46;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:8px;border-top:1px solid rgba(255,255,255,0.05);padding-top:16px">Filters</div>', unsafe_allow_html=True)

        geo_options = ["All", "Global", "LATAM", "Venezuela", "Spain", "US", "Other"]
        geo_filter = st.selectbox("Geography", geo_options, index=0, label_visibility="visible")

        score_range = st.slider(
            "Score range",
            min_value=0.0,
            max_value=10.0,
            value=(0.0, 10.0),
            step=0.1,
        )

        # Footer
        st.markdown('<div style="position:absolute;bottom:16px;left:16px;font-family:JetBrains Mono,monospace;font-size:8px;color:#1F2937;letter-spacing:1px">OPP-OS v1 · STREAMLIT</div>', unsafe_allow_html=True)

    return geo_filter, score_range


# ─── Tab 1: Command Center ────────────────────────────────────────────────────

def tab_command_center(opps, filtered_opps, quotas):
    st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:8px 0 20px 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:24px">
  <div style="width:7px;height:7px;background:#22C55E;border-radius:50%;box-shadow:0 0 0 2px rgba(34,197,94,0.2)"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#52525B;letter-spacing:0.05em">Live · {today}</span>
</div>
""".format(today=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
    st.markdown(section_header("Command Center"), unsafe_allow_html=True)

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
        st.markdown(subsection("Full Ranking"), unsafe_allow_html=True)
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


# ─── Tab 2: All Opportunities ─────────────────────────────────────────────────

def tab_all_opportunities(opps, geo_filter, score_range):
    import pandas as pd

    st.markdown(section_header("All Opportunities"), unsafe_allow_html=True)

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

    for opp_idx, o in enumerate(filtered):
        score = float(o.get(SCORE_FIELD) or 0)
        lane = o.get("portfolio_lane") or "—"
        geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
        lane_color = LANE_COLORS.get(lane, "#888")

        label = f"{o.get('name', '—')}  ·  {geo}  ·  {score:.2f}/10  ·  {lane}  ·  {o.get('stage', 'scout')}"

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
                    st.plotly_chart(radar_chart(o), width="stretch", key=f"radar_all_{opp_idx}")

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

            # Cross-tab deep dive button
            st.markdown("---")
            btn_col, hint_col = st.columns([1, 3])
            with btn_col:
                if st.button("📊 → Super Deep Dive", key=f"goto_dd_{opp_idx}", use_container_width=True):
                    st.session_state["deep_dive_opp_name"] = o.get("name")
                    st.session_state["active_tab_hint"] = True
            with hint_col:
                if st.session_state.get("active_tab_hint") and st.session_state.get("deep_dive_opp_name") == o.get("name"):
                    st.info("↑ Switch to the **Deep Dive** tab above to see the full intelligence brief.")


# ─── Tab 3: Pipeline Health ────────────────────────────────────────────────────

def tab_pipeline_health():
    import pandas as pd
    from collections import Counter

    st.markdown(section_header("Pipeline Health"), unsafe_allow_html=True)

    runs = load_automation_runs()
    metrics_list = load_machine_metrics()
    failures = load_pipeline_failures()

    col1, col2 = st.columns(2)

    # ── Last 10 automation runs
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

    # ── Machine metrics table
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

    # ── Score history chart (opps with multi-point history)
    st.markdown(subsection("Score History"), unsafe_allow_html=True)
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
        st.plotly_chart(fig, width="stretch", key="pipeline_score_hist")


# ─── Tab 4: Venezuela Focus ────────────────────────────────────────────────────

def tab_venezuela_focus(opps):
    import pandas as pd
    from collections import Counter

    st.markdown(section_header("Venezuela Focus"), unsafe_allow_html=True)

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
        st.markdown(subsection("Wedge Category Breakdown"), unsafe_allow_html=True)
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
        st.plotly_chart(fig, width="stretch", key="ve_wedge_bar")

    # ── Lane breakdown
    with col2:
        st.markdown(subsection("Lane Distribution"), unsafe_allow_html=True)
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
        st.plotly_chart(fig2, width="stretch", key="ve_lane_pie")

    st.divider()

    # ── VE opportunities table
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
        width="stretch",
        hide_index=True,
        column_config={
            "Score": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    # ── Expandable detail per VE opp
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


# ─── Tab 5: Weekly Ritual ─────────────────────────────────────────────────────

def tab_weekly_ritual(opps, quotas):
    from datetime import datetime, timedelta
    import pandas as pd

    st.markdown(section_header("Weekly Ritual"), unsafe_allow_html=True)

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
        st.markdown(subsection("Rising Signals"), unsafe_allow_html=True)
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
        st.markdown(subsection("Top 3 to Validate"), unsafe_allow_html=True)
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
        st.markdown(subsection("Candidates to Kill (score < 4.0)"), unsafe_allow_html=True)
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
        st.markdown(subsection("This Week's Conviction Area"), unsafe_allow_html=True)
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
    st.markdown(subsection("Weekly Pipeline Summary (last 7 days)"), unsafe_allow_html=True)
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


# ─── Tab 6: Super Deep Dive ──────────────────────────────────────────────────

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
    """Super Deep Dive — full intelligence brief for a selected opportunity."""
    active_opps = sorted(
        [o for o in opps if not o.get("kill_decision", False)],
        key=lambda o: float(o.get(SCORE_FIELD) or 0),
        reverse=True,
    )
    if not active_opps:
        st.info("No opportunities loaded. Run the daily pipeline first.")
        return

    opp_labels = [
        f"[{float(o.get(SCORE_FIELD) or 0):.1f}]  {o.get('name', '—')[:58]}  ·  {(o.get('geography') or '').upper()}"
        for o in active_opps
    ]

    # Pre-select from cross-tab navigation
    default_idx = 0
    if "deep_dive_opp_name" in st.session_state:
        for i, o in enumerate(active_opps):
            if o.get("name") == st.session_state.deep_dive_opp_name:
                default_idx = i
                break
        del st.session_state["deep_dive_opp_name"]

    selected_idx = st.selectbox(
        "Intelligence brief",
        options=range(len(active_opps)),
        format_func=lambda i: opp_labels[i],
        index=default_idx,
        key="super_deep_dive_selector",
    )

    o = active_opps[selected_idx]
    opp_id = o.get("id", "")
    opp_name = o.get("name", "—")
    score = float(o.get(SCORE_FIELD) or 0)
    geo = o.get("geography", "global")
    geo_label = GEO_LABELS.get(geo, geo.upper())
    lane = o.get("portfolio_lane") or "—"
    bucket = (o.get("bucket") or "").replace("_", " ").upper()
    stage = o.get("stage") or "scout"
    archetype = (o.get("benchmark_archetype") or "—").replace("_", " ").title()
    problem = o.get("problem_statement") or ""
    tam_raw = o.get("tam_usd_estimate") or o.get("tam")
    tam_str = f"${float(tam_raw)/1e6:.0f}M" if tam_raw else "—"
    wedge = o.get("daniels_wedge_score")
    ve_wedge = (o.get("venezuela_wedge_category") or "").replace("_", " ").upper()

    # Decision logic
    if score >= 8.5:
        decision_label, decision_color = "GO", "#22C55E"
    elif score >= 6.5:
        decision_label, decision_color = "WATCH", "#F59E0B"
    elif score >= 4.5:
        decision_label, decision_color = "HOLD", "#71717A"
    else:
        decision_label, decision_color = "KILL", "#EF4444"
    score_color = "#3B82F6"

    # ── Full-width intelligence brief hero ────────────────────────────────────
    wedge_pill = (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#52525B">'
        f'WEDGES <span style="color:#3B82F6;font-weight:600">{wedge}/6</span></span>'
        if wedge is not None else ""
    )
    ve_pill = (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#52525B">'
        f'VE WEDGE <span style="color:#F59E0B">{ve_wedge}</span></span>'
        if ve_wedge else ""
    )
    st.markdown(f"""
<div style="background:#18181B;
     border:1px solid rgba(255,255,255,0.07);border-left:3px solid {decision_color};
     border-radius:10px;padding:28px 32px;margin-bottom:20px;position:relative;overflow:hidden">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px">
    <div style="flex:1">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;
           letter-spacing:0.07em;text-transform:uppercase;margin-bottom:10px">
        {geo_label.upper()} &nbsp;·&nbsp; {bucket or "UNCLASSIFIED"}
      </div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:700;
           color:#F4F4F5;margin-bottom:10px;line-height:1.25;max-width:600px;letter-spacing:-0.025em">{opp_name}</div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#A1A1AA;
           line-height:1.75;margin-bottom:20px;max-width:640px">{problem[:320]}{'…' if len(problem) > 320 else ''}</div>
      <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
          TAM <span style="color:#3B82F6;font-weight:600">{tam_str}</span>
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
          LANE <span style="color:{LANE_COLORS.get(lane, '#888')};font-weight:600">{lane.upper()}</span>
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
          STAGE <span style="color:#A1A1AA;font-weight:600">{stage.upper()}</span>
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B">
          ARCHETYPE <span style="color:#A1A1AA">{archetype}</span>
        </span>
        {wedge_pill}
        {ve_pill}
      </div>
    </div>
    <div style="text-align:center;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
         border-radius:8px;padding:24px 32px;min-width:130px;flex-shrink:0">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#52525B;
           letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px">Decision</div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:24px;font-weight:700;
           color:{decision_color};margin-bottom:12px">{decision_label}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:40px;font-weight:600;
           color:{score_color};line-height:1">{score:.1f}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;margin-top:4px">/10</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 3-column intelligence sections ────────────────────────────────────────
    col_pain, col_market, col_build = st.columns(3)

    # ── PAIN ─────────────────────────────────────────────────────────────────
    with col_pain:
        st.markdown(subsection("The Pain"), unsafe_allow_html=True)

        pvs = o.get("pain_validation_score")
        pain_sev = o.get("pain_severity")
        gauge_val = float(pvs) if pvs is not None else (float(pain_sev) if pain_sev is not None else None)
        gauge_title = "PAIN VALIDATION" if pvs is not None else "PAIN SEVERITY"

        if gauge_val is not None:
            st.plotly_chart(
                score_gauge(gauge_val, gauge_title),
                use_container_width=True,
                key=f"dd_gauge_{opp_id}",
            )

        phrases = o.get("exact_customer_phrases")
        if phrases:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:10px 0 8px 0">CUSTOMER LANGUAGE</div>',
                unsafe_allow_html=True,
            )
            for p in (phrases if isinstance(phrases, list) else [phrases])[:3]:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.02);border-left:2px solid rgba(59,130,246,0.4);'
                    f'padding:8px 12px;margin-bottom:6px;border-radius:0 6px 6px 0">'
                    f'<span style="font-family:Plus Jakarta Sans,sans-serif;font-size:12px;'
                    f'color:#A1A1AA;font-style:italic">"{str(p)[:130]}"</span></div>',
                    unsafe_allow_html=True,
                )

        workarounds = o.get("workarounds_found")
        if workarounds:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:12px 0 6px 0">WORKAROUNDS TODAY</div>',
                unsafe_allow_html=True,
            )
            for w in (workarounds if isinstance(workarounds, list) else [workarounds])[:3]:
                st.markdown(
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    f'color:#9CA3AF;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03)">'
                    f'→ {str(w)[:110]}</div>',
                    unsafe_allow_html=True,
                )

        pain_sources = o.get("pain_evidence_sources")
        if pain_sources:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:12px 0 6px 0">EVIDENCE SOURCES</div>',
                unsafe_allow_html=True,
            )
            for src in (pain_sources if isinstance(pain_sources, list) else [pain_sources])[:2]:
                st.caption(str(src)[:120])

    # ── MARKET ────────────────────────────────────────────────────────────────
    with col_market:
        st.markdown(subsection("The Market"), unsafe_allow_html=True)

        if tam_raw:
            sam_raw = o.get("sam_usd_estimate")
            som_raw = o.get("som_usd_estimate")
            st.plotly_chart(
                tam_funnel_chart(float(tam_raw), float(sam_raw) if sam_raw else None, float(som_raw) if som_raw else None),
                use_container_width=True,
                key=f"dd_tam_{opp_id}",
            )
            if o.get("tam_rationale"):
                st.caption(str(o.get("tam_rationale"))[:200])

        timing = o.get("timing_tailwind")
        comp = o.get("competition_intensity")
        defensibility = o.get("defensibility")

        row_items = []
        if timing is not None:
            row_items.append(("TIMING", float(timing), "#F59E0B"))
        if comp is not None:
            comp_color = "#22C55E" if float(comp) < 4 else "#F59E0B" if float(comp) < 7 else "#EF4444"
            row_items.append(("COMPETITION", float(comp), comp_color))
        if defensibility is not None:
            row_items.append(("DEFENSIBILITY", float(defensibility), "#3B82F6"))

        if row_items:
            items_html = "".join([
                f'<div style="flex:1;text-align:center;padding:10px 8px;'
                f'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px">'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#52525B;'
                f'letter-spacing:0.07em;text-transform:uppercase;margin-bottom:6px">{label}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:20px;'
                f'font-weight:600;color:{color}">{val:.0f}</div></div>'
                for label, val, color in row_items
            ])
            st.markdown(
                f'<div style="display:flex;gap:8px;margin-bottom:12px">{items_html}</div>',
                unsafe_allow_html=True,
            )

        why_now = o.get("why_now")
        if why_now:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:0.07em;text-transform:uppercase;margin:12px 0 6px 0">WHY NOW</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                f'color:#9CA3AF;line-height:1.65">{str(why_now)[:300]}</div>',
                unsafe_allow_html=True,
            )

        target_customer = o.get("target_customer")
        if target_customer:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:12px 0 6px 0">TARGET BUYER</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                f'color:#F4F4F5;font-weight:500;line-height:1.5">{str(target_customer)[:180]}</div>',
                unsafe_allow_html=True,
            )

    # ── BUILD ─────────────────────────────────────────────────────────────────
    with col_build:
        st.markdown(subsection("The Build"), unsafe_allow_html=True)

        speed_mvp = o.get("speed_to_mvp")
        cap_eff = o.get("capital_efficiency")
        if speed_mvp is not None or cap_eff is not None:
            speed_html = (
                f'<div style="flex:1;text-align:center;padding:12px 8px;'
                f'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px">'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#52525B;'
                f'letter-spacing:0.07em;text-transform:uppercase;margin-bottom:6px">SPEED TO MVP</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:22px;font-weight:600;'
                f'color:#3B82F6">{float(speed_mvp):.0f}</div></div>'
                if speed_mvp is not None else ""
            )
            cap_html = (
                f'<div style="flex:1;text-align:center;padding:12px 8px;'
                f'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px">'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#52525B;'
                f'letter-spacing:0.07em;text-transform:uppercase;margin-bottom:6px">CAPITAL EFF.</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:22px;font-weight:600;'
                f'color:#22C55E">{float(cap_eff):.0f}</div></div>'
                if cap_eff is not None else ""
            )
            st.markdown(
                f'<div style="display:flex;gap:8px;margin-bottom:14px">{speed_html}{cap_html}</div>',
                unsafe_allow_html=True,
            )

        frp = (
            o.get("path_to_first_revenue_description")
            or o.get("path_to_first_revenue")
            or o.get("first_revenue_path_description")
        )
        if frp:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">PATH TO FIRST REVENUE</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="background:rgba(59,130,246,0.04);border:1px solid rgba(59,130,246,0.12);'
                f'border-radius:6px;padding:10px 14px;font-family:Plus Jakarta Sans,sans-serif;'
                f'font-size:12px;color:#A1A1AA;line-height:1.7">{str(frp)[:300]}</div>',
                unsafe_allow_html=True,
            )

        dist_channels = o.get("top_distribution_channels")
        if dist_channels:
            ch_list = dist_channels if isinstance(dist_channels, list) else [dist_channels]
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px 0">DISTRIBUTION CHANNELS</div>',
                unsafe_allow_html=True,
            )
            pills = "".join([
                f'<span style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);'
                f'border-radius:4px;padding:4px 10px;font-family:JetBrains Mono,monospace;font-size:10px;'
                f'color:#3B82F6;margin-right:6px;margin-bottom:6px;display:inline-block">{str(c)[:45]}</span>'
                for c in ch_list[:4]
            ])
            st.markdown(f'<div style="line-height:2.2">{pills}</div>', unsafe_allow_html=True)

        cac = o.get("estimated_cac_logic")
        if cac:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;'
                f'margin-top:6px">CAC → {str(cac)[:120]}</div>',
                unsafe_allow_html=True,
            )

        path10 = o.get("first_10_customer_path")
        if path10:
            st.markdown(
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                'letter-spacing:2px;text-transform:uppercase;margin:14px 0 6px 0">FIRST 10 CUSTOMERS</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                f'color:#C9D1D9;line-height:1.65">{str(path10)[:300]}</div>',
                unsafe_allow_html=True,
            )

        trust = o.get("trust_mechanism_latam")
        if trust:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;'
                f'margin-top:8px">TRUST → {str(trust)[:120]}</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Bottom: Scoring breakdown + Actions ───────────────────────────────────
    col_scoring, col_actions = st.columns([1.6, 1])

    with col_scoring:
        st.markdown(subsection("Scoring Breakdown"), unsafe_allow_html=True)
        fig_breakdown = score_breakdown_chart(o)
        if fig_breakdown:
            st.plotly_chart(fig_breakdown, use_container_width=True, key=f"dd_breakdown_{opp_id}")
        else:
            has_dims = any(o.get(f) for f in DIMENSION_FIELDS)
            if has_dims:
                col_r, col_f = st.columns(2)
                with col_r:
                    st.plotly_chart(radar_chart(o), use_container_width=True, key=f"radar_dd_{opp_id}")
                with col_f:
                    scored = {k: v for k, v in o.items() if isinstance(v, (int, float)) and v is not None}
                    for k, v in sorted(scored.items()):
                        st.caption(f"{k.replace('_', ' ').title()}: **{v}**")
            else:
                st.info("No scored dimensions found. Run the scoring pipeline to populate these fields.")

    with col_actions:
        st.markdown(subsection("Actions"), unsafe_allow_html=True)

        # Status badges
        stage_color = {"validation": "#F59E0B", "validated": "#10B981", "killed": "#EF4444"}.get(stage, "#6B7280")
        research_check_fields = ["pain_validation_score", "exact_customer_phrases", "first_10_customer_path", "distribution_validated"]
        has_research = any(o.get(f) for f in research_check_fields)

        st.markdown(f"""
<div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
  <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:{stage_color};
       background:{stage_color}15;border:1px solid {stage_color}40;border-radius:3px;padding:5px 12px">
    STAGE: {stage.upper()}
  </span>
  <span style="font-family:JetBrains Mono,monospace;font-size:10px;
       color:{'#10B981' if has_research else '#6B7280'};
       background:{'rgba(16,185,129,0.08)' if has_research else 'rgba(107,114,128,0.06)'};
       border:1px solid {'#10B98140' if has_research else '#6B728035'};border-radius:3px;padding:5px 12px">
    {'✓ RESEARCH' if has_research else '○ NO RESEARCH'}
  </span>
</div>""", unsafe_allow_html=True)

        run_val = st.button(
            "▶ Run Validation Package",
            key="btn_run_val_super",
            use_container_width=True,
            help="Runs the full 8-section validation package for this opportunity",
        )
        run_res = st.button(
            "▶ Expand Research (Pain + Dist)",
            key="btn_run_res_super",
            use_container_width=True,
            help="Runs combined pain + distribution web research (1 API call)",
        )

        if run_val:
            if not opp_id:
                st.error("No ID — cannot run validation.")
            else:
                with st.spinner(f"Validating: {opp_name[:40]}…"):
                    ok, out = _run_subprocess(
                        ["uv", "run", "--no-sync", "opp-os", "validate", opp_id],
                        "Validation",
                    )
                    st.session_state[f"super_val_{selected_idx}"] = (ok, out)
                    st.cache_data.clear()

        if run_res:
            if not opp_id:
                st.error("No ID.")
            else:
                with st.spinner(f"Researching: {opp_name[:40]}…"):
                    ok, out = _run_subprocess(
                        ["uv", "run", "--no-sync", "opp-os", "research", opp_id],
                        "Research",
                    )
                    st.session_state[f"super_res_{selected_idx}"] = (ok, out)
                    st.cache_data.clear()

        for sess_key, label in [
            (f"super_val_{selected_idx}", "Validation"),
            (f"super_res_{selected_idx}", "Research"),
        ]:
            if sess_key in st.session_state:
                ok, out = st.session_state[sess_key]
                if ok:
                    st.success(f"{label} complete.")
                else:
                    st.warning(f"{label} had errors.")
                with st.expander(f"▸ {label} output", expanded=False):
                    st.code(out[-2500:], language="text")

        val_md = _load_validation_report(opp_id)
        if val_md:
            with st.expander("▸ Latest validation report", expanded=False):
                st.markdown(val_md[:5000])
        else:
            st.caption("No validation report yet. Run validation above.")

        # ── Kill Gate ────────────────────────────────────────────────────────
        st.markdown("---")

        def _kl(t):
            return (
                '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                f'letter-spacing:0.07em;text-transform:uppercase;margin:10px 0 6px 0">{t}</div>'
            )

        def _yn(v):
            c, lb = ("#22C55E", "PASS") if v else ("#EF4444", "FAIL")
            return (
                f'<span style="color:{c};font-weight:600;'
                f'font-family:JetBrains Mono,monospace;font-size:10px">{lb}</span>'
            )

        _KILL_QS = [
            ("Pain in 1 sentence?",      bool(o.get("problem_statement", ""))),
            ("Named buyer?",              bool(o.get("target_customer"))),
            ("CAC cheap enough?",         bool(o.get("estimated_cac_logic"))),
            ("Revenue < 90 days?",        bool(o.get("path_to_first_revenue_description") or o.get("path_to_first_revenue"))),
            ("MVP in 2–6 weeks?",         o.get("speed_to_mvp") is not None and float(o.get("speed_to_mvp") or 0) >= 6),
            ("TAM > $10M?",              bool(tam_raw) and float(tam_raw) > 10_000_000),
            ("Has wedge?",               bool(o.get("benchmark_archetype")) or float(o.get("daniels_wedge_score") or 0) >= 2),
        ]
        _kg_pass = sum(1 for _, a in _KILL_QS if a)
        _kg_color = "#22C55E" if _kg_pass >= 6 else "#F59E0B" if _kg_pass >= 5 else "#EF4444"
        _kg_killed = o.get("kill_decision", False)
        _gate_html = "".join([
            f'<div style="display:flex;justify-content:space-between;padding:4px 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#9CA3AF">{q}</span>'
            f'{_yn(ans)}</div>'
            for q, ans in _KILL_QS
        ])
        st.markdown(_kl("KILL GATE"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);'
            f'border-radius:6px;padding:10px 12px">'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:{_kg_color};'
            f'font-weight:600;margin-bottom:8px">{_kg_pass}/7 PASSED'
            f'{"  ·  KILLED" if _kg_killed else ""}</div>'
            f'{_gate_html}</div>',
            unsafe_allow_html=True,
        )

        # ── Decision Filters ─────────────────────────────────────────────────
        _COMPOUND = {
            "local_clone", "workflow_unbundling", "smb_operating_system",
            "fragmented_supply_marketplace", "ai_operator_replacement",
        }
        _df_stored = o.get("decision_filter_results") or {}
        _FILTERS = [
            ("Sell fast (< 2 wks)?", _df_stored.get("can_sell_fast",   o.get("distribution_validated") is True)),
            ("Build lean (< $2K)?",  _df_stored.get("can_build_lean",  o.get("capital_efficiency") is not None and float(o.get("capital_efficiency") or 0) >= 6)),
            ("Can compound?",        _df_stored.get("can_compound",    (o.get("benchmark_archetype") or "") in _COMPOUND)),
        ]
        _fp = sum(1 for _, a in _FILTERS if a)
        _fc = "#22C55E" if _fp == 3 else "#F59E0B" if _fp >= 2 else "#EF4444"
        _filter_html = "".join([
            f'<div style="display:flex;justify-content:space-between;padding:4px 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#9CA3AF">{q}</span>'
            f'{_yn(ans)}</div>'
            for q, ans in _FILTERS
        ])
        st.markdown(_kl("DECISION FILTERS"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);'
            f'border-radius:6px;padding:10px 12px">'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:{_fc};'
            f'font-weight:600;margin-bottom:8px">{_fp}/3 FILTERS'
            f'{"  ·  CAP 5.0" if _fp < 2 else ""}</div>'
            f'{_filter_html}</div>',
            unsafe_allow_html=True,
        )

        with st.expander("▸ All raw fields", expanded=False):
            st.json({k: v for k, v in o.items() if k != "score_history"})

    # ── Decision Memo ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown(subsection("Decision Memo"), unsafe_allow_html=True)

    def _ml(t):
        return (
            '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
            f'letter-spacing:0.07em;text-transform:uppercase;margin:10px 0 6px 0">{t}</div>'
        )

    def _mtext(txt, color="#A1A1AA", size="12px"):
        return (
            f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:{size};'
            f'color:{color};line-height:1.7">{txt}</div>'
        )

    _wedge_names = ["Growth & GTM", "Narrative", "LATAM intuition", "Fintech/crypto", "Speed to build", "Distribution"]
    _wedge_n     = int(o.get("daniels_wedge_score") or 0)
    _wedge_list  = _wedge_names[:_wedge_n]
    _why_now     = o.get("why_now") or str(o.get("timing_tailwind") or "—")
    _frp         = o.get("path_to_first_revenue_description") or str(o.get("path_to_first_revenue") or "—")
    _risks       = o.get("kill_reasons") or []
    _sam_raw     = o.get("sam_usd_estimate")
    _som_raw     = o.get("som_usd_estimate")

    mc1, mc2, mc3 = st.columns(3)

    with mc1:
        st.markdown(_ml("THESIS"), unsafe_allow_html=True)
        st.markdown(_mtext(f"<em>{str(problem)[:220]}</em>"), unsafe_allow_html=True)

        st.markdown(_ml("TARGET BUYER"), unsafe_allow_html=True)
        st.markdown(_mtext(str(o.get("target_customer") or "—")[:180]), unsafe_allow_html=True)

        st.markdown(_ml("MARKET SIZE"), unsafe_allow_html=True)
        _msizes = [f'TAM <strong style="color:#3B82F6">{tam_str}</strong>']
        if _sam_raw:
            _msizes.append(f'SAM <strong>${float(_sam_raw)/1e6:.0f}M</strong>')
        if _som_raw:
            _msizes.append(f'SOM <strong>${float(_som_raw)/1e6:.0f}M</strong>')
        st.markdown(_mtext("  ·  ".join(_msizes), color="#9CA3AF"), unsafe_allow_html=True)

    with mc2:
        st.markdown(_ml("WHY NOW"), unsafe_allow_html=True)
        st.markdown(_mtext(str(_why_now)[:300]), unsafe_allow_html=True)

        st.markdown(_ml("WHY DANIEL WINS"), unsafe_allow_html=True)
        if _wedge_list:
            _wins_html = "".join([
                f'<div style="color:#22C55E;font-family:JetBrains Mono,monospace;'
                f'font-size:10px;padding:2px 0">&#10003; {w}</div>'
                for w in _wedge_list
            ])
            if _wedge_n < 2:
                _wins_html += (
                    '<div style="color:#F59E0B;font-family:JetBrains Mono,monospace;'
                    'font-size:10px;padding:2px 0">&#9888; Founder-fit risk (&lt;2 wedges)</div>'
                )
            st.markdown(_wins_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#F59E0B;font-family:JetBrains Mono,monospace;font-size:10px">'
                '&#9888; No wedge match — run scorer</div>',
                unsafe_allow_html=True,
            )

    with mc3:
        st.markdown(_ml("KEY RISKS"), unsafe_allow_html=True)
        if _risks:
            st.markdown("".join([
                f'<div style="color:#F59E0B;font-family:JetBrains Mono,monospace;'
                f'font-size:10px;padding:2px 0">&#9888; {str(r)[:90]}</div>'
                for r in _risks[:4]
            ]), unsafe_allow_html=True)
        else:
            st.markdown(_mtext("No kill signals logged."), unsafe_allow_html=True)

        st.markdown(_ml("NEXT TEST THIS WEEK"), unsafe_allow_html=True)
        st.markdown(_mtext(str(_frp)[:220]), unsafe_allow_html=True)

        # Conviction bar
        _conv = min(100, round(score * 10))
        _bc   = "#22C55E" if _conv >= 85 else "#3B82F6" if _conv >= 65 else "#F59E0B"
        st.markdown(
            f'<div style="margin-top:14px">'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
            f'letter-spacing:0.07em;text-transform:uppercase;margin-bottom:6px">CONVICTION</div>'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;overflow:hidden">'
            f'<div style="width:{_conv}%;height:100%;background:{_bc};border-radius:4px"></div></div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:14px;color:{_bc};'
            f'margin-top:6px;font-weight:600">{_conv}%</div></div>',
            unsafe_allow_html=True,
        )


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
