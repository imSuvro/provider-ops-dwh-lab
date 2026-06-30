-- Grain: one row per detected issue and affected source record.
-- This mart turns common mapping and domain problems into reviewable rows while
-- leaving detailed sensitive source attributes in the raw layer.

with patients as (
    select * from {{ ref('stg_patients') }}
),

providers as (
    select * from {{ ref('stg_providers') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

enrollments as (
    select * from {{ ref('stg_enrollments') }}
),

consents as (
    select * from {{ ref('stg_consents') }}
),

device_orders as (
    select * from {{ ref('stg_device_orders') }}
),

duplicate_patient_external_ids as (
    select patient_external_id
    from patients
    where patient_external_id is not null
    group by patient_external_id
    having count(*) > 1
),

base_issues as (
    select
        'MISSING_PROVIDER' as issue_type,
        'patient' as record_type,
        p.patient_id as record_id,
        p.customer_id,
        p.patient_id,
        'Primary provider is missing or does not map to staging providers.'
            as issue_details
    from patients p
    left join providers pr
        on p.primary_provider_id = pr.provider_id
    where p.primary_provider_id is null or pr.provider_id is null

    union all

    select
        'MISSING_CONSENT' as issue_type,
        'enrollment' as record_type,
        e.enrollment_id as record_id,
        e.customer_id,
        e.patient_id,
        'Enrollment has no matching consent record.' as issue_details
    from enrollments e
    where not exists (
        select 1
        from consents c
        where c.enrollment_id = e.enrollment_id
    )

    union all

    select
        'INVALID_ENROLLMENT_STATUS' as issue_type,
        'enrollment' as record_type,
        enrollment_id as record_id,
        customer_id,
        patient_id,
        'Enrollment status is outside the supported status set.'
            as issue_details
    from enrollments
    where enrollment_status not in (
        'RECEIVED',
        'ELIGIBLE',
        'CONSENTED',
        'ONBOARDED',
        'ACTIVE',
        'DECLINED'
    )
        or enrollment_status is null

    union all

    select
        'INVALID_CONSENT_STATUS' as issue_type,
        'consent' as record_type,
        c.consent_id as record_id,
        e.customer_id,
        c.patient_id,
        'Consent status is outside the supported status set.'
            as issue_details
    from consents c
    left join enrollments e
        on c.enrollment_id = e.enrollment_id
    where c.consent_status not in ('PENDING', 'COMPLETED', 'DECLINED')
        or c.consent_status is null

    union all

    select
        'INVALID_DEVICE_STATUS' as issue_type,
        'device_order' as record_type,
        device_order_id as record_id,
        customer_id,
        patient_id,
        'Device status is outside the supported status set.'
            as issue_details
    from device_orders
    where order_status not in ('ORDERED', 'SHIPPED', 'DELIVERED', 'DELAYED')
        or order_status is null

    union all

    select
        'DUPLICATE_PATIENT_EXTERNAL_ID' as issue_type,
        'patient' as record_type,
        p.patient_id as record_id,
        p.customer_id,
        p.patient_id,
        'Patient external ID appears on more than one patient record.'
            as issue_details
    from patients p
    inner join duplicate_patient_external_ids d
        on p.patient_external_id = d.patient_external_id

    union all

    select
        'MISSING_CUSTOMER_MAPPING' as issue_type,
        'patient' as record_type,
        p.patient_id as record_id,
        p.customer_id,
        p.patient_id,
        'Patient customer is missing or does not map to staging customers.'
            as issue_details
    from patients p
    left join customers c
        on p.customer_id = c.customer_id
    where p.customer_id is null or c.customer_id is null
)

select
    md5(concat_ws(
        '|',
        issue_type,
        record_type,
        coalesce(record_id, 'MISSING')
    )) as data_quality_issue_key,
    issue_type,
    record_type,
    record_id,
    customer_id,
    patient_id,
    issue_details
from base_issues
