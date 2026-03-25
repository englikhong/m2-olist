"""
dashboards/lanson/app.py — Reviews & Satisfaction (v2 simplified)
──────────────────────────────────────────────────────────────────
Owner:      Lanson
Tab:        ⭐ Reviews
Standalone: python dashboards/lanson/app.py
Exports:    dashboard (gr.Blocks)

Single page — 4 charts with explanations:
    1. NPS Proxy Trend
    2. Silent Sufferer Rate
    3. NPS by Product Category
    4. Fault Attribution Trend
"""

import gradio as gr
import plotly.graph_objects as go
import pandas as pd

from shared.theme import olist_theme, CUSTOM_CSS, COLORS, PLOTLY_LAYOUT, FONT_HEAD
from shared.components import page_header, section_title, error_figure
from shared.utils import make_bq_client_getter, dev_config_path

_get_client = make_bq_client_getter(dev_config_path("lanson"))


# ── Layout helper ─────────────────────────────────────────────
def _layout(**overrides):
    """Merge PLOTLY_LAYOUT with overrides — overrides always win."""
    return {**{k: v for k, v in PLOTLY_LAYOUT.items()
               if k not in overrides}, **overrides}


# ── Colour constants ──────────────────────────────────────────
_GREEN  = "#639922"
_GRAY   = "#888780"
_AMBER  = "#BA7517"
_RED    = "#E24B4A"
_BLUE   = "#185FA5"


# ── Explanation card helper ───────────────────────────────────
def _explain(title: str, what: str, how: str, formula: str) -> str:
    return f"""
    <div style="background:rgba(10,5,0,0.85);border:1px solid rgba(255,140,0,0.25);
                border-left:3px solid #FF8C00;border-radius:8px;
                padding:16px 20px;margin:4px 0 12px 0">
        <div style="font-size:1rem;font-weight:700;color:#FFD700;
                    letter-spacing:1px;margin-bottom:8px">{title}</div>
        <div style="font-size:0.875rem;color:{COLORS['text_primary']};
                    line-height:1.7;margin-bottom:10px">{what}</div>
        <div style="font-size:0.8rem;color:{COLORS['text_secondary']};
                    line-height:1.6;margin-bottom:10px">
            <span style="color:#FF8C00;font-weight:600">How it is calculated: </span>
            {how}
        </div>
        <div style="background:rgba(255,140,0,0.06);border-radius:6px;
                    padding:8px 12px;font-family:'Space Mono',monospace;
                    font-size:0.78rem;color:#FFD700">
            {formula}
        </div>
    </div>
    """


# ── NPS explainer at top of page ─────────────────────────────
_NPS_EXPLAINER = f"""
<div style="background:rgba(24,95,165,0.08);border:1px solid rgba(24,95,165,0.35);
            border-radius:10px;padding:20px 24px;margin:8px 0 16px 0">
    <div style="font-size:1.1rem;font-weight:700;color:#FFD700;
                letter-spacing:1.5px;margin-bottom:12px">
        ⭐ What is NPS (Net Promoter Score)?
    </div>
    <div style="font-size:0.9rem;color:{COLORS['text_primary']};
                line-height:1.8;margin-bottom:14px">
        <b style="color:#FF8C00">NPS</b> measures how likely customers are to
        recommend a business. It was developed by Bain & Company and is now
        one of the most widely used customer loyalty metrics globally.
        A high NPS means more customers are advocates than critics.
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);
                gap:12px;margin-bottom:14px">
        <div style="background:rgba(99,153,34,0.12);border:1px solid rgba(99,153,34,0.4);
                    border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:1.5rem;margin-bottom:4px">😊</div>
            <div style="color:#639922;font-weight:700;font-size:0.85rem">PROMOTERS</div>
            <div style="color:{COLORS['text_secondary']};font-size:0.78rem;margin-top:4px">
                5★ reviews<br>Loyal enthusiasts who recommend to others
            </div>
        </div>
        <div style="background:rgba(136,135,128,0.12);border:1px solid rgba(136,135,128,0.4);
                    border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:1.5rem;margin-bottom:4px">😐</div>
            <div style="color:#888780;font-weight:700;font-size:0.85rem">PASSIVES</div>
            <div style="color:{COLORS['text_secondary']};font-size:0.78rem;margin-top:4px">
                4★ reviews<br>Satisfied but not enthusiastic — excluded from score
            </div>
        </div>
        <div style="background:rgba(226,75,74,0.12);border:1px solid rgba(226,75,74,0.4);
                    border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:1.5rem;margin-bottom:4px">😠</div>
            <div style="color:#E24B4A;font-weight:700;font-size:0.85rem">DETRACTORS</div>
            <div style="color:{COLORS['text_secondary']};font-size:0.78rem;margin-top:4px">
                1★ 2★ 3★ reviews<br>Unhappy customers who may warn others away
            </div>
        </div>
    </div>
    <div style="background:rgba(255,215,0,0.06);border-radius:6px;
                padding:10px 14px;font-family:'Space Mono',monospace;
                font-size:0.85rem;color:#FFD700;text-align:center">
        NPS = (% Promoters) − (% Detractors) &nbsp;|&nbsp;
        Scale: −100 (all detractors) → +100 (all promoters)
    </div>
    <div style="margin-top:12px;font-size:0.8rem;
                color:{COLORS['text_secondary']};line-height:1.6">
        <b style="color:#FF8C00">Why we use it for Olist: </b>
        Olist's review system uses 1–5 star ratings, which we map directly to
        NPS categories. This gives us a single comparable score across time,
        product categories, and seller performance — making it easy to spot
        where satisfaction is improving or declining.
    </div>
</div>
"""

