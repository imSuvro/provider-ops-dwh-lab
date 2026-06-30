-- Grain: one row per customer, provider, program, and enrollment status.
-- Counts preserve the current source status and expose both enrollments and
-- distinct patients for funnel reporting.

with enrollments as (
    select * from {{ ref('stg_enrollments') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

providers as (
    select * from {{ ref('stg_providers') }}
),

programs as (
    select * from {{ ref('stg_programs') }}
),

grouped as (
    select
        e.customer_id,
        c.customer_name,
        e.provider_id,
        p.provider_name,
        e.program_id,
        e.program_code,
        pr.program_name,
        e.enrollment_status,
        count(*) as enrollment_count,
        count(distinct e.patient_id) as patient_count,
        min(e.received_at) as first_received_at,
        max(e.status_updated_at) as latest_status_updated_at
    from enrollments e
    left join customers c
        on e.customer_id = c.customer_id
    left join providers p
        on e.provider_id = p.provider_id
    left join programs pr
        on e.program_id = pr.program_id
    group by
        e.customer_id,
        c.customer_name,
        e.provider_id,
        p.provider_name,
        e.program_id,
        e.program_code,
        pr.program_name,
        e.enrollment_status
)

select
    md5(concat_ws(
        '|',
        coalesce(customer_id, 'MISSING'),
        coalesce(provider_id, 'MISSING'),
        coalesce(program_id, 'MISSING'),
        coalesce(enrollment_status, 'MISSING')
    )) as enrollment_funnel_key,
    *
from grouped
