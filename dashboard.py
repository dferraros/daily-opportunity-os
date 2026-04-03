"""
Opportunity OS Dashboard — interactive explorer for all scored opportunities.

Run: streamlit run dashboard.py --server.port 8502
     (from project root: C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os/)
"""

import json
import os
from pathlib import Path
from datetime import datetime, date

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Opportunity OS",
    page_icon="★",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _project_root() -> Path:
    current = Path(__file__).resolve().parent
    if (current / "pyproject.toml").exists():
        return current
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current


def load_opportunities() -> list[dict]:
    """Load all opportunities from JSONL. No caching — file changes on every daily run."""
    root = _project_root()
    jsonl_path = root / "data" / "opportunities" / "opportunities.jsonl"
    if not jsonl_path.exists():
        return []
    opps = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    opps.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return opps


def load_interview_status() -> dict:
    """Load interview tracker data."""
    root = _project_root()
    try:
        sys_path_backup = __import__("sys").path[:]
        __import__("sys").path.insert(0, str(root / "src"))
        from opportunity_os.interview_tracker import get_interview_quota_status
        return get_interview_quota_status()
    except Exception:
        return {"completed": 0, "total_required": 15, "on_track": False, "days_remaining": 0}


def load_calibration_report() -> dict:
    """Load outcome calibration data."""
    root = _project_root()
    outcome_file = root / "data" / "outcome_tracking.jsonl"
    if not outcome_file.exists():
        return {"total_tracked": 0, "score_accuracy": 0.0}
    try:
        __import__("sys").path.insert(0, str(root / "src"))
        from opportunity_os.outcome_tracking import get_calibration_report
        return get_calibration_report()
    except Exception:
        return {"total_tracked": 0, "score_accuracy": 0.0}


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(opps: list[dict]) -> list[dict]:
    st.sidebar.title("★ Opportunity OS")
    st.sidebar.markdown("---")

    # Filters
    geos = sorted(set(o.get("geography", "global") for o in opps))
    sel_geo = st.sidebar.multiselect("Geography", geos, default=geos)

    lanes = sorted(set(o.get("portfolio_lane", "strategic") for o in opps if o.get("portfolio_lane")))
    sel_lane = st.sidebar.multiselect("Portfolio Lane", lanes, default=lanes)

    buckets = sorted(set(o.get("bucket", "venture_scale") for o in opps if o.get("bucket")))
    sel_bucket = st.sidebar.multiselect("Bucket", buckets, default=buckets)

    stages = sorted(set(o.get("stage", "scout") for o in opps if o.get("stage")))
    sel_stage = st.sidebar.multiselect("Stage", stages, default=stages)

    score_min, score_max = st.sidebar.slider(
        "Score range", min_value=0.0, max_value=10.0,
        value=(0.0, 10.0), step=0.1
    )

    show_killed = st.sidebar.checkbox("Show killed opportunities", value=False)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"*Last refreshed: {datetime.now().strftime('%H:%M:%S')}*")
    if st.sidebar.button("Refresh data"):
        st.rerun()

    # Apply filters
    filtered = opps
    if sel_geo:
        filtered = [o for o in filtered if o.get("geography", "global") in sel_geo]
    if sel_lane:
        filtered = [o for o in filtered if o.get("portfolio_lane", "strategic") in sel_lane]
    if sel_bucket:
        filtered = [o for o in filtered if o.get("bucket", "venture_scale") in sel_bucket]
    if sel_stage:
        filtered = [o for o in filtered if o.get("stage", "scout") in sel_stage]
    filtered = [o for o in filtered if score_min <= float(o.get("final_score") or 0) <= score_max]
    if not show_killed:
        filtered = [o for o in filtered if not o.get("kill_decision")]
    return sorted(filtered, key=lambda x: float(x.get("final_score") or 0), reverse=True)


# ── Metrics row ───────────────────────────────────────────────────────────────

