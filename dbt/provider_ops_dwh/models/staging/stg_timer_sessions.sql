with source as (
    select * from {{ source('raw', 'mongo_timer_sessions') }}
),

renamed as (
    select
        source_id as timer_session_id,
        nullif(trim(raw_doc ->> 'enrollment_id'), '') as enrollment_id,
        nullif(trim(raw_doc ->> 'patient_id'), '') as patient_id,
        nullif(trim(raw_doc ->> 'provider_id'), '') as provider_id,
        nullif(trim(raw_doc ->> 'program_code'), '') as program_code,
        (raw_doc ->> 'duration_minutes')::integer as duration_minutes,
        (raw_doc #>> '{session_date,$date}')::timestamptz::date
            as session_date,
        upper(nullif(trim(raw_doc ->> 'activity_type'), '')) as activity_type,
        extracted_at,
        source_updated_at
    from source
)

select * from renamed
