"""
dashboards/lanson/queries.py — v2 simplified
"""
from google.cloud import bigquery
from shared.utils import run_query, qualified_table


def get_nps_trend(client: bigquery.Client, cfg: dict):
    fct_r = qualified_table(cfg, "fct_reviews")
    sql = f"""
    SELECT
        review_month AS month,
        COUNTIF(nps_category = 'promoter')  AS promoters,
        COUNTIF(nps_category = 'passive')   AS passives,
        COUNTIF(nps_category = 'detractor') AS detractors,
        COUNT(*) AS total,
        ROUND(
            SAFE_DIVIDE(COUNTIF(nps_category='promoter')*100.0, COUNT(*)) -
            SAFE_DIVIDE(COUNTIF(nps_category='detractor')*100.0, COUNT(*))
        , 1) AS nps_score,
        ROUND(SAFE_DIVIDE(COUNTIF(nps_category='promoter')*100.0,  COUNT(*)), 1) AS promoter_pct,
        ROUND(SAFE_DIVIDE(COUNTIF(nps_category='passive')*100.0,   COUNT(*)), 1) AS passive_pct,
        ROUND(SAFE_DIVIDE(COUNTIF(nps_category='detractor')*100.0, COUNT(*)), 1) AS detractor_pct
    FROM {fct_r}
    WHERE review_month IS NOT NULL
    GROUP BY review_month
    ORDER BY review_month
    """
    return run_query(client, sql)


def get_silent_sufferer_trend(client: bigquery.Client, cfg: dict):
    fct_o = qualified_table(cfg, "fct_orders")
    fct_r = qualified_table(cfg, "fct_reviews")
    sql = f"""
    SELECT
        o.order_month AS month,
        COUNTIF(o.is_late) AS late_orders,
        COUNT(DISTINCT CASE
            WHEN o.is_late = TRUE
            AND r.order_id IS NULL
            THEN o.order_id END) AS silent_sufferers,
        ROUND(SAFE_DIVIDE(
            COUNT(DISTINCT CASE
                WHEN o.is_late = TRUE
                AND r.order_id IS NULL
                THEN o.order_id END) * 100.0,
            NULLIF(COUNTIF(o.is_late), 0)
        ), 1) AS silent_sufferer_pct
    FROM {fct_o} o
    LEFT JOIN {fct_r} r ON o.order_id = r.order_id
    WHERE o.order_month IS NOT NULL
    GROUP BY o.order_month
    ORDER BY o.order_month
    """
    return run_query(client, sql)


def get_category_nps(client: bigquery.Client, cfg: dict):
    dim_p = qualified_table(cfg, "dim_products")
    sql = f"""
    SELECT
        product_category,
        category_nps,
        overall_nps,
        nps_gap_vs_benchmark,
        nps_performance,
        total_orders,
        ROUND(avg_review_score, 2) AS avg_review_score
    FROM {dim_p}
    WHERE product_category IS NOT NULL
    ORDER BY category_nps ASC
    """
    return run_query(client, sql)


def get_fault_attribution_trend(client: bigquery.Client, cfg: dict):
    fct_r = qualified_table(cfg, "fct_reviews")
    sql = f"""
    SELECT
        review_month AS month,
        ROUND(SAFE_DIVIDE(
            COUNTIF(review_score <= 2 AND fault_attribution = 'logistics')*100.0,
            NULLIF(COUNTIF(review_score <= 2), 0)
        ), 1) AS logistics_pct,
        ROUND(SAFE_DIVIDE(
            COUNTIF(review_score <= 2 AND fault_attribution = 'seller_or_product')*100.0,
            NULLIF(COUNTIF(review_score <= 2), 0)
        ), 1) AS seller_product_pct,
        ROUND(SAFE_DIVIDE(
            COUNTIF(review_score <= 2 AND fault_attribution = 'other')*100.0,
            NULLIF(COUNTIF(review_score <= 2), 0)
        ), 1) AS other_pct
    FROM {fct_r}
    WHERE review_month IS NOT NULL
    GROUP BY review_month
    ORDER BY review_month
    """
    return run_query(client, sql)


def get_overall_kpis(client: bigquery.Client, cfg: dict) -> dict:
    fct_r = qualified_table(cfg, "fct_reviews")
    fct_o = qualified_table(cfg, "fct_orders")
    sql = f"""
    WITH review_kpis AS (
        SELECT
            ROUND(
                SAFE_DIVIDE(COUNTIF(nps_category='promoter')*100.0, COUNT(*)) -
                SAFE_DIVIDE(COUNTIF(nps_category='detractor')*100.0, COUNT(*))
            , 1) AS overall_nps,
            ROUND(AVG(review_score), 2) AS avg_score,
            COUNT(*) AS total_reviews,
            ROUND(SAFE_DIVIDE(COUNTIF(is_early_review)*100.0, COUNT(*)), 1)
                AS early_review_pct
        FROM {fct_r}
    ),
    sufferer_kpis AS (
        SELECT
            ROUND(SAFE_DIVIDE(
                COUNT(DISTINCT CASE
                    WHEN o.is_late = TRUE
                    AND r.order_id IS NULL
                    THEN o.order_id END) * 100.0,
                NULLIF(COUNTIF(o.is_late), 0)
            ), 1) AS silent_sufferer_pct
        FROM {fct_o} o
        LEFT JOIN {fct_r} r ON o.order_id = r.order_id
    )
    SELECT
        r.overall_nps,
        r.avg_score,
        r.total_reviews,
        r.early_review_pct,
        s.silent_sufferer_pct
    FROM review_kpis r
    CROSS JOIN sufferer_kpis s
    """
    df = run_query(client, sql)
    return df.iloc[0].to_dict() if len(df) else {}