with source as (
    select * from {{ source('raw', 'mongo_coordinator_notes') }}
),

renamed as (
    select
        source_id as coordinator_note_id,
        nullif(trim(raw_doc ->> 'enrollment_id'), '') as enrollment_id,
        nullif(trim(raw_doc ->> 'patient_id'), '') as patient_id,
        nullif(trim(raw_doc ->> 'customer_id'), '') as customer_id,
        upper(nullif(trim(raw_doc ->> 'note_type'), '')) as note_type,
        (raw_doc #>> '{created_at,$date}')::timestamptz as created_at,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
