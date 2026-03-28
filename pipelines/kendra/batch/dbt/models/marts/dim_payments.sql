select
    p.payment_key,
    p.order_id,
    p.payment_sequential,
    p.payment_type,
    p.payment_installments,
    p.payment_value,
    o.order_purchase_timestamp,
    o.customer_id
from {{ ref('stg_order_payments') }} p
left join {{ ref('stg_orders') }} o using (order_id)
