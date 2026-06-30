# Architecture

## Intended flow

1. Synthetic operational documents are generated in MongoDB.
2. Synthetic reference and batch data is supplied as CSV files.
3. Python jobs extract each source into timestamped files in `raw_archive/`.
4. Python jobs load those snapshots into PostgreSQL raw tables and record load
   outcomes in the audit schema.
5. dbt builds staging models and analytics marts in PostgreSQL.
6. Metabase queries the marts for dashboards and interactive SQL reports.

## Design boundaries

- Local development only.
- Synthetic fake healthcare operations data only.
- No PHI, production data, or company-confidential data.
- Raw inputs are treated as immutable snapshots once written.

Implementation details and data contracts are intentionally deferred.
