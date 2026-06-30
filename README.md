# Provider Operations Data Warehouse Lab

A small, local healthcare operations data warehouse built as a personal
learning and portfolio project. It shows how operational and file-based data
can move through a practical analytics pipeline while remaining approachable
for managers, technical leaders, recruiters, and engineers new to data
warehousing.

## Why it exists

The lab is preparation for contributing to and eventually leading a real data
warehouse initiative. It focuses on architecture, data flow, testing,
documentation, and reporting tradeoffs rather than enterprise-scale claims.

## Architecture

```text
Synthetic MongoDB operational data + synthetic CSV files
  -> Python extraction/loading jobs
  -> local raw archive
  -> PostgreSQL raw and staging tables
  -> dbt Core transformations
  -> PostgreSQL analytics marts
  -> Metabase dashboards and SQL reports
```

## Current status

The local services, dependency image, minimal dbt project, synthetic MongoDB
seed records, synthetic CSV source files, and PostgreSQL schema initialization
scripts are present. Extraction/loading jobs, warehouse models, tests,
reporting queries, and dashboards are planned but not yet implemented.

## Technology

- MongoDB for the simulated operational source
- CSV files for batch and reference sources
- Python, pandas, PyMongo, and Psycopg for future data jobs
- PostgreSQL for local raw, staging, marts, and audit schemas
- dbt Core with `dbt-postgres` for future transformations and tests
- Metabase for future dashboards and SQL exploration
- Docker Compose for the local environment

## Data safety

**Synthetic data only. No PHI.** Never add real patient/provider identifiers,
production exports, company data, secrets, or credentials. This is not a
production healthcare system and makes no compliance or production-readiness
claim.

## Production mapping

| Local lab component | Possible future production equivalent |
| --- | --- |
| Local PostgreSQL | Amazon RDS PostgreSQL |
| `raw_archive/` | Controlled Amazon S3 file archive |
| Python scripts | Scheduled jobs, backend cron jobs, or AWS Lambda |
| dbt Core | Transformation layer |
| Metabase | Metabase or Amazon QuickSight |

These mappings explain the learning intent; AWS deployment is outside the MVP.

## Local services

### Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose v2
- Git
- Host ports `27017`, `5432`, and `3000` available, or different ports set in
  `.env`
- GNU Make is optional

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

### Open Metabase

Open [http://localhost:3000](http://localhost:3000), or use the port configured
by `METABASE_PORT`. Complete Metabase's setup wizard in the browser.

When adding PostgreSQL as a Metabase data source later, use host `postgres`
(not `localhost`), port `5432`, database `provider_ops_dwh`, and the PostgreSQL
username and password from `.env`.

### Optional Python/dbt tools

Build the existing tools image and check the dbt connection:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools dbt debug --project-dir dbt --profiles-dir dbt
```

No extraction or loading jobs are implemented yet.

## Repository layout

```text
data/input/    Committed synthetic CSV source files
data/csv/      Future generated CSV files
raw_archive/   Local immutable-style extraction snapshots
scripts/       Python extraction and loading jobs
dbt/           dbt models, tests, and configuration
sql/init/      PostgreSQL schema and table initialization
sql/           Future validation and reporting SQL
docs/          Architecture, scope, decisions, and working guidance
```

Committed fixtures in `data/input/` are intentionally versioned. Generated
files in `data/csv/` and `raw_archive/` are ignored by Git.

## Supporting documentation

- [Project one-pager](docs/PROJECT_ONE_PAGER.md)
- [Architecture notes](docs/architecture.md)
- [Scope guardrails](docs/SCOPE_GUARDRAILS.md)
- [AI development workflow](docs/AI_DEVELOPMENT_WORKFLOW.md)
- [Branching and commit guidance](docs/BRANCHING_AND_COMMITS.md)
- [Task brief template](docs/TASK_BRIEF_TEMPLATE.md)
- [Decision log](docs/DECISION_LOG.md)
- [Troubleshooting handoff](docs/TROUBLESHOOTING_HANDOFF.md)
- [AI agent guide](AGENTS.md)
