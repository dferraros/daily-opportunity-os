---
name: streamlit
description: Build interactive data dashboards and internal tools with Streamlit in Python. Use this skill when Daniel needs a quick web UI for data exploration, a live calculator (e.g. Growth Model simulator), a lifecycle dashboard, a campaign planner, or any internal tool that needs sliders, dropdowns, charts, and BigQuery data — without writing any HTML or JavaScript.
---

# Streamlit — Interactive Internal Tools

## What is Streamlit

Streamlit is a Python library that turns a plain `.py` script into a shareable web app. Every time the user interacts with a widget (slider, button, dropdown), Streamlit reruns the script from top to bottom and re-renders the output. No frontend knowledge required.

**Best use cases for Daniel:**
- Growth Model interactive calculator (NURR/CURR/RURR sliders → WAU/MMU/Revenue projections)
- Lifecycle dashboard fed from BigQuery with cached queries
- Campaign planner / A/B test sizing tool
- FOMO Score simulator
- Segment explorer (37 segments × filters)

**Install:**
```bash
pip install streamlit plotly pandas google-cloud-bigquery
streamlit run app.py
```

---

## Core Components Reference

### Text & Display
```python
import streamlit as st

st.title("Bit2Me Growth Model")          # Large H1
st.header("Weekly Projections")          # H2
st.subheader("Markov Buckets")           # H3
st.write("Any text, dataframe, or fig")  # Swiss-army display
st.markdown("**Bold**, _italic_, `code`")
st.caption("Small grey annotation")
st.divider()                             # Horizontal rule
```

### KPI Boxes
```python
# st.metric shows a number with an optional delta arrow
col1, col2, col3 = st.columns(3)
col1.metric("MMU", "23,000", delta="+1,200 vs last week")
col2.metric("WAU", "8,400", delta="-3%", delta_color="inverse")
col3.metric("Weekly Revenue", "€42,000", delta="+€6k")
```

### Input Widgets
```python
# Sidebar is the standard location for controls
with st.sidebar:
    st.header("Model Parameters")
    nurr = st.slider("NURR (New User Retention)", 0.0, 1.0, 0.45, step=0.01,
                     help="% of new users retained week-over-week")
    curr = st.slider("CURR (Core Retention)", 0.0, 1.0, 0.72)
    rurr = st.slider("RURR (Reactivation Rate)", 0.0, 1.0, 0.08)
    weeks = st.number_input("Projection Weeks", min_value=4, max_value=52, value=12)
    segment = st.selectbox("Segment Filter", ["All", "Spain", "LATAM", "Power Users"])
    scenario = st.radio("Scenario", ["Base", "Optimistic", "Conservative"])
    run = st.button("Recalculate", type="primary")
```

### Data Display
```python
import pandas as pd

df = pd.DataFrame({"Segment": ["New", "Active", "Dormant"], "Users": [5000, 12000, 72400]})

st.dataframe(df, use_container_width=True)   # Interactive, sortable
st.table(df)                                  # Static, clean
st.json({"mmu": 23000, "wau": 8400})          # Collapsible JSON viewer
```

### Charts (Plotly recommended)
```python
import plotly.graph_objects as go
import plotly.express as px

# Line chart
fig = px.line(df_projections, x="week", y=["wau_base", "wau_optimistic"],
              title="12-Week WAU Projection",
              labels={"value": "Weekly Active Users", "week": "Week"})
fig.update_layout(legend_title="Scenario")
st.plotly_chart(fig, use_container_width=True)

# Bar chart
fig2 = px.bar(df_buckets, x="bucket", y="users", color="bucket",
              title="Markov Bucket Population")
st.plotly_chart(fig2, use_container_width=True)
```

### Layout
```python
# Columns
col1, col2 = st.columns(2)
with col1:
    st.metric("Base WAU", "8,400")
with col2:
    st.metric("Optimistic WAU", "11,200")

# Columns with custom widths (ratio)
left, right = st.columns([1, 3])

# Expander (collapsible section)
with st.expander("Show raw data"):
    st.dataframe(df)

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Projections", "Segments"])
with tab1:
    st.write("Dashboard content here")
```

---

## BigQuery Integration

