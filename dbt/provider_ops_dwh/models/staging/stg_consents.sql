with source as (
    select * from {{ source('raw', 'mongo_consents') }}
),

renamed as (
    select
        source_id as consent_id,
        nullif(trim(raw_doc ->> 'enrollment_id'), '') as enrollment_id,
        nullif(trim(raw_doc ->> 'patient_id'), '') as patient_id,
        nullif(trim(raw_doc ->> 'program_code'), '') as program_code,
        upper(nullif(trim(raw_doc ->> 'status'), '')) as consent_status,
        upper(nullif(trim(raw_doc ->> 'method'), '')) as consent_method,
        (raw_doc #>> '{requested_at,$date}')::timestamptz as requested_at,
        (raw_doc #>> '{completed_at,$date}')::timestamptz as completed_at,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
