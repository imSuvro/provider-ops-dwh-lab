-- Purpose: list current data-quality issues with customer context and counts
-- that can be summarized in a dashboard.

with issues as (
    select
        q.data_quality_issue_key,
        q.issue_type,
        initcap(replace(q.issue_type, '_', ' ')) as issue_type_label,
        q.record_type,
        q.record_id,
        q.customer_id,
        c.customer_name,
        q.patient_id,
        q.issue_details
    from marts.mart_data_quality_issues q
    left join staging.stg_customers c
        on q.customer_id = c.customer_id
)

select
    *,
    count(*) over (
        partition by issue_type
    ) as issue_type_count,
    count(*) over () as total_issue_count
from issues
order by
    issue_type,
    customer_name nulls last,
    record_type,
    record_id;
