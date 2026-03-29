SELECT
    p.product_id,
    p.product_category_name,
    p.product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    ROUND((p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000, 2) AS volume_litres
FROM {{ ref('stg_products') }} p
