"""Tab 2: All Opportunities — searchable, filterable list with radar charts and deep-dive nav."""

import streamlit as st

from .components import (
    DIMENSION_FIELDS,
    GEO_LABELS,
    LANE_COLORS,
    SCORE_FIELD,
    radar_chart,
    section_header,
)
from .data import _parse_tam


def tab_all_opportunities(opps, geo_filter, score_range):
    import pandas as pd  # noqa: F401 — available for callers

    st.markdown(section_header("All Opportunities"), unsafe_allow_html=True)

    # Local filters
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

    # Apply sidebar geo + score first
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

    # Apply local filters
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

    # Sort by score descending
    filtered = sorted(
        filtered, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True
    )

    st.caption(f"Showing {len(filtered)} of {len(opps)} opportunities")

    if not filtered:
        st.info("No opportunities match the current filters.")
        return

    for opp_idx, o in enumerate(filtered):
        score = float(o.get(SCORE_FIELD) or 0)
        lane = o.get("portfolio_lane") or "—"
        geo = GEO_LABELS.get(o.get("geography", ""), o.get("geography", "—"))

        label = (
            f"{o.get('name', '—')}  ·  {geo}  ·  {score:.2f}/10"
            f"  ·  {lane}  ·  {o.get('stage', 'scout')}"
        )

        with st.expander(label, expanded=False):
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

                # TAM / SAM / SOM
                tam = _parse_tam(o.get("tam_usd_estimate") or o.get("tam"))
                sam = _parse_tam(o.get("sam_usd_estimate"))
                som = _parse_tam(o.get("som_usd_estimate"))
                if tam:
                    tam_str = f"${tam/1e6:.0f}M"
                    sam_str = f"${sam/1e6:.0f}M" if sam else "—"
                    som_str = f"${som/1e6:.0f}M" if som else "—"
                    st.markdown(
                        f"**TAM / SAM / SOM:** {tam_str} / {sam_str} / {som_str}"
                    )
                    if o.get("tam_rationale"):
                        st.caption(str(o.get("tam_rationale"))[:200])

            with c2:
                st.markdown("**Intelligence**")
                first_seen_val = o.get("first_seen") or ""
                discovered_label = str(first_seen_val)[:10] if first_seen_val else None
                intel = {
                    "Discovered": discovered_label,
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

            # Scores summary
            st.markdown(
                f"**Attractiveness:** {o.get('attractiveness_score', '—')} · "
                f"**Executability:** {o.get('executability_score', '—')} · "
                f"**Strategic Value:** {o.get('strategic_value_score', '—')}"
            )

            if o.get("ai_scored_at"):
                st.caption(
                    f"AI scored: {o.get('ai_scored_at')} · "
                    f"Venezuela lens: {'Yes' if o.get('venezuela_lens_applied') else 'No'}"
                )

            # Cross-tab deep dive navigation
            st.markdown("---")
            btn_col, hint_col = st.columns([1, 3])
            with btn_col:
                if st.button(
                    "📊 → Super Deep Dive",
                    key=f"goto_dd_{opp_idx}",
                    use_container_width=True,
                ):
                    st.session_state["deep_dive_opp_name"] = o.get("name")
                    st.session_state["active_tab_hint"] = True
            with hint_col:
                if (
                    st.session_state.get("active_tab_hint")
                    and st.session_state.get("deep_dive_opp_name") == o.get("name")
                ):
                    st.info(
                        "↑ Switch to the **Deep Dive** tab above to see the full intelligence brief."
                    )
