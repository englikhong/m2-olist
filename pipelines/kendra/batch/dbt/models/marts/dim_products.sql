select
    p.product_id,
    p.product_category_name,
    case p.product_category_name
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
        when 'brinquedos' then 'Toys'
        when 'cool_stuff' then 'Cool Stuff'
        when 'perfumaria' then 'Perfumery'
        when 'papelaria' then 'Stationery'
        when 'fashion_bolsas_e_acessorios' then 'Fashion Bags Accessories'
        else coalesce(p.product_category_name, 'Other')
    end as product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    round((p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000, 2) as volume_litres
from {{ ref('stg_products') }} p
