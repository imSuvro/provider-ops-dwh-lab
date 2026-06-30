-- Grain: one row per patient, program, and month that meets every computed
-- readiness rule in mart_patient_month.
-- The source billing flag is shown as a comparison, not as a readiness input.

with patient_month as (
    select * from {{ ref('mart_patient_month') }}
),

ready_patient_months as (
    select *
    from patient_month
    where is_billable_ready
)

select
    patient_month_key as billable_activity_key,
    patient_month,
    patient_id,
    customer_id,
    customer_name,
    provider_id,
    provider_name,
    program_id,
    program_code,
    program_name,
    enrollment_id,
    consent_id,
    device_order_id,
    timer_minutes,
    monthly_minimum_minutes,
    device_status,
    source_billable_candidate,
    billing_amount,
    currency,
    is_billable_ready,
    case
        when coalesce(source_billable_candidate, false)
            then 'READY_AND_SOURCE_CANDIDATE'
        else 'READY_NOT_SOURCE_CANDIDATE'
    end as billing_alignment_status
from ready_patient_months
