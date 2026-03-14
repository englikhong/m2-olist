"""
dashboards/ben/queries.py
───────────────────────────
BigQuery queries for Product Analytics dashboard.
Implement each function to return a pandas DataFrame.

Usage in app.py:
    from dashboards.ben.queries import get_top_categories
    df = get_top_categories(client, cfg)
"""

# from shared.utils import run_query, qualified_table


def get_top_categories(client, cfg, limit: int = 15):
    """
    Top product categories by revenue and order count.

    Expected columns:
        category (str), orders (int), revenue (float), avg_order_value (float)

    Note: use product_category_name_english (join translation in dbt Silver model).
    """
    raise NotImplementedError("Implement get_top_categories")


def get_top_products(client, cfg, limit: int = 20):
    """
    Top products by revenue.

    Expected columns:
        product_id (str), category (str), product_weight_g (float),
        orders (int), revenue (float)
    """
    raise NotImplementedError("Implement get_top_products")


def get_category_review_scores(client, cfg):
    """
    Average review score per product category (min 50 reviews).

    Expected columns:
        category (str), avg_score (float), review_count (int)
    """
    raise NotImplementedError("Implement get_category_review_scores")


def get_monthly_category_trend(client, cfg, category: str):
    """
    Monthly order and revenue trend for a given category.

    Expected columns:
        month (str, 'YYYY-MM'), orders (int), revenue (float)
    """
    raise NotImplementedError("Implement get_monthly_category_trend")
