"""
dashboards/ben/queries.py
───────────────────────────
BigQuery queries for Product Analytics dashboard.
All functions return pandas DataFrames.

Usage in app.py:
    from dashboards.ben.queries import get_top_categories
    df = get_top_categories(client, cfg)
"""

from shared.utils import run_query, qualified_table


def get_kpi_summary(client, cfg):
    """
    High-level KPIs: total revenue, orders, unique products, avg review score.
    Returns: single-row DataFrame with columns: total_revenue, total_orders, unique_products, avg_review_score
    """
    fact = qualified_table(cfg, "Fact_Orders")

    items = f"`{cfg['project_id']}.olist_silver_ben.stg_order_items`"
    sql = f"""
    SELECT
        ROUND(SUM(f.items_total), 2)           AS total_revenue,
        COUNT(DISTINCT f.order_id)             AS total_orders,
        (SELECT COUNT(DISTINCT product_id) FROM {items}) AS unique_products,
        ROUND(AVG(f.review_score), 2)          AS avg_review_score
    FROM {fact} f
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    """
    return run_query(client, sql)


def get_top_categories(client, cfg, limit: int = 15):
    """
    Top product categories by revenue and order count.

    Expected columns:
        category (str), orders (int), revenue (float), avg_order_value (float), avg_review_score (float)
    """
    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    SELECT
        COALESCE(f.product_category_name_english, 'Unknown') AS category,
        COUNT(DISTINCT f.order_id)                           AS orders,
        ROUND(SUM(f.items_total), 2)                         AS revenue,
        ROUND(AVG(f.items_total), 2)                         AS avg_order_value,
        ROUND(AVG(f.review_score), 2)                        AS avg_review_score
    FROM {fact} f
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1
    ORDER BY revenue DESC
    LIMIT {limit}
    """
    return run_query(client, sql)


def get_top_products(client, cfg, limit: int = 20):
    """
    Top products by revenue.

    Expected columns:
        product_id (str), category (str), product_weight_g (float), orders (int), revenue (float)
    """
    fact = qualified_table(cfg, "Fact_Orders")
    products = qualified_table(cfg, "Dim_Products")
    items = f"`{cfg['project_id']}.olist_silver_ben.stg_order_items`"

    sql = f"""
    SELECT
        oi.product_id,
        COALESCE(p.product_category_name_english, 'Unknown')  AS category,
        p.product_weight_g,
        COUNT(DISTINCT f.order_id)                             AS orders,
        ROUND(SUM(oi.price), 2)                                AS revenue
    FROM {fact} f
    LEFT JOIN {items} oi USING (order_id)
    LEFT JOIN {products} p ON oi.product_id = p.product_id
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1, 2, 3
    ORDER BY revenue DESC
    LIMIT {limit}
    """
    return run_query(client, sql)


def get_category_review_scores(client, cfg, min_reviews: int = 50):
    """
    Average review score per product category (min N reviews).

    Expected columns:
        category (str), avg_score (float), review_count (int)
    """
    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    SELECT
        COALESCE(f.product_category_name_english, 'Unknown') AS category,
        ROUND(AVG(f.review_score), 2)                        AS avg_score,
        COUNT(DISTINCT f.order_id)                           AS review_count
    FROM {fact} f
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
      AND f.review_score IS NOT NULL
    GROUP BY 1
    HAVING COUNT(DISTINCT f.order_id) >= {min_reviews}
    ORDER BY avg_score DESC
    """
    return run_query(client, sql)


