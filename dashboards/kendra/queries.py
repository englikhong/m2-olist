"""
dashboards/kendra/queries.py
──────────────────────────────
BigQuery queries for Geography Analytics dashboard.
Each function returns a pandas DataFrame.
"""

from shared.utils import run_query, qualified_table


def get_kpi_data(client, cfg):
    """KPI summary: total states, total orders, avg delivery days, on-time %."""
    fact = qualified_table(cfg, "fact_orders")
    sql = f"""
    SELECT
        COUNT(DISTINCT customer_state) AS total_states,
        COUNT(*) AS total_orders,
        ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days,
        ROUND(SAFE_DIVIDE(COUNTIF(on_time_delivery = TRUE),
              COUNTIF(on_time_delivery IS NOT NULL)) * 100, 1) AS on_time_pct
    FROM {fact}
    WHERE order_status = 'delivered'
    """
    return run_query(client, sql)


def get_customer_density_by_state(client, cfg):
    """Customer count per Brazilian state (for choropleth)."""
    fact = qualified_table(cfg, "fact_orders")
    sql = f"""
    SELECT
        customer_state AS state,
        COUNT(*) AS orders,
        ROUND(SUM(payment_value), 2) AS revenue
    FROM {fact}
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1
    ORDER BY orders DESC
    """
    return run_query(client, sql)


def get_delivery_time_by_state(client, cfg):
    """Average actual delivery days by customer state."""
    fact = qualified_table(cfg, "fact_orders")
    sql = f"""
    SELECT
        customer_state AS state,
        ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days,
        COUNT(*) AS orders
    FROM {fact}
    WHERE order_status = 'delivered' AND actual_delivery_days IS NOT NULL
    GROUP BY 1
    ORDER BY avg_delivery_days DESC
    """
    return run_query(client, sql)


def get_geolocation_sample(client, cfg, limit: int = 3000):
    """Sample of customer lat/lng points for scatter map."""
    cust = qualified_table(cfg, "dim_customers")
    sql = f"""
    SELECT
        customer_lat AS lat,
        customer_lng AS lng,
        customer_state AS state,
        customer_city AS city
    FROM {cust}
    WHERE customer_lat IS NOT NULL AND customer_lng IS NOT NULL
        AND customer_lat BETWEEN -35 AND 6
        AND customer_lng BETWEEN -75 AND -30
    ORDER BY RAND()
    LIMIT {limit}
    """
    return run_query(client, sql)


def get_underserved_regions(client, cfg):
    """States with high customer count but low seller count."""
    cust = qualified_table(cfg, "dim_customers")
    sell = qualified_table(cfg, "dim_sellers")
    sql = f"""
    WITH cust_counts AS (
        SELECT customer_state AS state, COUNT(DISTINCT customer_id) AS customers
        FROM {cust}
        GROUP BY 1
    ),
    sell_counts AS (
        SELECT seller_state AS state, COUNT(DISTINCT seller_id) AS sellers
        FROM {sell}
        GROUP BY 1
    )
    SELECT
        c.state,
        c.customers,
        COALESCE(s.sellers, 0) AS sellers,
        ROUND(SAFE_DIVIDE(c.customers, COALESCE(s.sellers, 1)), 1)
            AS customer_seller_ratio
    FROM cust_counts c
    LEFT JOIN sell_counts s USING (state)
    ORDER BY customer_seller_ratio DESC
    """
    return run_query(client, sql)


def get_revenue_by_state(client, cfg):
    """Revenue and order metrics by state."""
    fact = qualified_table(cfg, "fact_orders")
    sql = f"""
    SELECT
        customer_state AS state,
        COUNT(*) AS orders,
        ROUND(SUM(payment_value), 2) AS revenue,
        ROUND(AVG(payment_value), 2) AS avg_order_value
    FROM {fact}
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1
    ORDER BY revenue DESC
    """
    return run_query(client, sql)


def get_seller_distribution_by_state(client, cfg):
    """Seller count per Brazilian state."""
    sell = qualified_table(cfg, "dim_sellers")
    sql = f"""
    SELECT
        seller_state AS state,
        COUNT(DISTINCT seller_id) AS sellers
    FROM {sell}
    GROUP BY 1
    ORDER BY sellers DESC
    """
    return run_query(client, sql)


def get_monthly_orders_by_top_states(client, cfg, top_n: int = 5):
    """Monthly order trend for top N states."""
    fact = qualified_table(cfg, "fact_orders")
    sql = f"""
    WITH top_states AS (
        SELECT customer_state
        FROM {fact}
        WHERE order_status NOT IN ('canceled', 'unavailable')
        GROUP BY 1
        ORDER BY COUNT(*) DESC
        LIMIT {top_n}
    )
    SELECT
        FORMAT_DATE('%Y-%m', DATE(f.order_purchase_timestamp)) AS month,
        f.customer_state AS state,
        COUNT(*) AS orders
    FROM {fact} f
    JOIN top_states t ON f.customer_state = t.customer_state
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    return run_query(client, sql)
