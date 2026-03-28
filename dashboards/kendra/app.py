"""
dashboards/kendra/app.py — Geography Analytics
────────────────────────────────────────────────
Owner: Kendra
Standalone: python dashboards/kendra/app.py
Exports: dashboard (gr.Blocks)
"""

import gradio as gr

from shared.theme import olist_theme, CUSTOM_CSS, FONT_HEAD
from shared.components import page_header, section_title
from dashboards.kendra.charts import (
    load_kpis,
    load_choropleth,
    load_delivery_bar,
    load_scatter_map,
    load_underserved_table,
    load_seller_distribution,
    load_revenue_bar,
    load_monthly_trend,
)

# ── Dashboard UI ──────────────────────────────────────────────

with gr.Blocks(analytics_enabled=False) as dashboard:

    page_header(
        "Geography Analytics",
        subtitle="Customer density \u00b7 Delivery times \u00b7 Underserved regions \u00b7 Location map",
        icon="\U0001f5fa",
    )

    kpi_html = gr.HTML()

    with gr.Tabs():
        with gr.TabItem("Overview"):
            with gr.Row():
                with gr.Column(scale=1):
                    section_title("Order Volume by State", accent="orange")
                    choropleth_chart = gr.Plot()
                with gr.Column(scale=1):
                    section_title("Revenue by State", accent="gold")
                    revenue_chart = gr.Plot()
            with gr.Row():
                with gr.Column():
                    section_title("Monthly Orders \u2014 Top 5 States", accent="green")
                    monthly_chart = gr.Plot()

        with gr.TabItem("Delivery"):
            with gr.Row():
                with gr.Column():
                    section_title("Avg Delivery Days by State", accent="orange")
                    delivery_chart = gr.Plot()

        with gr.TabItem("Sellers"):
            with gr.Row():
                with gr.Column():
                    section_title("Seller Distribution by State", accent="green")
                    seller_chart = gr.Plot()
            with gr.Row():
                with gr.Column():
                    section_title("Underserved Regions (Customer/Seller Ratio)", accent="red")
                    underserved_chart = gr.Plot()

        with gr.TabItem("Geography"):
            with gr.Row():
                with gr.Column():
                    section_title("Customer Location Map (3k sample)", accent="gold")
                    scatter_chart = gr.Plot()

    # Load all on page load
    dashboard.load(fn=load_kpis, outputs=[kpi_html])
    dashboard.load(fn=load_choropleth, outputs=[choropleth_chart])
    dashboard.load(fn=load_revenue_bar, outputs=[revenue_chart])
    dashboard.load(fn=load_monthly_trend, outputs=[monthly_chart])
    dashboard.load(fn=load_delivery_bar, outputs=[delivery_chart])
    dashboard.load(fn=load_seller_distribution, outputs=[seller_chart])
    dashboard.load(fn=load_underserved_table, outputs=[underserved_chart])
    dashboard.load(fn=load_scatter_map, outputs=[scatter_chart])


if __name__ == "__main__":
    dashboard.launch(
        server_port=7867, show_error=True,
        theme=olist_theme, css=CUSTOM_CSS, head=FONT_HEAD,
    )
