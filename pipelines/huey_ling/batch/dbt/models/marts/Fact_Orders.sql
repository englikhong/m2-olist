-- One row per order-seller pair so the dashboard can filter/group by seller_id directly.
WITH order_items_agg AS (
    SELECT
        order_id,
        seller_id,
        COUNT(*)                   AS item_count,
        SUM(price)                 AS items_total,
        SUM(freight_value)         AS freight_total,
        COUNT(DISTINCT product_id) AS product_count
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id, seller_id
),
payments AS (
    SELECT
        order_id,
        SUM(payment_value)        AS payment_value,
        MAX(payment_type)         AS payment_type,
        MAX(payment_installments) AS payment_installments
    FROM {{ ref('stg_order_payments') }}
    GROUP BY order_id
),
reviews AS (
    SELECT
        order_id,
        MAX(review_score)           AS review_score,
        MAX(review_comment_message) AS review_comment
    FROM {{ ref('stg_order_reviews') }}
    GROUP BY order_id
)
SELECT
    CONCAT(o.order_id, '_', oi.seller_id) AS order_seller_key,
    o.order_id,
    oi.seller_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATE_DIFF(
        DATE(o.order_delivered_customer_date),
        DATE(o.order_estimated_delivery_date),
        DAY
    )                                                        AS delivery_delay_days,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN TRUE
        ELSE FALSE
    END                                                      AS on_time_delivery,
    oi.item_count,
    oi.items_total,
    oi.freight_total,
    COALESCE(p.payment_value, oi.items_total + oi.freight_total, 0) AS payment_value,
    p.payment_type,
    COALESCE(p.payment_installments, 1)                      AS payment_installments,
    r.review_score,
    r.review_comment
FROM {{ ref('stg_orders') }} o
JOIN order_items_agg oi USING (order_id)
LEFT JOIN payments p USING (order_id)
LEFT JOIN reviews  r USING (order_id)
