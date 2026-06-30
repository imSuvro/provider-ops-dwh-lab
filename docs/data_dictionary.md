# Data Dictionary

This dictionary describes the most important PostgreSQL and dbt objects in the
local warehouse. All records are synthetic. The staging and mart layers
intentionally omit unnecessary sensitive-shaped source fields.

## Schemas

| Schema | Purpose |
| --- | --- |
| `raw` | Source-shaped MongoDB documents and typed CSV rows loaded by Python |
| `staging` | dbt views with normalized names, types, statuses, and timestamps |
| `marts` | dbt tables at reporting-friendly business grains |
| `audit` | ETL run, file, and error history |

## Raw MongoDB tables

The nine MongoDB raw tables share the same structure:

- `raw.mongo_customers`
- `raw.mongo_providers`
- `raw.mongo_patients`
- `raw.mongo_programs`
- `raw.mongo_enrollments`
- `raw.mongo_consents`
- `raw.mongo_timer_sessions`
- `raw.mongo_device_orders`
- `raw.mongo_coordinator_notes`

| Column | Type | Meaning |
| --- | --- | --- |
| `raw_record_id` | bigint | Warehouse-generated row identifier |
| `source_id` | text | MongoDB document identifier; used for local upserts |
| `raw_doc` | jsonb | Source document serialized as JSON |
| `source_collection` | text | MongoDB collection name |
| `extracted_at` | timestamptz | Time the extraction snapshot was created |
| `source_updated_at` | timestamptz, nullable | Update time supplied by the source when available |

The local loader keeps one current raw row per `source_id` through upserts.
The dated JSONL archive and audit history preserve execution evidence.

## Raw CSV tables

### `raw.csv_vob_files`

Typed verification-of-benefits rows.

| Important column | Meaning |
| --- | --- |
| `vob_id` | Synthetic VOB record identifier |
| `patient_id`, `customer_id` | Source relationship identifiers |
| `payer_name` | Synthetic payer display name |
| `member_reference` | Sensitive-shaped source member reference; excluded from staging |
| `coverage_status` | Source coverage state |
| `verified_on` | Verification date |
| `program` | Source program code |
| `estimated_copay` | Synthetic estimated patient amount |
| `source_file_name`, `source_row_number` | File lineage |
| `loaded_at` | Raw load timestamp |

### `raw.csv_billing_exports`

Typed monthly billing-candidate rows.

| Important column | Meaning |
| --- | --- |
| `export_id` | Synthetic billing export row identifier |
| `patient_id`, `customer_id` | Source relationship identifiers |
| `patient_month` | First day of the represented calendar month |
| `program` | Source program code |
| `billable_candidate` | Candidate flag supplied by the source export |
| `amount`, `currency` | Synthetic source billing amount and currency |
| `exported_at` | Source export timestamp |
| `source_file_name`, `source_row_number` | File lineage |
| `loaded_at` | Raw load timestamp |

### `raw.csv_customer_roster_uploads`

Typed customer roster rows.

| Important column | Meaning |
| --- | --- |
| `roster_record_id` | Synthetic roster row identifier |
| `customer_id`, `patient_id`, `provider_id` | Source relationship identifiers |
| `first_name`, `last_name`, `date_of_birth`, `phone` | Sensitive-shaped raw fields; excluded from staging |
| `state` | Two-character state code |
| `program_interest` | Source program code |
| `uploaded_at` | Source upload timestamp |
| `source_file_name`, `source_row_number` | File lineage |
| `loaded_at` | Raw load timestamp |

## Staging models

Staging models are views in the `staging` schema. Common metadata columns
include `extracted_at` and `source_updated_at` for MongoDB sources, or
`source_file_name`, `source_row_number`, and `loaded_at` for CSV sources.

### Reference and identity models

| Model and grain | Important columns | Meaning |
| --- | --- | --- |
| `stg_customers` — one customer | `customer_id`, `customer_code`, `customer_name`, `region`, `timezone`, `is_active`, `contract_start_date` | Customer identity and operating attributes |
| `stg_providers` — one provider | `provider_id`, `provider_external_id`, `customer_id`, `provider_name`, `specialty`, `is_active` | Provider identity and customer ownership |
| `stg_patients` — one patient | `patient_id`, `patient_external_id`, `customer_id`, `primary_provider_id`, `state`, `is_active`, `created_at` | Operational patient identifiers without names, birth date, or phone |
| `stg_programs` — one program | `program_id`, `program_code`, `program_name`, `requires_device`, `monthly_minimum_minutes`, `is_active` | Program reference and local readiness settings |

