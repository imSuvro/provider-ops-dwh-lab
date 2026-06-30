-- Purpose: list patient-program-months that meet every local billing-readiness
-- rule and show whether the source billing export agrees.

select
    patient_month,
    customer_id,
    customer_name,
    provider_id,
    provider_name,
    program_id,
    program_code,
    program_name,
    patient_id,
    enrollment_id,
    consent_id,
    device_order_id,
    timer_minutes,
    monthly_minimum_minutes,
    timer_minutes - coalesce(monthly_minimum_minutes, 0)
        as timer_minutes_above_minimum,
    device_status,
    coalesce(source_billable_candidate, false) as source_billable_candidate,
    billing_alignment_status,
    billing_amount,
    currency
from marts.mart_billable_activity
order by
    patient_month,
    customer_name,
    provider_name,
    program_code,
    patient_id;
