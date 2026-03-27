-- Dim_Sellers: one row per seller with aggregated performance metrics.
-- Rebuilt from Fact_Orders so delivery/review metrics stay consistent.
WITH order_metrics AS (
    SELECT
        seller_id,
        COUNT(DISTINCT order_id)                                            AS total_orders,
        ROUND(SUM(items_total), 2)                                          AS total_revenue,
        ROUND(AVG(review_score), 2)                                         AS avg_review_score,
        ROUND(
            COUNTIF(on_time_delivery IS TRUE)
                / NULLIF(COUNTIF(on_time_delivery IS NOT NULL), 0),
            3
        )                                                                   AS on_time_rate
    FROM {{ ref('Fact_Orders') }}
    GROUP BY 1
),
product_counts AS (
    SELECT
        seller_id,
        COUNT(DISTINCT product_id) AS unique_products
    FROM {{ ref('stg_order_items') }}
    GROUP BY 1
),
-- Take one representative lat/lon per zip code prefix (already averaged in staging)
geo AS (
    SELECT
        TO_HEX(MD5(zip_code_prefix)) AS zip_hash,
        latitude,
        longitude
    FROM {{ ref('stg_geolocation') }}
),
-- Tag power sellers (top 1% revenue AND avg review >= 4)
revenue_ranked AS (
    SELECT
        seller_id,
        PERCENT_RANK() OVER (ORDER BY total_revenue) AS revenue_pct
    FROM order_metrics
)
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    g.latitude,
    g.longitude,
    COALESCE(om.total_orders, 0)                                            AS total_orders,
    COALESCE(om.total_revenue, 0)                                           AS total_revenue,
    ROUND(
        COALESCE(om.total_revenue, 0) / NULLIF(COALESCE(om.total_orders, 0), 0),
        2
    )                                                                       AS avg_order_value,
    om.avg_review_score,
    om.on_time_rate,
    COALESCE(pc.unique_products, 0)                                         AS unique_products,
    CASE
        WHEN rr.revenue_pct >= 0.99 AND om.avg_review_score >= 4.0 THEN TRUE
        ELSE FALSE
    END                                                                     AS power_seller,
    CASE
        WHEN om.avg_review_score < 3.0
          OR om.on_time_rate < 0.70
        THEN TRUE
        ELSE FALSE
    END                                                                     AS at_risk
FROM {{ ref('stg_sellers') }} s
LEFT JOIN order_metrics    om  USING (seller_id)
LEFT JOIN product_counts   pc  USING (seller_id)
LEFT JOIN revenue_ranked   rr  USING (seller_id)
LEFT JOIN geo              g   ON s.seller_zip_hash = g.zip_hash