Supported `program_code` values are `RPM`, `RTM`, `CCM`, `CoCM`, and `APCM`.

### Operational event models

| Model and grain | Important columns | Meaning |
| --- | --- | --- |
| `stg_enrollments` — one enrollment | `enrollment_id`, `patient_id`, `customer_id`, `provider_id`, `program_id`, `program_code`, `enrollment_status`, `received_at`, `status_updated_at` | Current enrollment lifecycle record |
| `stg_consents` — one consent | `consent_id`, `enrollment_id`, `patient_id`, `program_code`, `consent_status`, `consent_method`, `requested_at`, `completed_at` | Consent state and timestamps |
| `stg_timer_sessions` — one timer session | `timer_session_id`, `enrollment_id`, `patient_id`, `provider_id`, `program_code`, `duration_minutes`, `session_date`, `activity_type` | Recorded program activity time |
| `stg_device_orders` — one device order | `device_order_id`, `enrollment_id`, `patient_id`, `customer_id`, `program_code`, `device_type`, `order_status`, `ordered_at`, `status_updated_at` | Device fulfillment state without tracking references |
| `stg_coordinator_notes` — one note metadata record | `coordinator_note_id`, `enrollment_id`, `patient_id`, `customer_id`, `note_type`, `created_at` | Note classification and relationships without free text |

Status domains:

| Field | Supported values |
| --- | --- |
| `enrollment_status` | `RECEIVED`, `ELIGIBLE`, `CONSENTED`, `ONBOARDED`, `ACTIVE`, `DECLINED` |
| `consent_status` | `PENDING`, `COMPLETED`, `DECLINED` |
| `order_status` | `ORDERED`, `SHIPPED`, `DELIVERED`, `DELAYED` |

### File-based staging models

| Model and grain | Important columns | Meaning |
| --- | --- | --- |
| `stg_vob_files` — one VOB row | `vob_id`, `patient_id`, `customer_id`, `payer_name`, `coverage_status`, `verified_on`, `program_code`, `estimated_copay` | Normalized coverage verification data without member reference |
| `stg_billing_exports` — one export row | `export_id`, `patient_id`, `customer_id`, `patient_month`, `program_code`, `billable_candidate`, `amount`, `currency`, `exported_at` | Source-provided monthly billing candidates |
| `stg_customer_roster_uploads` — one roster row | `roster_record_id`, `customer_id`, `patient_id`, `provider_id`, `state`, `program_code`, `uploaded_at` | Normalized roster relationships without names, birth date, or phone |

## Analytics marts

Marts are tables in the `marts` schema.

### `marts.mart_enrollment_funnel`

**Grain:** One row per customer, provider, program, and enrollment status.

| Column | Meaning |
| --- | --- |
| `enrollment_funnel_key` | Deterministic key for the mart grain |
| `customer_id`, `customer_name` | Customer dimension |
| `provider_id`, `provider_name` | Provider dimension |
| `program_id`, `program_code`, `program_name` | Program dimension |
| `enrollment_status` | Current normalized enrollment status |
| `enrollment_count` | Enrollment records in the group |
| `patient_count` | Distinct patients in the group |
| `first_received_at` | Earliest enrollment receipt timestamp in the group |
| `latest_status_updated_at` | Latest status timestamp in the group |

### `marts.mart_patient_month`

**Grain:** One row per patient, program, and observed calendar month.

An observed month comes from an enrollment, consent request, timer session,
device order, or billing export.

| Column group | Important columns | Meaning |
| --- | --- | --- |
| Key and period | `patient_month_key`, `patient_month` | Deterministic grain key and first day of month |
| Dimensions | `patient_id`, `customer_id`, `customer_name`, `provider_id`, `provider_name`, `program_id`, `program_code`, `program_name` | Reporting relationships |
| Enrollment | `enrollment_id`, `enrollment_status`, `enrollment_received_at` | Latest available enrollment record |
| Consent | `consent_id`, `consent_status`, `consent_completed_at` | Latest available consent record |
| Device | `device_order_id`, `device_type`, `device_status`, `requires_device` | Latest available device state and program rule |
| Activity | `monthly_minimum_minutes`, `timer_session_count`, `timer_minutes` | Program threshold and monthly recorded activity |
| Billing source | `billing_export_count`, `source_billable_candidate`, `billing_amount`, `currency` | Values supplied by the synthetic billing export |
| Readiness | `is_active_enrollment`, `has_completed_consent`, `has_required_minutes`, `is_device_ready`, `is_billable_ready` | Computed month-end readiness flags |

