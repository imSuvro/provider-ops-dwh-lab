-- Grain: one row per customer, program, and calendar month.
-- Counts are distinct patients at the patient-month grain. Billing candidates
-- reflect the source export flag; billable-ready patients use computed rules.

with patient_month as (
    select * from {{ ref('mart_patient_month') }}
),

grouped as (
    select
        patient_month,
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name,
        count(distinct patient_id) as patient_count,
        count(distinct patient_id) filter (
            where is_active_enrollment
        ) as active_patient_count,
        count(distinct patient_id) filter (
            where has_completed_consent
        ) as consented_patient_count,
        sum(timer_minutes) as timer_minutes,
        count(distinct patient_id) filter (
            where device_status = 'DELAYED'
        ) as delayed_device_count,
        count(distinct patient_id) filter (
            where coalesce(source_billable_candidate, false)
        ) as billable_candidate_count,
        count(distinct patient_id) filter (
            where is_billable_ready
        ) as billable_ready_patient_count
    from patient_month
    group by
        patient_month,
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name
)

select
    md5(concat_ws(
        '|',
        coalesce(customer_id, 'MISSING'),
        coalesce(program_id, 'MISSING'),
        patient_month::text
    )) as customer_performance_key,
    *,
    round(
        billable_ready_patient_count::numeric
        / nullif(patient_count, 0),
        4
    ) as billable_readiness_rate
from grouped
