"""Opportunity OS — Streamlit Dashboard (slim orchestrator)."""

import streamlit as st

# set_page_config MUST be first Streamlit call — before any submodule imports
# (submodule imports register @st.cache_data decorators)
st.set_page_config(
    page_title="Opportunity OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from opportunity_os.env import load_env_file  # noqa: E402
load_env_file()

from opportunity_os.dashboard_tabs.styles import CUSTOM_CSS  # noqa: E402
from opportunity_os.dashboard_tabs.data import (  # noqa: E402
    load_automation_runs,
    load_opportunities,
    load_weekly_quotas,
)
from opportunity_os.dashboard_tabs.components import SCORE_FIELD, apply_filters  # noqa: E402
from opportunity_os.dashboard_tabs.sidebar import render_sidebar  # noqa: E402
from opportunity_os.dashboard_tabs.tab_command_center import tab_command_center  # noqa: E402
from opportunity_os.dashboard_tabs.tab_all_opportunities import tab_all_opportunities  # noqa: E402
from opportunity_os.dashboard_tabs.tab_pipeline_health import tab_pipeline_health  # noqa: E402
from opportunity_os.dashboard_tabs.tab_venezuela_focus import tab_venezuela_focus  # noqa: E402
from opportunity_os.dashboard_tabs.tab_weekly_ritual import tab_weekly_ritual  # noqa: E402
from opportunity_os.dashboard_tabs.tab_deep_dive import tab_deep_dive  # noqa: E402


def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    all_opps = load_opportunities()
    runs = load_automation_runs()
    quotas = load_weekly_quotas()

    geo_filter, score_range = render_sidebar(runs)
    filtered_opps = apply_filters(all_opps, geo_filter, score_range[0], score_range[1])

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
        ve_filtered = [
            o for o in all_opps
            if (o.get("geography") or "").lower() == "venezuela"
            and score_range[0] <= float(o.get(SCORE_FIELD) or 0) <= score_range[1]
        ]
        tab_venezuela_focus(ve_filtered)

    with tabs[4]:
        tab_weekly_ritual(all_opps, quotas)

    with tabs[5]:
        tab_deep_dive(all_opps)


main()
