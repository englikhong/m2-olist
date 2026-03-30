"""
dashboards/ben/charts.py
────────────────────────
Chart builder functions for Product Analytics dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from copy import deepcopy
import pandas as pd
import numpy as np

from shared.theme import COLORS, PLOTLY_LAYOUT, OLIST_COLORSCALE
from shared.components import kpi_card, error_figure
from shared.utils import dev_config_path, make_bq_client_getter

_get_client = make_bq_client_getter(dev_config_path("ben"))


def _fmt(value, prefix="", suffix=""):
    """Format numeric values with human-readable suffixes (K, M)."""
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.1f}M{suffix}"
    if value >= 1_000:
        return f"{prefix}{value / 1_000:.1f}K{suffix}"
    return f"{prefix}{value:,.0f}{suffix}"


def _layout(**overrides):
    """Build Plotly layout by merging overrides with theme defaults."""
    layout = deepcopy(PLOTLY_LAYOUT)
    layout.update(overrides)
    return layout


# ── Summary KPI Row ──────────────────────────────────────────


def load_kpis():
    """
    Load top-level KPI metrics: Revenue, Orders, Unique Products, Avg Review Score.
    Returns: HTML string with 4 KPI cards
    """
    client, cfg, err = _get_client()
    if err:
        return f'<div style="color:{COLORS["red"]}">GCP not configured — see quick-setup.md</div>'

    from dashboards.ben.queries import get_kpi_summary

    try:
        df = get_kpi_summary(client, cfg)
        if df.empty:
            return f'<div style="color:{COLORS["red"]}">No data available</div>'

        row = df.iloc[0]
        total_rev = row["total_revenue"]
        total_orders = row["total_orders"]
        unique_products = row["unique_products"]
        avg_review = row["avg_review_score"]

        cards = "".join([
            kpi_card("Total Revenue", _fmt(total_rev, prefix="R$ "), color="orange"),
            kpi_card("Total Orders", _fmt(total_orders), color="gold"),
            kpi_card("Unique Products", _fmt(unique_products), color="green"),
            kpi_card("Avg Review Score", f"{avg_review:.1f} ⭐", color="orange"),
        ])
        return f'<div style="display:flex;gap:12px;flex-wrap:wrap">{cards}</div>'
    except Exception as e:
        return f'<div style="color:{COLORS["red"]}">Error loading KPIs: {str(e)[:100]}</div>'


# ── Top Categories Bar Chart ────────────────────────────────


def load_top_categories_bar():
    """
    Load horizontal bar chart of top 15 product categories by revenue.
    Color by average review score (gradient).
    """
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")

    from dashboards.ben.queries import get_top_categories

    try:
        df = get_top_categories(client, cfg, limit=15)
        if df.empty:
            return error_figure("No data available")

        # Sort by revenue descending for better visualization
        df = df.sort_values("revenue", ascending=True)

        fig = px.bar(
            df,
            y="category",
            x="revenue",
            orientation="h",
            title="Top 15 Categories by Revenue",
            labels={"category": "Category", "revenue": "Revenue (R$)"},
            color="avg_review_score",
            color_continuous_scale=OLIST_COLORSCALE,
            hover_data={
                "orders": True,
                "avg_order_value": ":.2f",
                "avg_review_score": ":.2f",
            },
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Revenue: R$ %{x:,.0f}<br>Orders: %{customdata[0]}<br>Avg Order Value: R$ %{customdata[1]:.2f}<br>Avg Review: %{customdata[2]:.2f}<extra></extra>"
        )
        fig.update_layout(**_layout(
            height=450,
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_colorbar=dict(
                title="Avg Review<br>Score",
                tickfont=dict(size=10),
                thickness=15,
                len=0.7,
            ),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {str(e)[:100]}")


# ── Top Products Table ───────────────────────────────────────


def load_top_products_table():
    """
    Load top 20 products by revenue as a pandas DataFrame.
    Returns: DataFrame (Gradio Table expects df, not figure)
    """
    _empty = pd.DataFrame(columns=["Product ID", "Category", "Weight", "Orders", "Revenue"])

    client, cfg, err = _get_client()
    if err:
        return _empty

    from dashboards.ben.queries import get_top_products

    try:
        df = get_top_products(client, cfg, limit=20)
        if df.empty:
            return _empty

        # Format display columns
        df_display = df.copy()
        df_display["revenue"] = df_display["revenue"].apply(lambda x: f"R$ {x:,.2f}")
        df_display["product_weight_g"] = df_display["product_weight_g"].apply(
            lambda x: f"{x:,.0f}g" if pd.notna(x) else "—"
        )
        df_display = df_display.rename(columns={
            "product_id": "Product ID",
            "category": "Category",
            "product_weight_g": "Weight",
            "orders": "Orders",
            "revenue": "Revenue",
        })
        return df_display[["Product ID", "Category", "Weight", "Orders", "Revenue"]]
    except Exception:
        return _empty


# ── Category Revenue Pie Chart ──────────────────────────────


def load_category_revenue_pie():
    """
    Donut pie chart: revenue contribution (%) by product category.
    Shows top 20 categories by revenue.
    """
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")

    from dashboards.ben.queries import get_top_categories

    try:
        df = get_top_categories(client, cfg, limit=20)
        if df.empty:
            return error_figure("No data available")

        fig = px.pie(
            df,
            values="revenue",
            names="category",
            title="Revenue Contribution by Product Category",
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.35,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Revenue: R$ %{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
        fig.update_layout(**_layout(
            height=500,
            showlegend=False,
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {str(e)[:100]}")


# ── Monthly Trend for Selected Category ──────────────────────


def load_monthly_trend_stacked(category: str = "All Categories"):
    """
    Monthly order and revenue trend for a selected product category.
    Shows dual traces: orders (left axis) and revenue (right axis).

    Args:
        category (str): Product category name. If empty, returns error figure.
    """
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")

    from dashboards.ben.queries import get_monthly_category_trend, get_monthly_trend_by_category

    try:
        if not category or category == "All Categories":
            df = get_monthly_trend_by_category(client, cfg, top_n=10)
            if df.empty:
                return error_figure("No data available")

            fig = px.bar(
                df,
                x="month",
                y="revenue",
                color="category",
                title="Monthly Revenue by Category (Top 10)",
                labels={"month": "Month", "revenue": "Revenue (R$)", "category": "Category"},
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Revenue: R$ %{y:,.0f}<extra></extra>"
            )
            fig.update_layout(**_layout(
                height=420,
                hovermode="x unified",
                xaxis=dict(title="Month", gridcolor="rgba(255,140,0,0.08)"),
                yaxis=dict(title="Revenue (R$)", gridcolor="rgba(255,140,0,0.08)"),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
            ))
            return fig

        df = get_monthly_category_trend(client, cfg, category)
        if df.empty:
            return error_figure(f"No data for: {category}")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["month"],
            y=df["orders"],
            name="Orders",
            marker_color=COLORS["orange"],
            yaxis="y1",
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=df["month"],
            y=df["revenue"],
            name="Revenue",
            line=dict(color=COLORS["green"], width=3),
            mode="lines+markers",
            yaxis="y2",
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>Revenue: R$ %{y:,.2f}<extra></extra>",
        ))
        fig.update_layout(**_layout(
            title=f"Monthly Trend: {category}",
            height=420,
            hovermode="x unified",
            yaxis=dict(
                title=dict(text="Orders", font=dict(color=COLORS["orange"])),
                tickfont=dict(color=COLORS["orange"]),
                gridcolor="rgba(255,140,0,0.08)",
            ),
            yaxis2=dict(
                title=dict(text="Revenue (R$)", font=dict(color=COLORS["green"])),
                tickfont=dict(color=COLORS["green"]),
                anchor="x",
                overlaying="y",
                side="right",
            ),
            xaxis=dict(title="Month", gridcolor="rgba(255,140,0,0.08)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {str(e)[:100]}")


# ── Top Products by Category Table ──────────────────────────


def load_top_products_by_category_table():
    """
    HTML pivot table: each top-5 category is a column group containing
    Product ID / Qty Sold / Revenue sub-columns, with top 10 products per category.
    """
    client, cfg, err = _get_client()
    if err:
        return f'<div style="color:{COLORS["red"]}">GCP not configured — see quick-setup.md</div>'

    from dashboards.ben.queries import get_top_products_by_top_categories

    try:
        df = get_top_products_by_top_categories(client, cfg)
        if df.empty:
            return f'<div style="color:{COLORS["red"]}">No data available</div>'

        categories = df["category"].unique().tolist()

        # Build per-category list of rows (up to 10 each)
        cat_data = {}
        for cat in categories:
            rows = df[df["category"] == cat][["product_id", "qty_sold", "revenue"]].reset_index(drop=True)
            cat_data[cat] = rows

        n_rows = max(len(v) for v in cat_data.values())

        # ── Styles ──────────────────────────────────────────────
        th_cat = (
            "padding:10px 6px;text-align:center;font-size:12px;font-weight:700;"
            f"color:{COLORS['orange']};background:#111;border:1px solid #333;"
            "white-space:nowrap;letter-spacing:0.5px;"
        )
        th_sub = (
            "padding:6px 8px;text-align:center;font-size:11px;font-weight:600;"
            f"color:{COLORS['gold']};background:#1a1a1a;border:1px solid #2a2a2a;"
        )
        td_id = (
            "padding:6px 8px;font-size:11px;font-family:monospace;"
            "color:#ddd;background:#141414;border:1px solid #222;"
            "word-break:break-all;white-space:normal;max-width:160px;"
        )
        td_num = (
            "padding:6px 8px;font-size:11px;text-align:right;"
            "color:#ccc;background:#141414;border:1px solid #222;"
        )
        td_empty = (
            "padding:6px 8px;background:#111;border:1px solid #1e1e1e;"
        )

        # ── Header rows ─────────────────────────────────────────
        cat_headers = "".join(
            f'<th colspan="3" style="{th_cat}">{cat}</th>'
            for cat in categories
        )
        sub_headers = "".join(
            f'<th style="{th_sub}">Product ID</th>'
            f'<th style="{th_sub}">Qty Sold</th>'
            f'<th style="{th_sub}">Revenue (R$)</th>'
            for _ in categories
        )

        # ── Data rows ────────────────────────────────────────────
        data_rows = ""
        for i in range(n_rows):
            bg = "#161616" if i % 2 == 0 else "#141414"
            cells = ""
            for cat in categories:
                rows = cat_data[cat]
                if i < len(rows):
                    row = rows.iloc[i]
                    cells += (
                        f'<td style="{td_id}">{row["product_id"]}</td>'
                        f'<td style="{td_num}">{int(row["qty_sold"]):,}</td>'
                        f'<td style="{td_num}">R$ {row["revenue"]:,.2f}</td>'
                    )
                else:
                    cells += f'<td style="{td_empty}"></td>' * 3
            data_rows += f'<tr style="background:{bg}">{cells}</tr>'

        html = f"""
        <div style="overflow-x:auto;padding:4px 0;">
          <table style="border-collapse:collapse;width:100%;font-size:12px;">
            <thead>
              <tr>{cat_headers}</tr>
              <tr>{sub_headers}</tr>
            </thead>
            <tbody>{data_rows}</tbody>
          </table>
        </div>
        """
        return html

    except Exception as e:
        return f'<div style="color:{COLORS["red"]}">Error: {str(e)[:150]}</div>'


# ── Category Performance Heatmap ─────────────────────────────


def load_category_heatmap():
    """
    2x2 heatmap matrix showing category performance.
    X axis: Review Score (Low ← → High)
    Y axis: Revenue (Low ← → High)
    Cell values: Order Volume count
    """
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")

    from dashboards.ben.queries import get_category_revenue_vs_reviews

    try:
        df = get_category_revenue_vs_reviews(client, cfg)
        if df.empty:
            return error_figure("No data available")

        # Create quartile bins for review score and revenue
        df["review_quartile"] = pd.qcut(
            df["avg_review_score"],
            q=4,
            labels=["Very Low (0.0-2.5)", "Low (2.5-3.5)", "High (3.5-4.5)", "Very High (4.5-5.0)"],
            duplicates="drop"
        )
        df["revenue_quartile"] = pd.qcut(
            df["total_revenue"],
            q=4,
            labels=["Low", "Medium", "High", "Very High"],
            duplicates="drop"
        )

        # Create pivot table for heatmap
        heatmap_data = df.groupby(
            ["revenue_quartile", "review_quartile"], as_index=False, observed=True
        )["order_volume"].sum()

        # Pivot for matrix format
        matrix = heatmap_data.pivot_table(
            index="revenue_quartile",
            columns="review_quartile",
            values="order_volume",
            fill_value=0,
            observed=True,
        )

        fig = px.imshow(
            matrix,
            labels=dict(x="Review Score Quartile", y="Revenue Quartile", color="Order Volume"),
            title="Category Performance Matrix",
            color_continuous_scale=OLIST_COLORSCALE,
            text_auto=True,
            aspect="auto",
        )
        fig.update_traces(
            text=matrix.values.astype(int),
            texttemplate="%{text:,}",
            textfont=dict(size=12, color="white"),
            hovertemplate="Revenue: %{y}<br>Review Score: %{x}<br>Orders: %{z:,}<extra></extra>"
        )
        fig.update_layout(**_layout(
            height=380,
            coloraxis_colorbar=dict(
                title="Order<br>Volume",
                tickfont=dict(size=10),
                thickness=15,
                len=0.7,
            ),
            xaxis=dict(title="Average Review Score (Quartile)"),
            yaxis=dict(title="Total Revenue (Quartile)"),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {str(e)[:100]}")