# ── Chart-level explanations ──────────────────────────────────
_EXPLAIN_NPS_TREND = _explain(
    title="📈 Chart 1 — NPS Proxy Trend",
    what=(
        "This stacked bar chart shows how the mix of Promoters, Passives, and "
        "Detractors changes every month. Each bar represents 100% of reviews "
        "in that month. The line of NPS score in the tooltip shows whether "
        "overall sentiment is improving or declining over time."
    ),
    how=(
        "Every review is classified: 5★ = Promoter, 4★ = Passive, 1–3★ = Detractor. "
        "We count how many reviews fall into each category per month, convert "
        "to percentages, and compute the monthly NPS score."
    ),
    formula=(
        "Monthly NPS = (Promoter count / Total reviews × 100) "
        "− (Detractor count / Total reviews × 100)"
    ),
)

_EXPLAIN_SILENT = _explain(
    title="🤫 Chart 2 — Silent Sufferer Rate",
    what=(
        "A 'silent sufferer' is a customer who experienced a late delivery, "
        "left no review, and never ordered again. They are the most dangerous "
        "type of dissatisfied customer — they do not complain, they just leave. "
        "This chart tracks what percentage of late orders resulted in a silent sufferer."
    ),
    how=(
        "For each month, we count all late orders (delivered after the estimated date). "
        "Among those, we identify orders where: (1) no review was submitted, "
        "and (2) the customer made no subsequent purchase. "
        "The rate is the share of late orders that meet all three conditions."
    ),
    formula=(
        "Silent Sufferer Rate = "
        "(Late orders with no review AND no reorder) / All late orders × 100%"
    ),
)

_EXPLAIN_CATEGORY = _explain(
    title="🏷️ Chart 3 — NPS by Product Category",
    what=(
        "Not all product categories perform equally. This horizontal bar chart "
        "ranks every product category from worst to best NPS. Bars in red fall "
        "below the overall NPS benchmark (shown as a dashed amber line). "
        "Bars in green are performing above average. "
        "This helps operations and merchandising teams prioritise which "
        "product categories need urgent attention."
    ),
    how=(
        "We join reviews to orders to products, group by English category name, "
        "and compute the NPS for each category using the same Promoter/Detractor "
        "formula. We then compare each category's NPS against the overall NPS "
        "across all categories to get the gap."
    ),
    formula=(
        "Category NPS = (Category Promoters / Category Reviews × 100) "
        "− (Category Detractors / Category Reviews × 100) | "
        "Gap = Category NPS − Overall NPS"
    ),
)

