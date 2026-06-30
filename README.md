# Provider Operations Data Warehouse Lab

## What this project is

This is a small, runnable healthcare operations data warehouse built as a
personal learning and portfolio lab. It combines invented MongoDB records and
synthetic CSV feeds, preserves source extracts, loads PostgreSQL, transforms
the data with dbt Core, and exposes management-oriented marts for SQL and
Metabase reporting.

The project is deliberately local and inspectable. It gives managers and
technical leaders a concrete pipeline to discuss without implying that a
production platform or real healthcare data has been implemented.

## Why it exists

The lab is preparation for contributing to and eventually leading a real data
warehouse initiative. It turns warehouse concepts—source ownership, raw
retention, dimensional grain, data quality, metric definitions, orchestration,
and reporting—into something that can be run and reviewed end to end.

It is also a conversation aid: the working demo makes it easier to separate
what has been learned locally from the business, security, scale, and
operational decisions that still need owners before a real implementation.

## Architecture

```text
Synthetic MongoDB collections          Synthetic CSV files
               |                               |
               +--------- Python ETL ----------+
                              |
                 dated local raw_archive
                              |
                    PostgreSQL raw schema
                              |
                      dbt staging views
                              |
                 dbt analytics mart tables
                              |
                    Metabase / SQL reports

               ETL run and file metadata
                              |
                    PostgreSQL audit schema
```

The layers are intentionally separated. Python captures and loads source data;
the raw layer retains source-shaped records; dbt standardizes and tests them;
and the marts provide stable reporting grains. The audit schema records load
runs and processed files.

## Current status

The local services, dependency image, synthetic MongoDB seed records, synthetic
CSV source files, PostgreSQL schema initialization, Python ETL, dbt staging
models, analytics marts, data tests, reporting queries, and manual Metabase
dashboard guidance are present. Metabase dashboards are not preconfigured.

## Technology

- MongoDB for the simulated operational source
- CSV files for batch and reference sources
- Python, pandas, PyMongo, and Psycopg for extraction and loading jobs
- PostgreSQL for local raw, staging, marts, and audit schemas
- dbt Core with `dbt-postgres` for transformations and tests
- Metabase for manual dashboards and SQL exploration
- Docker Compose for the local environment

## Data safety

**Synthetic data only. No PHI.** Never add real patient/provider identifiers,
production exports, company data, secrets, or credentials. This is not a
production healthcare system and makes no compliance or production-readiness
claim.

## Production mapping

The local design maps to the proposed real data warehouse architecture as
follows:

| Local lab component | Proposed production mapping |
| --- | --- |
| Local PostgreSQL | Amazon RDS PostgreSQL |
| Local `raw_archive/` | Amazon S3 controlled archive |
| Python scripts | Scheduled jobs or AWS Lambda |
| dbt Core | dbt Core |
| Metabase | Metabase or Amazon QuickSight |

This is a conceptual mapping, not a production design claim. The local pipeline
helps test responsibilities and data flow, but it does not validate AWS
networking, sizing, security, service levels, or operating cost.

## Important limitations

- Synthetic data only
- Not production-ready
- No real PHI
- No AWS networking
- No change data capture (CDC)
- No real Provider Dashboard integration

The demo also does not establish production billing rules, compliance,
multi-tenant access controls, disaster recovery, or platform sizing.

## Local services

### Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose v2
- Git
- Host ports `27017`, `5432`, and `3000` available, or different ports set in
  `.env`
- GNU Make for the one-command demo

### Run the full demo

From the repository root, run:

```powershell
make demo
```

The command:

1. Creates `.env` from `.env.example` when it is missing.
2. Starts MongoDB, PostgreSQL, and Metabase.
3. Builds the reusable Python/dbt tools image.
4. Seeds deterministic synthetic MongoDB records.
5. Extracts MongoDB to `raw_archive/` and loads MongoDB and CSV data into the
   PostgreSQL `raw` schema.
