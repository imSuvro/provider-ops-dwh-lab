# Python jobs

Implemented source-data utilities:

- `seed_mongo.py` validates and loads a deterministic synthetic demo batch into
  the nine MongoDB source collections.
- `reset_demo_data.py` removes only records tagged with that demo batch.

Both scripts load MongoDB settings from the repository `.env` file. The seed
operation replaces its own batch on each run, which avoids duplicates while
preserving unrelated records.

Extraction, raw archive, and PostgreSQL loading jobs are not implemented yet.
