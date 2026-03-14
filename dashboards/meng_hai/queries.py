"""
dashboards/meng_hai/queries.py
────────────────────────────────
BigQuery queries for Payment Analytics dashboard.
Implement each function to return a pandas DataFrame.

Usage in app.py:
    from dashboards.meng_hai.queries import get_payment_summary
    df = get_payment_summary(client, cfg)
"""

# from shared.utils import run_query, qualified_table


def get_payment_summary(client, cfg):
    """
    Total revenue, order count, AOV, and avg instalments by payment type.

    Expected columns:
        payment_type (str), orders (int), total_revenue (float),
        avg_order_value (float), avg_instalments (float)

    Hint:
        SELECT payment_type, COUNT(DISTINCT order_id) AS orders,
               SUM(payment_value) AS total_revenue, ...
        FROM <Dim_Payments> JOIN <Fact_Orders> USING (order_id)
        GROUP BY 1
    """
    raise NotImplementedError("Implement get_payment_summary")


def get_monthly_revenue_by_type(client, cfg):
    """
    Monthly revenue split by payment type.

    Expected columns:
        month (str, 'YYYY-MM'), payment_type (str), revenue (float)
    """
    raise NotImplementedError("Implement get_monthly_revenue_by_type")


def get_instalment_distribution(client, cfg):
    """
    Distribution of credit-card orders by number of instalments (1–24).

    Expected columns:
        instalments (int), orders (int)
    """
    raise NotImplementedError("Implement get_instalment_distribution")


def get_cancellation_rate(client, cfg):
    """
    Monthly cancellation rate.

    Expected columns:
        month (str, 'YYYY-MM'), canceled (int), total (int),
        cancel_rate_pct (float)
    """
    raise NotImplementedError("Implement get_cancellation_rate")
