"""
dashboards/home/mockup2.py — Mission-Control Home MOCK-UP
──────────────────────────────────────────────────────────
Inspired by the "Data Product Accelerator" command-centre aesthetic.
Standalone, zero GCP dependency — all data is static/hardcoded.

Run:
    python -m dashboards.home.mockup2
    → http://localhost:7868
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from shared.theme import COLORS, PLOTLY_LAYOUT

# ─────────────────────────────────────────────────────────────
# MISSION CONTROL CSS — dark glow aesthetic
# ─────────────────────────────────────────────────────────────

MC_CSS = """
* { box-sizing: border-box; }

body, .gradio-container {
    background-color: #050505 !important;
    color: #E0E0E0 !important;
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
}

/* ── Panel cards with glow border ── */
.mc-panel {
    background: linear-gradient(145deg, #0A0A0A 0%, #111111 100%);
    border: 1px solid rgba(255,140,0,0.35);
    border-radius: 6px;
    padding: 14px;
    margin: 4px;
    box-shadow: 0 0 12px rgba(255,140,0,0.08), inset 0 0 20px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
.mc-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,0,0.6), transparent);
}

/* ── Section labels ── */
.mc-label {
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #FF8C00;
    font-weight: 700;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(255,140,0,0.2);
    padding-bottom: 6px;
}

