with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select customer_id, customer_key, customer_state, customer_zip_code_prefix
    from {{ ref('dim_customers') }}
),

geolocation as (
    select zip_code_prefix, city, state, lat, lng
    from {{ ref('dim_geolocation') }}
),

items as (
    select
        order_id,
        count(*)                    as item_count,
        sum(price)                  as items_total,
        sum(freight_value)          as freight_total,
        sum(price + freight_value)  as order_value,
        string_agg(distinct seller_id, ',') as seller_ids
    from {{ ref('stg_order_items') }}
    group by order_id
),

payments as (
    select
        order_id,
        sum(payment_value)        as payment_value,
        max(payment_type)         as payment_type,
        max(payment_installments) as payment_installments
    from {{ ref('stg_order_payments') }}
    group by order_id
),

reviews as (
    select
        order_id,
        max(review_score)          as review_score,
        max(review_comment_message) as review_comment
    from {{ ref('stg_order_reviews') }}
    group by order_id
),

products as (
    select
        oi.order_id,
        max(p.product_category_name) as product_category_name,
        max(case p.product_category_name
            when 'cama_mesa_banho' then 'Bed Bath Table'
            when 'beleza_saude' then 'Health Beauty'
            when 'esporte_lazer' then 'Sports Leisure'
            when 'moveis_decoracao' then 'Furniture Decor'
            when 'informatica_acessorios' then 'Computers Accessories'
            when 'utilidades_domesticas' then 'Housewares'
            when 'relogios_presentes' then 'Watches Gifts'
            when 'telefonia' then 'Telephony'
            when 'ferramentas_jardim' then 'Garden Tools'
            when 'automotivo' then 'Auto'
            else coalesce(p.product_category_name, 'Other')
        end) as product_category_name_english
    from {{ ref('stg_order_items') }} oi
    left join {{ ref('stg_products') }} p using (product_id)
    group by oi.order_id
),

sellers as (
    select
        oi.order_id,
        max(s.seller_state) as seller_state
    from {{ ref('stg_order_items') }} oi
    left join {{ ref('stg_sellers') }} s using (seller_id)
    group by oi.order_id
)

select
    -- Surrogate key for the fact row
    {{ dbt_utils.generate_surrogate_key(['o.order_id']) }} as order_key,

    -- Foreign keys to dimensions
    o.order_id,
    c.customer_key,
    cast(o.order_purchase_timestamp as date)       as order_date_key,
    cast(o.order_delivered_customer_date as date)  as delivery_date_key,

    -- Dimension attributes (degenerate / convenience denorms)
    o.order_status,
    c.customer_state,
    c.customer_zip_code_prefix,
    g.state as geo_state,
    g.city  as geo_city,

    -- Revenue measures
    coalesce(i.item_count, 0)                             as item_count,
    coalesce(i.items_total, 0)                            as items_total,
    coalesce(i.freight_total, 0)                          as freight_total,
    coalesce(pay.payment_value, i.order_value, 0)          as payment_value,
    pay.payment_type,
    coalesce(pay.payment_installments, 1)                 as payment_installments,

    -- Review measures
    r.review_score,
    r.review_comment,

    -- Product category
    pr.product_category_name,
    pr.product_category_name_english,

    -- Seller state
    sl.seller_state,

    -- Delivery time metrics (in days)
    date_diff(cast(o.order_delivered_customer_date as date),
              cast(o.order_purchase_timestamp as date), day) as actual_delivery_days,

    date_diff(cast(o.order_estimated_delivery_date as date),
              cast(o.order_purchase_timestamp as date), day) as estimated_delivery_days,

    date_diff(cast(o.order_estimated_delivery_date as date),
              cast(o.order_delivered_customer_date as date), day) as delivery_delta_days,

    case
        when o.order_delivered_customer_date is null then null
        when o.order_delivered_customer_date <= o.order_estimated_delivery_date then true
        else false
    end as on_time_delivery,

    -- Raw timestamps
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date

from orders o
left join customers   c  on o.customer_id = c.customer_id
left join geolocation g  on c.customer_zip_code_prefix = g.zip_code_prefix
left join items       i  on o.order_id = i.order_id
left join payments    pay on o.order_id = pay.order_id
left join reviews     r  on o.order_id = r.order_id
left join products    pr on o.order_id = pr.order_id
left join sellers     sl on o.order_id = sl.order_id
