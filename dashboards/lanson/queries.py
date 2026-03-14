"""
dashboards/lanson/queries.py
──────────────────────────────
BigQuery queries for Reviews & Satisfaction dashboard.
Implement each function to return a pandas DataFrame.

Usage in app.py:
    from dashboards.lanson.queries import get_review_score_distribution
    df = get_review_score_distribution(client, cfg)
"""

# from shared.utils import run_query, qualified_table


def get_review_score_distribution(client, cfg):
    """
    Count and percentage of reviews per score (1–5).

    Expected columns:
        review_score (int), review_count (int), pct (float)
    """
    raise NotImplementedError("Implement get_review_score_distribution")


def get_review_score_over_time(client, cfg):
    """
    Monthly average review score.

    Expected columns:
        month (str, 'YYYY-MM'), avg_score (float)
    """
    raise NotImplementedError("Implement get_review_score_over_time")


def get_score_vs_delivery_delay(client, cfg):
    """
    Average delivery delay (actual - estimated, in days) grouped by review score.
    Negative values mean delivery was early.

    Expected columns:
        review_score (int), avg_delivery_delay_days (float)
    """
    raise NotImplementedError("Implement get_score_vs_delivery_delay")


def get_low_score_orders(client, cfg, max_score: int = 2):
    """
    Orders with review score <= max_score for triage.

    Expected columns:
        order_id (str), review_score (int), review_comment_message (str),
        order_purchase_timestamp (datetime), customer_state (str)
    """
    raise NotImplementedError("Implement get_low_score_orders")
