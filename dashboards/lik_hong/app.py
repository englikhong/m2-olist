"""
dashboards/lik_hong/app.py — Customer 360 + Next Best Action
──────────────────────────────────────────────────────────────
Owner: Lik Hong
Standalone: python dashboards/lik_hong/app.py
Merged via: app.py → gr.Tab("👤 Customer 360 — Lik Hong")
Exports: dashboard (gr.Blocks)
"""

import os
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from shared.theme import olist_theme, CUSTOM_CSS, COLORS, PLOTLY_LAYOUT
from shared.components import (
    page_header, kpi_row, section_title, alert_box,
    status_row, freshness_badge, empty_state, error_figure
)
from shared.utils import dev_config_path, make_bq_client_getter

_get_client = make_bq_client_getter(dev_config_path("lik_hong"))

# ── Customer 360 Radar helpers ─────────────────────────────────

_RADAR_CATS = ["Recency", "Frequency", "Monetary", "Satisfaction", "Loyalty", "Diversity"]
# Portfolio benchmarks (Champion / Average / At-Risk)
_BENCH_CHAMP = [90, 88, 85, 95, 82, 75]
_BENCH_AVG   = [52, 45, 48, 72, 38, 50]


def _score_customer(profile: dict) -> list[float]:
    """Normalise a customer profile dict into 0-100 radar scores."""
    days   = float(profile.get("days_since_last_order") or 365)
    orders = float(profile.get("total_orders") or 1)
    spend  = float(profile.get("total_spend") or 0)
    score  = float(profile.get("avg_review_score") or 3.0)

    recency     = max(0.0, 100.0 - days / 3.0)          # 0d→100, 300d→0
    frequency   = min(100.0, orders * 20.0)              # 5+ orders→100
    monetary    = min(100.0, spend / 10.0)               # R$1000+→100
    satisfaction = (score / 5.0) * 100.0
    loyalty     = min(100.0, 60.0 + (20.0 if orders >= 5 else 0)
                      + (20.0 if spend > 500 else 0))
    diversity   = min(100.0, orders * 15.0)              # proxy via orders

    return [round(x, 1) for x in [recency, frequency, monetary, satisfaction, loyalty, diversity]]


def build_radar_portfolio():
    """Default radar: Champions vs Average portfolio (shown before any lookup)."""
    cats  = _RADAR_CATS + [_RADAR_CATS[0]]
    champ = _BENCH_CHAMP + [_BENCH_CHAMP[0]]
    avg   = _BENCH_AVG   + [_BENCH_AVG[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=champ, theta=cats, fill="toself", name="Champions",
        fillcolor="rgba(0,200,81,0.15)",
        line=dict(color="#00C851", width=2),
        marker=dict(size=5, color="#00C851"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=avg, theta=cats, fill="toself", name="Avg Customer",
        fillcolor="rgba(255,140,0,0.10)",
        line=dict(color=COLORS["orange"], width=1.5, dash="dot"),
        marker=dict(size=4, color=COLORS["orange"]),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Customer 360° — Portfolio Benchmark",
        showlegend=True,
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)",
                    x=0.78, y=0.08, orientation="v"),
        polar=dict(
            bgcolor="rgba(8,4,0,0.6)",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                            gridcolor="rgba(255,140,0,0.12)",
                            linecolor="rgba(255,140,0,0.15)"),
            angularaxis=dict(tickfont=dict(size=11, color=COLORS["gold"]),
                             gridcolor="rgba(255,140,0,0.1)",
                             linecolor="rgba(255,140,0,0.2)"),
        ),
        height=380,
    )
    return fig


