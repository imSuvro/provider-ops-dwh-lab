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

The repository is an early scaffold. The local services, dependency image, and
minimal dbt project are present. Synthetic datasets, extraction/loading jobs,
warehouse models, tests, reporting queries, and dashboards are planned but not
yet implemented.

## Technology

- MongoDB for the simulated operational source
- CSV files for batch and reference sources
- Python, pandas, PyMongo, and Psycopg for future data jobs
- PostgreSQL for local raw, staging, and marts schemas
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

## Quick start

Prerequisites: Docker Desktop with Docker Compose and Git. GNU Make is optional.

```powershell
Copy-Item .env.example .env
docker compose up -d postgres mongo metabase
docker compose ps
```

Open Metabase at [http://localhost:3000](http://localhost:3000). For its
PostgreSQL connection, use host `postgres`, port `5432`, database
`provider_ops_dwh`, username `warehouse`, and password `warehouse` unless
changed in `.env`.

Build the Python/dbt tools image and check the dbt connection:

```powershell
docker compose --profile tools build tools
docker compose --profile tools run --rm tools dbt debug --project-dir dbt --profiles-dir dbt
```

Stop the stack with `docker compose down`. Adding `--volumes` permanently
deletes local lab state.

## Repository layout

```text
data/          Synthetic CSV source files
raw_archive/   Local immutable-style extraction snapshots
scripts/       Python extraction and loading jobs
dbt/           dbt models, tests, and configuration
sql/           Validation and reporting SQL
docs/          Architecture, scope, decisions, and working guidance
```

Generated files in `data/csv/` and `raw_archive/` are ignored by Git.

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
