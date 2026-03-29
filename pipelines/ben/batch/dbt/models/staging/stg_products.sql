WITH source AS (SELECT * FROM {{ source('olist_raw', 'olist_products') }}),
translation AS (
    SELECT product_category_name, product_category_name_english
    FROM {{ source('olist_raw', 'product_category_name_translation') }}
),
renamed AS (
    SELECT
        s.product_id,
        CAST(s.product_category_name AS STRING)                                    AS product_category_name,
        COALESCE(t.product_category_name_english, s.product_category_name)         AS product_category_name_english,
        CAST(s.product_name_lenght AS INT64)                                       AS product_name_length,
        CAST(s.product_description_lenght AS INT64)                                AS product_description_length,
        CAST(s.product_photos_qty AS INT64)                                        AS product_photos_qty,
        CAST(s.product_weight_g AS FLOAT64)                                        AS product_weight_g,
        CAST(s.product_length_cm AS FLOAT64)                                       AS product_length_cm,
        CAST(s.product_height_cm AS FLOAT64)                                       AS product_height_cm,
        CAST(s.product_width_cm AS FLOAT64)                                        AS product_width_cm
    FROM source s
    LEFT JOIN translation t ON CAST(s.product_category_name AS STRING) = t.product_category_name
    WHERE s.product_id IS NOT NULL
)
SELECT * FROM renamed
