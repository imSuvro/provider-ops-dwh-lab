# SQL workspace

`init/` contains ordered PostgreSQL initialization scripts:

1. `001_create_schemas.sql` creates `raw`, `staging`, `marts`, and `audit`.
2. `002_create_raw_tables.sql` creates MongoDB raw document tables and typed CSV
   source tables in `raw`.
3. `003_create_audit_tables.sql` creates load run, load error, and file history
   tables in `audit`.

Docker mounts this directory at `/docker-entrypoint-initdb.d`. PostgreSQL runs
the files automatically only when initializing a new data volume. See the
root README for non-destructive commands that apply them to an existing local
volume.

Future SQL files outside `init/` will contain lightweight validation queries
and learning reports that complement dbt models and Metabase dashboards.
