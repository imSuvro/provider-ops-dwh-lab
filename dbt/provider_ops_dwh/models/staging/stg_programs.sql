with source as (
    select * from {{ source('raw', 'mongo_programs') }}
),

renamed as (
    select
        source_id as program_id,
        nullif(trim(raw_doc ->> 'program_code'), '') as program_code,
        nullif(trim(raw_doc ->> 'program_name'), '') as program_name,
        (raw_doc ->> 'requires_device')::boolean as requires_device,
        (raw_doc ->> 'monthly_minimum_minutes')::integer
            as monthly_minimum_minutes,
        (raw_doc ->> 'active')::boolean as is_active,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