`source_billable_candidate` and `is_billable_ready` are deliberately separate:
the former is a source assertion, while the latter is computed from local
rules.

### `marts.mart_billable_activity`

**Grain:** One row per billing-ready patient, program, and month.

| Column | Meaning |
| --- | --- |
| `billable_activity_key` | Same deterministic key as the qualifying patient-month |
| `patient_month`, `patient_id` | Reporting month and patient |
| Customer/provider/program columns | Reporting dimensions inherited from `mart_patient_month` |
| `timer_minutes`, `monthly_minimum_minutes` | Actual activity and local threshold |
| `device_status` | Latest available device status |
| `source_billable_candidate` | Source export comparison flag |
| `billing_amount`, `currency` | Synthetic source billing values |
| `is_billable_ready` | Always true for rows in this filtered mart |
| `billing_alignment_status` | Whether computed readiness agrees with a positive source candidate |

### `marts.mart_clinic_or_customer_performance`

**Grain:** One row per customer, program, and calendar month.

| Column | Meaning |
| --- | --- |
| `customer_performance_key` | Deterministic key for the mart grain |
| `patient_month` | First day of the reporting month |
| Customer and program columns | Reporting dimensions |
| `patient_count` | Distinct observed patients |
| `active_patient_count` | Distinct patients with active enrollment |
| `consented_patient_count` | Distinct patients with completed consent |
| `timer_minutes` | Sum of recorded timer minutes |
| `delayed_device_count` | Distinct patients with delayed device status |
| `billable_candidate_count` | Distinct positive source billing candidates |
| `billable_ready_patient_count` | Distinct patient-months meeting computed readiness |
| `billable_readiness_rate` | Computed ready patients divided by observed patients |

### `marts.mart_data_quality_issues`

**Grain:** One row per detected issue and affected source record.

| Column | Meaning |
| --- | --- |
| `data_quality_issue_key` | Deterministic issue key |
| `issue_type` | Standardized issue category |
| `record_type`, `record_id` | Affected record category and identifier |
| `customer_id`, `patient_id` | Available investigation context |
| `issue_details` | Human-readable issue explanation without raw sensitive fields |

Supported issue types:

- `MISSING_PROVIDER`
- `MISSING_CONSENT`
- `INVALID_ENROLLMENT_STATUS`
- `INVALID_CONSENT_STATUS`
- `INVALID_DEVICE_STATUS`
- `DUPLICATE_PATIENT_EXTERNAL_ID`
- `MISSING_CUSTOMER_MAPPING`

## Audit tables

### `audit.load_runs`

One row per extraction or loading execution.

| Important column | Meaning |
| --- | --- |
| `load_run_id` | Warehouse-generated run identifier |
| `pipeline_name`, `source_type`, `source_name` | Run classification |
| `status` | `RUNNING`, `SUCCEEDED`, `FAILED`, or `PARTIAL` |
| `started_at`, `completed_at` | Run timing |
| `records_read`, `records_loaded`, `records_rejected` | Run counts |
| `error_message` | Run-level failure summary |
| `metadata` | Additional structured execution context |

### `audit.file_load_history`

One row per file handled by a load run.

| Important column | Meaning |
| --- | --- |
| `file_load_history_id`, `load_run_id` | File event key and parent run |
| `file_name`, `file_path` | File identity |
| `file_checksum`, `file_size_bytes` | File integrity metadata |
| `row_count` | Rows processed |
| `status` | `DISCOVERED`, `LOADING`, `LOADED`, `FAILED`, or `SKIPPED` |
| `discovered_at`, `loaded_at` | File processing timing |

### `audit.load_errors`

One row per captured load error.

| Important column | Meaning |
| --- | --- |
| `load_error_id`, `load_run_id` | Error key and parent run |
| `source_record_id`, `source_file_name`, `source_row_number` | Available source location |
| `error_stage`, `error_code`, `error_message` | Failure classification and explanation |
| `raw_payload` | Optional source payload for local diagnosis |
| `occurred_at` | Error timestamp |

## Related references

- [KPI definitions](kpi_definitions.md)
- [Source-to-target mapping](source_to_target_mapping.md)
- [Architecture](architecture.md)
