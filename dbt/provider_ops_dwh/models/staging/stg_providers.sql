with source as (
    select * from {{ source('raw', 'mongo_providers') }}
),

renamed as (
    select
        source_id as provider_id,
        nullif(trim(raw_doc ->> 'provider_external_id'), '')
            as provider_external_id,
        nullif(trim(raw_doc ->> 'customer_id'), '') as customer_id,
        nullif(trim(raw_doc ->> 'display_name'), '') as provider_name,
        nullif(trim(raw_doc ->> 'specialty'), '') as specialty,
        (raw_doc ->> 'active')::boolean as is_active,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
