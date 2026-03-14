"""
dashboards/huey_ling/queries.py
─────────────────────────────────
BigQuery queries for Seller Performance dashboard.
Implement each function to return a pandas DataFrame.

Usage in app.py:
    from dashboards.huey_ling.queries import get_seller_leaderboard
    df = get_seller_leaderboard(client, cfg)
"""

# from shared.utils import run_query, qualified_table


def get_seller_leaderboard(client, cfg, limit: int = 20):
    """
    Top sellers by revenue, with review score and on-time rate.

    Expected columns:
        seller_id (str), seller_state (str), orders (int),
        revenue (float), avg_review_score (float), on_time_pct (float)
    """
    raise NotImplementedError("Implement get_seller_leaderboard")


def get_delivery_latency_distribution(client, cfg):
    """
    Distribution of orders by delivery delay (actual - estimated, in days).

    Expected columns:
        delay_days (int), orders (int)

    Hint: DATETIME_DIFF(order_delivered_customer_date,
                        order_estimated_delivery_date, DAY)
    """
    raise NotImplementedError("Implement get_delivery_latency_distribution")


def get_seller_rating_distribution(client, cfg):
    """
    Count of orders per seller state and review score (for heatmap).

    Expected columns:
        seller_state (str), review_score (int), count (int)
    """
    raise NotImplementedError("Implement get_seller_rating_distribution")


def get_at_risk_sellers(client, cfg):
    """
    Sellers flagged as at-risk: avg review < 3.0 OR late delivery rate > 30%.

    Expected columns:
        seller_id (str), seller_state (str), orders (int),
        avg_review_score (float), late_pct (float), risk_reason (str)
    """
    raise NotImplementedError("Implement get_at_risk_sellers")
