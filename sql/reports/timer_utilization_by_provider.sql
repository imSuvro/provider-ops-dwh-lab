-- Purpose: compare recorded timer minutes with program minimums for active
-- patient-months that have a positive timer requirement.

with timer_eligible_patient_months as (
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
        timer_session_count,
        timer_minutes,
        monthly_minimum_minutes,
        has_required_minutes
    from marts.mart_patient_month
    where is_active_enrollment
        and monthly_minimum_minutes > 0
),

provider_utilization as (
    select
        patient_month,
        customer_id,
        customer_name,
        provider_id,
        provider_name,
        program_id,
        program_code,
        program_name,
        count(distinct patient_id) as active_patient_count,
        count(distinct patient_id) filter (
            where has_required_minutes
        ) as patient_at_or_above_minimum_count,
        sum(timer_session_count) as timer_session_count,
        sum(timer_minutes) as timer_minutes,
        sum(monthly_minimum_minutes) as required_timer_minutes
    from timer_eligible_patient_months
    group by
        patient_month,
        customer_id,
        customer_name,
        provider_id,
        provider_name,
        program_id,
        program_code,
        program_name
)

select
    *,
    round(
        100.0 * timer_minutes
        / nullif(required_timer_minutes, 0),
        2
    ) as timer_utilization_pct
from provider_utilization
order by
    patient_month,
    customer_name,
    provider_name,
    program_code;