/* ── KPI strip ── */
.mc-kpi-strip {
    display: flex;
    gap: 0;
    background: #060606;
    border: 1px solid rgba(255,140,0,0.3);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 6px;
}
.mc-kpi-cell {
    flex: 1;
    padding: 10px 14px;
    border-right: 1px solid rgba(255,140,0,0.15);
    text-align: center;
}
.mc-kpi-cell:last-child { border-right: none; }
.mc-kpi-val {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1;
}
.mc-kpi-lbl {
    font-size: 0.55rem;
    letter-spacing: 2px;
    color: #888;
    margin-top: 4px;
    text-transform: uppercase;
}
.col-orange { color: #FF8C00; }
.col-gold   { color: #FFD700; }
.col-green  { color: #00C851; }
.col-red    { color: #FF4444; }
.col-cyan   { color: #00BFFF; }

/* ── Status ticker ── */
.mc-ticker {
    display: flex;
    gap: 20px;
    align-items: center;
    background: #060606;
    border: 1px solid rgba(255,140,0,0.2);
    border-radius: 4px;
    padding: 7px 14px;
    font-size: 0.65rem;
    letter-spacing: 1px;
    color: #888;
    overflow: hidden;
}
.mc-ticker-item { display: flex; align-items: center; gap: 6px; }

/* ── Pulse dots ── */
@keyframes pulse-green {
    0%,100% { box-shadow: 0 0 4px #00C851; opacity:1; }
    50%      { box-shadow: 0 0 10px #00C851; opacity:0.6; }
}
@keyframes pulse-orange {
    0%,100% { box-shadow: 0 0 4px #FF8C00; opacity:1; }
    50%      { box-shadow: 0 0 10px #FF8C00; opacity:0.6; }
}
.pdot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
}
.pdot-green  { background:#00C851; animation: pulse-green  1.8s ease-in-out infinite; }
.pdot-orange { background:#FF8C00; animation: pulse-orange 2.2s ease-in-out infinite; }
.pdot-grey   { background:#444; }

/* ── Progress bar ── */
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
.mc-progress-wrap {
    margin-top: 6px;
    background: #111;
    border: 1px solid rgba(255,140,0,0.2);
    border-radius: 3px;
    height: 6px;
    overflow: hidden;
}
.mc-progress-bar {
    height: 100%;
    width: 72%;
    background: linear-gradient(90deg, #FF4444 0%, #FF8C00 30%, #FFD700 60%, #00C851 100%);
    background-size: 200% auto;
    animation: shimmer 2.5s linear infinite;
    border-radius: 3px;
}

/* ── Central hero ── */
.mc-hero {
    text-align: center;
    padding: 18px 10px 14px;
    position: relative;
}
.mc-hero-title {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #FF8C00;
    text-shadow: 0 0 20px rgba(255,140,0,0.5), 0 0 40px rgba(255,140,0,0.2);
    line-height: 1.15;
    margin-bottom: 4px;
}
.mc-hero-sub {
    font-size: 0.65rem;
    letter-spacing: 4px;
    color: #FFD700;
    text-transform: uppercase;
    text-shadow: 0 0 10px rgba(255,215,0,0.4);
}

/* ── Arrow glow ── */
@keyframes arrow-glow {
    0%,100% { filter: drop-shadow(0 0 6px #FF8C00) drop-shadow(0 0 12px rgba(255,140,0,0.4)); }
    50%      { filter: drop-shadow(0 0 12px #FFD700) drop-shadow(0 0 24px rgba(255,215,0,0.5)); }
}
.mc-arrow {
    font-size: 3.5rem;
    display: inline-block;
    animation: arrow-glow 2s ease-in-out infinite;
    line-height: 1;
    margin: 8px 0;
}

/* ── Table ── */
.mc-table { width: 100%; border-collapse: collapse; font-size: 0.7rem; }
.mc-table th {
    background: #111;
    color: #FF8C00;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 0.55rem;
    padding: 7px 8px;
    border-bottom: 1px solid rgba(255,140,0,0.25);
    text-align: left;
}
.mc-table td {
    padding: 7px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #C0C0C0;
}
.mc-table tr:hover td { background: rgba(255,140,0,0.04); }

/* ── Bar (funnel row) ── */
.funnel-row { margin-bottom: 6px; }
.funnel-bar-bg {
    background: #111;
    border-radius: 2px;
    height: 22px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,140,0,0.15);
}
.funnel-bar-fill {
    height: 100%;
    border-radius: 2px;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.funnel-label {
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    color: #888;
    text-transform: uppercase;
    margin-bottom: 3px;
    display: flex;
    justify-content: space-between;
}

/* Plotly transparent bg */
.js-plotly-plot .plotly { background: transparent !important; }

/* Gradio overrides */
.gradio-container { max-width: 100% !important; padding: 8px !important; }
footer { display: none !important; }
"""

# ─────────────────────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────────────────────

# Customer journey funnel
FUNNEL_STAGES = [
    ("AWARENESS",      1_000_000, "#FF4444",  "100%"),
    ("BROWSE / VISIT",   420_000, "#FF8C00",   "42%"),
    ("FIRST PURCHASE",   112_650, "#FFD700",  "11.3%"),
    ("REPEAT BUYER",      42_800, "#00C851",   "4.3%"),
    ("LOYAL CUSTOMER",    14_200, "#00BFFF",   "1.4%"),
]

# Daily orders last 30 days (realistic trend with weekend dips)
np.random.seed(42)
_days = pd.date_range("2026-02-12", periods=30)
_base = np.linspace(340, 420, 30) + np.sin(np.linspace(0, 6, 30)) * 30
_daily_orders = pd.DataFrame({
    "date":    _days,
    "orders":  (_base + np.random.normal(0, 18, 30)).clip(280).astype(int),
    "revenue": (_base * 1180 + np.random.normal(0, 15000, 30)).clip(300_000).astype(int),
})

# State data — customer count + seller count
_STATE_DATA = pd.DataFrame({
    "state":     ["SP","RJ","MG","RS","PR","SC","BA","GO","DF","PE","CE","PA","AM","MT","MS","ES","PB","RN","AL","PI","MA","SE","TO","AC","RO","RR","AP"],
    "customers": [41746,12852,11635,5466,5045,3637,3380,2755,2140,1650,1336,722,481,430,391,378,536,485,460,395,747,368,280,81,253,46,68],
    "sellers":   [17956,2725,2294,1312,1146,785,391,534,218,312,182,48,31,85,62,79,52,37,28,21,37,22,18,6,19,3,4],
})

# Pipeline feature status
PIPELINE_STATUS = [
    ("Meltano EL",        "CSV → GCS Bronze",     "LIVE",    "#00C851",  "100%"),
    ("dbt Silver",        "Cleanse & normalise",   "LIVE",    "#00C851",  "100%"),
    ("dbt Gold",          "Star schema (MERGE)",   "LIVE",    "#00C851",  "100%"),
    ("BigQuery Serving",  "6 domain datasets",     "LIVE",    "#00C851",   "96%"),
    ("Real-time Sim",     "Pub/Sub → Gold",        "ACTIVE",  "#FF8C00",   "72%"),
    ("Redis Cache",       "Dimension hot-cache",   "STANDBY", "#FFD700",   "45%"),
    ("Sentiment CF",      "Cloud Function (NLP)",  "PLANNED", "#888888",    "0%"),
]

# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────

_MC_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono, monospace", color="#A0A0A0", size=10),
    margin=dict(l=32, r=12, t=28, b=28),
    xaxis=dict(gridcolor="rgba(255,140,0,0.08)", linecolor="rgba(255,140,0,0.2)",
               zerolinecolor="rgba(255,140,0,0.1)", tickfont=dict(size=9)),
    yaxis=dict(gridcolor="rgba(255,140,0,0.08)", linecolor="rgba(255,140,0,0.2)",
               zerolinecolor="rgba(255,140,0,0.1)", tickfont=dict(size=9)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888", size=9)),
)


def _daily_orders_chart():
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_daily_orders["date"], y=_daily_orders["orders"],
        marker=dict(
            color=_daily_orders["orders"],
            colorscale=[[0, "rgba(255,68,68,0.6)"], [0.5, "rgba(255,140,0,0.7)"], [1, "rgba(0,200,81,0.8)"]],
            showscale=False,
            line=dict(width=0),
        ),
        name="Orders",
        hovertemplate="%{x|%b %d}: %{y:,} orders<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=_daily_orders["date"], y=_daily_orders["orders"].rolling(7, min_periods=1).mean(),
        mode="lines",
        line=dict(color="#FFD700", width=1.5, dash="dot"),
        name="7-day avg",
        hoverinfo="skip",
    ))
    fig.update_layout(
        **_MC_LAYOUT,
        title=dict(text="DAILY ORDER VOLUME", font=dict(color="#FF8C00", size=9, family="JetBrains Mono"), x=0),
        height=190,
        showlegend=False,
    )
    return fig


def _brazil_choropleth():
    fig = px.choropleth(
        _STATE_DATA,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations="state",
        featureidkey="properties.sigla",
        color="customers",
        color_continuous_scale=[
            [0.0, "rgba(255,68,68,0.3)"],
            [0.3, "rgba(255,140,0,0.6)"],
            [0.7, "rgba(255,215,0,0.8)"],
            [1.0, "rgba(0,200,81,1.0)"],
        ],
        hover_data={"customers": ":,", "sellers": ":,"},
        labels={"customers": "Customers"},
    )
    fig.update_geos(
        fitbounds="locations", visible=False,
        bgcolor="rgba(0,0,0,0)",
        landcolor="rgba(20,20,20,0.8)",
        showcoastlines=False,
    )
    layout = {**_MC_LAYOUT, "margin": dict(l=0, r=0, t=0, b=0)}
    fig.update_layout(
        **layout,
        height=280,
        coloraxis_showscale=False,
        coloraxis_colorbar=None,
    )
    return fig


def _seller_scatter():
    fig = px.scatter(
        _STATE_DATA,
        x="customers", y="sellers",
        text="state",
        size="customers",
        size_max=30,
        color="sellers",
        color_continuous_scale=[
            [0, "#FF4444"], [0.5, "#FF8C00"], [1, "#00C851"]
        ],
        labels={"customers": "Customers", "sellers": "Sellers"},
        hover_data={"state": True, "customers": ":,", "sellers": ":,"},
    )
    fig.update_traces(textposition="top center", textfont=dict(size=8, color="#FFD700"))
    fig.update_layout(
        **_MC_LAYOUT,
        title=dict(text="SELLER vs CUSTOMER DENSITY", font=dict(color="#FF8C00", size=9), x=0),
        height=190,
        showlegend=False,
        coloraxis_showscale=False,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# HTML BUILDERS
# ─────────────────────────────────────────────────────────────

def _kpi_strip():
    kpis = [
        ("112,650",  "TOTAL ORDERS",    "col-orange"),
        ("R$13.6M",  "TOTAL GMV",       "col-gold"),
        ("+11.2%",   "MRR GROWTH",      "col-green"),
        ("4.09 ★",   "AVG REVIEW",      "col-green"),
        ("3,095",    "ACTIVE SELLERS",  "col-orange"),
        ("87.3%",    "ON-TIME RATE",    "col-green"),
        ("12.8%",    "REPEAT RATE",     "col-cyan"),
    ]
    cells = "".join(f"""
    <div class="mc-kpi-cell">
        <div class="mc-kpi-val {cls}">{val}</div>
        <div class="mc-kpi-lbl">{lbl}</div>
    </div>""" for val, lbl, cls in kpis)
    return f'<div class="mc-kpi-strip">{cells}</div>'


def _ticker():
    items = [
        ("pdot-green",  "BATCH PIPELINE · ONLINE"),
        ("pdot-orange", "REAL-TIME · ACTIVE"),
        ("pdot-green",  "BIGQUERY · 6 DATASETS"),
        ("pdot-grey",   "REDIS CACHE · STANDBY"),
        ("pdot-green",  "dbt · LAST RUN 02:14 UTC"),
    ]
    parts = "".join(f"""
    <div class="mc-ticker-item">
        <span class="pdot {cls}"></span>
        <span>{lbl}</span>
    </div>""" for cls, lbl in items)
    return f'<div class="mc-ticker">{parts}</div>'


def _funnel_html():
    max_val = FUNNEL_STAGES[0][1]
    rows = []
    for stage, val, color, pct in FUNNEL_STAGES:
        width_pct = int(val / max_val * 100)
        formatted = f"{val:,}"
        rows.append(f"""
        <div class="funnel-row">
            <div class="funnel-label">
                <span>{stage}</span>
                <span style="color:{color}">{formatted} &nbsp; {pct}</span>
            </div>
            <div class="funnel-bar-bg">
                <div class="funnel-bar-fill"
                     style="width:{width_pct}%;
                            background:linear-gradient(90deg,{color}99,{color}dd)">
                </div>
            </div>
        </div>""")
    return "\n".join(rows)


def _pipeline_table():
    rows = ""
    for name, desc, status, color, pct in PIPELINE_STATUS:
        rows += f"""
        <tr>
            <td style="color:#E0E0E0;font-weight:600">{name}</td>
            <td style="color:#666">{desc}</td>
            <td>
                <span style="color:{color};font-size:0.6rem;
                             letter-spacing:1px">{status}</span>
            </td>
            <td>
                <div style="background:#111;border-radius:2px;height:8px;
                            border:1px solid rgba(255,255,255,0.06)">
                    <div style="width:{pct};height:100%;border-radius:2px;
                                background:linear-gradient(90deg,{color}88,{color})">
                    </div>
                </div>
                <div style="font-size:0.55rem;color:{color};text-align:right;
                            margin-top:2px">{pct}</div>
            </td>
        </tr>"""
    return f"""
    <table class="mc-table">
        <thead>
            <tr>
                <th>COMPONENT</th>
                <th>DESCRIPTION</th>
                <th>STATUS</th>
                <th style="width:80px">ADOPTION</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""


def _hero_html():
    return f"""
    <div class="mc-hero">
        <div class="mc-hero-title">Olist Data Product</div>
        <div class="mc-hero-sub">End-to-End Analytics Platform</div>
        <div class="mc-arrow">↗</div>
        <div style="font-size:0.6rem;letter-spacing:3px;color:#666;margin-top:4px">
            GCP · DAGSTER · dbt · BIGQUERY · GRADIO
        </div>
        <div style="margin-top:10px">
            <div style="font-size:0.55rem;letter-spacing:2px;color:#FF8C00;margin-bottom:4px">
                SYSTEM INITIALIZING
            </div>
            <div class="mc-progress-wrap"><div class="mc-progress-bar"></div></div>
        </div>
    </div>"""


def _team_grid():
    team = [
        ("👤", "Lik Hong",  "Customer 360 + Pipeline", "#FF8C00", "255,140,0"),
        ("💳", "Meng Hai",  "Payment Analytics",       "#FFD700", "255,215,0"),
        ("⭐", "Lanson",    "Reviews & Satisfaction",  "#00C851", "0,200,81"),
        ("📦", "Ben",       "Product Analytics",       "#FFD700", "255,215,0"),
        ("🏪", "Huey Ling", "Seller Performance",      "#FF8C00", "255,140,0"),
        ("🗺", "Kendra",    "Geography Analytics",     "#00C851", "0,200,81"),
    ]
    cards = "".join(f"""
    <div style="flex:1;min-width:120px;text-align:center;
                background:#0A0A0A;border:1px solid rgba({rgb},0.3);
                border-radius:4px;padding:10px 6px;margin:3px">
        <div style="font-size:1.4rem">{icon}</div>
        <div style="font-size:0.7rem;font-weight:700;color:{color};
                    letter-spacing:0.5px;margin-top:4px">{name}</div>
        <div style="font-size:0.55rem;color:#666;margin-top:3px;
                    letter-spacing:0.5px">{role}</div>
    </div>""" for icon, name, role, color, rgb in team)
    return f'<div style="display:flex;flex-wrap:wrap;gap:0">{cards}</div>'


# ─────────────────────────────────────────────────────────────
# DASHBOARD LAYOUT
# ─────────────────────────────────────────────────────────────

with gr.Blocks(
    theme=gr.themes.Base(
        font=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
    ),
    css=MC_CSS,
    analytics_enabled=False,
    title="Olist — Mission Control",
) as dashboard:

    # ── Top header ─────────────────────────────────────────
    gr.HTML(f"""
    <div style="background:#060606;border-bottom:1px solid rgba(255,140,0,0.3);
                padding:10px 12px;margin-bottom:4px">
        <div style="display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:8px">
            <div>
                <span style="font-size:0.6rem;letter-spacing:4px;color:#FF8C00;
                             text-transform:uppercase">
                    ◈ OLIST DATA PRODUCT ACCELERATOR
                </span>
                <span style="font-size:0.55rem;color:#444;margin-left:16px;
                             letter-spacing:2px">
                    MISSION CONTROL · 2026-03-14 02:14 UTC
                </span>
            </div>
            <div style="font-size:0.55rem;letter-spacing:2px;color:#00C851">
                ● ALL SYSTEMS NOMINAL
            </div>
        </div>
        {_kpi_strip()}
        {_ticker()}
    </div>
    """)

    # ── 3-column body ──────────────────────────────────────
    with gr.Row(equal_height=False):

        # LEFT COLUMN
        with gr.Column(scale=3, min_width=280):

            # Customer journey funnel
            gr.HTML(f"""
            <div class="mc-panel">
                <div class="mc-label">◈ Customer Journey Funnel</div>
                {_funnel_html()}
                <div style="margin-top:8px;font-size:0.6rem;color:#444;
                            letter-spacing:1px;text-align:right">
                    CONVERSION: VISIT→PURCHASE 11.3% · REPEAT RATE 38%
                </div>
            </div>
            """)

            # Daily orders chart
            gr.HTML('<div class="mc-panel"><div class="mc-label">◈ Daily Order Volume &amp; Trend</div></div>')
            gr.Plot(value=_daily_orders_chart(), show_label=False)

            # Seller vs Customer scatter
            gr.HTML('<div class="mc-panel" style="margin-top:0"><div class="mc-label">◈ Market Coverage by State</div></div>')
            gr.Plot(value=_seller_scatter(), show_label=False)

        # CENTER COLUMN
        with gr.Column(scale=4, min_width=360):

            # Hero title
            gr.HTML(f'<div class="mc-panel">{_hero_html()}</div>')

            # Brazil map
            gr.HTML('<div class="mc-panel"><div class="mc-label">◈ Customer Density — Brazil States</div></div>')
            gr.Plot(value=_brazil_choropleth(), show_label=False)

            # Team grid
            gr.HTML(f"""
            <div class="mc-panel">
                <div class="mc-label">◈ Analyst Team — 6 Domains</div>
                {_team_grid()}
            </div>
            """)

        # RIGHT COLUMN
        with gr.Column(scale=3, min_width=280):

            # Top-state leaderboard
            gr.HTML(f"""
            <div class="mc-panel">
                <div class="mc-label">◈ Top States by Customer Volume</div>
                <table class="mc-table">
                    <thead>
                        <tr>
                            <th>#</th><th>STATE</th>
                            <th>CUSTOMERS</th><th>SELLERS</th><th>RATIO</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f'''
                        <tr>
                            <td style="color:#444">{i+1}</td>
                            <td style="color:#FFD700;font-weight:700">{row.state}</td>
                            <td style="color:#FF8C00">{row.customers:,}</td>
                            <td style="color:#00C851">{row.sellers:,}</td>
                            <td style="color:#888">{row.customers/max(row.sellers,1):.0f}x</td>
                        </tr>'''
                        for i, row in _STATE_DATA.nlargest(8, "customers").iterrows())}
                    </tbody>
                </table>
            </div>
            """)

            # Pipeline & feature status
            gr.HTML(f"""
            <div class="mc-panel">
                <div class="mc-label">◈ Pipeline &amp; Feature Status</div>
                {_pipeline_table()}
            </div>
            """)

            # Dashboard registry
            gr.HTML(f"""
            <div class="mc-panel">
                <div class="mc-label">◈ Dashboard Registry</div>
                <table class="mc-table">
                    <thead>
                        <tr><th>DOMAIN</th><th>OWNER</th><th>PORT</th><th>MODE</th></tr>
                    </thead>
                    <tbody>
                        {"".join(f'''<tr>
                            <td style="color:#E0E0E0">{d}</td>
                            <td style="color:#888;font-size:0.65rem">{o}</td>
                            <td style="color:#FFD700">:{p}</td>
                            <td><span style="color:{mc};font-size:0.6rem">{m}</span></td>
                        </tr>''' for d,o,p,mc,m in [
                            ("Customer 360","Lik Hong", 7862,"#00C851","● LIVE"),
                            ("Payments",    "Meng Hai", 7863,"#FF8C00","BATCH"),
                            ("Reviews",     "Lanson",   7864,"#FF8C00","BATCH"),
                            ("Products",    "Ben",      7865,"#FF8C00","BATCH"),
                            ("Sellers",     "Huey Ling",7866,"#FF8C00","BATCH"),
                            ("Geography",   "Kendra",   7867,"#FF8C00","BATCH"),
                        ])}
                    </tbody>
                </table>
                <div class="mc-progress-wrap" style="margin-top:10px">
                    <div class="mc-progress-bar"></div>
                </div>
                <div style="font-size:0.55rem;letter-spacing:2px;color:#444;
                            text-align:center;margin-top:4px">
                    INITIALIZING DASHBOARDS...
                </div>
            </div>
            """)

    # ── Footer ─────────────────────────────────────────────
    gr.HTML(f"""
    <div style="text-align:center;padding:10px 0;
                border-top:1px solid rgba(255,140,0,0.15);margin-top:4px;
                font-size:0.55rem;letter-spacing:3px;color:#333">
        OLIST DATA PRODUCT · M2 DATA SCIENCE · 2026 ·
        <span style="color:#FF8C00">MOCK-UP</span>
    </div>
    """)


if __name__ == "__main__":
    dashboard.launch(server_port=7868, show_error=True)
