# provider-ops-dwh-lab

A small, local learning project for practicing a healthcare operations data
warehouse workflow:

```text
synthetic MongoDB data + synthetic CSV files
  -> Python extraction/loading jobs
  -> local raw archive
  -> PostgreSQL raw/staging tables
  -> dbt Core transformations
  -> analytics marts
  -> Metabase dashboards and SQL reports
```

This repository is a skeleton only. Extraction jobs, schemas, dbt models,
synthetic datasets, and dashboards will be added in later stages.

## Data safety

Use synthetic, invented data only. Never put real protected health information
(PHI), production exports, company data, secrets, or patient identifiers in this
repository.

## Prerequisites

- Docker Desktop with Docker Compose
- Git
- Optional: GNU Make. Direct Docker commands are provided below for Windows
  systems where `make` is unavailable.

Python, dbt Core, and database drivers run in the `tools` container, so they do
not need to be installed on the host.

## Quick start

From PowerShell:

```powershell
Set-Location D:\Personal\provider-ops-dwh-lab
Copy-Item .env.example .env
docker compose up -d postgres mongo metabase
docker compose ps
```

Open Metabase at [http://localhost:3000](http://localhost:3000). Its first-start
wizard may take a minute to appear.

When Metabase asks for a PostgreSQL connection, use:

| Setting | Value |
| --- | --- |
| Host | `postgres` |
| Port | `5432` |
| Database | `provider_ops_dwh` |
| Username | `warehouse` |
| Password | `warehouse` |

Use the values from `.env` if you change the defaults. Containers address each
other by service name, so Metabase must use `postgres`, not `localhost`.

Build the Python/dbt tools image and verify the dbt connection:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools dbt debug --project-dir dbt --profiles-dir dbt
```

Stop the stack:

```powershell
docker compose down
```

To also delete all local database and Metabase volumes:

```powershell
docker compose down --volumes
```

The volume-removal command permanently deletes the local lab state.

## Make commands

If GNU Make is installed:

```text
make setup
make up
make ps
make build-tools
make dbt-debug
make logs
make down
```

Run `make help` for the complete list.

## Repository layout

```text
provider-ops-dwh-lab/
|-- data/             Synthetic source CSV files
|-- raw_archive/      Local immutable-style extraction snapshots
|-- scripts/          Future Python extraction and loading jobs
|-- dbt/              dbt project, profiles, and future models
|-- docs/             Architecture notes and learning documentation
|-- sql/              Ad hoc validation and reporting SQL
|-- docker-compose.yml
|-- Dockerfile
|-- Makefile
`-- requirements.txt
```

Generated data under `data/csv/` and `raw_archive/` is ignored by Git. Keep only
small, explicitly synthetic fixtures in version control when they are added.

## Current scope

The stack currently supplies:

- PostgreSQL for warehouse raw, staging, and mart schemas
- MongoDB as an operational source
- Metabase for future dashboards and SQL exploration
- A Python/dbt tools image with the intended client dependencies
- A minimal dbt project whose connection can be tested

No source collections, warehouse tables, transformations, or dashboards are
created yet.
