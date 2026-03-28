with source as (select * from {{ source('olist_raw', 'order_items') }}),
renamed as (
    select
        concat(order_id, '_', cast(order_item_id as string)) as order_item_key,
        order_id,
        cast(order_item_id as int64)       as order_item_id,
        product_id,
        seller_id,
        cast(shipping_limit_date as timestamp) as shipping_limit_date,
        cast(price as float64)             as price,
        cast(freight_value as float64)     as freight_value
    from source
    where order_id is not null
)
select * from renamed
