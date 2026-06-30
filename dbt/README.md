# dbt workspace

The dbt Core project lives in `provider_ops_dwh/`. It contains:

- A local `dbt-postgres` profile configured through environment variables
- Source declarations for the twelve PostgreSQL raw tables
- Twelve staging views that flatten and normalize MongoDB and CSV records
- Data tests for keys, accepted values, and source relationships
- An empty `models/marts/` folder reserved for later analytical models

No external dbt packages are currently required; `packages.yml` is intentionally
empty.

The staging layer intentionally excludes unnecessary sensitive source fields.
Run the project through the Docker tools service using the commands in the root
README.