_EXPLAIN_FAULT = _explain(
    title="⚙️ Chart 4 — Fault Attribution Trend",
    what=(
        "When a customer gives a 1★ or 2★ review, who is responsible? "
        "This chart breaks down the share of low-score reviews attributed to "
        "three fault domains each month: Logistics (late delivery or review "
        "submitted before delivery), Seller/Product (poor quality or wrong item), "
        "and Other (unclassified). "
        "This helps operations teams direct corrective action to the right part "
        "of the supply chain."
    ),
    how=(
        "We filter to reviews with score ≤ 2★. For each review, we apply "
        "fault attribution rules: if the review was submitted before the order "
        "arrived, or the delay was > 3 days, it is classified as a Logistics fault. "
        "Otherwise if the order was on time, it is a Seller/Product fault."
    ),
    formula=(
        "Logistics % = (1-2★ reviews where delay > 3d OR early review) "
        "/ All 1-2★ reviews × 100% | "
        "Seller/Product % = remaining on-time 1-2★ reviews / All 1-2★ reviews × 100%"
    ),
)


# ── Chart builders ────────────────────────────────────────────

def _build_nps_trend(df: pd.DataFrame) -> go.Figure:
    if df is None or df.empty:
        return error_figure("No NPS trend data")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month"], y=df["promoter_pct"],
        name="Promoters (5★)", marker_color=_GREEN,
        hovertemplate="<b>%{x}</b><br>Promoters: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["month"], y=df["passive_pct"],
        name="Passives (4★)", marker_color=_GRAY,
        hovertemplate="<b>%{x}</b><br>Passives: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["month"], y=df["detractor_pct"],
        name="Detractors (1-3★)", marker_color=_RED,
        customdata=df["nps_score"],
        hovertemplate=(
            "<b>%{x}</b><br>Detractors: %{y:.1f}%"
            "<br>NPS this month: %{customdata}<extra></extra>"
        ),
    ))
    fig.update_layout(**_layout(
        barmode="stack",
        title="NPS Proxy Trend — Monthly (hover for monthly NPS score)",
        yaxis_title="% of Reviews",
        xaxis_title="Month",
        legend=dict(orientation="h", y=1.12, x=0),
        height=400,
    ))
    return fig


def _build_silent_sufferer(df: pd.DataFrame) -> go.Figure:
    if df is None or df.empty:
        return error_figure("No silent sufferer data")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"],
        y=df["silent_sufferer_pct"],
        mode="lines+markers",
        line=dict(color=_RED, width=2.5),
        marker=dict(size=6, color=_RED),
        fill="tozeroy",
        fillcolor="rgba(226,75,74,0.08)",
        customdata=df[["late_orders", "silent_sufferers"]],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Silent sufferer rate: %{y:.1f}%<br>"
            "Late orders: %{customdata[0]}<br>"
            "Silent sufferers: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(**_layout(
        title="Silent Sufferer Rate — % of Late Orders with No Review & No Reorder",
        yaxis_title="% of Late Orders",
        xaxis_title="Month",
        height=400,
    ))
    return fig


def _build_category_nps(df: pd.DataFrame) -> go.Figure:
    if df is None or df.empty:
        return error_figure("No category NPS data")
    overall = float(df["overall_nps"].iloc[0]) if "overall_nps" in df.columns else 0
    colors  = [_GREEN if v >= overall else _RED for v in df["category_nps"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["category_nps"],
        y=df["product_category"],
        orientation="h",
        marker_color=colors,
        customdata=df[["nps_gap_vs_benchmark", "total_orders", "avg_review_score"]],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Category NPS: %{x}<br>"
            "Gap vs benchmark: %{customdata[0]:+.1f} pts<br>"
            "Total orders: %{customdata[1]:,}<br>"
            "Avg review score: %{customdata[2]}★"
            "<extra></extra>"
        ),
    ))
    fig.add_vline(
        x=overall, line_dash="dash", line_color=_AMBER,
        annotation_text=f"Overall NPS benchmark: {overall}",
        annotation_font_color=_AMBER,
        annotation_position="top right",
    )
    fig.update_layout(**_layout(
        title="NPS by Product Category — Red = below benchmark, Green = above",
        xaxis_title="NPS Proxy Score",
        height=max(450, len(df) * 22),
    ))
    return fig


def _build_fault_attribution(df: pd.DataFrame) -> go.Figure:
    if df is None or df.empty:
        return error_figure("No fault attribution data")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month"], y=df["logistics_pct"],
        name="Logistics", marker_color=_RED,
        hovertemplate="<b>%{x}</b><br>Logistics fault: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["month"], y=df["seller_product_pct"],
        name="Seller / Product", marker_color=_AMBER,
        hovertemplate="<b>%{x}</b><br>Seller/Product fault: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["month"], y=df["other_pct"],
        name="Other", marker_color=_GRAY,
        hovertemplate="<b>%{x}</b><br>Other: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**_layout(
        barmode="stack",
        title="Fault Attribution — Share of 1-2★ Reviews by Root Cause",
        yaxis_title="% of Low-Score Reviews",
        xaxis_title="Month",
        legend=dict(orientation="h", y=1.12, x=0),
        height=400,
    ))
    return fig


