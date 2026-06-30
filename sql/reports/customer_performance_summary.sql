-- Purpose: present the monthly customer and program scorecard with readable
-- percentages alongside the underlying counts.

select
    patient_month,
    customer_id,
    customer_name,
    program_id,
    program_code,
    program_name,
    patient_count,
    active_patient_count,
    round(
        100.0 * active_patient_count / nullif(patient_count, 0),
        2
    ) as active_patient_pct,
    consented_patient_count,
    round(
        100.0 * consented_patient_count / nullif(patient_count, 0),
        2
    ) as consented_patient_pct,
    timer_minutes,
    delayed_device_count,
    round(
        100.0 * delayed_device_count / nullif(patient_count, 0),
        2
    ) as delayed_device_pct,
    billable_candidate_count,
    billable_ready_patient_count,
    round(100.0 * billable_readiness_rate, 2)
        as billable_readiness_pct
from marts.mart_clinic_or_customer_performance
order by
    patient_month,
    customer_name,
    program_code;
