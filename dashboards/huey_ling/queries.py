"""
dashboards/huey_ling/queries.py
────────────────────────────────
BigQuery queries for the Seller Performance dashboard.
All public functions return (result, error_str) where result is a
pandas DataFrame or Plotly Figure, and error_str is None on success.
"""

from copy import deepcopy

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from shared.utils import run_query, qualified_table
from shared.theme import PLOTLY_LAYOUT, COLORS, OLIST_COLORSCALE


# ── Helpers ───────────────────────────────────────────────────

def _layout(**overrides) -> dict:
    """Return a merged PLOTLY_LAYOUT dict with optional overrides."""
    layout = deepcopy(PLOTLY_LAYOUT)
    layout.update(overrides)
    return layout


def _empty_fig(title: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**_layout(title=title))
    return fig


# ── KPI summary ───────────────────────────────────────────────

def get_kpi_summary(client, cfg: dict) -> tuple[dict, str | None]:
    """
    Return a dict with marketplace-level KPIs:
        total_sellers, active_sellers, total_revenue, avg_order_value,
        avg_review_score, on_time_rate, power_sellers, at_risk_sellers
    """
    sql = f"""
    SELECT
        COUNT(*)                                            AS total_sellers,
        COUNTIF(total_orders > 0)                           AS active_sellers,
        ROUND(SUM(total_revenue), 2)                        AS total_revenue,
        ROUND(SUM(total_revenue) / NULLIF(SUM(total_orders), 0), 2) AS avg_order_value,
        ROUND(AVG(avg_review_score), 2)                     AS avg_review_score,
        ROUND(
            SUM(total_orders * on_time_rate)
                / NULLIF(SUM(CASE WHEN on_time_rate IS NOT NULL THEN total_orders END), 0),
            3
        )                                                   AS on_time_rate,
        COUNTIF(power_seller IS TRUE)                       AS power_sellers,
        COUNTIF(at_risk IS TRUE)                            AS at_risk_sellers
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    """
    try:
        df = run_query(client, sql)
        return df.iloc[0].to_dict(), None
    except Exception as e:
        return {}, str(e)


# ── Top sellers scatter ───────────────────────────────────────

def get_top_sellers_scatter(client, cfg: dict) -> tuple[go.Figure, str | None]:
    """
    Scatter: total_orders (x) vs total_revenue (y).
    Bubble size & colour = avg_review_score.
    Symbol = power_seller flag (star) vs regular (circle).
    Footnote states the Power Seller definition.
    """
    sql = f"""
    SELECT
        SUBSTR(seller_id, 1, 8)     AS seller_short,
        seller_state,
        total_orders,
        ROUND(total_revenue, 0)     AS total_revenue,
        avg_review_score,
        CASE WHEN power_seller THEN 'Power Seller' ELSE 'Regular' END AS seller_type
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    WHERE total_orders > 0
      AND avg_review_score IS NOT NULL
    """
    try:
        df = run_query(client, sql)
        fig = px.scatter(
            df,
            x="total_orders",
            y="total_revenue",
            size="avg_review_score",
            size_max=18,
            color="avg_review_score",
            color_continuous_scale=[
                [0, COLORS["red"]], [0.5, COLORS["orange"]], [1, COLORS["green"]]
            ],
            symbol="seller_type",
            symbol_map={"Power Seller": "star", "Regular": "circle"},
            hover_data={
                "seller_short": True,
                "seller_state": True,
                "avg_review_score": ":.2f",
                "seller_type": True,
            },
            labels={
                "total_orders": "Total Orders",
                "total_revenue": "Total Revenue (BRL)",
                "avg_review_score": "Avg Rating",
                "seller_type": "Seller Type",
            },
            opacity=0.75,
        )
        fig.update_layout(**_layout(
            title="Sellers Sales Orders vs Revenue with Average Rating Score",
        ))
        fig.update_layout(
            legend=dict(title="Seller Type", orientation="v", x=1.12, y=0.5),
            coloraxis_colorbar=dict(title="Avg Rating"),
        )
        fig.update_xaxes(title_text="Total Orders", title_standoff=30)
        return fig, None
    except Exception as e:
        return _empty_fig(f"Error: {e}"), str(e)


# ── Power sellers bar ─────────────────────────────────────────