def build_radar_customer(profile: dict, customer_id: str):
    """Radar for a single looked-up customer vs Champion benchmark."""
    scores = _score_customer(profile)
    cats   = _RADAR_CATS + [_RADAR_CATS[0]]
    cust   = scores + [scores[0]]
    champ  = _BENCH_CHAMP + [_BENCH_CHAMP[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=champ, theta=cats, fill="toself", name="Champion Benchmark",
        fillcolor="rgba(0,200,81,0.08)",
        line=dict(color="#00C851", width=1, dash="dot"),
        marker=dict(size=3, color="#00C851"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=cust, theta=cats, fill="toself", name=f"Customer",
        fillcolor="rgba(255,140,0,0.18)",
        line=dict(color=COLORS["gold"], width=2),
        marker=dict(size=6, color=COLORS["gold"]),
        text=[f"{s}%" for s in scores],
        hovertemplate="%{theta}: %{r:.0f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=f"Customer 360° — {customer_id[:16]}…",
        showlegend=True,
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)",
                    x=0.72, y=0.05, orientation="v"),
        polar=dict(
            bgcolor="rgba(8,4,0,0.6)",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                            gridcolor="rgba(255,140,0,0.12)",
                            linecolor="rgba(255,140,0,0.15)"),
            angularaxis=dict(tickfont=dict(size=11, color=COLORS["gold"]),
                             gridcolor="rgba(255,140,0,0.1)",
                             linecolor="rgba(255,140,0,0.2)"),
        ),
        height=380,
    )
    return fig


# ── Data loaders ──────────────────────────────────────────────

