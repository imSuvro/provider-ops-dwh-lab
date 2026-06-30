with source as (
    select * from {{ source('raw', 'csv_billing_exports') }}
),

renamed as (
    select
        export_id,
        patient_id,
        customer_id,
        patient_month::date as patient_month,
        nullif(trim(program), '') as program_code,
        billable_candidate::boolean as billable_candidate,
        amount::numeric(12, 2) as amount,
        upper(nullif(trim(currency), '')) as currency,
        exported_at::timestamptz as exported_at,
        source_file_name,
        source_row_number,
        loaded_at
    from source
)

select * from renamed
