with source as (
    select * from {{ source('raw', 'mongo_patients') }}
),

renamed as (
    select
        source_id as patient_id,
        nullif(trim(raw_doc ->> 'patient_external_id'), '')
            as patient_external_id,
        nullif(trim(raw_doc ->> 'customer_id'), '') as customer_id,
        nullif(trim(raw_doc ->> 'primary_provider_id'), '')
            as primary_provider_id,
        upper(nullif(trim(raw_doc ->> 'state'), '')) as state,
        (raw_doc ->> 'active')::boolean as is_active,
        (raw_doc #>> '{created_at,$date}')::timestamptz as created_at,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