def load_rfm_chart():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured — see quick-setup.md")
    from dashboards.lik_hong.queries import get_rfm_segments
    try:
        df = get_rfm_segments(client, cfg)
        fig = px.bar(
            df, x="segment", y="customer_count",
            color="avg_monetary",
            color_continuous_scale=["#FF4444", "#FF8C00", "#FFD700", "#00C851"],
            labels={"customer_count": "Customers", "segment": "Segment",
                    "avg_monetary": "Avg Spend (R$)"},
            title="RFM Customer Segments",
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_revenue_trend():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured — see quick-setup.md")
    from dashboards.lik_hong.queries import get_revenue_trend
    try:
        df = get_revenue_trend(client, cfg)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["revenue"],
            mode="lines+markers",
            line=dict(color=COLORS["orange"], width=2),
            fill="tozeroy",
            fillcolor=f"rgba(255,140,0,0.1)",
            name="Revenue (R$)",
        ))
        fig.add_trace(go.Bar(
            x=df["month"], y=df["unique_customers"],
            name="Unique Customers",
            marker_color=COLORS["gold"],
            opacity=0.5,
            yaxis="y2",
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Monthly Revenue & Customer Trend",
            yaxis2=dict(overlaying="y", side="right", gridcolor="#2A2A2A"),
        )
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_customer_profile(customer_id: str):
    """Returns (summary_md, order_table, radar_fig)."""
    if not customer_id.strip():
        return "Enter a customer ID to look up their 360° profile.", None, build_radar_portfolio()
    client, cfg, err = _get_client()
    if err:
        return f"GCP not configured: {err}", None, build_radar_portfolio()
    from dashboards.lik_hong.queries import get_customer_profile, get_order_history
    try:
        profile = get_customer_profile(client, cfg, customer_id.strip())
        if not profile:
            return "Customer not found.", None, build_radar_portfolio()
        cid = profile.get('customer_unique_id', '—')
        summary = (
            f"**Customer:** `{cid}`  \n"
            f"**Location:** {profile.get('customer_city','—')}, {profile.get('customer_state','—')}  \n"
            f"**Total Orders:** {profile.get('total_orders','—')}  \n"
            f"**Total Spend:** R$ {profile.get('total_spend','—')}  \n"
            f"**Avg Order Value:** R$ {profile.get('avg_order_value','—')}  \n"
            f"**Last Order:** {profile.get('last_order_date','—')}  \n"
            f"**Days Since Last Order:** {profile.get('days_since_last_order','—')}  \n"
            f"**Avg Review Score:** {profile.get('avg_review_score','—')} / 5.0  \n"
        )
        history = get_order_history(client, cfg, customer_id.strip())
        radar   = build_radar_customer(profile, cid)
        return summary, history, radar
    except Exception as e:
        return f"Error: {e}", None, build_radar_portfolio()


def get_nba(customer_id: str):
    """Next Best Action heuristics based on customer profile."""
    client, cfg, err = _get_client()
    if err:
        return f"GCP not configured: {err}"
    from dashboards.lik_hong.queries import get_customer_profile
    try:
        p = get_customer_profile(client, cfg, customer_id.strip())
        if not p:
            return "Customer not found."
        actions = []
        days = p.get("days_since_last_order", 999)
        score = p.get("avg_review_score", 5.0)
        spend = p.get("total_spend", 0)
        orders = p.get("total_orders", 0)

        if days > 180:
            actions.append("🔴 **Win-back campaign** — send personalised re-engagement offer (180+ days inactive)")
        elif days > 90:
            actions.append("🟠 **Retention email** — highlight new arrivals in their preferred category (90+ days)")
        else:
            actions.append("🟢 **Upsell** — recommend complementary products based on last order")

        if score and score < 3.0:
            actions.append("🔴 **Service recovery** — escalate to support team (avg review < 3.0)")
        if orders and orders >= 5 and spend and spend > 500:
            actions.append("🟡 **Loyalty programme** — eligible for VIP tier (5+ orders, R$500+ spend)")
        if not actions:
            actions.append("✅ Customer in good standing — monitor for next purchase opportunity")
        return "\n\n".join(actions)
    except Exception as e:
        return f"Error: {e}"


# ── Dashboard UI ──────────────────────────────────────────────
with gr.Blocks(analytics_enabled=False, title="Customer 360 — Lik Hong") as dashboard:

    page_header(
        "Customer 360 + Next Best Action",
        subtitle="RFM segmentation · Churn risk · Personalised next actions",
        icon="👤",
    )

    kpi_row([
        {"label": "Total Customers",  "value": "—",   "color": "orange"},
        {"label": "Active (90d)",     "value": "—",   "color": "green"},
        {"label": "At-Risk (180d+)",  "value": "—",   "color": "red"},
        {"label": "Avg Review Score", "value": "—",   "color": "gold"},
        {"label": "Total Revenue",    "value": "R$ —","color": "orange"},
    ])

    # ── Main layout: Radar (primary) + lookup/profile side-panel ──
    with gr.Row():
        with gr.Column(scale=2):
            section_title("Customer 360° Radar", accent="gold")
            radar_chart = gr.Plot(value=build_radar_portfolio())

        with gr.Column(scale=1):
            section_title("Customer Lookup", accent="green")
            customer_id_input = gr.Textbox(
                label="Customer Unique ID",
                placeholder="Enter customer_unique_id…",
            )
            lookup_btn = gr.Button("🔍 Look Up", variant="primary")
            profile_md = gr.Markdown("Enter a customer ID to see their 360° profile.")

            section_title("Next Best Action", accent="red")
            nba_btn    = gr.Button("⚡ Generate NBA", variant="secondary")
            nba_output = gr.Markdown("Look up a customer first.")

    # ── Order history ──────────────────────────────────────────
    section_title("Order History", accent="orange")
    order_table = gr.DataFrame(label="Orders", interactive=False)

    # ── Supporting charts ──────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=1):
            section_title("RFM Segmentation", accent="gold")
            rfm_chart = gr.Plot()
        with gr.Column(scale=1):
            section_title("Revenue & Customer Trend", accent="orange")
            revenue_chart = gr.Plot()

    # Wire up events
    dashboard.load(fn=load_rfm_chart,     outputs=rfm_chart)
    dashboard.load(fn=load_revenue_trend, outputs=revenue_chart)
    lookup_btn.click(fn=load_customer_profile,
                     inputs=customer_id_input,
                     outputs=[profile_md, order_table, radar_chart])
    nba_btn.click(fn=get_nba,
                  inputs=customer_id_input,
                  outputs=nba_output)


if __name__ == "__main__":
    dashboard.launch(server_port=7862, show_error=True, css=CUSTOM_CSS)
