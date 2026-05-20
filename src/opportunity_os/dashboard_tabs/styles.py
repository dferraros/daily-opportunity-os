# Custom CSS — Intelligence Terminal Aesthetic for Opportunity OS dashboard

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #09090B;
    --surface: #18181B;
    --surface-2: #27272A;
    --border: rgba(255,255,255,0.06);
    --border-strong: rgba(255,255,255,0.10);
    --blue: #3B82F6;
    --blue-dim: rgba(59,130,246,0.10);
    --green: #22C55E;
    --red: #EF4444;
    --amber: #F59E0B;
    --text: #F4F4F5;
    --text-muted: #A1A1AA;
    --text-dim: #52525B;
}

/* ── Hide Streamlit chrome ── */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    color: var(--text-muted) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
}

/* ── App shell ── */
.stApp {
    background: var(--bg) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.025em !important;
    color: var(--text) !important;
}

/* Apply font only to actual text elements, not Streamlit internals */
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stText, .stCaption,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stExpander"] summary p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Streamlit 1.56 uses Material Symbols Rounded for expander toggle icons.
   Our .stApp font-family !important cascades down and breaks ligature rendering —
   keyboard_arrow_right becomes visible text instead of a glyph.
   Fix: restore the exact font on spans, then override <p> (the label) separately. */
[data-testid="stExpander"] summary span {
    font-family: 'Material Symbols Rounded' !important;
    font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' -25, 'opsz' 20 !important;
    font-size: 20px !important;
    line-height: 1 !important;
    user-select: none !important;
    -webkit-font-smoothing: antialiased !important;
}
/* Label paragraph and any inline spans inside it use the custom font, not icon font */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary p span {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* ── Tab nav ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em !important;
    text-transform: none !important;
    color: var(--text-dim) !important;
    padding: 10px 20px !important;
    background: transparent !important;
    border: none !important;
    transition: color 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-muted) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--blue) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--blue) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
}
[data-testid="metric-container"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 500 !important;
    color: var(--text) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stDataFrame"] th {
    background: var(--surface-2) !important;
    color: var(--text-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-strong) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
    margin-bottom: 6px !important;
    transition: border-color 0.15s ease !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-strong) !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    padding: 12px 16px !important;
}
/* Only the label text paragraph gets our custom font */
[data-testid="stExpander"] summary p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0C0C0E !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stWidgetLabel > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: var(--blue-dim) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    color: var(--blue) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 9px 0 !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.18) !important;
    border-color: var(--blue) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--blue) !important;
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: var(--text-dim) !important;
    font-size: 10px !important;
}

/* ── Global inputs ── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--surface) !important;
    border-color: var(--border-strong) !important;
}

[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

/* ── Alerts ── */
hr { border-color: var(--border) !important; }

[data-testid="stSuccess"] {
    background: rgba(34,197,94,0.07) !important;
    border-color: rgba(34,197,94,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stError"] {
    background: rgba(239,68,68,0.07) !important;
    border-color: rgba(239,68,68,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stInfo"] {
    background: var(--blue-dim) !important;
    border-color: rgba(59,130,246,0.3) !important;
    border-radius: 6px !important;
}
[data-testid="stWarning"] {
    background: rgba(245,158,11,0.07) !important;
    border-color: rgba(245,158,11,0.3) !important;
    border-radius: 6px !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-dim) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface-2); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }

/* ── Main content ── */
.stMainBlockContainer, [data-testid="stMainBlockContainer"],
section[data-testid="stMain"] > div:first-child {
    padding-top: 0px !important;
    padding-left: 32px !important;
    padding-right: 32px !important;
}

/* Small top clearance for the toolbar */
.stApp > section[data-testid="stMain"] {
    padding-top: 10px !important;
}
</style>
"""
