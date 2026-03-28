"""
dashboards/kendra/charts.py
─────────────────────────────
Chart builder functions for Geography Analytics dashboard.
Each function returns a Plotly figure or HTML string.
"""

import plotly.express as px
import plotly.graph_objects as go
from copy import deepcopy

from shared.theme import COLORS, PLOTLY_LAYOUT
from shared.components import kpi_card, error_figure
from shared.utils import dev_config_path, make_bq_client_getter

_get_client = make_bq_client_getter(dev_config_path("kendra"))


def _layout(**overrides):
    d = deepcopy(PLOTLY_LAYOUT)
    d.update(overrides)
    return d


def load_kpis():
    from dashboards.kendra.queries import get_kpi_data
    client, cfg, err = _get_client()
    if err:
        return '<div class="olist-card" style="color:#FF4444">GCP not configured</div>'
    try:
        df = get_kpi_data(client, cfg)
        r = df.iloc[0]
        cards = "".join([
            kpi_card("States Covered", str(int(r["total_states"])), "orange"),
            kpi_card("Delivered Orders", f"{int(r['total_orders']):,}", "gold"),
            kpi_card("Avg Delivery Days", str(r["avg_delivery_days"]), "green"),
            kpi_card("On-Time Delivery", f"{r['on_time_pct']}%", "green"),
        ])
        return f'<div style="display:flex;gap:12px;flex-wrap:nowrap">{cards}</div>'
    except Exception as e:
        return f'<div class="olist-card" style="color:#FF4444">Error: {e}</div>'


def _brazil_geojson():
    """Load or fetch Brazil states GeoJSON (cached in module)."""
    if not hasattr(_brazil_geojson, "_cache"):
        import json
        import urllib.request
        url = (
            "https://raw.githubusercontent.com/codeforamerica/"
            "click_that_hood/master/public/data/brazil-states.geojson"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            _brazil_geojson._cache = json.loads(resp.read())
    return _brazil_geojson._cache


def load_choropleth():
    from dashboards.kendra.queries import get_customer_density_by_state
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_customer_density_by_state(client, cfg)
        geojson = _brazil_geojson()
        # Map state abbreviations to GeoJSON feature names
        _abbr_to_name = {
            "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
            "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
            "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
            "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba",
            "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
            "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
            "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
            "TO": "Tocantins",
        }
        df = df.copy()
        df["state_name"] = df["state"].map(_abbr_to_name)
        fig = px.choropleth(
            df, locations="state_name", color="orders",
            geojson=geojson, featureidkey="properties.name",
            color_continuous_scale=["#1a0a00", COLORS["orange"], COLORS["gold"]],
            hover_data={"revenue": ":,.0f", "orders": ":,", "state": True,
                        "state_name": False},
        )
        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
        fig.update_layout(**_layout(
            title="Order Volume by State",
            margin=dict(l=0, r=0, t=40, b=0), height=450,
            geo=dict(bgcolor="rgba(0,0,0,0)"),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_delivery_bar():
    from dashboards.kendra.queries import get_delivery_time_by_state
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_delivery_time_by_state(client, cfg)
        fig = px.bar(
            df, x="avg_delivery_days", y="state", orientation="h",
            color="avg_delivery_days",
            color_continuous_scale=[COLORS["green"], COLORS["gold"], COLORS["red"]],
            hover_data={"orders": ":,"},
        )
        fig.update_layout(**_layout(
            title="Avg Delivery Days by State",
            yaxis=dict(autorange="reversed", categoryorder="total ascending",
                       gridcolor="rgba(255,140,0,0.08)"),
            xaxis=dict(title="Days", gridcolor="rgba(255,140,0,0.08)"),
            height=600, showlegend=False, coloraxis_showscale=False,
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_scatter_map():
    from dashboards.kendra.queries import get_geolocation_sample
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_geolocation_sample(client, cfg)
        fig = px.scatter_map(
            df, lat="lat", lon="lng", color="state",
            hover_data=["city"],
            zoom=3, center={"lat": -14.5, "lon": -51},
            height=500,
        )
        fig.update_layout(**_layout(
            title="Customer Locations (3k sample)",
            margin=dict(l=0, r=0, t=40, b=0),
            map_style="carto-darkmatter",
            legend=dict(bgcolor="rgba(0,0,0,0.7)",
                        font=dict(color="rgba(255,140,0,0.7)", size=10)),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_underserved_table():
    from dashboards.kendra.queries import get_underserved_regions
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_underserved_regions(client, cfg)
        colors = []
        for ratio in df["customer_seller_ratio"]:
            if ratio >= 100:
                colors.append(COLORS["red"])
            elif ratio >= 50:
                colors.append(COLORS["orange"])
            else:
                colors.append(COLORS["green"])
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["State", "Customers", "Sellers", "Cust/Seller Ratio"],
                fill_color="#262626", font=dict(color="#A0A0A0", size=12),
                align="left",
            ),
            cells=dict(
                values=[df["state"], df["customers"], df["sellers"],
                        df["customer_seller_ratio"]],
                fill_color="#1A1A1A",
                font=dict(color=[["#F0F0F0"] * len(df),
                                 ["#F0F0F0"] * len(df),
                                 ["#F0F0F0"] * len(df),
                                 colors], size=12),
                align="left",
            ),
        )])
        fig.update_layout(**_layout(
            title="Underserved Regions (High Customer / Low Seller)",
            height=500, margin=dict(l=0, r=0, t=40, b=0),
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_seller_distribution():
    from dashboards.kendra.queries import get_seller_distribution_by_state
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_seller_distribution_by_state(client, cfg)
        fig = px.bar(
            df, x="state", y="sellers", color="sellers",
            color_continuous_scale=["#1a0a00", COLORS["green"], COLORS["gold"]],
        )
        fig.update_layout(**_layout(
            title="Seller Distribution by State",
            xaxis=dict(title="State", gridcolor="rgba(255,140,0,0.08)"),
            yaxis=dict(title="Sellers", gridcolor="rgba(255,140,0,0.08)"),
            height=400, showlegend=False, coloraxis_showscale=False,
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_revenue_bar():
    from dashboards.kendra.queries import get_revenue_by_state
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_revenue_by_state(client, cfg).head(15)
        fig = px.bar(
            df, x="state", y="revenue", color="revenue",
            color_continuous_scale=["#1a0a00", COLORS["orange"], COLORS["gold"]],
            hover_data={"orders": ":,", "avg_order_value": ":.2f"},
        )
        fig.update_layout(**_layout(
            title="Revenue by State (Top 15)",
            xaxis=dict(title="State", gridcolor="rgba(255,140,0,0.08)"),
            yaxis=dict(title="Revenue (R$)", gridcolor="rgba(255,140,0,0.08)"),
            height=400, showlegend=False, coloraxis_showscale=False,
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")


def load_monthly_trend():
    from dashboards.kendra.queries import get_monthly_orders_by_top_states
    client, cfg, err = _get_client()
    if err:
        return error_figure("GCP not configured")
    try:
        df = get_monthly_orders_by_top_states(client, cfg)
        fig = px.line(
            df, x="month", y="orders", color="state",
            markers=True,
        )
        fig.update_layout(**_layout(
            title="Monthly Orders - Top 5 States",
            xaxis=dict(title="Month", gridcolor="rgba(255,140,0,0.08)"),
            yaxis=dict(title="Orders", gridcolor="rgba(255,140,0,0.08)"),
            height=400,
        ))
        return fig
    except Exception as e:
        return error_figure(f"Error: {e}")
