"""Shared constants, helper functions, and chart builders for Opportunity OS dashboard."""

from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px  # noqa: F401 — available for callers
import streamlit as st

from .data import _parse_tam

# ─── Constants ────────────────────────────────────────────────────────────────

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
    except (ValueError, OSError):
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


# ─── HTML Components ──────────────────────────────────────────────────────────

def hero_card(o: dict, rank: int) -> str:
    """Render a top-opportunity hero card as HTML."""
    score = float(o.get(SCORE_FIELD) or 0)
    lane = o.get("portfolio_lane") or "—"
    geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
    name = o.get("name", "—")
    problem = (o.get("problem_statement") or "")[:180]
    tam = _parse_tam(o.get("tam_usd_estimate") or o.get("tam"))
    tam_str = f"${tam/1e6:.0f}M" if tam else "—"
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


# ─── Chart Builders ───────────────────────────────────────────────────────────

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
    """Plotly gauge chart for a score value."""
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