```python
from google.cloud import bigquery
import streamlit as st
import pandas as pd

# Credentials: store in .streamlit/secrets.toml (never commit to git)
# [gcp]
# project = "bit2me-data"
# credentials = { ... service account JSON ... }

@st.cache_data(ttl=3600)  # Cache for 1 hour — critical for expensive BQ queries
def load_lifecycle_data() -> pd.DataFrame:
    """Pull current user counts per lifecycle stage from BigQuery Gold Layer."""
    client = bigquery.Client(project=st.secrets["gcp"]["project"])
    query = """
        SELECT
            lifecycle_stage,
            COUNT(*) AS user_count,
            SUM(balance_eur) AS total_auc
        FROM `bit2me_lifecycle.v_user_segments`
        WHERE snapshot_date = CURRENT_DATE()
        GROUP BY lifecycle_stage
        ORDER BY user_count DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=900)   # 15-min cache for near-realtime metrics
def load_weekly_revenue(weeks_back: int = 12) -> pd.DataFrame:
    client = bigquery.Client(project=st.secrets["gcp"]["project"])
    query = f"""
        SELECT week_start, revenue_eur, mmu, wau
        FROM `bit2me_lifecycle.v_weekly_kpis`
        WHERE week_start >= DATE_SUB(CURRENT_DATE(), INTERVAL {weeks_back} WEEK)
        ORDER BY week_start
    """
    return client.query(query).to_dataframe()

# Usage in app
df_stages = load_lifecycle_data()
st.dataframe(df_stages)

# Force cache refresh
if st.button("Refresh data from BigQuery"):
    st.cache_data.clear()
    st.rerun()
```

**Secrets file** (`.streamlit/secrets.toml`, git-ignored):
```toml
[gcp]
project = "bit2me-data"

[gcp.credentials]
type = "service_account"
project_id = "bit2me-data"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "streamlit@bit2me-data.iam.gserviceaccount.com"
```

---

## Complete Example: Bit2Me Growth Model Simulator

Save as `growth_model_app.py` and run with `streamlit run growth_model_app.py`.

