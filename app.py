"""
app.py — Olist Data Product Main Application
─────────────────────────────────────────────
Mounts all 6 developer dashboards + home + admin as Gradio Tabs.
Run:  python app.py
      make run
      ./launch.sh
"""

import os
import gradio as gr
from shared.theme import olist_theme, CUSTOM_CSS

# ── Import each developer's dashboard ────────────────────────
from dashboards.home.app      import dashboard as home_dashboard
from dashboards.admin.app     import dashboard as admin_dashboard
from dashboards.lik_hong.app  import dashboard as likhong_dashboard
from dashboards.meng_hai.app  import dashboard as menghai_dashboard
from dashboards.lanson.app    import dashboard as lanson_dashboard
from dashboards.ben.app       import dashboard as ben_dashboard
from dashboards.huey_ling.app import dashboard as hueying_dashboard
from dashboards.kendra.app    import dashboard as kendra_dashboard

# ── Assemble main app ─────────────────────────────────────────
with gr.Blocks(
    theme=olist_theme,
    css=CUSTOM_CSS,
    title="Olist Data Product",
    analytics_enabled=False,
) as app:

    with gr.Tabs() as tabs:

        with gr.Tab("🏠 Home"):
            home_dashboard.render()

        with gr.Tab("👤 Customer 360 — Lik Hong"):
            likhong_dashboard.render()

        with gr.Tab("💳 Payment — Meng Hai"):
            menghai_dashboard.render()

        with gr.Tab("⭐ Reviews — Lanson"):
            lanson_dashboard.render()

        with gr.Tab("📦 Products — Ben"):
            ben_dashboard.render()

        with gr.Tab("🏪 Sellers — Huey Ling"):
            hueying_dashboard.render()

        with gr.Tab("🗺 Geography — Kendra"):
            kendra_dashboard.render()

        with gr.Tab("⚙️ Admin"):
            admin_dashboard.render()


# ── Launch ───────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.getenv("GRADIO_SERVER_PORT", 7860))
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        show_error=True,
        favicon_path=None,
    )
