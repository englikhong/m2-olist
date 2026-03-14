#!/usr/bin/env python3
"""
Mockup 3 — Olist Mission Control v3
Warm amber/orange aesthetic; six business domains as the centrepiece.
Run: python -m dashboards.home.mockup3   (from project root)
Port: 7869
"""

import gradio as gr
import plotly.graph_objects as go
import numpy as np

# ── Palette ────────────────────────────────────────────────────────
AMBER = "#FF8C00"
GOLD  = "#FFD700"
GREEN = "#00C851"
RED   = "#FF4444"

# ── Base Plotly layout for mini charts ────────────────────────────
_M = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=4, b=8),
    font=dict(color=AMBER, family="Courier New, monospace", size=9),
    showlegend=False,
)


# ── Charts ─────────────────────────────────────────────────────────

def _fig_funnel():
    fig = go.Figure(go.Funnel(
        y=["Awareness", "Interest", "Trial", "Adoption"],
        x=[99441, 67832, 41234, 22587],
        textinfo="value+percent previous",
        textfont=dict(size=8, color=GOLD),
        connector=dict(line=dict(color="rgba(255,140,0,0.2)", width=1)),
        marker=dict(
            color=["rgba(255,140,0,0.9)", "rgba(255,140,0,0.7)",
                   "rgba(255,140,0,0.5)", "rgba(255,215,0,0.9)"],
            line=dict(color="rgba(0,0,0,0.4)", width=1),
        ),
    ))
    fig.update_layout(**{**_M, "height": 168})
    return fig


def _fig_donut():
    fig = go.Figure(go.Pie(
        labels=["Credit Card", "Boleto", "Voucher", "Debit Card"],
        values=[76795, 19784, 5775, 1529],
        hole=0.55,
        marker=dict(
            colors=[AMBER, "#CC7000", GOLD, "#996000"],
            line=dict(color="rgba(0,0,0,0.5)", width=1),
        ),
        textinfo="label+percent",
        textfont=dict(size=8, color=GOLD),
        insidetextorientation="horizontal",
    ))
    fig.update_layout(**{**_M, "height": 168})
    return fig


def _fig_reviews():
    fig = go.Figure(go.Bar(
        x=[1, 2, 3, 4, 5],
        y=[11424, 3244, 8179, 19142, 57328],
        marker_color=[RED, "#FF6600", AMBER, "#CCAA00", GREEN],
        marker_line=dict(color="rgba(0,0,0,0.4)", width=1),
        text=["11.5k", "3.2k", "8.2k", "19.1k", "57.3k"],
        textfont=dict(size=7, color=GOLD),
        textposition="outside",
    ))
    fig.update_layout(**{**_M, "height": 168,
        "xaxis": dict(showgrid=False,
                      tickvals=[1, 2, 3, 4, 5],
                      ticktext=["★", "★★", "★★★", "★★★★", "★★★★★"],
                      tickfont=dict(size=9, color=AMBER)),
        "yaxis": dict(showgrid=False, showticklabels=False, range=[0, 68000]),
    })
    return fig


def _fig_products():
    cats = ["Bed Bath", "Health Beauty", "Sports", "Furniture", "Computers",
            "Electronics", "Housewares"]
    vals = [11115, 9670, 8641, 8334, 6526, 5964, 5750]
    alphas = [0.95, 0.85, 0.75, 0.65, 0.55, 0.48, 0.40]
    colors = [f"rgba(255,{int(80+i*18)},0,{a})" for i, a in enumerate(alphas)]
    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker_color=colors,
        marker_line=dict(color="rgba(0,0,0,0.3)", width=1),
        text=[f"{v:,}" for v in vals],
        textfont=dict(size=8, color=GOLD),
        textposition="inside",
    ))
    fig.update_layout(**{**_M, "height": 168,
        "xaxis": dict(showgrid=False, showticklabels=False),
        "yaxis": dict(showgrid=False, tickfont=dict(size=8, color=GOLD)),
    })
    return fig


