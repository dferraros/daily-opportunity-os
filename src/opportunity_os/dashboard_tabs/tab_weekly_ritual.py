"""Tab 5: Weekly Ritual — quota check, rising signals, validation queue, kill candidates."""

from datetime import datetime, timedelta

import streamlit as st

from .components import GEO_LABELS, SCORE_FIELD, section_header, subsection
from .data import load_machine_metrics


def tab_weekly_ritual(opps, quotas):
    import pandas as pd  # noqa: F401 — available for callers

    st.markdown(section_header("Weekly Ritual"), unsafe_allow_html=True)

    active = [o for o in opps if not o.get("kill_decision", False)]
    sorted_opps = sorted(
        active, key=lambda o: float(o.get(SCORE_FIELD) or 0), reverse=True
    )

    weekly_q = quotas.get("weekly_quotas", {})
    validation_target = weekly_q.get("validations_run", {}).get("target", 2)
    metrics_list = load_machine_metrics()

    # Count validations completed this week
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    validations_done = 0
    for m in metrics_list:
        if m.get("date", "") >= week_ago:
            validations_done += int(m.get("opportunities_validated_pass", 0) or 0)

    # ── Interview quota indicator ──────────────────────────────────────────────
    quota_met = validations_done >= validation_target
    if quota_met:
        st.success(
            f"Validation quota met: {validations_done} / {validation_target} this week"
        )
    else:
        st.error(
            f"Validation quota BEHIND: {validations_done} / {validation_target} this week"
            " — run validation-runner on top opps"
        )

    st.divider()

    col1, col2 = st.columns(2)

    # ── Rising signals ─────────────────────────────────────────────────────────
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
                score = float(o.get(SCORE_FIELD) or 0)
                st.markdown(
                    f"- **{o.get('name', '—')}** — +{delta:.2f} · Score: `{score:.2f}`"
                )

    # ── Top 3 to validate ─────────────────────────────────────────────────────
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
                    f"- **{o.get('name', '—')}** — Score: `{score:.2f}`"
                    f" · {geo} · Lane: `{o.get('portfolio_lane', '—')}`"
                )
                if o.get("path_to_first_revenue"):
                    st.caption(f"  Path: {str(o.get('path_to_first_revenue'))[:120]}…")

    st.divider()

    col3, col4 = st.columns(2)

    # ── Kill candidates ────────────────────────────────────────────────────────
    with col3:
        st.markdown(subsection("Candidates to Kill (score < 4.0)"), unsafe_allow_html=True)
        kill_candidates = sorted(
            [o for o in active if float(o.get(SCORE_FIELD) or 0) < 4.0],
            key=lambda o: float(o.get(SCORE_FIELD) or 0),
        )
        if not kill_candidates:
            st.success("No low-score opportunities to kill.")
        else:
            for o in kill_candidates[:5]:
                score = float(o.get(SCORE_FIELD) or 0)
                st.markdown(
                    f"- **{o.get('name', '—')}** — Score: `{score:.2f}`"
                    f" · Stage: `{o.get('stage', '—')}`"
                )

    # ── Conviction area ────────────────────────────────────────────────────────
    with col4:
        st.markdown(subsection("This Week's Conviction Area"), unsafe_allow_html=True)
        ve_opps = [
            o for o in sorted_opps
            if (o.get("geography") or "") == "venezuela"
        ]
        if ve_opps:
            top_ve = ve_opps[0]
            st.info(
                f"**Venezuela — {top_ve.get('name', '—')}**\n\n"
                f"{(top_ve.get('problem_statement') or '')[:200]}"
            )
        elif sorted_opps:
            top = sorted_opps[0]
            geo_label = GEO_LABELS.get(top.get("geography", ""), top.get("geography", ""))
            st.info(
                f"**{geo_label} — {top.get('name', '—')}**\n\n"
                f"{(top.get('problem_statement') or '')[:200]}"
            )
        else:
            st.info("No opportunities loaded yet.")

    st.divider()

    # ── Weekly pipeline summary ────────────────────────────────────────────────
    st.markdown(subsection("Weekly Pipeline Summary (last 7 days)"), unsafe_allow_html=True)
    if not metrics_list:
        st.info("No machine metrics yet.")
        return

    recent_metrics = [m for m in metrics_list if m.get("date", "") >= week_ago]
    if not recent_metrics:
        st.info("No metrics recorded in the last 7 days.")
        return

    totals = {
        "Signals ingested":       sum(m.get("signals_ingested", 0) for m in recent_metrics),
        "Opportunities scored":   sum(m.get("opportunities_scored", 0) for m in recent_metrics),
        "Killed":                 sum(m.get("opportunities_killed", 0) for m in recent_metrics),
        "Promoted to validation": sum(m.get("opportunities_promoted_to_validation", 0) for m in recent_metrics),
        "Validated (pass)":       sum(m.get("opportunities_validated_pass", 0) for m in recent_metrics),
        "Deep dives":             sum(m.get("deep_dives_produced", 0) for m in recent_metrics),
    }
    targets = {
        "Signals ingested":       weekly_q.get("signals_ingested", {}).get("target", 40),
        "Opportunities scored":   weekly_q.get("structured_opportunities", {}).get("target", 10),
        "Deep dives":             weekly_q.get("deep_dives_produced", {}).get("target", 3),
        "Promoted to validation": weekly_q.get("validations_run", {}).get("target", 2),
    }

    cols = st.columns(len(totals))
    for col, (label, value) in zip(cols, totals.items()):
        target = targets.get(label)
        if target:
            delta = value - target
            col.metric(
                label, value,
                delta=f"{delta:+d} vs target",
                delta_color="normal" if delta >= 0 else "inverse",
            )
        else:
            col.metric(label, value)
