-- Purpose: show the current enrollment-status distribution by customer and
-- program. This is a snapshot funnel, not a status-transition history.

with enrollment_status_counts as (
    select
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name,
        enrollment_status,
        case enrollment_status
            when 'RECEIVED' then 1
            when 'ELIGIBLE' then 2
            when 'CONSENTED' then 3
            when 'ONBOARDED' then 4
            when 'ACTIVE' then 5
            when 'DECLINED' then 6
            else 99
        end as funnel_stage_order,
        sum(enrollment_count) as enrollment_count
    from marts.mart_enrollment_funnel
    group by
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name,
        enrollment_status
),

with_conversion as (
    select
        *,
        sum(enrollment_count) over (
            partition by customer_id, program_id
        ) as total_enrollment_count,
        sum(enrollment_count) filter (
            where enrollment_status = 'ACTIVE'
        ) over (
            partition by customer_id, program_id
        ) as active_enrollment_count
    from enrollment_status_counts
)

select
    customer_id,
    customer_name,
    program_id,
    program_code,
    program_name,
    enrollment_status,
    funnel_stage_order,
    enrollment_count,
    total_enrollment_count,
    coalesce(active_enrollment_count, 0) as active_enrollment_count,
    round(
        100.0 * coalesce(active_enrollment_count, 0)
        / nullif(total_enrollment_count, 0),
        2
    ) as enrollment_conversion_pct
from with_conversion
order by
    customer_name,
    program_code,
    funnel_stage_order;
