# dbt workspace

The dbt Core project lives in `provider_ops_dwh/`. It contains:

- A local `dbt-postgres` profile configured through environment variables
- Source declarations for the twelve PostgreSQL raw tables
- Twelve staging views that flatten and normalize MongoDB and CSV records
- Five table-materialized analytics marts for enrollment, patient-month,
  billing readiness, customer performance, and data quality
- Data tests for keys, accepted values, and model relationships

No external dbt packages are currently required; `packages.yml` is intentionally
empty.

The staging and mart layers intentionally exclude unnecessary sensitive source
fields. Billing readiness is a local analytical rule that combines active
enrollment, completed consent, required timer minutes, and delivered devices
for programs that require them. Source billing candidacy remains a separate
field for comparison.

Run the project through the Docker tools service using the commands in the root
README.
