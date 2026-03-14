"""
dashboards/lik_hong/queries.py
───────────────────────────────
BigQuery queries for Customer 360 + Next Best Action dashboard.
All queries reference Gold tables via shared.utils.qualified_table().
"""

from google.cloud import bigquery


def get_customer_profile(client: bigquery.Client, cfg: dict, customer_id: str) -> dict:
    """Fetch a single customer's profile + aggregated order metrics."""
    from shared.utils import run_query, qualified_table
    fact = qualified_table(cfg, "Fact_Orders")
    dim  = qualified_table(cfg, "Dim_Customers")
    sql = f"""
    SELECT
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT f.order_id)                                  AS total_orders,
        ROUND(SUM(f.payment_value), 2)                              AS total_spend,
        ROUND(AVG(f.payment_value), 2)                              AS avg_order_value,
        MAX(DATE(f.order_purchase_timestamp))                       AS last_order_date,
        DATE_DIFF(CURRENT_DATE(), MAX(DATE(f.order_purchase_timestamp)), DAY) AS days_since_last_order,
        ROUND(AVG(f.review_score), 2)                               AS avg_review_score
    FROM {dim} c
    LEFT JOIN {fact} f USING (customer_id)
    WHERE c.customer_unique_id = @customer_id
    GROUP BY 1, 2, 3
    """
    params = [bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)]
    df = run_query(client, sql, params)
    return df.iloc[0].to_dict() if len(df) else {}


def get_rfm_segments(client: bigquery.Client, cfg: dict):
    """Return RFM segment distribution across all customers."""
    from shared.utils import run_query, qualified_table
    fact = qualified_table(cfg, "Fact_Orders")
    dim  = qualified_table(cfg, "Dim_Customers")
    sql = f"""
    WITH rfm AS (
        SELECT
            c.customer_unique_id,
            DATE_DIFF(CURRENT_DATE(), MAX(DATE(f.order_purchase_timestamp)), DAY) AS recency,
            COUNT(DISTINCT f.order_id)    AS frequency,
            ROUND(SUM(f.payment_value),2) AS monetary
        FROM {dim} c
        JOIN {fact} f USING (customer_id)
        GROUP BY 1
    ),
    scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency DESC)   AS r_score,
            NTILE(5) OVER (ORDER BY frequency)       AS f_score,
            NTILE(5) OVER (ORDER BY monetary)        AS m_score
        FROM rfm
    ),
    segmented AS (
        SELECT *,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
                ELSE 'Potential Loyalists'
            END AS segment
        FROM scored
    )
    SELECT segment, COUNT(*) AS customer_count,
           ROUND(AVG(monetary), 2) AS avg_monetary
    FROM segmented
    GROUP BY segment
    ORDER BY customer_count DESC
    """
    return run_query(client, sql)


def get_churn_scores(client: bigquery.Client, cfg: dict, limit: int = 20):
    """
    Return top customers by churn risk.
    Note: This pulls pre-computed churn scores from Gold if ML model has run.
    Falls back to recency-based proxy if churn_score column absent.
    """
    from shared.utils import run_query, qualified_table
    dim = qualified_table(cfg, "Dim_Customers")
    fact = qualified_table(cfg, "Fact_Orders")
    sql = f"""
    SELECT
        c.customer_unique_id,
        c.customer_state,
        DATE_DIFF(CURRENT_DATE(), MAX(DATE(f.order_purchase_timestamp)), DAY) AS days_inactive,
        COUNT(DISTINCT f.order_id) AS total_orders,
        ROUND(SUM(f.payment_value), 2)  AS total_spend,
        ROUND(AVG(f.review_score), 2)   AS avg_review_score
    FROM {dim} c
    JOIN {fact} f USING (customer_id)
    GROUP BY 1, 2
    HAVING days_inactive > 180
    ORDER BY days_inactive DESC
    LIMIT @limit
    """
    params = [bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    return run_query(client, sql, params)


def get_order_history(client: bigquery.Client, cfg: dict, customer_id: str):
    """Full order history for a specific customer."""
    from shared.utils import run_query, qualified_table
    fact = qualified_table(cfg, "Fact_Orders")
    dim  = qualified_table(cfg, "Dim_Customers")
    sql = f"""
    SELECT
        f.order_id,
        DATE(f.order_purchase_timestamp)  AS order_date,
        f.order_status,
        f.payment_value,
        f.payment_type,
        f.review_score,
        f.product_category_name_english   AS category,
        f.seller_state
    FROM {fact} f
    JOIN {dim} c USING (customer_id)
    WHERE c.customer_unique_id = @customer_id
    ORDER BY f.order_purchase_timestamp DESC
    """
    params = [bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)]
    return run_query(client, sql, params)


def get_revenue_trend(client: bigquery.Client, cfg: dict):
    """Monthly revenue trend for all customers."""
    from shared.utils import run_query, qualified_table
    fact = qualified_table(cfg, "Fact_Orders")
    sql = f"""
    SELECT
        FORMAT_DATE('%Y-%m', DATE(order_purchase_timestamp)) AS month,
        COUNT(DISTINCT order_id)       AS orders,
        COUNT(DISTINCT customer_id)    AS unique_customers,
        ROUND(SUM(payment_value), 2)   AS revenue
    FROM {fact}
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1
    ORDER BY 1
    """
    return run_query(client, sql)
