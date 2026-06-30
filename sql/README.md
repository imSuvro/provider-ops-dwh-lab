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

`reports/` contains portable PostgreSQL queries for:

- enrollment funnel by customer
- consent conversion by program
- timer utilization by provider
- billable patient-month detail
- customer performance summary
- data quality issues

Run a report with:

```powershell
Get-Content -Raw sql/reports/customer_performance_summary.sql |
  docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh
```

The reports query dbt marts and are intended for direct SQL exploration or
manual use in Metabase. See the
[Metabase dashboard guide](../docs/metabase_dashboard_guide.md).