def render_metrics(opps: list[dict], all_opps: list[dict]):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    live = [o for o in all_opps if not o.get("kill_decision")]
    now_lane = [o for o in live if o.get("portfolio_lane") == "now"]
    ve_opps = [o for o in live if o.get("geography") == "venezuela"]
    validation_opps = [o for o in live if o.get("stage") == "validation"]
    researched = [o for o in live if o.get("research_executed_at")]
    ai_scored = [o for o in live if o.get("ai_scored_at")]

    c1.metric("Total Live", len(live), delta=f"{len(all_opps)} total")
    c2.metric("Showing", len(opps))
    c3.metric("Now Lane", len(now_lane), delta="act within 30d")
    c4.metric("Venezuela", len(ve_opps))
    c5.metric("Validation", len(validation_opps))
    c6.metric("Researched", len(researched), delta=f"{len(ai_scored)} AI-scored")


# ── Ranked table ──────────────────────────────────────────────────────────────

def render_table(opps: list[dict]) -> int | None:
    """Render ranked table. Returns index of selected opp (or None)."""
    if not opps:
        st.info("No opportunities match the current filters.")
        return None

    import pandas as pd

    rows = []
    for i, o in enumerate(opps):
        score = float(o.get("final_score") or 0)
        pain = o.get("pain_severity") or 0
        comp = o.get("competition_intensity") or 0
        researched = "yes" if o.get("research_executed_at") else ""
        validated = "yes" if o.get("distribution_validated") else ""
        rows.append({
            "#": i + 1,
            "Name": (o.get("name") or "")[:55],
            "Score": round(score, 2),
            "Lane": o.get("portfolio_lane") or "",
            "Geo": o.get("geography") or "",
            "Bucket": o.get("bucket") or "",
            "Stage": o.get("stage") or "",
            "Pain": pain,
            "Comp": comp,
            "Researched": researched,
            "Validated": validated,
        })

    df = pd.DataFrame(rows)
    selected = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Score": st.column_config.NumberColumn(format="%.2f"),
            "Pain": st.column_config.NumberColumn(format="%d"),
            "Comp": st.column_config.NumberColumn(format="%d"),
        }
    )

    if selected and selected.selection.rows:
        return selected.selection.rows[0]
    return None


# ── Detail view ───────────────────────────────────────────────────────────────

DIMENSIONS = [
    "pain_severity", "market_size", "timing_tailwind", "willingness_to_pay",
    "monetization_clarity", "speed_to_mvp", "capital_efficiency",
    "distribution_accessibility", "competition_intensity", "defensibility",
    "regional_fit", "founder_fit", "ai_leverage", "operational_simplicity",
    "regulatory_simplicity", "revenue_speed_score",
]

DIM_LABELS = {
    "pain_severity": "Pain Severity",
    "market_size": "Market Size",
    "timing_tailwind": "Timing Tailwind",
    "willingness_to_pay": "Willingness to Pay",
    "monetization_clarity": "Monetization Clarity",
    "speed_to_mvp": "Speed to MVP",
    "capital_efficiency": "Capital Efficiency",
    "distribution_accessibility": "Distribution",
    "competition_intensity": "Competition (inv.)",
    "defensibility": "Defensibility",
    "regional_fit": "Regional Fit",
    "founder_fit": "Founder Fit",
    "ai_leverage": "AI Leverage",
    "operational_simplicity": "Ops Simplicity",
    "regulatory_simplicity": "Regulatory",
    "revenue_speed_score": "Revenue Speed",
}