```python
"""
Bit2Me Growth Model — Interactive Simulator
Markov chain model: 7 lifecycle buckets, weekly transitions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- Page config (must be first Streamlit call) ---
st.set_page_config(
    page_title="Bit2Me Growth Model",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Constants: current population baseline (Mar 2026) ---
BASELINE_BUCKETS = {
    "New (W0)":         5_000,
    "Retained (W1-4)":  8_000,
    "Active (W5-12)":  10_000,
    "Power (W13+)":     4_000,
    "Near-Dormant":    15_000,
    "Dormant-Bal":     72_400,
    "Dormant-Zero":   285_000,
}

ARPU = {
    "New (W0)":          2.0,
    "Retained (W1-4)":   8.5,
    "Active (W5-12)":   18.0,
    "Power (W13+)":     45.0,
    "Near-Dormant":      3.0,
    "Dormant-Bal":       0.5,
    "Dormant-Zero":      0.0,
}

def run_markov(buckets: dict, nurr: float, curr: float, rurr: float,
               iwaurr: float, surr: float, weeks: int) -> pd.DataFrame:
    """
    Simplified 7-bucket Markov model.
    Returns a DataFrame with one row per week, columns = bucket names + totals.

    Transitions (simplified):
    - New → Retained at rate NURR; rest churn to Dormant-Zero
    - Retained → Active at rate CURR; rest fall to Near-Dormant
    - Active → Power at 5%; rest stay Active (CURR) or fall Near-Dormant
    - Power → Active (churn back) at 2%
    - Near-Dormant → Retained at rate IWAURR; rest deepen dormancy
    - Dormant-Bal → Near-Dormant at rate RURR
    - New users injected each week at SURR * current_new
    """
    records = []
    b = {k: float(v) for k, v in buckets.items()}

    for w in range(weeks + 1):
        wau = (b["New (W0)"] + b["Retained (W1-4)"] +
               b["Active (W5-12)"] + b["Power (W13+)"])
        mmu = wau  # simplified: WAU ≈ MMU for active buckets
        revenue = sum(b[k] * ARPU[k] for k in b)

        records.append({
            "week": w,
            **b,
            "WAU": wau,
            "MMU": mmu,
            "Weekly_Revenue_EUR": revenue,
        })

        if w == weeks:
            break

        # Transitions
        new_to_retained   = b["New (W0)"] * nurr
        retained_to_active = b["Retained (W1-4)"] * curr
        active_to_power   = b["Active (W5-12)"] * 0.05
        power_churn       = b["Power (W13+)"] * 0.02
        near_to_retained  = b["Near-Dormant"] * iwaurr
        dorm_to_near      = b["Dormant-Bal"] * rurr
        new_users_injected = b["New (W0)"] * surr

        b_new = {
            "New (W0)":        new_users_injected,
            "Retained (W1-4)": new_to_retained + near_to_retained,
            "Active (W5-12)":  retained_to_active + power_churn,
            "Power (W13+)":    b["Power (W13+)"] * 0.98 + active_to_power,
            "Near-Dormant":    b["Retained (W1-4)"] * (1 - curr) + dorm_to_near,
            "Dormant-Bal":     b["Dormant-Bal"] * (1 - rurr),
            "Dormant-Zero":    b["Dormant-Zero"] + b["New (W0)"] * (1 - nurr),
        }
        b = b_new

    return pd.DataFrame(records)


# =====================================================================
# SIDEBAR — Model Parameters
# =====================================================================
with st.sidebar:
    st.image("https://bit2me.com/favicon.ico", width=32)
    st.title("Growth Model")
    st.caption("Markov chain — 7 lifecycle buckets")
    st.divider()

    st.subheader("Transition Rates")
    nurr   = st.slider("NURR — New User Retention",       0.0, 1.0, 0.45, 0.01,
                        help="% of W0 users who become W1+ retained")
    curr   = st.slider("CURR — Core Retention",           0.0, 1.0, 0.72, 0.01,
                        help="% of Retained users who reach Active")
    rurr   = st.slider("RURR — Reactivation Rate",        0.0, 0.20, 0.03, 0.005,
                        help="% of Dormant-Bal users reactivated per week")
    iwaurr = st.slider("iWAURR — Near-Dormant Revival",   0.0, 0.30, 0.08, 0.01,
                        help="% of Near-Dormant users returning to Retained")
    surr   = st.slider("SURR — New User Supply Rate",     0.0, 2.0, 1.0, 0.05,
                        help="Multiplier on new user injection vs current cohort")

    st.divider()
    weeks  = st.number_input("Projection Weeks", 4, 52, 12)

    st.subheader("Scenario Comparison")
    show_optimistic = st.checkbox("Show Optimistic (+20% all rates)", value=True)
    show_conservative = st.checkbox("Show Conservative (-20% all rates)", value=False)


# =====================================================================
# MAIN — Run model
# =====================================================================
df_base = run_markov(BASELINE_BUCKETS, nurr, curr, rurr, iwaurr, surr, weeks)

# Optimistic: all rates +20% (capped at 1.0)
if show_optimistic:
    df_opt = run_markov(
        BASELINE_BUCKETS,
        min(nurr * 1.2, 1.0), min(curr * 1.2, 1.0),
        min(rurr * 1.2, 0.20), min(iwaurr * 1.2, 0.30), surr * 1.2,
        weeks
    )

if show_conservative:
    df_con = run_markov(
        BASELINE_BUCKETS,
        nurr * 0.8, curr * 0.8, rurr * 0.8, iwaurr * 0.8, surr * 0.8,
        weeks
    )

# =====================================================================
# HEADER
# =====================================================================
st.title("Bit2Me Growth Model Simulator")
st.caption(f"Baseline: Mar 2026 — {weeks}-week projection | Model: Markov 7-bucket")
st.divider()

# =====================================================================
# WEEK-0 KPI BOXES
# =====================================================================
w0 = df_base.iloc[0]
wN = df_base.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "WAU (Week 0)", f"{int(w0['WAU']):,}",
    delta=f"+{int(wN['WAU'] - w0['WAU']):,} by W{weeks}"
)
col2.metric(
    "MMU (Week 0)", f"{int(w0['MMU']):,}",
    delta=f"+{int(wN['MMU'] - w0['MMU']):,} by W{weeks}"
)
col3.metric(
    "Weekly Revenue (W0)", f"€{int(w0['Weekly_Revenue_EUR']):,}",
    delta=f"+€{int(wN['Weekly_Revenue_EUR'] - w0['Weekly_Revenue_EUR']):,}"
)
col4.metric(
    "Dormant-Bal", f"{int(w0['Dormant-Bal']):,}",
    delta=f"{int(wN['Dormant-Bal'] - w0['Dormant-Bal']):,}",
    delta_color="inverse"
)

st.divider()

# =====================================================================
# CHARTS
# =====================================================================
tab1, tab2, tab3 = st.tabs(["WAU / Revenue Projection", "Bucket Breakdown", "Scenario Compare"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_base["week"], y=df_base["WAU"],
        name="WAU (Base)", line=dict(color="#4C8BFF", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_base["week"], y=df_base["Weekly_Revenue_EUR"],
        name="Revenue EUR (Base)", line=dict(color="#00C49F", width=2),
        yaxis="y2"
    ))
    if show_optimistic:
        fig.add_trace(go.Scatter(
            x=df_opt["week"], y=df_opt["WAU"],
            name="WAU (Optimistic)", line=dict(color="#4C8BFF", dash="dash")
        ))
    if show_conservative:
        fig.add_trace(go.Scatter(
            x=df_con["week"], y=df_con["WAU"],
            name="WAU (Conservative)", line=dict(color="#FF6B6B", dash="dot")
        ))
    fig.update_layout(
        title=f"{weeks}-Week WAU & Revenue Projection",
        xaxis_title="Week",
        yaxis=dict(title="WAU"),
        yaxis2=dict(title="Weekly Revenue (EUR)", overlaying="y", side="right"),
        legend=dict(x=0, y=1),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    bucket_cols = list(BASELINE_BUCKETS.keys())
    df_long = df_base[["week"] + bucket_cols].melt(
        id_vars="week", var_name="Bucket", value_name="Users"
    )
    fig2 = px.area(
        df_long, x="week", y="Users", color="Bucket",
        title="Lifecycle Bucket Evolution",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    scenarios = {"Base": df_base}
    if show_optimistic:
        scenarios["Optimistic"] = df_opt
    if show_conservative:
        scenarios["Conservative"] = df_con

    metric_choice = st.selectbox("Metric", ["WAU", "MMU", "Weekly_Revenue_EUR"])
    fig3 = go.Figure()
    colors = {"Base": "#4C8BFF", "Optimistic": "#00C49F", "Conservative": "#FF6B6B"}
    for name, df_s in scenarios.items():
        fig3.add_trace(go.Scatter(
            x=df_s["week"], y=df_s[metric_choice],
            name=name, line=dict(color=colors[name], width=2)
        ))
    fig3.update_layout(title=f"Scenario Comparison — {metric_choice}", height=400)
    st.plotly_chart(fig3, use_container_width=True)

# =====================================================================
# BUCKET TABLE (Week N)
# =====================================================================
st.subheader(f"Bucket State at Week {weeks}")
bucket_data = []
for b in BASELINE_BUCKETS:
    w0_count = df_base.iloc[0][b]
    wN_count = df_base.iloc[-1][b]
    bucket_data.append({
        "Bucket": b,
        "Week 0": f"{int(w0_count):,}",
        f"Week {weeks}": f"{int(wN_count):,}",
        "Delta": f"{int(wN_count - w0_count):+,}",
        "ARPU (€/wk)": ARPU[b],
        f"Revenue W{weeks} (€)": f"{int(wN_count * ARPU[b]):,}",
    })
st.dataframe(pd.DataFrame(bucket_data), use_container_width=True, hide_index=True)

# =====================================================================
# RAW DATA (collapsible)
# =====================================================================
with st.expander("Show raw weekly data"):
    st.dataframe(df_base.round(0).astype(int, errors="ignore"), use_container_width=True)
    st.download_button(
        "Download CSV",
        df_base.to_csv(index=False).encode("utf-8"),
        file_name=f"growth_model_{weeks}weeks.csv",
        mime="text/csv"
    )
```

