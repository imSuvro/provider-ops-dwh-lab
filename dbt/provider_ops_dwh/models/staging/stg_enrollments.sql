with source as (
    select * from {{ source('raw', 'mongo_enrollments') }}
),

renamed as (
    select
        source_id as enrollment_id,
        nullif(trim(raw_doc ->> 'patient_id'), '') as patient_id,
        nullif(trim(raw_doc ->> 'customer_id'), '') as customer_id,
        nullif(trim(raw_doc ->> 'provider_id'), '') as provider_id,
        nullif(trim(raw_doc ->> 'program_id'), '') as program_id,
        nullif(trim(raw_doc ->> 'program_code'), '') as program_code,
        upper(nullif(trim(raw_doc ->> 'status'), '')) as enrollment_status,
        (raw_doc #>> '{received_at,$date}')::timestamptz as received_at,
        (raw_doc #>> '{status_updated_at,$date}')::timestamptz
            as status_updated_at,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
