"""Sidebar renderer for Opportunity OS dashboard."""

import os
import subprocess

import streamlit as st

from .components import fmt_ts, get_last_run_ts
from .data import PROJECT_ROOT


def render_sidebar(runs) -> tuple:
    """Render the sidebar; return (geo_filter, score_range)."""
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
        st.markdown(
            '<div style="padding:0 4px;font-family:JetBrains Mono,monospace;font-size:8px;'
            'color:#1F2937;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">ACTIONS</div>',
            unsafe_allow_html=True,
        )

        if st.button("▶  Run Daily Pipeline"):
            with st.spinner("Running pipeline…"):
                try:
                    env = {**os.environ, "UV_LINK_MODE": "copy"}
                    result = subprocess.run(
                        ["uv", "run", "--no-sync", "opp-os", "daily"],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True,
                        timeout=300,
                        env=env,
                    )
                    if result.returncode == 0:
                        st.success("Pipeline complete.")
                        if result.stdout:
                            st.code(result.stdout[-1000:], language="text")
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
            st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

        # Filters section
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="padding:0 4px;font-family:JetBrains Mono,monospace;font-size:10px;'
            'color:#3F3F46;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:8px;'
            'border-top:1px solid rgba(255,255,255,0.05);padding-top:16px">Filters</div>',
            unsafe_allow_html=True,
        )

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
        st.markdown(
            '<div style="position:absolute;bottom:16px;left:16px;font-family:JetBrains Mono,monospace;'
            'font-size:8px;color:#1F2937;letter-spacing:1px">OPP-OS v1 · STREAMLIT</div>',
            unsafe_allow_html=True,
        )

    return geo_filter, score_range