---

## Session State (Multi-Step Forms)

Use `st.session_state` when you need to preserve values across reruns (e.g., multi-page wizards, accumulated results).

```python
# Initialize once
if "test_results" not in st.session_state:
    st.session_state.test_results = []

# Append on button click
if st.button("Add test result"):
    st.session_state.test_results.append({"test": "T-001", "lift": 0.12})

# Display accumulated state
st.write(st.session_state.test_results)

# Clear state
if st.button("Reset"):
    st.session_state.test_results = []
    st.rerun()
```

---

## Progress & Status Feedback

```python
import time

# Progress bar for long computations
progress = st.progress(0, text="Running simulation...")
for i in range(100):
    time.sleep(0.01)
    progress.progress(i + 1, text=f"Week {i+1}/100 simulated")
progress.empty()  # Remove bar when done

# Status messages
st.success("Model ran successfully — 12 weeks projected.")
st.warning("NURR below 30% — model may be unstable.")
st.error("BigQuery connection failed. Check secrets.toml.")
st.info("Tip: use the Optimistic scenario to set OKR targets.")

# Spinner for blocking operations
with st.spinner("Fetching data from BigQuery..."):
    df = load_lifecycle_data()
```

---

## Deployment

### Local (development)
```bash
pip install streamlit
streamlit run growth_model_app.py
# Opens at http://localhost:8501
```

