with source as (
    select * from {{ source('raw', 'mongo_device_orders') }}
),

renamed as (
    select
        source_id as device_order_id,
        nullif(trim(raw_doc ->> 'enrollment_id'), '') as enrollment_id,
        nullif(trim(raw_doc ->> 'patient_id'), '') as patient_id,
        nullif(trim(raw_doc ->> 'customer_id'), '') as customer_id,
        nullif(trim(raw_doc ->> 'program_code'), '') as program_code,
        nullif(trim(raw_doc ->> 'device_type'), '') as device_type,
        upper(nullif(trim(raw_doc ->> 'status'), '')) as order_status,
        (raw_doc #>> '{ordered_at,$date}')::timestamptz as ordered_at,
        (raw_doc #>> '{status_updated_at,$date}')::timestamptz
            as status_updated_at,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
