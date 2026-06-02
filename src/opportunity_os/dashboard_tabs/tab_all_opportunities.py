"""Tab 2: All Opportunities — searchable, filterable list with inline actions and data badges."""

import logging
import os
import subprocess

import streamlit as st

from .components import (
    DIMENSION_FIELDS,
    GEO_LABELS,
    LANE_COLORS,
    SCORE_FIELD,
    radar_chart,
    section_header,
    subsection,
)
from .data import PROJECT_ROOT, _parse_tam

logger = logging.getLogger(__name__)


# ── Subprocess helper (mirrors tab_deep_dive) ─────────────────────────────────

def _run_subprocess(cmd: list, label: str) -> tuple[bool, str]:
    """Run a CLI command, return (success, output_text)."""
    try:
        env = {**os.environ, "UV_LINK_MODE": "copy"}
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        stderr_block = "\n--- STDERR ---\n" + result.stderr if result.stderr else ""
        output = (result.stdout or "") + stderr_block
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"{label} timed out after 5 minutes."
    except Exception as exc:  # noqa: BLE001
        return False, f"Could not run {label}: {exc}"


def _data_badge_html(label: str, value, color: str = "#3B82F6") -> str:
    """Small monospace badge for a data-backed signal field."""
    if value is None:
        return ""
    return (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;'
        f'color:{color};background:{color}18;border:1px solid {color}38;'
        f'border-radius:3px;padding:2px 7px;margin-right:5px">'
        f'{label} <b>{value}</b></span>'
    )


def _opp_card_header_html(o: dict) -> str:
    """Dark metadata banner injected at the top of each expanded opportunity card.

    Shows name + geo/stage eyebrow + score floating right + metadata token row
    (TAM, LANE, BUCKET, WEDGES). Problem statement is intentionally omitted —
    it lives in full in the content columns directly below.
    """
    score = float(o.get(SCORE_FIELD) or 0)
    lane = o.get("portfolio_lane") or "no"
    geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
    name = o.get("name", "—")
    stage = (o.get("stage") or "scout").upper()

    tam_raw = _parse_tam(o.get("tam_usd_estimate") or o.get("tam"))
    if tam_raw and tam_raw >= 1e9:
        tam_str = f"${tam_raw / 1e9:.1f}B"
    elif tam_raw and tam_raw >= 1e6:
        tam_str = f"${tam_raw / 1e6:.0f}M"
    elif tam_raw:
        tam_str = f"${tam_raw / 1e3:.0f}K"
    else:
        tam_str = "—"

    lane_color = LANE_COLORS.get(lane, "#52525B")
    score_color = "#3B82F6" if score >= 8 else "#F59E0B" if score >= 6 else "#EF4444" if score < 4 else "#71717A"

    bucket_raw = (o.get("bucket") or "").replace("_", " ").upper()
    bucket_html = (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
        f'BUCKET <span style="color:#A1A1AA">{bucket_raw}</span></span>'
        if bucket_raw else ""
    )
    wedge = o.get("daniels_wedge_score")
    wedge_html = (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
        f'WEDGES <span style="color:#3B82F6">{wedge}/6</span></span>'
        if wedge is not None else ""
    )
    archetype_raw = (o.get("benchmark_archetype") or "").replace("_", " ").title()
    archetype_html = (
        f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
        f'ARCH <span style="color:#A1A1AA">{archetype_raw}</span></span>'
        if archetype_raw else ""
    )

    return (
        f'<div style="background:#18181B;border:1px solid rgba(255,255,255,0.06);'
        f'border-left:3px solid {lane_color};border-radius:8px;padding:14px 18px;'
        f'margin-bottom:14px;position:relative;overflow:hidden">'
        f'  <div style="position:absolute;top:12px;right:16px;'
        f'font-family:JetBrains Mono,monospace;font-size:26px;font-weight:600;'
        f'color:{score_color};line-height:1">{score:.1f}'
        f'<span style="font-size:9px;color:#52525B;margin-left:2px">/10</span></div>'
        f'  <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
        f'letter-spacing:0.09em;text-transform:uppercase;margin-bottom:4px">'
        f'{geo} · {stage}</div>'
        f'  <div style="font-family:Plus Jakarta Sans,sans-serif;font-size:15px;font-weight:600;'
        f'color:#F4F4F5;margin-bottom:10px;max-width:78%;letter-spacing:-0.01em">{name}</div>'
        f'  <div style="display:flex;gap:14px;flex-wrap:wrap;align-items:center">'
        f'    <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
        f'TAM <span style="color:#3B82F6">{tam_str}</span></span>'
        f'    <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
        f'LANE <span style="color:{lane_color}">{lane.upper()}</span></span>'
        f'    {bucket_html}'
        f'    {archetype_html}'
        f'    {wedge_html}'
        f'  </div>'
        f'</div>'
    )


