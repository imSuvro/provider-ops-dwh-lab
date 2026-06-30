with source as (
    select * from {{ source('raw', 'mongo_customers') }}
),

renamed as (
    select
        source_id as customer_id,
        nullif(trim(raw_doc ->> 'customer_code'), '') as customer_code,
        nullif(trim(raw_doc ->> 'customer_name'), '') as customer_name,
        nullif(trim(raw_doc ->> 'region'), '') as region,
        nullif(trim(raw_doc ->> 'timezone'), '') as timezone,
        (raw_doc ->> 'active')::boolean as is_active,
        (raw_doc #>> '{contract_start_date,$date}')::timestamptz::date
            as contract_start_date,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