def get_power_sellers_bar(client, cfg: dict) -> tuple[go.Figure, str | None]:
    """
    Dual-axis bar: power sellers sorted by AOV descending.
    Left y = avg_order_value (bars), right y = total_orders (line).
    """
    sql = f"""
    SELECT
        SUBSTR(seller_id, 1, 8)         AS seller_short,
        total_orders,
        ROUND(avg_order_value, 0)       AS avg_order_value
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    WHERE power_seller IS TRUE
    ORDER BY avg_order_value DESC
    """
    try:
        df = run_query(client, sql)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=df["seller_short"],
                y=df["avg_order_value"],
                name="Avg Order Value (BRL)",
                marker_color=COLORS["orange"],
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=df["seller_short"],
                y=df["total_orders"],
                name="Total Orders",
                mode="markers+lines",
                marker=dict(color=COLORS["gold"], size=9, symbol="diamond"),
                line=dict(color=COLORS["gold"], width=2, dash="dot"),
            ),
            secondary_y=True,
        )
        fig.update_layout(**_layout(
            title=f"Power Sellers ({len(df)}) — Average Order Value Ranking vs Total Orders",
            legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
            bargap=0.25,
        ))
        fig.update_xaxes(title_text="Seller ID (first 8 chars, ranked by AOV ↓)")
        fig.update_yaxes(title_text="Avg Order Value (BRL)", secondary_y=False, tickprefix="R$")
        fig.update_yaxes(title_text="Total Orders", secondary_y=True)
        return fig, None
    except Exception as e:
        return _empty_fig(f"Error: {e}"), str(e)


# ── On-time rate by state ─────────────────────────────────────

def get_state_ontime_chart(client, cfg: dict) -> tuple[go.Figure, str | None]:
    """
    Bar chart of average on-time delivery rate by seller state.
    Bar text shows on-time rate % + delayed order count.
    """
    sql = f"""
    SELECT
        seller_state,
        COUNT(*)                                            AS sellers,
        ROUND(AVG(on_time_rate), 3)                         AS avg_on_time,
        CAST(ROUND(SUM(total_orders * (1 - on_time_rate)), 0) AS INT64) AS delayed_orders
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    WHERE on_time_rate IS NOT NULL
      AND total_orders > 0
    GROUP BY 1
    ORDER BY avg_on_time DESC
    """
    try:
        df = run_query(client, sql)
        bar_text = [
            f"{row.avg_on_time:.0%}\n{row.delayed_orders:,}"
            for row in df.itertuples()
        ]
        fig = px.bar(
            df,
            x="seller_state",
            y="avg_on_time",
            color="avg_on_time",
            color_continuous_scale=[
                [0, COLORS["red"]], [0.5, COLORS["orange"]], [1, COLORS["green"]]
            ],
            text=bar_text,
            custom_data=["sellers", "delayed_orders"],
            labels={"seller_state": "State", "avg_on_time": "On-Time Rate"},
        )
        fig.update_traces(
            textposition="inside",
            textangle=-90,
            textfont=dict(size=10, color="#FFFFFF"),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "On-Time Rate: %{y:.1%}<br>"
                "Delayed Orders: %{customdata[1]:,}<br>"
                "Sellers: %{customdata[0]}<extra></extra>"
            ),
        )
        fig.update_layout(**_layout(
            title="Average On-Time Delivery Rate by Seller State",
            xaxis_title="Seller State",
            margin=dict(b=60),
        ))
        fig.update_layout(coloraxis_colorbar=dict(title="On-Time Rate", tickformat=".0%"))
        fig.update_yaxes(title_text="On-Time Rate", tickformat=".0%")
        return fig, None
    except Exception as e:
        return _empty_fig(f"Error: {e}"), str(e)


# ── At-risk sellers ───────────────────────────────────────────