### Streamlit Community Cloud (free, public)
1. Push `app.py` + `requirements.txt` to a public GitHub repo.
2. Go to share.streamlit.io → "New app" → connect repo.
3. Add secrets in the Streamlit Cloud UI (Settings → Secrets).
4. App is live at `https://yourname-appname.streamlit.app`.

**requirements.txt:**
```
streamlit>=1.32.0
plotly>=5.18.0
pandas>=2.0.0
google-cloud-bigquery>=3.17.0
db-dtypes>=1.2.0
```

### Docker (internal/private deployment)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t bit2me-growth-model .
docker run -p 8501:8501 bit2me-growth-model
```

---

## Best Practices

### Performance
- Always use `@st.cache_data` on BigQuery queries. Without it, every slider move re-queries.
- Use `ttl=` (seconds) to set expiry: `ttl=3600` for hourly, `ttl=900` for 15-min.
- `@st.cache_resource` for objects that should not be serialized (e.g., database connections).

### Layout
- Put all controls in `st.sidebar` — keeps the main canvas clean for output.
- Use `st.columns` for side-by-side metrics; avoid deeply nested columns.
- Use `st.tabs` to segment long dashboards without scrolling.
- Set `layout="wide"` in `st.set_page_config` for dashboards with charts.

### UX
- Always add `help=` text to sliders — explains what the rate means to non-modelers.
- Use `st.metric` with `delta=` for any KPI that has a comparison value.
- `st.download_button` for any table the user might want to export.
- Add `st.caption` with last-refreshed timestamp on cached data.

### Error handling
```python
try:
    df = load_lifecycle_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()  # Halt execution — don't render broken charts below
```

### Mobile responsiveness
- Streamlit is not natively mobile-optimized. For internal desktop tools, this is fine.
- Avoid more than 4 columns — they collapse poorly on narrow screens.
- Use `use_container_width=True` on all charts and dataframes.

---

## When to Use Streamlit vs Alternatives

| Need | Tool | Why |
|------|------|-----|
| Quick internal tool, data exploration, prototypes | **Streamlit** | Fastest path from Python to web UI |
| ML model demo with a single prediction input | **Gradio** | Even simpler for single-input/output |
| Complex multi-chart dashboard with fine control | **Dash (Plotly)** | More control, steeper learning curve |
| Polished public-facing product | **React / Next.js** | Streamlit's UI is recognizable and not customizable |
| Static report / one-time export | **Jupyter + nbconvert** | No server needed |
| Exec presentation with animations | **frontend-slides skill** | HTML/CSS for visual impact |

---

## Quick-Start Checklist

- [ ] `pip install streamlit plotly pandas`
- [ ] `st.set_page_config(layout="wide")` as first call
- [ ] All controls in `st.sidebar`
- [ ] All BigQuery calls wrapped in `@st.cache_data(ttl=3600)`
- [ ] Credentials in `.streamlit/secrets.toml` (git-ignored)
- [ ] KPIs as `st.metric` with `delta=`
- [ ] Charts with `use_container_width=True`
- [ ] `st.error` + `st.stop()` on failure paths
- [ ] `st.download_button` on exportable tables
