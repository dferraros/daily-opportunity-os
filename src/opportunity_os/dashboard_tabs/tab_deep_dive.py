"""Tab 6: Super Deep Dive — full intelligence brief, kill gate, decision memo."""

import html
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
    score_breakdown_chart,
    score_gauge,
    section_header,
    subsection,
    tam_funnel_chart,
)
from .data import PROJECT_ROOT, _parse_tam

logger = logging.getLogger(__name__)


def _run_subprocess(cmd: list, label: str) -> tuple[bool, str]:
    """Run a subprocess command, return (success, output_text)."""
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
    except Exception as e:  # noqa: BLE001
        return False, f"Could not run {label}: {e}"


def _load_validation_report(opp_id: str) -> str | None:
    """Find the most recent validation markdown for this opp_id."""
    val_dir = PROJECT_ROOT / "reports" / "validation"
    if not val_dir.exists():
        return None
    matches = sorted(val_dir.glob(f"*{opp_id[:20]}*-validation.md"), reverse=True)
    if not matches:
        all_matches = sorted(val_dir.glob("*-validation.md"), reverse=True)
        matches = [m for m in all_matches if opp_id[:16] in m.name]
    if matches:
        try:
            return matches[0].read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Could not read validation file %s: %s", matches[0], exc)
            return None
    return None


_REC_COLORS = {"go": "#22C55E", "validate": "#F59E0B", "pass": "#EF4444"}


def _render_intelligence_panel(o: dict) -> None:
    """Surface this-session intelligence: Sonnet synthesis, kill thesis, evidence coverage.

    Renders nothing when an opp has none of these (e.g. not yet deep-dived with
    --synthesize), so it degrades cleanly across the portfolio.
    """
    rec = (o.get("synthesis_recommendation") or "").lower()
    bull = o.get("synthesis_bull_case")
    swing = o.get("synthesis_swing_factors") or []
    unknown = o.get("synthesis_key_unknown")
    kt = o.get("kill_thesis")
    kt_strength = o.get("kill_thesis_strength")
    coverage = o.get("evidence_coverage")
    low_ev = o.get("low_evidence_flag")

    if not (rec or kt or coverage is not None):
        return

    badges = []
    if rec:
        rc = _REC_COLORS.get(rec, "#3B82F6")
        badges.append(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:{rc};'
            f'background:{rc}15;border:1px solid {rc}40;border-radius:3px;padding:5px 12px">'
            f'SONNET: {rec.upper()}</span>'
        )
    if kt_strength is not None:
        ktc = "#EF4444" if kt_strength >= 7 else "#F59E0B" if kt_strength >= 4 else "#22C55E"
        cap = " · CAPS 5.0" if kt_strength >= 7 else ""
        badges.append(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:{ktc};'
            f'background:{ktc}15;border:1px solid {ktc}40;border-radius:3px;padding:5px 12px">'
            f'KILL-THESIS {kt_strength}/10{cap}</span>'
        )
    if coverage is not None:
        cvc = "#EF4444" if low_ev else "#22C55E" if coverage >= 0.5 else "#F59E0B"
        warn = " · THIN" if low_ev else ""
        badges.append(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;color:{cvc};'
            f'background:{cvc}15;border:1px solid {cvc}40;border-radius:3px;padding:5px 12px">'
            f'EVIDENCE {coverage * 100:.0f}%{warn}</span>'
        )

    def _block(label, text, color="#A1A1AA"):
        return (
            '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
            f'letter-spacing:0.07em;text-transform:uppercase;margin:12px 0 5px 0">{label}</div>'
            f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:12px;color:{color};'
            f'line-height:1.7">{text}</div>'
        )

    body = ""
    if o.get("synthesis_rationale"):
        body += _block("Why", str(o.get("synthesis_rationale"))[:400], "#F4F4F5")
    if bull:
        body += _block("Bull case", str(bull)[:500])
    if swing:
        items = "".join(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#9CA3AF;'
            f'padding:3px 0;line-height:1.55">→ {str(s)[:240]}</div>'
            for s in (swing if isinstance(swing, list) else [swing])[:3]
        )
        body += (
            '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
            'letter-spacing:0.07em;text-transform:uppercase;margin:12px 0 5px 0">'
            'Swing factors (what decides go/no-go)</div>' + items
        )
    if unknown:
        body += (
            '<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#F59E0B;'
            'letter-spacing:0.07em;text-transform:uppercase;margin:12px 0 5px 0">Decisive unknown</div>'
            f'<div style="background:rgba(245,158,11,0.06);border-left:2px solid rgba(245,158,11,0.5);'
            f'padding:8px 12px;border-radius:0 6px 6px 0;font-family:Plus Jakarta Sans,sans-serif;'
            f'font-size:12px;color:#D4D4D8;line-height:1.6">{str(unknown)[:400]}</div>'
        )
    if kt:
        body += _block("Strongest kill thesis", str(kt)[:400], "#C9D1D9")

    st.html(f"""
<div style="background:#18181B;border:1px solid rgba(255,255,255,0.07);
     border-radius:10px;padding:20px 24px;margin-bottom:20px">
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#52525B;
       letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px">Analyst Intelligence</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px">{''.join(badges)}</div>
  {body}
</div>
""")


