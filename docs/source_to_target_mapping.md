# Source-to-Target Mapping

This document traces each implemented synthetic source through PostgreSQL raw
tables, dbt staging models, and the final analytics marts.

## Flow conventions

- MongoDB is extracted to
  `raw_archive/mongo/{collection}/date=YYYY-MM-DD/data.jsonl` before loading.
- MongoDB raw tables retain the source document in `raw_doc` JSONB plus
  extraction metadata.
- CSV raw tables use typed columns and retain source file and row metadata.
- dbt staging models normalize names, types, timestamps, and status values.
- Staging excludes unnecessary sensitive-shaped fields such as patient names,
  birth dates, phone numbers, member references, shipment tracking references,
  and coordinator note text.
- A dash in the final-mart column means the staging model is available for
  analysis but is not currently consumed by a final mart.

## MongoDB mappings

| Source collection | Archive and raw target | dbt staging model | Final mart consumers |
| --- | --- | --- | --- |
| `customers` | `raw_archive/mongo/customers/...` → `raw.mongo_customers` | `stg_customers` | `mart_enrollment_funnel`, `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month, `mart_data_quality_issues` |
| `providers` | `raw_archive/mongo/providers/...` → `raw.mongo_providers` | `stg_providers` | `mart_enrollment_funnel`, `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_data_quality_issues` |
| `patients` | `raw_archive/mongo/patients/...` → `raw.mongo_patients` | `stg_patients` | `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month, `mart_data_quality_issues` |
| `programs` | `raw_archive/mongo/programs/...` → `raw.mongo_programs` | `stg_programs` | `mart_enrollment_funnel`, `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month |
| `enrollments` | `raw_archive/mongo/enrollments/...` → `raw.mongo_enrollments` | `stg_enrollments` | `mart_enrollment_funnel`, `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month, `mart_data_quality_issues` |
| `consents` | `raw_archive/mongo/consents/...` → `raw.mongo_consents` | `stg_consents` | `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month, `mart_data_quality_issues` |
| `timer_sessions` | `raw_archive/mongo/timer_sessions/...` → `raw.mongo_timer_sessions` | `stg_timer_sessions` | `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month |
| `device_orders` | `raw_archive/mongo/device_orders/...` → `raw.mongo_device_orders` | `stg_device_orders` | `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month, `mart_data_quality_issues` |
| `coordinator_notes` | `raw_archive/mongo/coordinator_notes/...` → `raw.mongo_coordinator_notes` | `stg_coordinator_notes` | — |

## CSV mappings

| Source file | Raw target | dbt staging model | Final mart consumers |
| --- | --- | --- | --- |
| `data/input/vob_files.csv` | `raw.csv_vob_files` | `stg_vob_files` | — |
| `data/input/billing_exports.csv` | `raw.csv_billing_exports` | `stg_billing_exports` | `mart_patient_month`, `mart_billable_activity` through patient-month, `mart_clinic_or_customer_performance` through patient-month |
| `data/input/customer_roster_upload.csv` | `raw.csv_customer_roster_uploads` | `stg_customer_roster_uploads` | — |

## Mart lineage

| Final mart | Direct dbt inputs | Resulting grain |
| --- | --- | --- |
| `mart_enrollment_funnel` | `stg_enrollments`, `stg_customers`, `stg_providers`, `stg_programs` | Customer, provider, program, and enrollment status |
| `mart_patient_month` | `stg_enrollments`, `stg_consents`, `stg_timer_sessions`, `stg_device_orders`, `stg_billing_exports`, `stg_patients`, `stg_customers`, `stg_providers`, `stg_programs` | Patient, program, and observed calendar month |
| `mart_billable_activity` | `mart_patient_month` | Billing-ready patient, program, and month |
| `mart_clinic_or_customer_performance` | `mart_patient_month` | Customer, program, and month |
| `mart_data_quality_issues` | `stg_patients`, `stg_providers`, `stg_customers`, `stg_enrollments`, `stg_consents`, `stg_device_orders` | Detected issue and affected record |

## Operational metadata

The Python loaders write execution metadata independently of the analytical
lineage:

| Audit table | Purpose |
| --- | --- |
| `audit.load_runs` | One row per extraction or loading execution, including status and record counts |
| `audit.file_load_history` | File path, checksum, size, row count, status, and load timestamps |
| `audit.load_errors` | Record-level or file-level errors associated with a load run |

Audit tables are operational controls. They are not currently dbt sources or
mart inputs.
