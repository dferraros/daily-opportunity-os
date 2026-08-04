"""Hypothesis Lab tab — submit your own idea, browse hypothesis-mode runs.

The idea-validation platform's front door (2026-08-04 audit: hypothesis mode
was fully built but invisible in the UI). Intake calls run_hypothesis live
(real API spend, ~$0.30-0.50/run) and is therefore gated behind an explicit
button + key check.
"""

import streamlit as st

VERDICT_STYLE = {
    "build": ("#22C55E", "BUILD"),
    "validate": ("#F59E0B", "VALIDATE"),
    "pivot_to_neighbor": ("#3B82F6", "PIVOT TO NEIGHBOR"),
    "drop_but_run_neighbor": ("#8B5CF6", "DROP — RUN NEIGHBOR"),
    "absorb_into_asset": ("#14B8A6", "ABSORB INTO ASSET"),
}


def _verdict_badge(verdict: str) -> str:
    color, label = VERDICT_STYLE.get(verdict or "", ("#6B7280", (verdict or "no verdict").upper()))
    return (
        f'<span style="background:{color}22;color:{color};padding:3px 10px;'
        f'border-radius:4px;font-weight:700;font-size:0.8rem">{label}</span>'
    )


def _legal_badge(opp: dict) -> str:
    if not opp.get("legal_opinion_required"):
        return ""
    return (
        '<span style="background:#EF444422;color:#EF4444;padding:3px 10px;'
        'border-radius:4px;font-weight:700;font-size:0.8rem">'
        '⚠ LEGAL OPINION REQUIRED — build blocked</span>'
    )


def _render_intake_form():
    st.subheader("Submit a hypothesis")
    st.caption(
        "The machine runs adversarial-first: neighborhood map, kill thesis, "
        "feasibility + legal interrogation, revenue evidence, then a verdict. "
        "Live API run (~$0.30–0.50)."
    )
    idea = st.text_area(
        "Your idea (free text — customer, problem, how they cope today, how you'd charge)",
        height=120,
        key="hypothesis_idea_input",
        placeholder=(
            "A reconciliation tool for Venezuelan distributors that receive payments "
            "via pago móvil, Zelle, USDT and cash, who currently match payments to "
            "invoices in spreadsheets..."
        ),
    )
    skip_research = st.checkbox(
        "Skip revenue-evidence search (faster/cheaper, less grounded verdict)",
        value=False, key="hypothesis_skip_research",
    )
    if st.button("Run hypothesis", type="primary", key="hypothesis_run_btn"):
        if not (idea or "").strip():
            st.error("Write the idea first.")
            return
        from opportunity_os.hypothesis_neighbors import _get_api_key
        if not _get_api_key():
            st.error("ANTHROPIC_API_KEY is not configured — hypothesis mode refuses to run on heuristics.")
            return
        with st.spinner("Running adversarial validation (2–5 min: neighborhood, kill thesis, feasibility, evidence, verdict)..."):
            try:
                from opportunity_os.hypothesis_mode import run_hypothesis
                result = run_hypothesis(idea, skip_research=skip_research)
            except (RuntimeError, ValueError) as exc:
                st.error(f"Hypothesis run failed: {exc}")
                return
        st.success(f"Verdict: {result['verdict'].upper()}")
        st.markdown(_verdict_badge(result["verdict"]), unsafe_allow_html=True)
        st.write(result["rationale"])
        if result.get("best_neighbor"):
            st.info(f"Best neighbor: {result['best_neighbor']}")
        st.caption(f"Report: {result['report_path']}")
        st.cache_data.clear()  # the new record must appear in the browser below


def _render_run_card(opp: dict):
    verdict = opp.get("hypothesis_verdict")
    header = f"{opp.get('name', '?')}  ·  {opp.get('geography', '?')} / {opp.get('vertical', '?')}"
    with st.expander(header, expanded=False):
        st.markdown(
            _verdict_badge(verdict) + "&nbsp;&nbsp;" + _legal_badge(opp),
            unsafe_allow_html=True,
        )
        st.write(opp.get("hypothesis_rationale") or "_No rationale recorded._")

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", f"{opp.get('final_score', '—')}")
        col2.metric("Kill thesis", f"{opp.get('kill_thesis_strength', '—')}/10")
        cov = opp.get("evidence_coverage")
        col3.metric("Evidence", f"{cov * 100:.0f}%" if cov is not None else "—")

        if opp.get("kill_thesis"):
            st.markdown(f"**Kill thesis:** {opp['kill_thesis']}")

        legal_flags = opp.get("legal_flags") or []
        if legal_flags:
            st.markdown("**Legal flags:**")
            for f in legal_flags:
                st.markdown(f"- {f}")

        neighborhood = opp.get("neighborhood") or []
        if neighborhood:
            st.markdown("**Neighborhood map:**")
            rows = [
                {
                    "Neighbor": n.get("name"),
                    "Axis": n.get("axis"),
                    "Mini-score": n.get("mini_score"),
                    "Thesis": n.get("thesis"),
                }
                for n in neighborhood
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if opp.get("best_neighbor"):
            st.info(f"Best neighbor: {opp['best_neighbor']}")

        unknowns = opp.get("hypothesis_key_unknowns") or []
        if unknowns:
            st.markdown("**Questions that cannot yet be answered:**")
            for u in unknowns:
                st.markdown(f"- {u}")


def tab_hypothesis_lab(all_opps: list):
    st.header("Hypothesis Lab")
    _render_intake_form()

    st.divider()
    st.subheader("Past hypothesis runs")
    runs = sorted(
        [o for o in all_opps if o.get("stage") == "hypothesis" or o.get("hypothesis_verdict")],
        key=lambda o: o.get("hypothesis_at") or "",
        reverse=True,
    )
    if not runs:
        st.caption("No hypothesis runs yet. Submit one above, or run `opp-os hypothesize \"<idea>\"`.")
        return
    for opp in runs:
        _render_run_card(opp)
