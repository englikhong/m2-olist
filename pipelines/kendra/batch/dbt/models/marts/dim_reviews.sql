select
    r.review_id,
    r.order_id,
    r.review_score,
    r.review_comment_title,
    r.review_comment_message,
    r.review_creation_date,
    r.review_answer_timestamp,
    date_diff(r.review_answer_timestamp, r.review_creation_date, hour) as response_hours,
    o.customer_id,
    o.order_purchase_timestamp
from {{ ref('stg_order_reviews') }} r
left join {{ ref('stg_orders') }} o using (order_id)
