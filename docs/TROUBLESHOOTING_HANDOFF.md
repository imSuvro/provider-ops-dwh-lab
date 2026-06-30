# Troubleshooting Handoff

Use this page to give a new ChatGPT or Codex conversation enough context to help
without sharing sensitive data.

## Project summary

`provider-ops-dwh-lab` is a local learning and portfolio project that simulates
a small healthcare operations data warehouse. It uses invented data only and
is not a production healthcare system.

## Architecture flow

```text
Synthetic MongoDB + synthetic CSV
  -> Python extraction/loading jobs
  -> local raw_archive
  -> PostgreSQL raw/staging
  -> dbt Core transformations and tests
  -> PostgreSQL marts
  -> Metabase dashboards / SQL reports
```

## Tech stack

Docker Compose, MongoDB, Python, pandas, PyMongo, Psycopg, PostgreSQL, dbt Core,
`dbt-postgres`, Metabase, SQL, Git, and optional GNU Make.

## Current MVP scope

The MVP covers synthetic sources, batch extraction/loading, local raw snapshots,
PostgreSQL raw/staging/marts layers, dbt transformations and tests, SQL reports,
Metabase guidance, and documentation. It excludes real PHI or company data,
production AWS deployment, streaming, Kafka, Redshift, Aurora, production CDC,
a frontend, and authentication.

Check [`README.md`](../README.md) for the current implementation status; planned
components may not exist yet.

## Common commands

```powershell
Copy-Item .env.example .env
docker compose up -d postgres mongo metabase
docker compose ps
docker compose logs <service-name>
docker compose --profile tools build tools
docker compose --profile tools run --rm tools dbt debug --project-dir dbt --profiles-dir dbt
docker compose down
git status
git diff
```

`docker compose down --volumes` deletes local database and Metabase state; use
it only when a reset is intended. Never paste `.env` values into a help request.

## Expected folder structure

```text
data/csv/       Synthetic CSV inputs
raw_archive/    Generated immutable-style snapshots
scripts/        Python extraction/loading jobs
dbt/            dbt project, models, tests, and configuration
sql/            Validation and reporting queries
docs/           Architecture, scope, decisions, and handoff notes
```

Some folders are placeholders until their MVP task is implemented.

## Common failure areas

- Docker Desktop is stopped, unhealthy, or lacks resources.
- A host port such as `5432`, `27017`, or `3000` is already in use.
- `.env` is missing or differs from expected local connection values.
- Metabase uses `localhost` instead of Docker service name `postgres`.
- The tools image is stale after dependency changes.
- PostgreSQL or MongoDB is not healthy before a job starts.
- dbt is using the wrong project/profile path or database credentials.
- Generated folders, schemas, tables, or models have not been implemented yet.
- Local volumes contain stale state from an earlier schema version.

## What to paste when asking for help

Share:

- The goal and the exact command that failed
- The complete error message and relevant non-secret logs
- Operating system, Docker version, and current Git branch/commit
- `docker compose ps` output
- Relevant file snippets or a small diff
- What you expected, what happened, and what you already tried
- Whether local files, volumes, or configuration recently changed

Remove passwords, connection strings, tokens, `.env` content, personal data,
company data, and any real healthcare information.

## Reusable troubleshooting prompt

```text
I am working in provider-ops-dwh-lab, a local synthetic-data-only healthcare
operations DWH learning project.

Architecture:
Synthetic MongoDB + synthetic CSV -> Python jobs -> raw_archive -> PostgreSQL
raw/staging -> dbt Core -> marts -> Metabase/SQL.

Current task:
[What I am trying to do]

Current branch/commit:
[Branch and commit]

Command run:
[Exact command]

Expected result:
[What should have happened]

Actual result and full error:
[Paste sanitized output]

Relevant service status:
[Paste docker compose ps]

Relevant files or diff:
[Paste only the necessary sanitized snippets]

What I already tried:
[Steps taken]

Please diagnose the likely cause first. Do not expand scope or implement an
unrelated feature. Use no real PHI, company data, secrets, or production claims.
```