def render_detail(opp: dict):
    score = float(opp.get("final_score") or 0)
    lane_colors = {"now": "green", "soon": "orange", "strategic": "blue", "no": "red"}
    lane = opp.get("portfolio_lane", "strategic")
    lane_color = lane_colors.get(lane, "gray")

    st.markdown(f"## {opp.get('name', 'Unknown Opportunity')}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Score", f"{score:.2f} / 10")
    col2.metric("Lane", f":{lane_color}[{lane.upper()}]")
    col3.metric("Geography", opp.get("geography", "—").title())
    col4.metric("Stage", opp.get("stage", "scout").title())

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", "Scores", "Research", "Validation", "Economics", "Operations"
    ])

    # ── Tab 1: Overview ────────────────────────────────────────────────────────
    with tab1:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown("**Problem Statement**")
            st.write(opp.get("problem_statement") or opp.get("description") or "—")

            st.markdown("**Why Now**")
            st.write(opp.get("why_now") or opp.get("why_now_venezuela") or "—")

            st.markdown("**Path to First Revenue**")
            st.write(opp.get("path_to_first_revenue") or opp.get("first_revenue_path") or "—")

            st.markdown("**Target Customer**")
            st.write(opp.get("target_customer") or "—")

        with col_b:
            st.markdown("**Quick Facts**")
            facts = {
                "Bucket": opp.get("bucket") or "—",
                "Vertical": opp.get("vertical") or "—",
                "Wedge": opp.get("venezuela_wedge_category") or "—",
                "Kill Decision": "YES" if opp.get("kill_decision") else "No",
                "Kill Reason": opp.get("kill_reason") or "—",
                "First Seen": opp.get("first_seen") or "—",
                "AI Scored": opp.get("ai_scored_at") or "heuristic",
                "Researched": opp.get("research_executed_at") or "not yet",
            }
            for k, v in facts.items():
                st.markdown(f"- **{k}**: {v}")

    # ── Tab 2: Scores ──────────────────────────────────────────────────────────
    with tab2:
        import plotly.graph_objects as go

        scores_data = [(DIM_LABELS.get(d, d), opp.get(d) or 0, opp.get(f"{d}_reason") or "") for d in DIMENSIONS]
        scores_data.sort(key=lambda x: x[1])

        fig = go.Figure(go.Bar(
            x=[s[1] for s in scores_data],
            y=[s[0] for s in scores_data],
            orientation="h",
            text=[str(s[1]) for s in scores_data],
            textposition="outside",
            marker_color=[
                "#ef4444" if s[1] < 4 else "#f97316" if s[1] < 6 else "#22c55e" if s[1] >= 8 else "#3b82f6"
                for s in scores_data
            ],
        ))
        fig.update_layout(
            height=500,
            xaxis=dict(range=[0, 10.5], title="Score (1-10)"),
            margin=dict(l=10, r=60, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Dimension Reasoning**")
        for dim, score_val, reason in scores_data:
            if reason:
                st.markdown(f"- **{dim}** ({score_val}): {reason}")

    # ── Tab 3: Research ────────────────────────────────────────────────────────
    with tab3:
        if not opp.get("research_executed_at"):
            st.warning("No research executed yet. Run `scripts/run_research_backfill.py` to populate.")
        else:
            st.success(f"Researched: {opp.get('research_executed_at')[:10]}")

        col_pain, col_dist = st.columns(2)

        with col_pain:
            st.markdown("### Pain Validation")
            pain_score = opp.get("pain_validation_score")
            if pain_score is not None:
                color = "green" if pain_score >= 7 else "orange" if pain_score >= 5 else "red"
                st.markdown(f"**Pain Score**: :{color}[{pain_score:.1f}/10]")
            else:
                st.markdown("**Pain Score**: *not yet researched*")

            st.markdown("**Exact Customer Phrases**")
            phrases = opp.get("exact_customer_phrases") or []
            if phrases:
                for p in phrases:
                    st.markdown(f"> *{p}*")
            else:
                st.write("—")

            st.markdown("**Workarounds Found**")
            workarounds = opp.get("workarounds_found") or []
            if workarounds:
                for w in workarounds:
                    st.markdown(f"- {w}")
            else:
                st.write("—")

            st.markdown("**Evidence Sources**")
            sources = opp.get("pain_evidence_sources") or []
            if sources:
                for s in sources:
                    st.markdown(f"- {s}")
            else:
                st.write("—")

        with col_dist:
            st.markdown("### Distribution Validation")
            dist_ok = opp.get("distribution_validated")
            if dist_ok is not None:
                st.markdown(f"**Validated**: {'yes' if dist_ok else 'no'}")
            else:
                st.markdown("**Validated**: *not yet researched*")

            st.markdown("**Top Channels**")
            channels = opp.get("top_distribution_channels") or []
            if channels:
                for c in channels:
                    st.markdown(f"- {c}")
            else:
                st.write("—")

            st.markdown("**Estimated CAC Logic**")
            st.write(opp.get("estimated_cac_logic") or "—")

            st.markdown("**First 10 Customers Path**")
            st.write(opp.get("first_10_customer_path") or "—")

            st.markdown("**Trust Mechanism (LATAM)**")
            st.write(opp.get("trust_mechanism_latam") or "—")

    # ── Tab 4: Validation ──────────────────────────────────────────────────────
    with tab4:
        stage = opp.get("stage", "scout")
        validation_status = opp.get("validation_status") or "pending"
        st.markdown(f"**Stage**: {stage.title()} | **Validation Status**: {validation_status.title()}")

        val_notes = opp.get("validation_notes")
        if val_notes:
            st.markdown("**Validation Notes**")
            st.write(val_notes)

        val_report = opp.get("validation_report") or opp.get("validation_markdown")
        if val_report:
            st.markdown("**Validation Report**")
            st.markdown(val_report)
        elif stage != "validation":
            st.info("Opportunity not yet in validation stage. Promote with `opp-os validate --id <id>` when ready.")
        else:
            root = _project_root()
            opp_id = opp.get("id", "")
            report_dir = root / "reports" / "validation"
            if report_dir.exists():
                matches = list(report_dir.glob(f"*{opp_id[:20]}*validation.md"))
                if matches:
                    with open(matches[0], encoding="utf-8") as f:
                        st.markdown(f.read())
                else:
                    st.write("No validation report file found.")
            else:
                st.write("No validation reports directory.")

    # ── Tab 5: Economics ───────────────────────────────────────────────────────
    with tab5:
        col_tam, col_bench = st.columns(2)

        with col_tam:
            st.markdown("### Market Size")
            tam = opp.get("tam") or opp.get("tam_usd_estimate")
            sam = opp.get("sam")
            som = opp.get("som")
            tam_method = opp.get("tam_method") or opp.get("tam_estimation_method")

            if tam:
                try:
                    tam_f = float(tam)
                    if tam_f >= 1e9:
                        tam_str = f"${tam_f/1e9:.1f}B"
                    elif tam_f >= 1e6:
                        tam_str = f"${tam_f/1e6:.0f}M"
                    else:
                        tam_str = f"${tam_f:,.0f}"
                    st.metric("TAM", tam_str)
                except (TypeError, ValueError):
                    st.metric("TAM", str(tam))
            else:
                st.metric("TAM", "—")

            if sam:
                try:
                    sam_f = float(sam)
                    sam_str = f"${sam_f/1e6:.0f}M" if sam_f >= 1e6 else f"${sam_f:,.0f}"
                    st.metric("SAM", sam_str)
                except Exception:
                    st.metric("SAM", str(sam))

            if som:
                try:
                    som_f = float(som)
                    som_str = f"${som_f/1e6:.1f}M" if som_f >= 1e6 else f"${som_f:,.0f}"
                    st.metric("SOM", som_str)
                except Exception:
                    st.metric("SOM", str(som))

            if tam_method:
                st.markdown(f"**TAM Method**: {tam_method}")

        with col_bench:
            st.markdown("### Benchmarks")
            archetype = opp.get("benchmark_archetype")
            competitors = opp.get("competitors_found")
            whitespace = opp.get("whitespace_note")
            executability = opp.get("executability_score")

            if archetype:
                st.markdown(f"**Archetype**: {archetype}")
            if executability:
                try:
                    st.metric("Executability Score", f"{float(executability):.2f}/10")
                except Exception:
                    pass
            if whitespace:
                st.markdown("**Whitespace Note**")
                st.write(whitespace)
            if competitors:
                st.markdown("**Competitors Found**")
                if isinstance(competitors, list):
                    for c in competitors:
                        st.markdown(f"- {c}")
                else:
                    st.write(competitors)
            if not any([archetype, competitors, whitespace]):
                st.info("Run `scripts/run_weekly_ritual.sh` or benchmark-mapper skill to populate.")

    # ── Tab 6: Operations ──────────────────────────────────────────────────────
    with tab6:
        st.markdown("### Interview Tracker")
        try:
            interview_data = load_interview_status()
            completed = interview_data.get("completed", 0)
            required = interview_data.get("total_required", 15)
            on_track = interview_data.get("on_track", False)
            days_left = interview_data.get("days_remaining", 0)

            pct = min(int(completed / max(required, 1) * 100), 100)
            color = "green" if on_track else "red"

            col_int1, col_int2, col_int3 = st.columns(3)
            col_int1.metric("Interviews Done", f"{completed}/{required}")
            col_int2.metric("Days Left", days_left)
            col_int3.metric("On Track", "YES" if on_track else "NO")

            st.progress(pct / 100, text=f"{pct}% complete — deadline 2026-04-08")
            if not on_track:
                needed_per_day = max((required - completed) / max(days_left, 1), 0)
                st.warning(f"Behind schedule. Need {needed_per_day:.1f} interviews/day to hit deadline.")
        except Exception as e:
            st.warning(f"Interview tracker data unavailable: {e}")

        st.markdown("---")
        st.markdown("### Score Calibration")
        try:
            cal = load_calibration_report()
            total_tracked = cal.get("total_tracked", 0)
            accuracy = cal.get("score_accuracy", 0.0)

            if total_tracked > 0:
                col_cal1, col_cal2 = st.columns(2)
                col_cal1.metric("Outcomes Tracked", total_tracked)
                col_cal2.metric("Score Accuracy", f"{accuracy:.0%}")
            else:
                st.info("No outcome tracking data yet. Use `opp-os outcome track --id <id> --result <pass/fail>` to start calibrating.")
        except Exception as e:
            st.warning(f"Calibration data unavailable: {e}")

        st.markdown("---")
        st.markdown("### Notion Sync Status")
        root = _project_root()
        import glob as glob_mod
        notion_files = sorted(glob_mod.glob(str(root / "reports" / "daily" / "*-notion-sync.json")))
        if notion_files:
            latest = notion_files[-1]
            mtime = datetime.fromtimestamp(os.path.getmtime(latest))
            st.markdown(f"**Latest payload**: `{os.path.basename(latest)}`")
            st.markdown(f"**Generated**: {mtime.strftime('%Y-%m-%d %H:%M')}")
            try:
                with open(latest, encoding="utf-8") as f:
                    payload = json.load(f)
                st.metric("Opps to upsert", len(payload.get("upsert_opps", [])))
            except Exception:
                pass
            st.info("To sync to Notion: run `scripts/notion_push.py` or ask Claude to fire the MCP calls from the JSON payload.")
        else:
            st.info("No Notion sync payloads found. Run `opp-os daily` to generate.")

        st.markdown("---")
        st.markdown("### Weekly Ritual")
        weekly_files = sorted(glob_mod.glob(str(root / "reports" / "weekly" / "*.md")))
        if weekly_files:
            latest_weekly = weekly_files[-1]
            mtime_w = datetime.fromtimestamp(os.path.getmtime(latest_weekly))
            st.markdown(f"**Latest weekly report**: `{os.path.basename(latest_weekly)}`")
            st.markdown(f"**Generated**: {mtime_w.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No weekly reports found. Invoke the weekly-review skill every Friday.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    all_opps = load_opportunities()

    if not all_opps:
        st.error("No opportunities found. Check that `data/opportunities/opportunities.jsonl` exists.")
        st.code("Run: PYTHONPATH=src uv run python -m opportunity_os.main daily")
        return

    filtered_opps = render_sidebar(all_opps)

    # Top metrics row
    st.markdown("## ★ Opportunity OS")
    render_metrics(filtered_opps, all_opps)
    st.markdown("---")

    # Main table
    st.markdown(f"### {len(filtered_opps)} Opportunities (sorted by score)")
    selected_idx = render_table(filtered_opps)

    # Detail view (shown when row is selected)
    if selected_idx is not None and selected_idx < len(filtered_opps):
        st.markdown("---")
        render_detail(filtered_opps[selected_idx])


if __name__ == "__main__":
    main()
