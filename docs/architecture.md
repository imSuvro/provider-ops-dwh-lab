# Architecture

## What this project does

This project is a small local data warehouse built for learning. It starts with
invented operational data, keeps a copy of each extraction, loads PostgreSQL,
and builds reporting tables with dbt. Metabase can then query those tables.

It does not use real patient data or company data, and it is not a production
healthcare system.

## Pipeline at a glance

```text
Synthetic MongoDB collections        Synthetic CSV files
              |                              |
              +---------- Python ETL --------+
                             |
                  dated local raw_archive
                             |
                    PostgreSQL raw schema
                             |
                         dbt staging
                             |
                      dbt analytics marts
                             |
                  Metabase or direct SQL

              ETL runs and files -> audit schema
```

## Step-by-step flow

### 1. Synthetic sources

MongoDB represents an operational application. Its collections cover
customers, providers, patients, programs, enrollments, consents, timer
sessions, device orders, and coordinator note metadata.

Three committed CSV files represent file-based feeds:

- verification-of-benefits rows
- monthly billing exports
- customer roster uploads

Every record is invented for this lab.

### 2. Extraction archive

The MongoDB extraction script writes one JSONL file per collection:

```text
raw_archive/mongo/{collection}/date=YYYY-MM-DD/data.jsonl
```

This creates a dated source snapshot before transformation. In a production
design, controlled object storage could play a similar role, but this project
uses the local filesystem only.

### 3. Raw PostgreSQL layer

Python loaders copy MongoDB snapshots and CSV rows into the `raw` schema.

- MongoDB raw tables keep the original document in a JSONB column.
- CSV raw tables use practical typed columns.
- Source identifiers support local update-or-insert behavior on reruns.
- File names, row numbers, checksums, and load timestamps provide lineage.

The raw layer stays close to source shape. It is not intended for end-user
reporting.

### 4. Audit layer

The `audit` schema records how ingestion ran:

- `audit.load_runs` tracks each extraction or load execution.
- `audit.file_load_history` tracks each processed archive or CSV file.
- `audit.load_errors` stores captured load failures.

These tables answer operational questions such as what ran, when it ran, which
file was processed, and how many records loaded.

### 5. dbt staging layer

dbt creates views in the `staging` schema. Staging models:

- flatten MongoDB JSONB documents
- rename fields consistently
- cast dates, timestamps, booleans, numbers, and identifiers
- normalize operational statuses
- test keys and relationships
- exclude unnecessary sensitive-shaped fields

Each staging view remains close to one source collection or file. It is the
clean input to the analytics layer.

### 6. dbt analytics marts

dbt creates tables in the `marts` schema:

| Mart | Purpose |
| --- | --- |
| `mart_enrollment_funnel` | Enrollment and patient counts by customer, provider, program, and status |
| `mart_patient_month` | Monthly operational state for each patient and program |
| `mart_billable_activity` | Patient-months that meet the local readiness rule |
| `mart_clinic_or_customer_performance` | Monthly customer and program summary |
| `mart_data_quality_issues` | Reviewable mapping, status, consent, and duplication issues |

The central model is `mart_patient_month`. It combines enrollment, consent,
device, activity, billing, patient, customer, provider, and program data at one
patient-program-month grain. The billable and customer-performance marts build
from it so they use the same readiness logic.

### 7. Reporting

Metabase can connect to PostgreSQL over the Docker network and query the mart
tables. The reporting SQL in `sql/reports/` supports six manual dashboard
sections, and direct SQL can be used for validation and exploration.

The project documents how to create the dashboard manually but does not
preconfigure Metabase. Production reporting governance remains future work.

## Rerun behavior

The local workflow is designed to be repeatable:

- Seeding replaces only records tagged as the demo batch.
- MongoDB raw loads update or insert by `source_id`.
- CSV raw loads update or insert by their source record identifiers.
- Archive partitions are dated.
- Audit rows append for each execution.
- dbt rebuilds views and table marts from the current raw data.

This is practical idempotency for a learning project, not a production
change-data-capture design.

## Data safety boundaries

- Use only synthetic, invented data.
- Do not add real PHI, production exports, credentials, or confidential data.
- Raw source shapes may contain sensitive-looking fields for teaching purposes;
  staging and marts omit fields that are unnecessary for analytics.
- `.env`, generated archives, and local database volumes stay outside Git.
- Production access, retention, encryption, masking, and audit requirements
  must be decided before any real data is considered.

## Local-to-production learning map

| Local component | Possible future equivalent | Important note |
| --- | --- | --- |
| MongoDB and CSV demo sources | Operational databases, APIs, or managed file feeds | Real sources and owners are not yet known |
| `raw_archive/` | Controlled object storage such as Amazon S3 | Retention and encryption would need governance |
| Python scripts | Scheduled jobs, containers, or managed orchestration | Scheduler and service-level targets are undecided |
| PostgreSQL | Amazon RDS for PostgreSQL or another analytical store | Workload testing must drive the choice |
| dbt Core | Managed or self-hosted dbt execution | Deployment and credentials are out of scope |
| Metabase | Metabase or Amazon QuickSight | Reporting platform is an open decision |

These are learning comparisons, not a deployment plan.

## What is intentionally not included

- real PHI or company data
- AWS deployment
- production authentication or authorization
- real-time streaming
- production change data capture
- Kafka, Redshift, or Aurora
- a frontend application
- production billing logic or compliance claims

See the [scope guardrails](SCOPE_GUARDRAILS.md), [source-to-target
mapping](source_to_target_mapping.md), [data dictionary](data_dictionary.md),
and [open CTO questions](open_questions_for_cto.md) for more detail.
