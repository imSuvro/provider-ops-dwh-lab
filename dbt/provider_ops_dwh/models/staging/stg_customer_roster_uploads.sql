with source as (
    select * from {{ source('raw', 'csv_customer_roster_uploads') }}
),

renamed as (
    select
        roster_record_id,
        customer_id,
        patient_id,
        provider_id,
        upper(nullif(trim(state), '')) as state,
        nullif(trim(program_interest), '') as program_code,
        uploaded_at::timestamptz as uploaded_at,
        source_file_name,
        source_row_number,
        loaded_at
    from source
)

select * from renamed
