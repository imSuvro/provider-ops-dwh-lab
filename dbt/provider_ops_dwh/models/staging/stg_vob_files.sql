with source as (
    select * from {{ source('raw', 'csv_vob_files') }}
),

renamed as (
    select
        vob_id,
        patient_id,
        customer_id,
        nullif(trim(payer_name), '') as payer_name,
        upper(nullif(trim(coverage_status), '')) as coverage_status,
        verified_on::date as verified_on,
        nullif(trim(program), '') as program_code,
        estimated_copay::numeric(12, 2) as estimated_copay,
        source_file_name,
        source_row_number,
        loaded_at
    from source
)

select * from renamed
