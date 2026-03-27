"""
dashboards/huey_ling/app.py — Seller Performance
──────────────────────────────────────────────────
Owner: Huey Ling
Standalone: python dashboards/huey_ling/app.py
Exports: dashboard (gr.Blocks)
"""

import gradio as gr

from shared.theme import olist_theme, CUSTOM_CSS, FONT_HEAD, COLORS
from shared.utils import dev_config_path, make_bq_client_getter
from shared.components import (
    page_header, section_title, kpi_row, alert_box, error_figure,
)
from dashboards.huey_ling.queries import (
    get_kpi_summary,
    get_top_sellers_scatter,
    get_power_sellers_bar,
    get_at_risk_scatter,
    get_state_ontime_chart,
)

_get_client = make_bq_client_getter(dev_config_path("huey_ling"))


# ── Data loaders ──────────────────────────────────────────────

def _load_kpis():
    client, cfg, err = _get_client()
    if err:
        return gr.HTML(f'<div style="color:{COLORS["red"]}">{err}</div>')
    kpis, err2 = get_kpi_summary(client, cfg)
    if err2 or not kpis:
        return gr.HTML(alert_box(f"Failed to load KPIs: {err2}", "error"))
    return kpi_row([
        {"label": "Active Sellers",    "value": f"{int(kpis.get('active_sellers', 0)):,}",  "color": "orange"},
        {"label": "Total Revenue",     "value": f"R$ {kpis.get('total_revenue', 0):,.0f}", "color": "gold"},
        {"label": "Avg Order Value",   "value": f"R$ {kpis.get('avg_order_value', 0):,.0f}", "color": "orange"},
        {"label": "Avg Review Score",  "value": f"{kpis.get('avg_review_score', 0):.2f} ★", "color": "gold"},
        {"label": "On-Time Delivery",  "value": f"{kpis.get('on_time_rate', 0) * 100:.1f}%", "color": "green"},
        {"label": "Power Sellers ⭐",  "value": f"{int(kpis.get('power_sellers', 0)):,}",   "color": "gold"},
        {"label": "At-Risk Sellers ⚠️","value": f"{int(kpis.get('at_risk_sellers', 0)):,}", "color": "red"},
    ])


def _load_top_sellers_scatter():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    fig, _ = get_top_sellers_scatter(client, cfg)
    return fig


def _load_power_sellers_bar():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    fig, _ = get_power_sellers_bar(client, cfg)
    return fig


def _load_at_risk():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    fig, _ = get_at_risk_scatter(client, cfg)
    return fig


def _load_state_ontime():
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    fig, _ = get_state_ontime_chart(client, cfg)
    return fig



# ── Dashboard ─────────────────────────────────────────────────

with gr.Blocks(title="Seller Performance", analytics_enabled=False) as dashboard:

    page_header("Seller Performance", subtitle="Top Sellers · At-Risk · Delivery Performance", icon="🏪")

    # ── KPI strip ────────────────────────────────────────────
    kpi_display = gr.HTML()

    with gr.Tabs():

        # ── Tab 1: Sellers Overview ──────────────────────────────────
        with gr.Tab("Sellers Overview"):
            section_title("Sellers Overview", accent="orange")
            gr.HTML(f"""
            <div style="font-size:0.82rem;color:{COLORS['text_muted']};margin-bottom:8px">
                ★ Power Sellers are Top <b>1%</b> in revenue and average review score ≥ <b>4</b>. Identify these high-performing sellers and to improve the customer satisfaction for potential performers with strong revenue.    
            </div>
            """)
            top_sellers_chart = gr.Plot()
            section_title("Power Sellers — AOV Ranking vs Total Orders", accent="gold")
            gr.HTML(f"""
            <div style="font-size:0.82rem;color:{COLORS['text_muted']};margin-bottom:8px">
                Power sellers with higher AOV and low orders are premium sellers.
                Those with lower AOV and high orders are price-sensitive / mass market.
                To grow revenue further, increase AOV for high-volume mass market sellers and scale premium sellers.
            </div>
            """)
            power_sellers_bar = gr.Plot()

        # ── Tab 2: At-Risk Sellers ─────────────────────────────
        with gr.Tab("At-Risk Sellers"):
            section_title("⚠️ At-Risk Sellers", accent="red")
            gr.HTML(f"""
            <div class="olist-card" style="font-size:0.82rem;color:{COLORS['text_secondary']};
                                           margin-bottom:8px">
                Sellers are flagged <b style="color:{COLORS['red']}">at-risk</b> if their
                average review score is below <b>3.0</b> or their on-time delivery rate
                is below <b>70%</b>. These top sellers may require intervention or support before their business revenue is impacted.
            </div>
            """)
            at_risk_chart = gr.Plot()

        # ── Tab 3: Delivery Performance ───────────────────────
        with gr.Tab("Delivery Performance"):
            section_title("On-Time Delivery Rate by Seller State", accent="green")
            gr.HTML(f"""
            <div style="font-size:0.82rem;color:{COLORS['text_muted']};margin-bottom:8px">
                About 8% of deliveries are late. Deliveries are arranged through Olist logistics partners.
                Identify and prioritize seller states with on-time delivery rates below <b>95%</b> and <b>high delayed orders to address poor logistics performance.
        
            </div>
            """)
            state_ontime_chart = gr.Plot()


    # ── Load button ──────────────────────────────────────────
    load_btn = gr.Button("↻ Refresh Data", variant="primary", size="sm")

    def _refresh():
        return (
            _load_kpis(),
            _load_top_sellers_scatter(),
            _load_power_sellers_bar(),
            _load_at_risk(),
            _load_state_ontime(),
        )

    _all_outputs = [
        kpi_display,
        top_sellers_chart,
        power_sellers_bar,
        at_risk_chart,
        state_ontime_chart,
    ]

    load_btn.click(_refresh, outputs=_all_outputs)
    dashboard.load(_refresh, outputs=_all_outputs)


if __name__ == "__main__":
    dashboard.launch(
        server_port=7866,
        show_error=True,
        theme=olist_theme,
        css=CUSTOM_CSS,
        head=FONT_HEAD,
    )