6. Runs the dbt staging and mart models.
7. Runs the dbt data tests.
8. Prints the report query locations under `sql/reports/`.

The seed and load behavior is repeatable: demo records and raw business rows
are updated rather than duplicated, while audit history intentionally appends
on each run. On first use, Docker image downloads make the command slower.

After it completes:

- Open Metabase at [http://localhost:3000](http://localhost:3000) and follow the
  [dashboard setup guide](docs/metabase_dashboard_guide.md).
- Run any query in `sql/reports/` against PostgreSQL for a ready-made
  management view.
- Use `make ps` to inspect services and `make down` to stop them without
  deleting local data.

The detailed commands below are useful when demonstrating or troubleshooting
one layer at a time.

### Manual environment setup

Create the local environment file before starting the services:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux, use `cp .env.example .env`. The included values are for
local development only. Change them if needed, and never commit `.env`.

### Start the services

```powershell
docker compose up -d mongodb postgres metabase
docker compose ps
```

On the first run, Docker downloads the images and creates persistent volumes
for MongoDB, PostgreSQL, and Metabase. Wait until `docker compose ps` reports
the services as healthy before connecting.

### Stop the services

```powershell
docker compose down
```

This stops the containers without deleting their data. To intentionally reset
all local database and Metabase state, run `docker compose down --volumes`.

### Connect to MongoDB

Python scripts running on the host can connect with the values in `.env`:

```text
Host: localhost
Port: 27017
Database: provider_ops
Username: mongo
Password: mongo
Authentication database: admin
URI: mongodb://mongo:mongo@localhost:27017/provider_ops?authSource=admin
```

If a Python process runs inside the Compose network, use `mongodb` instead of
`localhost` as the host. The optional `tools` profile already exposes the
equivalent `MONGO_URI` to its container.

To open a MongoDB shell without installing one locally:

```powershell
docker compose exec mongodb mongosh --username mongo --password mongo --authenticationDatabase admin provider_ops
```

Use the credentials and database configured in `.env` if you changed the
defaults.

### Seed and reset demo source data

The seed script loads deterministic synthetic records into the `customers`,
`providers`, `patients`, `programs`, `enrollments`, `consents`,
`timer_sessions`, `device_orders`, and `coordinator_notes` collections.

With the MongoDB service running, use the tools container:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools python scripts/seed_mongo.py
```

The script replaces only records tagged with its demo batch, so it is safe to
rerun. To remove that batch without deleting other MongoDB records:

```powershell
docker compose --profile tools run --rm tools python scripts/reset_demo_data.py --yes
```

If the Python dependencies are installed on the host, the equivalent commands
are:

```powershell
python scripts/seed_mongo.py
python scripts/reset_demo_data.py --yes
```

The committed synthetic CSV inputs are in `data/input/`. Resetting MongoDB does
not remove or modify those files.

### Connect to PostgreSQL

Clients running on the host can use:

```text
Host: localhost
Port: 5432
Database: provider_ops_dwh
Username: warehouse
Password: warehouse
URI: postgresql://warehouse:warehouse@localhost:5432/provider_ops_dwh
```

To open `psql` inside the PostgreSQL container:

```powershell
docker compose exec postgres psql -U warehouse -d provider_ops_dwh
```

Again, use the values from `.env` if you changed the defaults.

### Initialize and inspect PostgreSQL schemas

PostgreSQL runs the files in `sql/init/` in numeric order when it creates a new
data volume. They create the `raw`, `staging`, `marts`, and `audit` schemas,
along with the raw source and audit tables.

PostgreSQL initialization files do not rerun automatically for an existing
data volume. To apply them without deleting local data, recreate the container
to mount the scripts and run each file explicitly:

```powershell
docker compose up -d --force-recreate postgres
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/001_create_schemas.sql
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/002_create_raw_tables.sql
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/003_create_audit_tables.sql
```

Use the PostgreSQL credentials and database configured in `.env` if you changed
the defaults. The scripts use `IF NOT EXISTS`, so reapplying them preserves
existing tables and data.

Inspect the schemas and tables with:

```powershell
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dn"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dt raw.*"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dt audit.*"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\d raw.csv_billing_exports"
```

### Run the local ETL

With the services running, seed MongoDB and run the complete extraction and
loading flow:

```powershell
make seed
make etl
```

Without GNU Make, use the equivalent Docker commands:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools python scripts/seed_mongo.py
docker compose --profile tools run --rm tools python scripts/run_etl.py
```

The ETL writes one JSONL file per MongoDB collection under:

```text
raw_archive/mongo/{collection}/date=YYYY-MM-DD/data.jsonl
```

It then loads the JSONL records and the three files in `data/input/` into the
matching `raw` tables. MongoDB rows are updated or inserted by `source_id`; CSV
rows are updated or inserted by their source record IDs. Repeating the ETL
therefore refreshes existing raw rows instead of duplicating them. Audit run
and file history rows are intentionally appended for every execution.

Inspect recent ETL activity with:

```powershell
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT load_run_id, pipeline_name, status, records_loaded, started_at FROM audit.load_runs ORDER BY load_run_id DESC LIMIT 10;"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT file_path, status, row_count, loaded_at FROM audit.file_load_history ORDER BY file_load_history_id DESC LIMIT 20;"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT count(*) FROM raw.mongo_patients;"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT count(*) FROM raw.csv_billing_exports;"
```

`make reset` stops the stack and deletes the MongoDB, PostgreSQL, and Metabase
volumes. It does not delete ignored archive files under `raw_archive/`.

### Open Metabase

Open [http://localhost:3000](http://localhost:3000), or use the port configured
by `METABASE_PORT`. Complete Metabase's setup wizard in the browser.

When adding PostgreSQL as a Metabase data source later, use host `postgres`
(not `localhost`), port `5432`, database `provider_ops_dwh`, and the PostgreSQL
username and password from `.env`.

### Run dbt

Run the ETL first so the raw tables contain source records. Then install dbt
dependencies, build the staging views, and run the data tests:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools dbt deps --project-dir dbt/provider_ops_dwh --profiles-dir dbt/provider_ops_dwh
docker compose --profile tools run --rm tools dbt run --project-dir dbt/provider_ops_dwh --profiles-dir dbt/provider_ops_dwh
docker compose --profile tools run --rm tools dbt test --project-dir dbt/provider_ops_dwh --profiles-dir dbt/provider_ops_dwh
```

No external dbt packages are currently declared, so `dbt deps` is a no-op and
reports that no packages were found.

With GNU Make, the equivalent commands are:

```powershell
make dbt-deps
make dbt-run
make dbt-test
```

The dbt profile reads the PostgreSQL host, port, user, password, and database
from environment variables. Staging views are created in the `staging` schema,
and analytics marts are materialized as tables in the `marts` schema. The
staging layer flattens the raw MongoDB JSON documents, normalizes operational
values, and excludes patient names, birth dates, phone numbers, member
references, shipment tracking references, and coordinator free text.

Inspect the resulting views with:

```powershell
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dv staging.*"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT * FROM staging.stg_enrollments LIMIT 10;"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dt marts.*"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT * FROM marts.mart_billable_activity ORDER BY patient_month, customer_name, patient_id;"
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "SELECT * FROM marts.mart_data_quality_issues ORDER BY issue_type, record_id;"
```

## What the final marts represent

The final marts are reporting contracts with explicit grains, not copies of
source tables:

- `mart_enrollment_funnel`: enrollment and patient counts by customer,
  provider, program, and current enrollment status; useful for showing where
  patients sit in the operational funnel
- `mart_patient_month`: one row per observed patient, program, and month; the
  shared operational fact table behind readiness reporting
- `mart_billable_activity`: patient-months that satisfy the local billing
  readiness rules; useful for reviewing computed readiness against the
  synthetic source candidate flag
- `mart_clinic_or_customer_performance`: monthly customer/program operational
  totals for patients, consent, timer activity, delayed devices, and billing
  readiness
- `mart_data_quality_issues`: missing mappings, missing consent, invalid
  statuses, and duplicate patient external IDs presented as an actionable
  review queue

Billing readiness is a learning-project rule, not a claim submission rule. A
patient-month is ready when its enrollment is active, consent is completed,
the program's minimum timer minutes are met, and any required device is
delivered by month-end. The source billing candidate flag remains separate so
the computed result can be compared with the synthetic billing export.

## Repository layout

```text
data/input/    Committed synthetic CSV source files
data/csv/      Future generated CSV files
raw_archive/   Local immutable-style extraction snapshots
scripts/       Python extraction and loading jobs
dbt/provider_ops_dwh/  dbt models, tests, and configuration
sql/init/      PostgreSQL schema and table initialization
sql/reports/   Reporting SQL for marts and Metabase
docs/          Architecture, scope, decisions, and working guidance
```

Committed fixtures in `data/input/` are intentionally versioned. Generated
files in `data/csv/` and `raw_archive/` are ignored by Git.

## What I learned from building it

- A useful warehouse starts with agreed source ownership and business grain,
  not with a dashboard.
- Preserving a source-shaped raw layer and load audit trail makes failures,
  reruns, and reconciliation easier to explain.
- Staging models are the right boundary for type casting, naming, status
  normalization, and removing fields that reporting does not need.
- Shared marts prevent dashboard queries from inventing competing definitions
  of enrollment, consent, activity, and billing readiness.
- Data quality is more useful when modeled as a visible operational output,
  rather than hidden inside pipeline logs.
- A small end-to-end implementation exposes important production questions
  earlier than an architecture diagram alone.

## What should be confirmed before real implementation

Before selecting services or onboarding any real data, confirm:

- authoritative source systems, data owners, stable identifiers, source
  history, deletion behavior, and file-feed contracts
- required freshness, cutoff times, late-arriving data handling, recovery
  objectives, and whether CDC is actually necessary
- approved KPI definitions, especially enrollment conversion, timer
  utilization, device fulfillment, and billability
- PHI classification, minimum necessary fields, retention, deletion, masking,
  encryption, audit, and non-production data rules
- user roles, tenant isolation, SSO, service accounts, secrets management,
  access approval, and export controls
- RDS workload sizing, availability, backup, VPC, subnet, security-group, and
  private-connectivity requirements
- whether Metabase or QuickSight best fits governance, embedded analytics,
  row-level access, licensing, and support ownership
- how the warehouse or reporting layer would integrate with the real Provider
  Dashboard, including API, identity, ownership, and support boundaries

The detailed discovery checklist is in
[Open questions for the CTO](docs/open_questions_for_cto.md). Durable decisions
should be recorded in [the decision log](docs/DECISION_LOG.md).

## Supporting documentation

- [Project one-pager](docs/PROJECT_ONE_PAGER.md)
- [Architecture notes](docs/architecture.md)
- [KPI definitions](docs/kpi_definitions.md)
- [Source-to-target mapping](docs/source_to_target_mapping.md)
- [Data dictionary](docs/data_dictionary.md)
- [Open questions for the CTO](docs/open_questions_for_cto.md)
- [Metabase dashboard guide](docs/metabase_dashboard_guide.md)
- [Scope guardrails](docs/SCOPE_GUARDRAILS.md)
- [AI development workflow](docs/AI_DEVELOPMENT_WORKFLOW.md)
- [Branching and commit guidance](docs/BRANCHING_AND_COMMITS.md)
- [Task brief template](docs/TASK_BRIEF_TEMPLATE.md)
- [Decision log](docs/DECISION_LOG.md)
- [Troubleshooting handoff](docs/TROUBLESHOOTING_HANDOFF.md)
- [AI agent guide](AGENTS.md)