def _render_full_scoring_breakdown(o: dict) -> None:
    """Every scoring variable with score, weight, contribution, and FULL reasoning.

    Reuses the report's data helpers (_DIM_LABELS, _data_backed_basis, layer field
    lists) so the dashboard and the markdown deep-dive never drift apart.
    """
    from opportunity_os.engines.scoring_engine import (
        ATTRACTIVENESS_FIELDS, EXECUTABILITY_FIELDS, STRATEGIC_VALUE_FIELDS, load_weights,
    )
    from opportunity_os.pipelines.deep_dive import (
        _DATA_BACKED_DIMS, _DIM_LABELS, _data_backed_basis,
    )

    weight_map = load_weights().get("weights", {})
    layers = [
        ("Attractiveness", "50%", ATTRACTIVENESS_FIELDS, "attractiveness_score"),
        ("Executability", "30%", EXECUTABILITY_FIELDS, "executability_score"),
        ("Strategic Value", "20%", STRATEGIC_VALUE_FIELDS, "strategic_value_score"),
    ]

    st.markdown(subsection("Every Variable — Full Reasoning"), unsafe_allow_html=True)

    for name, pct, fields, score_field in layers:
        ls = o.get(score_field)
        ls_str = f"{ls}/10" if ls is not None else "—"
        parts = [
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#71717A;'
            f'letter-spacing:0.07em;text-transform:uppercase;font-weight:600;margin:16px 0 8px 0">'
            f'{name} · {pct} of composite · layer {ls_str}</div>'
        ]
        for field in fields:
            value = o.get(field)
            weight = weight_map.get(field, 0.0)
            label = html.escape(_DIM_LABELS.get(field, field))

            if value is not None:
                v = float(value)
                sc = "#22C55E" if v >= 8 else "#F59E0B" if v >= 5 else "#EF4444"
                score_str = f"{value}/10"
            else:
                v, sc, score_str = None, "#6B7280", "not scored"

            if weight == 0.0:
                meta = "weight 0 · consolidated (redundant — folded into speed_to_mvp)"
            elif v is not None:
                eff = (10.0 - v) if field == "competition_intensity" else v
                meta = f"weight {weight:.2f} · contributes {eff * weight:.2f}"
            else:
                meta = f"weight {weight:.2f} · no value yet (run the scorer)"

            why = o.get(f"{field}_reason") or ""
            if not why and field in _DATA_BACKED_DIMS:
                why = _data_backed_basis(o, field)
            why = html.escape(str(why).replace("\n", " ").strip()[:450]) or \
                "<em>No reasoning recorded for this dimension yet.</em>"

            parts.append(
                f'<div style="border-left:2px solid {sc};background:rgba(255,255,255,0.02);'
                f'padding:10px 14px;margin-bottom:8px;border-radius:0 6px 6px 0">'
                f'<div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px">'
                f'<span style="font-family:Plus Jakarta Sans,sans-serif;font-size:13px;font-weight:600;'
                f'color:#F4F4F5">{label}</span>'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;font-weight:600;'
                f'color:{sc};white-space:nowrap">{score_str}</span></div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#52525B;'
                f'letter-spacing:0.05em;margin:4px 0 6px 0">{meta}</div>'
                f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:12px;color:#A1A1AA;'
                f'line-height:1.6">{why}</div></div>'
            )
        st.html("".join(parts))

    # Adversarial counterweight
    kt = o.get("kill_thesis")
    if kt:
        strength = o.get("kill_thesis_strength") or 0
        capped = strength >= 7
        kc = "#EF4444" if capped else "#F59E0B"
        st.html(
            f'<div style="border-left:2px solid {kc};background:rgba(239,68,68,0.05);'
            f'padding:10px 14px;margin-top:10px;border-radius:0 6px 6px 0">'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:{kc};'
            f'font-weight:600;margin-bottom:5px">ADVERSARIAL KILL THESIS · {strength}/10'
            f'{" · CAPS SCORE AT 5.0" if capped else " · watch-item"}</div>'
            f'<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:12px;color:#C9D1D9;'
            f'line-height:1.6">{html.escape(str(kt)[:400])}</div></div>'
        )


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
        f"[{float(o.get(SCORE_FIELD) or 0):.1f}]  {o.get('name', '—')[:58]}"
        f"  ·  {(o.get('geography') or '').upper()}"
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
    tam_raw = _parse_tam(o.get("tam_usd_estimate") or o.get("tam"))
    tam_str = f"${tam_raw/1e6:.0f}M" if tam_raw else "—"
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

    # ── Full-width intelligence brief hero ─────────────────────────────────────
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
    st.html(f"""
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
""")

    # ── Analyst Intelligence panel (Sonnet synthesis, kill thesis, evidence) ────
    _render_intelligence_panel(o)

    # ── 3-column intelligence sections ─────────────────────────────────────────
    col_pain, col_market, col_build = st.columns(3)

    # ── PAIN ──────────────────────────────────────────────────────────────────
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
            sam_raw = _parse_tam(o.get("sam_usd_estimate"))
            som_raw = _parse_tam(o.get("som_usd_estimate"))
            _funnel_fig, _has_est = tam_funnel_chart(tam_raw, sam_raw, som_raw)
            st.plotly_chart(
                _funnel_fig,
                use_container_width=True,
                key=f"dd_tam_{opp_id}",
            )
            if _has_est:
                st.caption("(est.) = modeled at 12% TAM / 18% SAM — not field-validated")
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

    # ── Scoring breakdown + Actions ────────────────────────────────────────────
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
        research_check_fields = [
            "pain_validation_score", "exact_customer_phrases",
            "first_10_customer_path", "distribution_validated",
        ]
        has_research = any(o.get(f) for f in research_check_fields)

        st.html(f"""
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
</div>""")

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
                    st.session_state[f"super_val_{opp_id}"] = (ok, out)
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
                    st.session_state[f"super_res_{opp_id}"] = (ok, out)
                    st.cache_data.clear()

        is_liked = bool(o.get("liked_at"))
        like_btn = st.button(
            "♥ Liked — marked for build" if is_liked else "♡ Like — mark for build",
            key="btn_like_super",
            use_container_width=True,
            disabled=is_liked,
            help="Sets the conviction flag (liked_at + recommendation=build). "
                 "Then use Download Report below, or `opp-os kickoff` for a Claude Code starter pack.",
        )
        if like_btn:
            if not opp_id:
                st.error("No ID — cannot like.")
            else:
                ok, out = _run_subprocess(
                    ["uv", "run", "--no-sync", "opp-os", "like", opp_id],
                    "Like",
                )
                st.session_state[f"super_like_{opp_id}"] = (ok, out)
                st.cache_data.clear()
                st.rerun()

        from opportunity_os.export_report import build_opportunity_report_md, find_attached_reports
        report_md = build_opportunity_report_md(o, find_attached_reports(opp_id)) if opp_id else ""
        st.download_button(
            "⬇ Download Full Report (.md)",
            data=report_md,
            file_name=f"{(opp_id or 'opportunity')[:50]}-report.md",
            mime="text/markdown",
            key="btn_dl_report_super",
            use_container_width=True,
            help="Self-contained markdown: scoring breakdown, evidence, market data, "
                 "risks, plus any validation/deep-dive reports on disk.",
        )

        for sess_key, label in [
            (f"super_val_{opp_id}", "Validation"),
            (f"super_res_{opp_id}", "Research"),
            (f"super_like_{opp_id}", "Like"),
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

        # ── Kill Gate ─────────────────────────────────────────────────────────
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
            ("Pain in 1 sentence?",  bool(o.get("problem_statement", ""))),
            ("Named buyer?",          bool(o.get("target_customer"))),
            ("CAC cheap enough?",     bool(o.get("estimated_cac_logic"))),
            ("Revenue < 90 days?",    bool(
                o.get("path_to_first_revenue_description") or o.get("path_to_first_revenue")
            )),
            ("Speed to MVP score ≥ 6",     (
                o.get("speed_to_mvp") is not None
                and float(o.get("speed_to_mvp") or 0) >= 6
            )),
            ("TAM > $10M?",           bool(tam_raw) and float(tam_raw) > 10_000_000),
            ("Has wedge?",            (
                bool(o.get("benchmark_archetype"))
                or float(o.get("daniels_wedge_score") or 0) >= 2
            )),
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

        # ── Decision Filters ──────────────────────────────────────────────────
        _COMPOUND = {
            "local_clone", "workflow_unbundling", "smb_operating_system",
            "fragmented_supply_marketplace", "ai_operator_replacement",
        }
        _df_stored = o.get("decision_filter_results") or {}
        _FILTERS = [
            ("Sell fast (< 2 wks)?", _df_stored.get("can_sell_fast",
                o.get("distribution_validated") is True)),
            ("Build lean (< $2K)?",  _df_stored.get("can_build_lean",
                o.get("capital_efficiency") is not None
                and float(o.get("capital_efficiency") or 0) >= 6)),
            ("Can compound?",        _df_stored.get("can_compound",
                (o.get("benchmark_archetype") or "") in _COMPOUND)),
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

    # ── Every Variable — Full Reasoning (per-dimension deep breakdown) ──────────
    st.divider()
    _render_full_scoring_breakdown(o)

    # ── Decision Memo ──────────────────────────────────────────────────────────
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

    _wedge_names = [
        "Growth & GTM", "Narrative", "LATAM intuition",
        "Fintech/crypto", "Speed to build", "Distribution",
    ]
    _wedge_n = int(o.get("daniels_wedge_score") or 0)
    _wedge_list = _wedge_names[:_wedge_n]
    _why_now = o.get("why_now") or str(o.get("timing_tailwind") or "—")
    _frp = o.get("path_to_first_revenue_description") or str(o.get("path_to_first_revenue") or "—")
    _risks = o.get("kill_reasons") or []
    _sam_raw = o.get("sam_usd_estimate")
    _som_raw = o.get("som_usd_estimate")

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
        _bc = "#22C55E" if _conv >= 85 else "#3B82F6" if _conv >= 65 else "#F59E0B"
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