def _fig_sellers():
    np.random.seed(42)
    n = 90
    orders  = np.random.exponential(45, n)
    ratings = np.clip(3.5 + np.random.normal(0, 0.7, n), 1, 5)
    revenue = orders * np.random.uniform(80, 600, n)
    fig = go.Figure(go.Scatter(
        x=orders, y=ratings, mode="markers",
        marker=dict(
            size=np.sqrt(revenue / 400),
            color=revenue,
            colorscale=[[0, "#3D1A00"], [0.5, AMBER], [1, GOLD]],
            opacity=0.75,
            line=dict(color="rgba(255,140,0,0.3)", width=0.5),
        ),
        hovertemplate="Orders: %{x:.0f}<br>Rating: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(**{**_M, "height": 168,
        "xaxis": dict(showgrid=False, tickfont=dict(size=8),
                      title=dict(text="Orders →", font=dict(size=8))),
        "yaxis": dict(showgrid=False, tickfont=dict(size=8), range=[1, 5],
                      title=dict(text="Rating →", font=dict(size=8))),
    })
    return fig


def _fig_geo():
    states = [
        ("SP", -23.5, -46.6, 41746), ("RJ", -22.9, -43.2, 12852),
        ("MG", -19.9, -43.9, 11635), ("RS", -30.0, -51.2, 8523),
        ("PR", -25.4, -49.3, 7011),  ("SC", -27.6, -48.5, 6360),
        ("BA", -12.9, -38.5, 3380),  ("GO", -16.7, -49.3, 2684),
        ("ES", -20.3, -40.3, 2222),  ("PE",  -8.1, -34.9, 1650),
        ("CE",  -3.7, -38.5, 1336),  ("AM",  -3.1, -60.0, 480),
        ("MT", -15.6, -56.1, 908),   ("MS", -20.4, -54.6, 714),
        ("PA",  -1.5, -48.5, 975),
    ]
    lats   = [s[1] for s in states]
    lons   = [s[2] for s in states]
    sizes  = [max(6, min(26, s[3] // 600)) for s in states]
    colors = [GREEN if s[3] > 5000 else (AMBER if s[3] > 2000 else RED)
              for s in states]
    texts  = [f"{s[0]}: {s[3]:,}" for s in states]
    fig = go.Figure(go.Scattergeo(
        lat=lats, lon=lons, mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.85,
                    line=dict(color="rgba(255,255,255,0.3)", width=0.5)),
        customdata=texts,
        hovertemplate="%{customdata}<extra></extra>",
    ))
    fig.update_layout(**{**_M, "height": 168,
        "geo": dict(
            bgcolor="rgba(0,0,0,0)",
            showland=True,  landcolor="rgba(25,12,0,0.9)",
            showocean=True, oceancolor="rgba(0,4,15,0.6)",
            showcoastlines=True, coastlinecolor="rgba(255,140,0,0.5)",
            showcountries=True, countrycolor="rgba(255,140,0,0.15)",
            showframe=False, scope="south america",
            lataxis_range=[-34, 6], lonaxis_range=[-75, -28],
        ),
    })
    return fig


def _fig_brazil_center():
    states = [
        ("SP", -23.5, -46.6, 41746), ("RJ", -22.9, -43.2, 12852),
        ("MG", -19.9, -43.9, 11635), ("RS", -30.0, -51.2, 8523),
        ("PR", -25.4, -49.3, 7011),  ("SC", -27.6, -48.5, 6360),
        ("BA", -12.9, -38.5, 3380),  ("GO", -16.7, -49.3, 2684),
        ("ES", -20.3, -40.3, 2222),  ("PE",  -8.1, -34.9, 1650),
        ("CE",  -3.7, -38.5, 1336),  ("AM",  -3.1, -60.0, 480),
        ("MT", -15.6, -56.1, 908),   ("MS", -20.4, -54.6, 714),
        ("PA",  -1.5, -48.5, 975),   ("RN",  -5.7, -35.2, 785),
        ("MA",  -2.5, -44.3, 747),   ("PB",  -7.1, -34.9, 536),
        ("RO", -11.5, -63.0, 253),   ("TO", -10.2, -48.3, 280),
    ]
    lats   = [s[1] for s in states]
    lons   = [s[2] for s in states]
    sizes  = [max(8, min(36, s[3] // 500)) for s in states]
    colors = [GREEN if s[3] > 8000 else
              (AMBER if s[3] > 3000 else
               ("#FFCC00" if s[3] > 1000 else RED))
              for s in states]
    texts  = [f"{s[0]}: {s[3]:,} orders" for s in states]
    fig = go.Figure(go.Scattergeo(
        lat=lats, lon=lons, mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.9,
                    line=dict(color="rgba(255,255,255,0.35)", width=0.5)),
        customdata=texts,
        hovertemplate="%{customdata}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=255,
        showlegend=False,
        font=dict(color=AMBER, family="Courier New"),
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            showland=True,  landcolor="rgba(30,12,0,0.97)",
            showocean=True, oceancolor="rgba(0,5,25,0.75)",
            showcoastlines=True, coastlinecolor="rgba(255,140,0,0.75)",
            showcountries=True, countrycolor="rgba(255,140,0,0.2)",
            showframe=False, scope="south america",
            lataxis_range=[-34, 6], lonaxis_range=[-75, -28],
            projection_type="natural earth",
        ),
    )
    return fig


# ── CSS ────────────────────────────────────────────────────────────
_CSS = """
/* ══ MOCKUP 3 — Olist Mission Control ══ */

.gradio-container {
    background: #060400 !important;
    font-family: 'Courier New', monospace !important;
    max-width: 100% !important;
    min-height: 100vh;
}
footer, header { display: none !important; }

/* Ambient radial glow */
.gradio-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 75% 55% at 50% 24%, rgba(190,78,0,0.24) 0%, transparent 65%),
        radial-gradient(ellipse 45% 35% at 18% 68%, rgba(110,44,0,0.11) 0%, transparent 55%),
        radial-gradient(ellipse 45% 35% at 82% 68%, rgba(110,44,0,0.11) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
}

/* Subtle dot grid overlay */
.gradio-container::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle, rgba(255,140,0,0.06) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
    z-index: 0;
}

/* ── KPI strip ── */
.kpi-strip {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 10px 28px;
    background: linear-gradient(90deg,
        rgba(255,140,0,0.02), rgba(255,140,0,0.12), rgba(255,140,0,0.02));
    border-bottom: 1px solid rgba(255,140,0,0.22);
    flex-wrap: wrap;
    gap: 6px;
}
.kpi-item { text-align: center; min-width: 78px; }
.kpi-val  {
    display: block;
    font-size: 22px; font-weight: 900;
    color: #FFD700;
    text-shadow: 0 0 12px rgba(255,215,0,0.55);
    line-height: 1.1;
}
.kpi-lbl {
    display: block; font-size: 8px;
    color: rgba(255,140,0,0.5);
    letter-spacing: 1.2px; text-transform: uppercase; margin-top: 1px;
}
.kpi-chg-p { color: #00C851; font-size: 9px; }
.kpi-chg-n { color: #FF4444; font-size: 9px; }
.kpi-sep   { width: 1px; height: 30px; background: rgba(255,140,0,0.14); }

/* ── Dashboard panel header ── */
.dh {
    background: rgba(10,5,0,0.97);
    border: 1px solid rgba(255,140,0,0.38);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 10px 12px 9px;
    position: relative; overflow: hidden;
}
.dh::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,140,0,0.8), transparent);
}
.dh-title { font-size: 10px; font-weight: bold; color: #FF8C00; letter-spacing: 2px; }
.dh-dev   { font-size: 9px; color: rgba(255,140,0,0.38); margin: 2px 0 6px; }
.dh-mrow  { display: flex; gap: 10px; }
.dh-m     { text-align: center; flex: 1; }
.dh-mv    { display: block; font-size: 14px; font-weight: bold; color: #FFD700; line-height: 1.1; }
.dh-ml    { display: block; font-size: 8px; color: rgba(255,140,0,0.48); text-transform: uppercase; }
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00C851; box-shadow: 0 0 6px #00C851;
    display: inline-block;
    animation: livePulse 2s ease-in-out infinite;
}

/* ── Mini chart containers ── */
.mini-chart, .mini-chart > .block {
    background: rgba(10,5,0,0.97) !important;
    border: 1px solid rgba(255,140,0,0.38) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 0 !important;
    margin: 0 0 8px 0 !important;
    box-shadow: 0 6px 24px rgba(255,140,0,0.07) !important;
}
.mini-chart > .block .wrap { padding: 2px !important; }

/* ── Center hero ── */
.hero {
    text-align: center;
    padding: 18px 14px 10px;
    background: rgba(8,4,0,0.75);
    border: 1px solid rgba(255,140,0,0.22);
    border-radius: 8px 8px 0 0;
    position: relative; overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #FF8C00, #FFD700, #FF8C00, transparent);
}
.hero-eyebrow {
    font-size: 9px; color: rgba(255,140,0,0.35);
    letter-spacing: 4px; margin-bottom: 10px;
}
.hero-t1 {
    font-size: 34px; font-weight: 900; color: #FFD700; letter-spacing: 7px;
    text-shadow: 0 0 22px rgba(255,215,0,0.7), 0 0 55px rgba(255,140,0,0.4);
    line-height: 1;
}
.hero-t2 {
    font-size: 13px; font-weight: bold;
    color: rgba(255,140,0,0.85); letter-spacing: 5px; margin: 5px 0;
}
.hero-t3 {
    font-size: 10px; color: rgba(255,140,0,0.4);
    letter-spacing: 3px; margin: 6px 0 10px;
}
.hero-arrow {
    font-size: 56px; color: #FF8C00; display: block; line-height: 1;
    text-shadow: 0 0 28px rgba(255,140,0,0.95), 0 0 65px rgba(255,140,0,0.45);
    animation: arrowFloat 2.6s ease-in-out infinite;
}
.hero-stats {
    display: flex; justify-content: center; gap: 0; margin: 10px 0 6px;
}
.hero-stat { text-align: center; padding: 0 18px; }
.hero-stat + .hero-stat {
    border-left: 1px solid rgba(255,140,0,0.18);
}
.hero-sv { font-size: 20px; font-weight: bold; color: #FFD700; display: block; }
.hero-sl { font-size: 8px; color: rgba(255,140,0,0.45); letter-spacing: 1px; text-transform: uppercase; }
.hero-live {
    font-size: 9px; color: rgba(0,200,81,0.72); letter-spacing: 2px; margin-top: 6px;
}

/* ── Brazil map container ── */
.brazil-map, .brazil-map > .block {
    background: rgba(8,4,0,0.97) !important;
    border: 1px solid rgba(255,140,0,0.22) !important;
    border-top: none !important; border-bottom: none !important;
    border-radius: 0 !important;
    padding: 0 !important; margin: 0 !important;
}

/* ── Sync bar ── */
.sync-wrap {
    background: rgba(8,4,0,0.97);
    border: 1px solid rgba(255,140,0,0.22);
    border-top: none; border-radius: 0 0 8px 8px;
    padding: 9px 14px 11px;
}
.sync-lbl   { font-size: 9px; color: rgba(255,140,0,0.48); letter-spacing: 2px; margin-bottom: 5px; }
.sync-track { height: 7px; background: rgba(255,140,0,0.08); border-radius: 4px; overflow: hidden; position: relative; }
.sync-fill  {
    height: 100%; width: 94%;
    background: linear-gradient(90deg, #3D1A00, #FF8C00, #FFD700);
    border-radius: 4px; position: relative; overflow: hidden;
}
.sync-shimmer {
    position: absolute; top: 0; bottom: 0; width: 55px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.38), transparent);
    animation: shimmer 2s linear infinite;
}
.sync-legs {
    display: flex; justify-content: space-between;
    margin-top: 5px; font-size: 8px; color: rgba(255,140,0,0.32);
}

/* ── Team panel ── */
.team-panel {
    background: rgba(8,4,0,0.92);
    border: 1px solid rgba(255,140,0,0.28);
    border-radius: 8px; padding: 12px 14px;
}
.team-title {
    font-size: 9px; color: rgba(255,140,0,0.45);
    letter-spacing: 3px; text-transform: uppercase;
    border-bottom: 1px solid rgba(255,140,0,0.1);
    padding-bottom: 6px; margin-bottom: 8px;
}
.team-row {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 0; border-bottom: 1px solid rgba(255,140,0,0.06);
}
.team-icon {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; flex-shrink: 0;
}
.team-name { font-size: 11px; font-weight: bold; flex: 1; }
.team-role { font-size: 8px; color: rgba(255,140,0,0.36); display: block; }
.team-port { font-size: 9px; color: rgba(255,140,0,0.28); }

/* ── Pipeline section (below the fold) ── */
.pipe-panel {
    background: rgba(5,2,0,0.98);
    border: 1px solid rgba(255,140,0,0.18);
    border-radius: 8px; padding: 14px 20px; margin-top: 6px;
}
.pipe-title {
    font-size: 9px; color: rgba(255,140,0,0.4);
    letter-spacing: 3px; text-transform: uppercase;
    border-bottom: 1px solid rgba(255,140,0,0.1);
    padding-bottom: 6px; margin-bottom: 10px;
}
.pipe-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px 20px; }
.pipe-row  { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.pipe-name { font-size: 10px; color: rgba(255,200,100,0.72); }
.pipe-badge { padding: 1px 8px; border-radius: 3px; font-size: 8px; letter-spacing: 1px; }
.ok   { background: rgba(0,200,81,0.09);  color: #00C851; border: 1px solid rgba(0,200,81,0.22); }
.warn { background: rgba(255,140,0,0.09); color: #FF8C00; border: 1px solid rgba(255,140,0,0.22); }
.idle { background: rgba(80,80,80,0.08);  color: rgba(255,255,255,0.22); border: 1px solid rgba(80,80,80,0.18); }

/* ── Gradio resets ── */
.gap  { gap: 6px !important; }
.form { background: transparent !important; }
.block { background: transparent !important; border: none !important; }
div[data-testid="column"] { gap: 0 !important; }

/* ── Animations ── */
@keyframes arrowFloat {
    0%,100% {
        transform: translateY(0) rotate(0deg);
        text-shadow: 0 0 28px rgba(255,140,0,0.95), 0 0 65px rgba(255,140,0,0.45);
    }
    50% {
        transform: translateY(-7px) rotate(2deg);
        text-shadow: 0 0 45px rgba(255,215,0,1), 0 0 90px rgba(255,140,0,0.7);
    }
}
@keyframes shimmer  { 0% { left: -55px; } 100% { left: 110%; } }
@keyframes livePulse {
    0%,100% { opacity: 1; box-shadow: 0 0 6px #00C851; }
    50%      { opacity: 0.28; box-shadow: none; }
}
"""


# ── HTML helpers ───────────────────────────────────────────────────

def _hex2rgb(h: str) -> str:
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


def _kpi_strip() -> str:
    items = [
        ("TOTAL ORDERS",     "99,441",  "▲ 12.3%", True),
        None,
        ("TOTAL REVENUE",    "R$13.6M", "▲ 8.7%",  True),
        None,
        ("AVG ORDER VALUE",  "R$136.8", "▲ 2.1%",  True),
        None,
        ("ACTIVE SELLERS",   "3,095",   "▲ 5.4%",  True),
        None,
        ("CUSTOMER BASE",    "99,441",  "▲ 15.2%", True),
        None,
        ("REVIEW SCORE",     "4.09 ★",  "▼ 0.3%",  False),
        None,
        ("ON-TIME DELIVERY", "92.3%",   "▲ 1.8%",  True),
        None,
        ("STATES COVERED",   "27",      "◈ Brazil", None),
    ]
    inner = ""
    for d in items:
        if d is None:
            inner += '<div class="kpi-sep"></div>'
        else:
            lbl, val, chg, pos = d
            if pos is True:
                ch = f'<span class="kpi-chg-p">{chg}</span>'
            elif pos is False:
                ch = f'<span class="kpi-chg-n">{chg}</span>'
            else:
                ch = f'<span style="color:rgba(255,140,0,0.38);font-size:9px;">{chg}</span>'
            inner += f"""<div class="kpi-item">
                <span class="kpi-val">{val}</span>{ch}
                <span class="kpi-lbl">{lbl}</span>
            </div>"""
    return f'<div class="kpi-strip">{inner}</div>'


def _panel_header(title: str, dev: str, port: str, metrics: list) -> str:
    mh = "".join(
        f'<div class="dh-m">'
        f'<span class="dh-mv">{v}</span>'
        f'<span class="dh-ml">{l}</span></div>'
        for l, v in metrics
    )
    return f"""<div class="dh">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;">
            <div>
                <span class="dh-title">{title}</span>
                <div class="dh-dev">↳ {dev} &nbsp;·&nbsp; :{port}</div>
            </div>
            <span class="live-dot"></span>
        </div>
        <div class="dh-mrow">{mh}</div>
    </div>"""


def _hero() -> str:
    return """<div class="hero">
        <div class="hero-eyebrow">◈ &nbsp; BRAZIL E-COMMERCE INTELLIGENCE &nbsp; ◈</div>
        <div class="hero-t1">OLIST</div>
        <div class="hero-t2">DATA PRODUCT</div>
        <div class="hero-t3">SIX DOMAINS · ONE PLATFORM · REAL-TIME</div>
        <span class="hero-arrow">↗</span>
        <div class="hero-stats">
            <div class="hero-stat">
                <span class="hero-sv">99K</span>
                <span class="hero-sl">Orders</span>
            </div>
            <div class="hero-stat">
                <span class="hero-sv">R$13.6M</span>
                <span class="hero-sl">Revenue</span>
            </div>
            <div class="hero-stat">
                <span class="hero-sv">6</span>
                <span class="hero-sl">Domains</span>
            </div>
        </div>
        <div class="hero-live">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                         background:#00C851;box-shadow:0 0 6px #00C851;margin-right:6px;
                         animation:livePulse 2s infinite;vertical-align:middle;"></span>
            LIVE DATA SYNC ACTIVE
        </div>
    </div>"""


def _sync_bar() -> str:
    return """<div class="sync-wrap">
        <div class="sync-lbl">◈ PIPELINE STATUS — 94% SYNCHRONIZED</div>
        <div class="sync-track">
            <div class="sync-fill"><div class="sync-shimmer"></div></div>
        </div>
        <div class="sync-legs">
            <span>MELTANO ●</span><span>dbt SILVER ●</span>
            <span>dbt GOLD ●</span><span>BIGQUERY ●</span><span>GRADIO ●</span>
        </div>
    </div>"""


def _team() -> str:
    team = [
        ("Lik Hong",  "Customer 360 + Pipeline Lead", "#FF8C00", "7862"),
        ("Meng Hai",  "Payment Analytics",            "#CC8800", "7863"),
        ("Lanson",    "Reviews & Satisfaction",        "#CCAA00", "7864"),
        ("Ben",       "Product Analytics",             "#FF8C00", "7865"),
        ("Huey Ling", "Seller Performance",            "#CC8800", "7866"),
        ("Kendra",    "Geography Analytics",           "#CCAA00", "7867"),
    ]
    rows = "".join(f"""<div class="team-row">
        <div class="team-icon"
             style="background:rgba({_hex2rgb(c)},0.1);border:1px solid {c};">
            <span style="color:{c};">◈</span>
        </div>
        <div style="flex:1;">
            <span class="team-name" style="color:{c};">{name}</span>
            <span class="team-role">{role}</span>
        </div>
        <span class="team-port">:{port}</span>
    </div>""" for name, role, c, port in team)
    return f'<div class="team-panel"><div class="team-title">◈ DEVELOPER TEAM</div>{rows}</div>'


def _pipeline() -> str:
    rows = [
        ("Meltano EL",    "COMPLETE",  "ok"),
        ("dbt Silver",    "COMPLETE",  "ok"),
        ("dbt Gold",      "COMPLETE",  "ok"),
        ("BigQuery Gold", "READY",     "ok"),
        ("Pub/Sub Topic", "RUNNING",   "warn"),
        ("Redis Cache",   "ACTIVE",    "ok"),
        ("Dagster",       "SCHEDULED", "warn"),
        ("Gradio App",    "LIVE",      "ok"),
    ]
    rh = "".join(
        f'<div class="pipe-row">'
        f'<span class="pipe-name">{n}</span>'
        f'<span class="pipe-badge {c}">{s}</span></div>'
        for n, s, c in rows
    )
    return f"""<div class="pipe-panel">
        <div class="pipe-title">⚙ DATA PIPELINE &amp; ADMIN — SYSTEM STATUS</div>
        <div class="pipe-grid">{rh}</div>
    </div>"""


# ── App ────────────────────────────────────────────────────────────
with gr.Blocks(analytics_enabled=False, title="Olist Data Product") as dashboard:

    gr.HTML(_kpi_strip())

    # ── Row 1: Left 2 · Center hero + map · Right 2 ───────────────
    with gr.Row(equal_height=False):

        # Left — Customer 360 + Payment Analytics
        with gr.Column(scale=2):
            gr.HTML(_panel_header(
                "CUSTOMER 360", "Lik Hong", "7862",
                [("Orders", "99,441"), ("Repeat Rate", "3.0%"), ("Avg CLV", "R$406")],
            ))
            gr.Plot(_fig_funnel(), show_label=False, elem_classes=["mini-chart"])

            gr.HTML(_panel_header(
                "PAYMENT ANALYTICS", "Meng Hai", "7863",
                [("Revenue", "R$13.6M"), ("Avg Instal.", "3.7×"), ("CC Share", "73.9%")],
            ))
            gr.Plot(_fig_donut(), show_label=False, elem_classes=["mini-chart"])

        # Center — hero + Brazil map + sync bar
        with gr.Column(scale=3):
            gr.HTML(_hero())
            gr.Plot(_fig_brazil_center(), show_label=False, elem_classes=["brazil-map"])
            gr.HTML(_sync_bar())

        # Right — Reviews + Product Analytics
        with gr.Column(scale=2):
            gr.HTML(_panel_header(
                "REVIEWS & SATISFACTION", "Lanson", "7864",
                [("Avg Score", "4.09 ★"), ("5-Stars", "57.8%"), ("NPS", "67")],
            ))
            gr.Plot(_fig_reviews(), show_label=False, elem_classes=["mini-chart"])

            gr.HTML(_panel_header(
                "PRODUCT ANALYTICS", "Ben", "7865",
                [("Categories", "71"), ("Top Cat", "Bed Bath"), ("Avg Weight", "2.3 kg")],
            ))
            gr.Plot(_fig_products(), show_label=False, elem_classes=["mini-chart"])

    # ── Row 2: Seller · Geography · Team ──────────────────────────
    with gr.Row(equal_height=False):

        with gr.Column(scale=2):
            gr.HTML(_panel_header(
                "SELLER PERFORMANCE", "Huey Ling", "7866",
                [("Sellers", "3,095"), ("Avg Rating", "4.1 ★"), ("Top State", "SP")],
            ))
            gr.Plot(_fig_sellers(), show_label=False, elem_classes=["mini-chart"])

        with gr.Column(scale=2):
            gr.HTML(_panel_header(
                "GEOGRAPHY ANALYTICS", "Kendra", "7867",
                [("States", "27"), ("Top State", "SP 42%"), ("Cities", "4,119")],
            ))
            gr.Plot(_fig_geo(), show_label=False, elem_classes=["mini-chart"])

        with gr.Column(scale=2):
            gr.HTML(_team())

    # ── Below the fold: pipeline / admin ──────────────────────────
    gr.HTML(_pipeline())


if __name__ == "__main__":
    dashboard.launch(server_port=7870, show_error=True, css=_CSS)
