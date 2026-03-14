"""
dashboards/home/mockup.py — Home Launchpad MOCK-UP
───────────────────────────────────────────────────
Standalone preview for Lik Hong to tune look & feel.
NO GCP dependency — all data is hardcoded/static.

Run:
    python dashboards/home/mockup.py
    → http://localhost:7861
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from shared.theme import olist_theme, CUSTOM_CSS, COLORS, PLOTLY_LAYOUT, OLIST_COLORSCALE
from shared.components import (
    section_title, kpi_row, status_row, freshness_badge, alert_box,
)

# ── Static placeholder data ────────────────────────────────────

DASHBOARDS = [
    {
        "icon": "👤",
        "title": "Customer 360 + NBA",
        "owner": "Lik Hong",
        "description": "360° customer view, RFM segmentation, churn score & next best actions",
        "badge": "live",
        "status": "ok",
    },
    {
        "icon": "💳",
        "title": "Payment Analytics",
        "owner": "Meng Hai",
        "description": "Payment methods, instalment trends, AOV & cancellation rates",
        "badge": "batch",
        "status": "ok",
    },
    {
        "icon": "⭐",
        "title": "Reviews & Satisfaction",
        "owner": "Lanson",
        "description": "Review scores, sentiment analysis, CSAT trends & low-score alerts",
        "badge": "batch",
        "status": "ok",
    },
    {
        "icon": "📦",
        "title": "Product Analytics",
        "owner": "Ben",
        "description": "Top products, category matrix, demand signals & return rates",
        "badge": "batch",
        "status": "ok",
    },
    {
        "icon": "🏪",
        "title": "Seller Performance",
        "owner": "Huey Ling",
        "description": "Seller leaderboard, fulfilment latency, ratings & risk flags",
        "badge": "batch",
        "status": "ok",
    },
    {
        "icon": "🗺",
        "title": "Geography Analytics",
        "owner": "Kendra",
        "description": "Customer & seller heatmaps, regional delivery times & opportunities",
        "badge": "batch",
        "status": "ok",
    },
]

BADGE_LABELS = {"live": "● LIVE", "batch": "BATCH", "offline": "OFFLINE"}

# Realistic Olist dataset numbers (Kaggle 2018 snapshot)
PLATFORM_KPIS = [
    {"label": "Total Orders",        "value": "112,650",  "color": "orange", "delta": "+8.3%"},
    {"label": "Gross Merchandise Value", "value": "R$13.6M","color": "gold",   "delta": "+11.2%"},
    {"label": "Avg Review Score",    "value": "4.09 ★",   "color": "green",  "delta": "+0.06"},
    {"label": "On-time Delivery",    "value": "87.3%",    "color": "green",  "delta": "-0.5%"},
    {"label": "Active Sellers",      "value": "3,095",    "color": "orange", "delta": "+142"},
]

# Monthly orders (Jan–Aug 2018 — representative trend from the dataset)
_MONTHLY_ORDERS = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
    "orders": [7211, 6728, 8187, 7786, 8415, 7760, 8289, 8732],
    "gmv":    [876_000, 814_000, 1_012_000, 957_000, 1_034_000, 956_000, 1_022_000, 1_097_000],
})

# Top 6 categories by revenue (mock, representative)
_TOP_CATS = pd.DataFrame({
    "category": [
        "Health & Beauty", "Watches & Gifts", "Bed & Bath", "Sports",
        "Computers", "Furniture",
    ],
    "revenue": [1_640_000, 1_290_000, 1_150_000, 980_000, 870_000, 740_000],
})

# Top 5 states by customer count
_STATE_CUSTOMERS = pd.DataFrame({
    "state": ["SP", "RJ", "MG", "RS", "PR"],
    "customers": [41746, 12852, 11635, 5466, 5045],
})


# ── Chart builders (all static data) ──────────────────────────

def _monthly_orders_chart() -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_MONTHLY_ORDERS["month"],
        y=_MONTHLY_ORDERS["orders"],
        marker_color=COLORS["orange"],
        name="Orders",
        hovertemplate="%{x}: %{y:,} orders<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=_MONTHLY_ORDERS["month"],
        y=_MONTHLY_ORDERS["orders"],
        mode="lines+markers",
        line=dict(color=COLORS["gold"], width=2, dash="dot"),
        marker=dict(size=6),
        name="Trend",
        hoverinfo="skip",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Monthly Order Volume (2018)",
        xaxis_title="Month",
        yaxis_title="Orders",
        showlegend=False,
        height=280,
    )
    return fig


def _category_revenue_chart() -> go.Figure:
    df = _TOP_CATS.sort_values("revenue")
    fig = go.Figure(go.Bar(
        x=df["revenue"],
        y=df["category"],
        orientation="h",
        marker=dict(
            color=df["revenue"],
            colorscale=[[0, COLORS["orange"]], [1, COLORS["gold"]]],
            showscale=False,
        ),
        text=df["revenue"].apply(lambda v: f"R${v/1e6:.2f}M"),
        textposition="outside",
        hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Top Categories by Revenue",
        xaxis_title="Revenue (R$)",
        yaxis_title="",
        height=280,
    )
    return fig


def _state_customers_chart() -> go.Figure:
    fig = go.Figure(go.Bar(
        x=_STATE_CUSTOMERS["state"],
        y=_STATE_CUSTOMERS["customers"],
        marker_color=[COLORS["orange"], COLORS["gold"], COLORS["green"],
                      COLORS["orange"], COLORS["gold"]],
        text=_STATE_CUSTOMERS["customers"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        hovertemplate="%{x}: %{y:,} customers<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Top 5 States by Customers",
        xaxis_title="State",
        yaxis_title="Customers",
        height=280,
    )
    return fig


# ── HTML helpers ───────────────────────────────────────────────

def _nav_grid_html() -> str:
    cards = []
    for d in DASHBOARDS:
        badge_cls = f"badge-{d['badge']}"
        dot_cls = f"status-{d['status']}"
        cards.append(f"""
        <div class="nav-tile" style="flex:1;min-width:220px;max-width:320px">
            <div style="display:flex;justify-content:flex-end;margin-bottom:4px">
                <span class="status-dot {dot_cls}"></span>
            </div>
            <div class="nav-tile-icon">{d['icon']}</div>
            <div class="nav-tile-title">{d['title']}</div>
            <div class="nav-tile-owner">{d['owner']}</div>
            <div style="font-size:0.75rem;color:{COLORS['text_secondary']};
                        margin:8px 0;padding:0 8px">{d['description']}</div>
            <span class="nav-tile-badge {badge_cls}">{BADGE_LABELS[d['badge']]}</span>
        </div>
        """)
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:16px;justify-content:flex-start;padding:8px 0">'
        + "".join(cards)
        + "</div>"
    )


def _architecture_html() -> str:
    return f"""
    <div class="olist-card" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                                   color:{COLORS['text_secondary']};line-height:1.9">
        <span style="color:{COLORS['orange']};font-weight:600">INGEST</span><br>
        &nbsp;&nbsp;Batch  → Meltano (CSV → GCS Bronze, incremental bookmarks)<br>
        &nbsp;&nbsp;Stream → Pub/Sub → GCS Streaming Bucket<br><br>
        <span style="color:{COLORS['orange']};font-weight:600">TRANSFORM</span><br>
        &nbsp;&nbsp;dbt (Silver cleanse → Gold star schema) — incremental MERGE by default<br>
        &nbsp;&nbsp;Full refresh only via Admin Panel (Lik Hong only)<br><br>
        <span style="color:{COLORS['orange']};font-weight:600">ORCHESTRATE</span><br>
        &nbsp;&nbsp;Dagster — batch jobs + real-time sensors + Redis dimension cache<br><br>
        <span style="color:{COLORS['orange']};font-weight:600">SERVE</span><br>
        &nbsp;&nbsp;BigQuery Gold ← each developer reads their own GCP project<br>
        &nbsp;&nbsp;Gradio App (this screen) → 6 domain dashboards
    </div>
    """


def _team_html() -> str:
    roles = [
        ("Lik Hong",  "👤 Customer 360 + Pipeline Lead"),
        ("Meng Hai",  "💳 Payment Analytics"),
        ("Lanson",    "⭐ Reviews & Satisfaction"),
        ("Ben",       "📦 Product Analytics"),
        ("Huey Ling", "🏪 Seller Performance"),
        ("Kendra",    "🗺 Geography Analytics"),
    ]
    cards = "".join(f"""
    <div class="olist-card" style="min-width:155px;text-align:center;flex:1">
        <div style="font-weight:600;color:{COLORS['text_primary']};font-size:0.9rem;margin-bottom:6px">{name}</div>
        <div style="font-size:0.75rem;color:{COLORS['text_secondary']}">{role}</div>
    </div>""" for name, role in roles)
    return f'<div style="display:flex;flex-wrap:wrap;gap:12px">{cards}</div>'


def _pipeline_health_html() -> str:
    rows = [
        ("Batch ingestion",        "ok",       "Last run: 2026-03-14 02:00 UTC",  "2h ago"),
        ("dbt transform",          "ok",       "Silver + Gold refreshed",          "2h ago"),
        ("Real-time simulator",    "inactive", "Stopped — start via Admin Panel",  "—"),
        ("Redis dimension cache",  "inactive", "Local Redis not running",          "—"),
    ]
    items = []
    for label, state, detail, age in rows:
        dot = f'<span class="status-dot status-{state}"></span>'
        state_label = {"ok": "Online", "inactive": "Offline", "warn": "Degraded", "error": "Error"}[state]
        items.append(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 0;
                    border-bottom:1px solid {COLORS['border']}">
            {dot}
            <div style="flex:1">
                <span style="color:{COLORS['text_primary']};font-size:0.85rem;font-weight:500">{label}</span>
                <span style="color:{COLORS['text_muted']};font-size:0.75rem;margin-left:8px">{detail}</span>
            </div>
            <div style="text-align:right">
                <span style="font-size:0.75rem;color:{COLORS['text_muted']}">{age}</span>
            </div>
        </div>""")
    return (
        f'<div class="olist-card">'
        + "".join(items)
        + "</div>"
    )


