-- Grain: one row per patient, program, and observed calendar month.
-- Billing readiness requires an active enrollment and completed consent by
-- month-end, the program's timer threshold, and a delivered device only when
-- the program requires one. Source billing candidacy is retained separately.

with enrollments as (
    select * from {{ ref('stg_enrollments') }}
),

consents as (
    select * from {{ ref('stg_consents') }}
),

timer_sessions as (
    select * from {{ ref('stg_timer_sessions') }}
),

device_orders as (
    select * from {{ ref('stg_device_orders') }}
),

billing_exports as (
    select * from {{ ref('stg_billing_exports') }}
),

patients as (
    select * from {{ ref('stg_patients') }}
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

observed_months as (
    select
        patient_id,
        program_code,
        date_trunc('month', received_at)::date as patient_month
    from enrollments
    where received_at is not null

    union

    select
        patient_id,
        program_code,
        date_trunc('month', requested_at)::date as patient_month
    from consents
    where requested_at is not null

    union

    select
        patient_id,
        program_code,
        date_trunc('month', session_date)::date as patient_month
    from timer_sessions
    where session_date is not null

    union

    select
        patient_id,
        program_code,
        date_trunc('month', ordered_at)::date as patient_month
    from device_orders
    where ordered_at is not null

    union

    select
        patient_id,
        program_code,
        patient_month
    from billing_exports
    where patient_month is not null
),

enrollment_ranked as (
    select
        *,
        row_number() over (
            partition by patient_id, program_code
            order by
                status_updated_at desc nulls last,
                received_at desc nulls last,
                enrollment_id desc
        ) as record_rank
    from enrollments
),

latest_enrollment as (
    select * from enrollment_ranked where record_rank = 1
),

consent_ranked as (
    select
        *,
        row_number() over (
            partition by patient_id, program_code
            order by
                coalesce(completed_at, requested_at) desc nulls last,
                consent_id desc
        ) as record_rank
    from consents
),

latest_consent as (
    select * from consent_ranked where record_rank = 1
),

device_ranked as (
    select
        *,
        row_number() over (
            partition by patient_id, program_code
            order by
                status_updated_at desc nulls last,
                ordered_at desc nulls last,
                device_order_id desc
        ) as record_rank
    from device_orders
),

latest_device_order as (
    select * from device_ranked where record_rank = 1
),

monthly_activity as (
    select
        patient_id,
        program_code,
        date_trunc('month', session_date)::date as patient_month,
        count(*) as timer_session_count,
        sum(duration_minutes) as timer_minutes
    from timer_sessions
    group by
        patient_id,
        program_code,
        date_trunc('month', session_date)::date
),

monthly_billing as (
    select
        patient_id,
        program_code,
        patient_month,
        max(customer_id) as customer_id,
        count(*) as billing_export_count,
        bool_or(billable_candidate) as source_billable_candidate,
        sum(amount) as billing_amount,
        max(currency) as currency
    from billing_exports
    group by patient_id, program_code, patient_month
),

assembled as (
    select
        m.patient_id,
        m.program_code,
        m.patient_month,
        coalesce(p.customer_id, e.customer_id, b.customer_id) as customer_id,
        coalesce(p.primary_provider_id, e.provider_id) as provider_id,
        pr.program_id,
        pr.program_name,
        pr.requires_device,
        pr.monthly_minimum_minutes,
        e.enrollment_id,
        e.enrollment_status,
        e.received_at as enrollment_received_at,
        e.status_updated_at as enrollment_status_updated_at,
        co.consent_id,
        co.consent_status,
        co.completed_at as consent_completed_at,
        d.device_order_id,
        d.device_type,
        d.order_status as device_status,
        d.status_updated_at as device_status_updated_at,
        coalesce(a.timer_session_count, 0) as timer_session_count,
        coalesce(a.timer_minutes, 0) as timer_minutes,
        coalesce(b.billing_export_count, 0) as billing_export_count,
        b.source_billable_candidate,
        coalesce(b.billing_amount, 0)::numeric(12, 2) as billing_amount,
        b.currency
    from observed_months m
    left join patients p
        on m.patient_id = p.patient_id
    left join latest_enrollment e
        on m.patient_id = e.patient_id
        and m.program_code = e.program_code
    left join latest_consent co
        on m.patient_id = co.patient_id
        and m.program_code = co.program_code
    left join latest_device_order d
        on m.patient_id = d.patient_id
        and m.program_code = d.program_code
    left join monthly_activity a
        on m.patient_id = a.patient_id
        and m.program_code = a.program_code
        and m.patient_month = a.patient_month
    left join monthly_billing b
        on m.patient_id = b.patient_id
        and m.program_code = b.program_code
        and m.patient_month = b.patient_month
    left join programs pr
        on m.program_code = pr.program_code
),

with_dimensions as (
    select
        a.*,
        c.customer_name,
        p.provider_name
    from assembled a
    left join customers c
        on a.customer_id = c.customer_id
    left join providers p
        on a.provider_id = p.provider_id
),

readiness_flags as (
    select
        *,
        (
            enrollment_status = 'ACTIVE'
            and coalesce(
                enrollment_status_updated_at,
                enrollment_received_at
            ) < patient_month + interval '1 month'
        ) as is_active_enrollment,
        (
            consent_status = 'COMPLETED'
            and consent_completed_at < patient_month + interval '1 month'
        ) as has_completed_consent,
        (
            coalesce(timer_minutes, 0)
            >= coalesce(monthly_minimum_minutes, 0)
        ) as has_required_minutes,
        case
            when program_id is null then false
            when not requires_device then true
            else (
                device_status = 'DELIVERED'
                and device_status_updated_at
                    < patient_month + interval '1 month'
            )
        end as is_device_ready
    from with_dimensions
)

select
    md5(concat_ws(
        '|',
        patient_id,
        program_code,
        patient_month::text
    )) as patient_month_key,
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
    enrollment_status,
    enrollment_received_at,
    consent_id,
    consent_status,
    consent_completed_at,
    device_order_id,
    device_type,
    device_status,
    requires_device,
    monthly_minimum_minutes,
    timer_session_count,
    timer_minutes,
    billing_export_count,
    source_billable_candidate,
    billing_amount,
    currency,
    is_active_enrollment,
    has_completed_consent,
    has_required_minutes,
    is_device_ready,
    (
        program_id is not null
        and is_active_enrollment
        and has_completed_consent
        and has_required_minutes
        and is_device_ready
    ) as is_billable_ready
from readiness_flags
