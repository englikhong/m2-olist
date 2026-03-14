"""
dashboards/kendra/queries.py
──────────────────────────────
BigQuery queries for Geography Analytics dashboard.
Implement each function to return a pandas DataFrame.

Usage in app.py:
    from dashboards.kendra.queries import get_customer_density_by_state
    df = get_customer_density_by_state(client, cfg)
"""

# from shared.utils import run_query, qualified_table


def get_customer_density_by_state(client, cfg):
    """
    Customer count per Brazilian state (for choropleth).

    Expected columns:
        state (str, 2-letter abbreviation e.g. 'SP'), customers (int)
    """
    raise NotImplementedError("Implement get_customer_density_by_state")


def get_delivery_time_by_state(client, cfg):
    """
    Average actual delivery days by customer state.

    Expected columns:
        state (str), avg_delivery_days (float)

    Hint: DATETIME_DIFF(order_delivered_customer_date,
                        order_purchase_timestamp, DAY)
    """
    raise NotImplementedError("Implement get_delivery_time_by_state")


def get_geolocation_sample(client, cfg, limit: int = 3000):
    """
    Sample of customer lat/lng points for scatter map.

    Expected columns:
        lat (float), lng (float), state (str)

    Hint: join Dim_Customers to Dim_Geolocation on zip_code_prefix.
          LIMIT to avoid rendering too many points.
    """
    raise NotImplementedError("Implement get_geolocation_sample")


def get_underserved_regions(client, cfg):
    """
    States with high customer count but low seller count (opportunity analysis).

    Expected columns:
        state (str), customers (int), sellers (int),
        customer_seller_ratio (float)

    Order by customer_seller_ratio DESC.
    """
    raise NotImplementedError("Implement get_underserved_regions")
