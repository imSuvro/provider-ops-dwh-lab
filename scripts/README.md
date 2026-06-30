# Python jobs

Implemented source-data utilities:

- `seed_mongo.py` validates and loads a deterministic synthetic demo batch into
  the nine MongoDB source collections.
- `reset_demo_data.py` removes only records tagged with that demo batch.
- `extract_mongo_to_archive.py` writes each MongoDB collection to a dated JSONL
  archive partition.
- `load_mongo_archive_to_postgres.py` loads archived records into the matching
  `raw.mongo_*` tables.
- `load_csv_to_postgres.py` loads the committed CSV sources into typed
  `raw.csv_*` tables.
- `run_etl.py` runs extraction followed by both PostgreSQL loaders.

The seed and reset scripts load MongoDB settings from the repository `.env`
file. The seed operation replaces its own batch on each run, which avoids
duplicates while preserving unrelated records.

The ETL scripts load MongoDB and PostgreSQL settings from `.env`, log progress
to the console, and write PostgreSQL load and file audit records. Raw rows use
simple source-key update/insert behavior for repeatable local runs.

dbt transformation and reporting assets live under `dbt/` and `sql/reports/`;
the root `Makefile` orchestrates them with the Python jobs through `make demo`.
