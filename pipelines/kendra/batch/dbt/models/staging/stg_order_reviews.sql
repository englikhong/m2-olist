with source as (select * from {{ source('olist_raw', 'order_reviews') }}),
renamed as (
    select
        review_id,
        order_id,
        cast(review_score as int64)              as review_score,
        cast(review_comment_title as string)     as review_comment_title,
        cast(review_comment_message as string)   as review_comment_message,
        cast(review_creation_date as timestamp)  as review_creation_date,
        cast(review_answer_timestamp as timestamp) as review_answer_timestamp
    from source
    where review_id is not null
)
select * from renamed