# ── Main tab ──────────────────────────────────────────────────────────────────

def tab_all_opportunities(opps, geo_filter, score_range):
    import pandas as pd  # noqa: F401 — available for callers

    st.markdown(section_header("All Opportunities"), unsafe_allow_html=True)

    # Cross-tab navigation banner — appears at page-top after "📊 Deep Dive" is pressed
    nav_name = st.session_state.get("deep_dive_opp_name")
    if nav_name:
        st.success(
            f"**{nav_name}** is pre-loaded in the **Deep Dive** tab — click the tab above to view the full brief.",
            icon="📊",
        )

    # ── Local filters ─────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input(
            "Search name or problem statement",
            placeholder="e.g. fintech, venezuela, SaaS…",
        )
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

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = opps
    if geo_filter and geo_filter != "All":
        filtered = [
            o for o in filtered
            if (o.get("geography") or "").lower() == geo_filter.lower()
        ]
    filtered = [
        o for o in filtered
        if score_range[0] <= float(o.get(SCORE_FIELD) or 0) <= score_range[1]
    ]
    if search:
        s = search.lower()
        filtered = [
            o for o in filtered
            if s in (o.get("name") or "").lower()
            or s in (o.get("problem_statement") or "").lower()
        ]
    if geo_multi:
        filtered = [o for o in filtered if o.get("geography") in geo_multi]
    if lane_multi:
        filtered = [o for o in filtered if o.get("portfolio_lane") in lane_multi]

    filtered = sorted(
        filtered, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True
    )

    # ── Count row + global Rescore action ─────────────────────────────────────
    cap_col, rescore_col = st.columns([3, 1])
    with cap_col:
        st.caption(f"Showing {len(filtered)} of {len(opps)} opportunities")
    with rescore_col:
        if st.button("↺ Rescore Portfolio", use_container_width=True, key="btn_rescore_top",
                     help="Re-score every opportunity and update final_score values"):
            with st.spinner("Rescoring portfolio…"):
                ok, out = _run_subprocess(
                    ["uv", "run", "--no-sync", "opp-os", "rescore-all"],
                    "Rescore",
                )
                st.session_state["ao_rescore_result"] = (ok, out)
                st.cache_data.clear()

    if "ao_rescore_result" in st.session_state:
        ok, out = st.session_state["ao_rescore_result"]
        st.success("Portfolio rescore complete.") if ok else st.warning("Rescore had errors.")
        with st.expander("▸ Rescore output", expanded=False):
            st.code(out[-2000:], language="text")

    if not filtered:
        st.info("No opportunities match the current filters.")
        return

    # ── Opportunity cards ─────────────────────────────────────────────────────
    for opp_idx, o in enumerate(filtered):
        score = float(o.get(SCORE_FIELD) or 0)
        lane = o.get("portfolio_lane") or "—"
        geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))
        opp_id = o.get("id", "")
        opp_name = o.get("name", "—")

        # Expander label kept minimal — the styled card header renders inside
        label = f"{opp_name}  ·  {score:.1f}/10  ·  {lane}"

        with st.expander(label, expanded=False):
            st.markdown(_opp_card_header_html(o), unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**Problem Statement**  \n{o.get('problem_statement', '—')}")
                st.markdown(f"**Target Customer**  \n{o.get('target_customer', '—')}")
                if o.get("path_to_first_revenue"):
                    st.markdown(
                        f"**Path to First Revenue**  \n{str(o.get('path_to_first_revenue'))}"
                    )
                if o.get("first_10_customer_path"):
                    st.markdown(
                        f"**First 10 Customers**  \n{str(o.get('first_10_customer_path'))[:300]}"
                    )
                if o.get("exact_customer_phrases"):
                    phrases = o.get("exact_customer_phrases")
                    if isinstance(phrases, list):
                        st.markdown("**Customer Language**")
                        for p in phrases[:3]:
                            st.markdown(f"> *{p}*")

                # TAM / SAM / SOM with (est.) disclaimer for modeled values
                tam = _parse_tam(o.get("tam_usd_estimate") or o.get("tam"))
                sam_raw = _parse_tam(o.get("sam_usd_estimate"))
                som_raw = _parse_tam(o.get("som_usd_estimate"))
                is_sam_est = sam_raw is None
                is_som_est = som_raw is None
                sam = sam_raw if sam_raw is not None else (tam * 0.12 if tam else None)
                som = som_raw if som_raw is not None else (sam * 0.18 if sam else None)

                if tam:
                    def _fmt(v, is_est):
                        base = f"${v/1e9:.1f}B" if v >= 1e9 else (
                            f"${v/1e6:.0f}M" if v >= 1e6 else f"${v/1e3:.0f}K"
                        )
                        return f"{base} (est.)" if is_est else base

                    parts = (
                        f"**TAM / SAM / SOM:** {_fmt(tam, False)}"
                        f" / {_fmt(sam, is_sam_est) if sam else '—'}"
                        f" / {_fmt(som, is_som_est) if som else '—'}"
                    )
                    st.markdown(parts)
                    if is_sam_est or is_som_est:
                        st.caption(
                            "⚠ Modeled at 12% TAM / 18% SAM — not field-validated"
                        )
                    if o.get("tam_rationale"):
                        st.caption(str(o.get("tam_rationale"))[:200])

            with c2:
                st.markdown(subsection("Intelligence"), unsafe_allow_html=True)
                first_seen_val = o.get("first_seen") or ""
                intel = {
                    "Discovered": str(first_seen_val)[:10] if first_seen_val else None,
                    "Thesis Fit": o.get("thesis_fit_score"),
                    "Daniel Wedges": (
                        f"{o.get('daniels_wedge_score')}/6"
                        if o.get("daniels_wedge_score") is not None else None
                    ),
                    "Archetype": (
                        (o.get("benchmark_archetype") or "").replace("_", " ").title() or None
                    ),
                    "Bucket": (
                        (o.get("bucket") or "").replace("_", " ").title() or None
                    ),
                    "VE Wedge": (
                        (o.get("venezuela_wedge_category") or "").replace("_", " ").title() or None
                    ),
                }
                for k, v in intel.items():
                    if v is not None:
                        st.caption(f"{k}: **{v}**")

                # Data-backed signal badges (new fields from P0-P3 upgrade)
                news_n = o.get("news_signal_count")
                pain_n = o.get("pain_signal_count")
                job_n = o.get("job_posting_count")
                neg_rate = o.get("competitor_negative_review_rate")
                badges = [
                    _data_badge_html("NEWS", news_n, "#3B82F6"),
                    _data_badge_html("PAIN", pain_n, "#F59E0B"),
                    _data_badge_html("JOBS", job_n, "#22C55E"),
                    (
                        _data_badge_html("NEG%", f"{int(neg_rate * 100)}%", "#EF4444")
                        if neg_rate is not None else ""
                    ),
                ]
                badge_html = "".join(b for b in badges if b)
                if badge_html:
                    st.markdown(
                        f'<div style="margin-top:8px">{badge_html}</div>',
                        unsafe_allow_html=True,
                    )

                has_dims = any(o.get(f) for f in DIMENSION_FIELDS)
                if has_dims:
                    st.plotly_chart(
                        radar_chart(o),
                        width="stretch",
                        key=f"radar_all_{opp_idx}",
                    )

            # Distribution channels
            channels = o.get("top_distribution_channels")
            if channels:
                if isinstance(channels, list):
                    st.caption("Distribution: " + " · ".join(str(c) for c in channels[:3]))
                else:
                    st.caption(f"Distribution: {str(channels)[:150]}")

            # Kill signals
            if o.get("kill_decision"):
                st.error(
                    f"KILLED — {', '.join(o.get('kill_reasons', [])) or 'No reason logged'}"
                )
            elif o.get("kill_reasons"):
                st.warning(f"Kill signals: {', '.join(o.get('kill_reasons', []))}")

            # Scores summary — styled token row
            _attr = o.get('attractiveness_score', '—')
            _exec = o.get('executability_score', '—')
            _strat = o.get('strategic_value_score', '—')
            _scored_at = str(o.get('ai_scored_at') or '')[:16]
            _ve_lens = 'YES' if o.get('venezuela_lens_applied') else 'NO'
            _scored_caption = (
                f'<span style="font-family:JetBrains Mono,monospace;font-size:9px;'
                f'color:#52525B"> · AI scored {_scored_at} · VE lens {_ve_lens}</span>'
                if o.get("ai_scored_at") else ""
            )
            _score_row = (
                f'<div style="display:flex;gap:18px;flex-wrap:wrap;align-items:center;'
                f'margin:10px 0 4px 0">'
                f'  <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
                f'ATTRACT <span style="color:#F4F4F5;font-weight:600">{_attr}</span></span>'
                f'  <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
                f'EXEC <span style="color:#F4F4F5;font-weight:600">{_exec}</span></span>'
                f'  <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#52525B">'
                f'STRATEGIC <span style="color:#F4F4F5;font-weight:600">{_strat}</span></span>'
                f'  {_scored_caption}'
                f'</div>'
            )
            st.markdown(_score_row, unsafe_allow_html=True)

            # ── Actions row ───────────────────────────────────────────────────
            st.markdown(
                '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0"/>',
                unsafe_allow_html=True,
            )
            btn_dd, btn_res, hint_col = st.columns([1, 1, 4])

            with btn_dd:
                if st.button(
                    "📊 Deep Dive",
                    key=f"goto_dd_{opp_idx}",
                    use_container_width=True,
                    help="Pre-load this opportunity in the Deep Dive tab",
                ):
                    st.session_state["deep_dive_opp_name"] = opp_name

            with btn_res:
                btn_res_disabled = not opp_id
                if st.button(
                    "▶ Research",
                    key=f"btn_res_{opp_idx}",
                    use_container_width=True,
                    disabled=btn_res_disabled,
                    help="Run pain + distribution research for this opportunity",
                ):
                    with st.spinner(f"Researching {opp_name[:40]}…"):
                        ok, out = _run_subprocess(
                            ["uv", "run", "--no-sync", "opp-os", "research", opp_id],
                            "Research",
                        )
                        st.session_state[f"ao_res_{opp_id}"] = (ok, out)
                        st.cache_data.clear()

            with hint_col:
                if st.session_state.get("deep_dive_opp_name") == opp_name:
                    st.success(
                        "Pre-loaded — click **Deep Dive** tab above ↑",
                        icon="📊",
                    )

            # Show per-opp research output
            res_key = f"ao_res_{opp_id}"
            if res_key in st.session_state:
                ok, out = st.session_state[res_key]
                st.success("Research complete.") if ok else st.warning("Research had errors.")
                with st.expander("▸ Research output", expanded=False):
                    st.code(out[-2000:], language="text")
