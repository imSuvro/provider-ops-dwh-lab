-- Purpose: show completed-consent conversion among observed patient-months
-- that have an enrollment record.

with enrolled_patient_months as (
    select
        patient_month,
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name,
        patient_id,
        consent_id,
        consent_status,
        has_completed_consent
    from marts.mart_patient_month
    where enrollment_id is not null
),

consent_summary as (
    select
        patient_month,
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name,
        count(distinct patient_id) as enrolled_patient_count,
        count(distinct patient_id) filter (
            where consent_id is not null
        ) as patient_with_consent_record_count,
        count(distinct patient_id) filter (
            where consent_status = 'PENDING'
        ) as pending_consent_patient_count,
        count(distinct patient_id) filter (
            where consent_status = 'DECLINED'
        ) as declined_consent_patient_count,
        count(distinct patient_id) filter (
            where has_completed_consent
        ) as completed_consent_patient_count
    from enrolled_patient_months
    group by
        patient_month,
        customer_id,
        customer_name,
        program_id,
        program_code,
        program_name
)

select
    *,
    round(
        100.0 * completed_consent_patient_count
        / nullif(enrolled_patient_count, 0),
        2
    ) as consent_conversion_pct
from consent_summary
order by
    patient_month,
    customer_name,
    program_code;