def get_at_risk_scatter(client, cfg: dict) -> tuple[go.Figure, str | None]:
    """
    Scatter: top 20 at-risk sellers by revenue.
    x = avg_review_score, y = on_time_rate, size = total_revenue.
    Colour & symbol = breach reason (Low Rating / High Late Rate / Both).
    """
    sql = f"""
    SELECT
        SUBSTR(seller_id, 1, 8)     AS seller_short,
        seller_state,
        avg_review_score,
        on_time_rate,
        ROUND(total_revenue, 0)     AS total_revenue,
        CASE
            WHEN avg_review_score < 3.0 AND on_time_rate < 0.70 THEN 'Both'
            WHEN avg_review_score < 3.0 THEN 'Low Rating'
            ELSE 'High Late Rate'
        END                         AS breach
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    WHERE at_risk IS TRUE
      AND avg_review_score IS NOT NULL
      AND on_time_rate IS NOT NULL
    ORDER BY total_revenue DESC
    LIMIT 20
    """
    try:
        df = run_query(client, sql)
        fig = px.scatter(
            df,
            x="avg_review_score",
            y="on_time_rate",
            color="breach",
            color_discrete_map={
                "Low Rating":    COLORS["gold"],
                "High Late Rate": COLORS["orange"],
                "Both":          COLORS["red"],
            },
            size="total_revenue",
            size_max=20,
            symbol="breach",
            symbol_map={
                "Low Rating":    "x",
                "High Late Rate": "triangle-down",
                "Both":          "x-open-dot",
            },
            text="seller_short",
            hover_data={
                "seller_short": True,
                "seller_state": True,
                "avg_review_score": ":.2f",
                "on_time_rate": ":.1%",
                "total_revenue": ":,.0f",
                "breach": True,
            },
            opacity=0.85,
            title="Top 20 At-Risk Sellers by Revenue — Review Score vs On-Time Rate (size = revenue)",
            labels={
                "avg_review_score": "Avg Review Score",
                "on_time_rate":     "On-Time Delivery Rate",
                "breach":           "At-Risk Reason",
            },
        )
        fig.update_traces(textposition="top center", textfont=dict(size=9, color="#CCCCCC"))
        fig.add_vline(x=3.0, line_dash="dash", line_color="#888888",
                      annotation_text="Review < 3.0", annotation_position="top right",
                      annotation_font_color="#888888")
        fig.add_hline(y=0.70, line_dash="dash", line_color="#888888",
                      annotation_text="On-time < 70%", annotation_position="bottom right",
                      annotation_font_color="#888888")
        fig.update_layout(**_layout(
            title="Top 20 At-Risk Sellers by Revenue — Review Score vs On-Time Rate (size = revenue)",
        ))
        return fig, None
    except Exception as e:
        return _empty_fig(f"Error: {e}"), str(e)


# ── Seller map ────────────────────────────────────────────────

def get_seller_map(client, cfg: dict) -> tuple[go.Figure, str | None]:
    """
    Scatter map of sellers by lat/lon.
    Marker size = total_revenue, colour = avg_review_score.
    """
    sql = f"""
    SELECT
        seller_id,
        seller_city,
        seller_state,
        latitude,
        longitude,
        total_orders,
        ROUND(total_revenue, 0)     AS total_revenue,
        avg_review_score,
        CASE WHEN power_seller THEN 'Power' WHEN at_risk THEN 'At-Risk' ELSE 'Regular' END AS seller_type
    FROM {qualified_table(cfg, 'Dim_Sellers')}
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
      AND total_orders > 0
    """
    try:
        df = run_query(client, sql)
        color_map = {"Power": COLORS["green"], "At-Risk": COLORS["red"], "Regular": COLORS["orange"]}
        fig = px.scatter_map(
            df,
            lat="latitude",
            lon="longitude",
            color="seller_type",
            color_discrete_map=color_map,
            size="total_revenue",
            size_max=20,
            hover_name="seller_id",
            hover_data={
                "seller_city": True,
                "seller_state": True,
                "total_orders": True,
                "total_revenue": True,
                "avg_review_score": True,
                "latitude": False,
                "longitude": False,
            },
            zoom=3,
            center={"lat": -14.2, "lon": -51.9},
        )
        fig.update_layout(
            **_layout(title="Seller Geographic Distribution"),
            map_style="carto-darkmatter",
            height=520,
            legend=dict(
                bgcolor="rgba(10,5,0,0.85)",
                bordercolor="rgba(255,140,0,0.3)",
                borderwidth=1,
                font=dict(color=COLORS["text_secondary"]),
            ),
        )
        return fig, None
    except Exception as e:
        return _empty_fig(f"Error: {e}"), str(e)