def get_monthly_trend_by_category(client, cfg, top_n: int = 10):
    """
    Monthly revenue by category, limited to top N categories by total revenue.
    Used for stacked bar chart.

    Expected columns:
        month (str, 'YYYY-MM'), category (str), revenue (float)
    """
    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    WITH top_cats AS (
        SELECT COALESCE(product_category_name_english, 'Unknown') AS category
        FROM {fact}
        WHERE order_status NOT IN ('canceled', 'unavailable')
        GROUP BY 1
        ORDER BY SUM(items_total) DESC
        LIMIT {top_n}
    )
    SELECT
        FORMAT_DATE('%Y-%m', DATE(f.order_purchase_timestamp)) AS month,
        COALESCE(f.product_category_name_english, 'Unknown')   AS category,
        ROUND(SUM(f.items_total), 2)                            AS revenue
    FROM {fact} f
    INNER JOIN top_cats
        ON COALESCE(f.product_category_name_english, 'Unknown') = top_cats.category
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1, 2
    ORDER BY 1 ASC
    """
    return run_query(client, sql)


def get_monthly_category_trend(client, cfg, category: str):
    """
    Monthly order and revenue trend for a given category.

    Expected columns:
        month (str, 'YYYY-MM'), orders (int), revenue (float)
    """
    from google.cloud import bigquery

    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    SELECT
        FORMAT_DATE('%Y-%m', DATE(f.order_purchase_timestamp)) AS month,
        COUNT(DISTINCT f.order_id)                             AS orders,
        ROUND(SUM(f.items_total), 2)                           AS revenue
    FROM {fact} f
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
      AND COALESCE(f.product_category_name_english, 'Unknown') = @category
    GROUP BY 1
    ORDER BY 1 ASC
    """
    params = [bigquery.ScalarQueryParameter("category", "STRING", category)]
    return run_query(client, sql, params)


def get_category_revenue_vs_reviews(client, cfg):
    """
    Category scatter data: revenue vs average review score.
    For bubble sized by order volume.
    """
    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    SELECT
        COALESCE(f.product_category_name_english, 'Unknown') AS category,
        ROUND(SUM(f.items_total), 2)                         AS total_revenue,
        ROUND(AVG(f.review_score), 2)                        AS avg_review_score,
        COUNT(DISTINCT f.order_id)                           AS order_volume
    FROM {fact} f
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
      AND f.review_score IS NOT NULL
    GROUP BY 1
    ORDER BY total_revenue DESC
    """
    return run_query(client, sql)


def get_top_products_by_top_categories(client, cfg, top_cats: int = 5, top_products: int = 10):
    """
    Top N products by revenue within the top M categories.

    Expected columns:
        product_id (str), category (str), revenue (float)
    """
    fact = qualified_table(cfg, "Fact_Orders")
    products = qualified_table(cfg, "Dim_Products")
    items = f"`{cfg['project_id']}.olist_silver_ben.stg_order_items`"

    sql = f"""
    WITH top_cats AS (
        SELECT COALESCE(product_category_name_english, 'Unknown') AS category
        FROM {fact}
        WHERE order_status NOT IN ('canceled', 'unavailable')
        GROUP BY 1
        ORDER BY SUM(items_total) DESC
        LIMIT {top_cats}
    ),
    product_rev AS (
        SELECT
            oi.product_id,
            COALESCE(p.product_category_name_english, 'Unknown') AS category,
            COUNT(*)                                             AS qty_sold,
            ROUND(SUM(oi.price), 2)                              AS revenue
        FROM {fact} f
        INNER JOIN top_cats tc
            ON COALESCE(f.product_category_name_english, 'Unknown') = tc.category
        INNER JOIN {items} oi USING (order_id)
        LEFT JOIN {products} p ON oi.product_id = p.product_id
        WHERE f.order_status NOT IN ('canceled', 'unavailable')
        GROUP BY 1, 2
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
        FROM product_rev
    )
    SELECT product_id, category, qty_sold, revenue
    FROM ranked
    WHERE rn <= {top_products}
    ORDER BY category ASC, revenue DESC
    """
    return run_query(client, sql)


def get_category_list(client, cfg):
    """
    Distinct product categories for dropdown filters.
    """
    fact = qualified_table(cfg, "Fact_Orders")

    sql = f"""
    SELECT DISTINCT
        COALESCE(product_category_name_english, 'Unknown') AS category
    FROM {fact}
    WHERE order_status NOT IN ('canceled', 'unavailable')
    ORDER BY category ASC
    """
    return run_query(client, sql)