# ── Dashboard layout ───────────────────────────────────────────

with gr.Blocks(
    theme=olist_theme,
    css=CUSTOM_CSS,
    analytics_enabled=False,
    title="Olist Data Product — Home",
) as dashboard:

    # ── Hero ──────────────────────────────────────────────────
    gr.HTML(f"""
    <div style="background:linear-gradient(135deg,#1A1A1A 0%,#0D0D0D 100%);
                border-bottom:2px solid {COLORS['orange']}22;
                padding:36px 28px 28px;margin-bottom:4px">
        <div style="max-width:960px">
            <div style="font-size:0.7rem;color:{COLORS['orange']};
                        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;
                        font-family:'JetBrains Mono',monospace">
                GCP · Dagster · dbt · BigQuery · Gradio &nbsp;·&nbsp;
                <span style="color:{COLORS['text_muted']}">MOCK-UP — safe to tune</span>
            </div>
            <h1 style="font-size:2.2rem;font-weight:800;color:{COLORS['text_primary']};
                       margin:0 0 10px 0;letter-spacing:-0.5px;line-height:1.15">
                Olist E-Commerce<br>
                <span style="color:{COLORS['orange']}">Data Product</span>
            </h1>
            <p style="color:{COLORS['text_secondary']};font-size:0.95rem;margin:0;max-width:560px">
                Brazil's largest e-commerce marketplace · 100k+ orders · 6 analytical domains ·
                end-to-end GCP pipeline built by the M2 Data Science team
            </p>
        </div>
    </div>
    """)

    # ── System status bar ─────────────────────────────────────
    status_row([
        {"name": "Batch Pipeline",   "state": "ok"},
        {"name": "Real-time Agent",  "state": "inactive"},
        {"name": "BigQuery",         "state": "ok"},
        {"name": "Redis Cache",      "state": "inactive"},
        {"name": "dbt",              "state": "ok"},
    ])

    gr.HTML(
        '<div style="margin:6px 0 2px 2px">'
        + freshness_badge("2026-03-14 02:14 UTC", "Last batch run")
        + '</div>'
    )

    # ── Platform KPIs ─────────────────────────────────────────
    section_title("Platform Summary", accent="orange")
    kpi_row(PLATFORM_KPIS)

    # ── Mini charts ───────────────────────────────────────────
    section_title("Platform Pulse", accent="gold")
    with gr.Row():
        with gr.Column():
            gr.Plot(value=_monthly_orders_chart())
        with gr.Column():
            gr.Plot(value=_category_revenue_chart())
        with gr.Column():
            gr.Plot(value=_state_customers_chart())

    # ── Dashboard tiles ───────────────────────────────────────
    section_title("Dashboards", accent="orange")
    gr.HTML(_nav_grid_html())

    # ── Pipeline health ───────────────────────────────────────
    section_title("Pipeline Health", accent="gold")
    gr.HTML(_pipeline_health_html())

    # ── Architecture ──────────────────────────────────────────
    section_title("Architecture", accent="gold")
    gr.HTML(_architecture_html())

    # ── Team ──────────────────────────────────────────────────
    section_title("Team", accent="green")
    gr.HTML(_team_html())

    # ── Footer ────────────────────────────────────────────────
    gr.HTML(f"""
    <div style="text-align:center;padding:24px 0 12px;
                color:{COLORS['text_muted']};font-size:0.75rem;
                border-top:1px solid {COLORS['border']};margin-top:16px">
        Olist Data Product · M2 Data Science · 2026 ·
        <span style="color:{COLORS['orange']}">MOCK-UP</span> — no live data
    </div>
    """)


if __name__ == "__main__":
    dashboard.launch(server_port=7861, show_error=True)