# ── KPI strip ─────────────────────────────────────────────────
def _kpi_strip(kpis: dict) -> str:
    nps   = kpis.get("overall_nps", "—")
    score = kpis.get("avg_score", "—")
    total = kpis.get("total_reviews", "—")
    ss    = kpis.get("silent_sufferer_pct", "—")
    early = kpis.get("early_review_pct", "—")

    def card(val, label, color):
        return f"""
        <div style="flex:1;min-width:150px;text-align:center;
                    background:rgba(10,5,0,0.85);
                    border:1px solid rgba(255,140,0,0.25);
                    border-radius:8px;padding:14px 10px">
            <div style="font-size:1.8rem;font-weight:900;color:{color};
                        text-shadow:0 0 10px {color}88">{val}</div>
            <div style="font-size:0.72rem;color:{COLORS['text_secondary']};
                        text-transform:uppercase;letter-spacing:1.5px;
                        margin-top:4px">{label}</div>
        </div>"""

    return f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 16px 0">
        {card(nps,   "Overall NPS",         "#185FA5")}
        {card(score, "Avg Review Score ★",  "#FFD700")}
        {card(f"{int(total):,}" if total != "—" else "—",
              "Total Reviews",              "#FF8C00")}
        {card(f"{ss}%", "Silent Sufferer Rate", "#E24B4A")}
        {card(f"{early}%", "Early Review Rate", "#BA7517")}
    </div>
    """


# ── Data loader ───────────────────────────────────────────────
def load_dashboard():
    client, cfg, err = _get_client()
    if err:
        ef = error_figure("GCP not configured — see quick-setup.md")
        return "", ef, ef, ef, ef

    from dashboards.lanson.queries import (
        get_overall_kpis, get_nps_trend,
        get_silent_sufferer_trend, get_category_nps,
        get_fault_attribution_trend,
    )
    try:
        kpis     = get_overall_kpis(client, cfg)
        nps_df   = get_nps_trend(client, cfg)
        ss_df    = get_silent_sufferer_trend(client, cfg)
        cat_df   = get_category_nps(client, cfg)
        fault_df = get_fault_attribution_trend(client, cfg)
    except Exception as e:
        ef = error_figure(f"Query error: {e}")
        return "", ef, ef, ef, ef

    return (
        _kpi_strip(kpis),
        _build_nps_trend(nps_df),
        _build_silent_sufferer(ss_df),
        _build_category_nps(cat_df),
        _build_fault_attribution(fault_df),
    )


# ── Dashboard UI ──────────────────────────────────────────────
with gr.Blocks(analytics_enabled=False,
               title="Reviews & Satisfaction") as dashboard:

    page_header(
        "Reviews & Satisfaction",
        subtitle=(
            "Customer satisfaction analysis using NPS proxy · "
            "Olist Brazilian E-Commerce Dataset (2016–2018)"
        ),
        icon="⭐",
    )

    # NPS explainer
    gr.HTML(_NPS_EXPLAINER)

    # KPI strip
    kpi_html = gr.HTML("")

    # Chart 1 — NPS Trend
    gr.HTML(_EXPLAIN_NPS_TREND)
    nps_chart = gr.Plot()

    # Chart 2 — Silent Sufferer
    gr.HTML(_EXPLAIN_SILENT)
    ss_chart = gr.Plot()

    # Chart 3 — Category NPS
    gr.HTML(_EXPLAIN_CATEGORY)
    cat_chart = gr.Plot()

    # Chart 4 — Fault Attribution
    gr.HTML(_EXPLAIN_FAULT)
    fault_chart = gr.Plot()

    # Load all on startup
    dashboard.load(
        fn=load_dashboard,
        outputs=[kpi_html, nps_chart, ss_chart, cat_chart, fault_chart],
    )


# ── Standalone launch ─────────────────────────────────────────
if __name__ == "__main__":
    dashboard.launch(
        server_port=7864,
        show_error=True,
        theme=olist_theme,
        css=CUSTOM_CSS,
        head=FONT_HEAD,
    )