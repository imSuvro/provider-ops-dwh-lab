# Metabase Dashboard Guide

This guide explains how to turn the committed reporting SQL into a manual
Metabase dashboard. It does not create or modify Metabase automatically.

The dashboard is for synthetic learning data only. The KPI definitions are
local assumptions and must not be treated as production billing or clinical
rules.

## Before you start

Start the services, load the synthetic sources, and build dbt:

```powershell
docker compose up -d mongodb postgres metabase
make seed
make etl
make dbt-run
make dbt-test
```

Without GNU Make, use the Docker commands in the root
[`README.md`](../README.md).

Confirm the mart tables exist:

```powershell
docker compose exec -T postgres psql -U warehouse -d provider_ops_dwh -c "\dt marts.*"
```

Open Metabase at [http://localhost:3000](http://localhost:3000).

## Connect Metabase to PostgreSQL

If the local PostgreSQL database has not been added:

1. Open Metabase administration settings.
2. Add a PostgreSQL database.
3. Use a descriptive name such as `Provider Ops DWH`.
4. Enter:
   - Host: `postgres`
   - Port: `5432`
   - Database: `provider_ops_dwh`
   - Username: the `POSTGRES_USER` value from `.env`
   - Password: the `POSTGRES_PASSWORD` value from `.env`
5. Save the connection and let Metabase synchronize the schemas.

Use `postgres`, not `localhost`, because Metabase and PostgreSQL run in the
same Docker Compose network.

## Create a collection and saved questions

Create a collection named `Provider Ops DWH`. For each file in
`sql/reports/`:

1. Start a new native SQL question.
2. Select the `Provider Ops DWH` database.
3. Copy the complete SQL file into the editor.
4. Run it and inspect the result.
5. Save it in the collection using the suggested question name below.

The committed files are standard PostgreSQL and intentionally contain no
Metabase template tags. This keeps them runnable in `psql` and other SQL
clients. Build the first dashboard without filters; add optional native-query
variables only after the cards work.

## Dashboard setup

Create a dashboard named `Provider Operations Overview`. Add a text card before
each group of questions so the six sections are easy to scan.

### 1. Enrollment Funnel

**SQL:** `sql/reports/enrollment_funnel_by_customer.sql`

**Saved question:** `Enrollment Funnel by Customer`

**Suggested visualization:** Bar chart.

- X-axis: `enrollment_status`
- Y-axis: `enrollment_count`
- Breakout: `program_code` or `customer_name`
- Sort: `funnel_stage_order`
- Display `enrollment_conversion_pct` in the tooltip or a companion table

The source stores a current status, not a full transition history. A bar chart
is more honest than implying that every record moved through every stage.

Useful companion cards:

- Number card using `active_enrollment_count`
- Number or gauge using `enrollment_conversion_pct`
- Table broken out by customer and program

### 2. Consent Conversion

**SQL:** `sql/reports/consent_conversion_by_program.sql`

**Saved question:** `Consent Conversion by Program`

**Suggested visualization:** Line chart or grouped bar chart.

- X-axis: `patient_month`
- Y-axis: `consent_conversion_pct`
- Breakout: `program_code`
- Include `customer_name` when a customer-level comparison is useful

Useful companion table columns:

- `enrolled_patient_count`
- `patient_with_consent_record_count`
- `pending_consent_patient_count`
- `declined_consent_patient_count`
- `completed_consent_patient_count`

The conversion denominator is patient-months with an enrollment record. Review
that definition with the KPI owner before broader use.

### 3. Timer Utilization

**SQL:** `sql/reports/timer_utilization_by_provider.sql`

**Saved question:** `Timer Utilization by Provider`

**Suggested visualization:** Horizontal bar chart.

- Y-axis: `provider_name`
- X-axis: `timer_utilization_pct`
- Breakout: `program_code`
- Display `timer_minutes` and `required_timer_minutes` in the tooltip

The query includes active patient-months with a positive program minimum.
Utilization may exceed 100% because recorded minutes are not capped.

Useful companion cards:

- Table of providers below 100%
- Number card for total `timer_minutes`
- Bar chart for `patient_at_or_above_minimum_count`

### 4. Billing Readiness

**SQL:** `sql/reports/billable_patient_months.sql`

**Saved question:** `Billable Patient-Months`

**Suggested visualization:** Detail table.

Recommended visible columns:

- `patient_month`
- `customer_name`
- `provider_name`
- `program_code`
- `patient_id`
- `timer_minutes`
- `monthly_minimum_minutes`
- `device_status`
- `source_billable_candidate`
- `billing_alignment_status`
- `billing_amount`

Useful companion cards:

- Number card that counts rows
- Bar chart grouped by `program_code`
- Bar chart grouped by `billing_alignment_status`

Every returned row meets the local computed readiness rule. The source
candidate flag is a comparison, not a readiness input.

### 5. Customer Performance

**SQL:** `sql/reports/customer_performance_summary.sql`

**Saved question:** `Customer Performance Summary`

**Suggested visualization:** Table with conditional formatting.

Recommended columns:

- `patient_month`
- `customer_name`
- `program_code`
- `active_patient_count`
- `consented_patient_count`
- `timer_minutes`
- `delayed_device_count`
- `billable_ready_patient_count`
- `billable_readiness_pct`

Useful companion cards:

- Line chart of `billable_readiness_pct` by month
- Bar chart of `active_patient_count` by customer
- Bar chart of `delayed_device_count` by customer

Avoid inventing red/amber/green thresholds until a business owner approves
targets.

### 6. Data Quality Monitor

**SQL:** `sql/reports/data_quality_issues.sql`

**Saved question:** `Data Quality Issues`

**Suggested visualization:** Detail table.

Recommended columns:

- `issue_type_label`
- `customer_name`
- `record_type`
- `record_id`
- `patient_id`
- `issue_details`
- `issue_type_count`

Useful companion cards:

- Number card that counts rows
- Bar chart grouped by `issue_type_label`
- Table grouped by `customer_name`

An empty result is expected when the synthetic dataset passes every current
quality rule. It means no modeled issues were detected, not that all possible
quality problems have been ruled out.

## Suggested dashboard layout

Use a simple two-column layout:

1. Section heading across the full width.
2. One or two summary cards on the first row.
3. Main chart or detail table across the full width below.
4. Repeat for the next section.

Put Data Quality Monitor last so operational exceptions do not crowd out the
primary performance story.

## Optional dashboard filters

Native SQL questions need Metabase template tags before dashboard filters can
be connected. Add them only after the unfiltered questions run correctly.

Useful filters and compatible sections:

| Filter | Compatible sections |
| --- | --- |
| Patient month | Consent Conversion, Timer Utilization, Billing Readiness, Customer Performance |
| Customer | All sections |
| Program | Enrollment Funnel, Consent Conversion, Timer Utilization, Billing Readiness, Customer Performance |
| Provider | Timer Utilization and Billing Readiness |

When adding a variable:

1. Wrap the committed query in a new outer query or add the optional predicate
   before its final `ORDER BY`.
2. Use Metabase's optional-clause syntax so a blank filter does not remove all
   rows.
3. Give the variable a clear type and label.
4. Map the dashboard filter only to cards that expose the matching field.
5. Test the blank state and at least one selected value.

Keep the committed report SQL portable. Save Metabase-specific variants as
questions in Metabase rather than replacing the repository files.

## Refreshing the dashboard

The cards query the current mart tables. To refresh the underlying demo data:

```powershell
make seed
make etl
make dbt-run
make dbt-test
```

Then refresh the dashboard in the browser. No scheduled refresh or Metabase API
automation is configured.

## Troubleshooting

- **Database connection fails:** confirm all services are healthy and use host
  `postgres`.
- **Mart tables are missing:** run the ETL and `dbt run`.
- **Questions return no rows:** confirm the raw tables contain data and inspect
  `marts.mart_patient_month`.
- **Data Quality Issues is empty:** this is valid when no current rule finds an
  issue.
- **A dashboard filter cannot connect:** add a matching template variable to
  that native SQL question.
- **Numbers look inconsistent:** confirm all cards use the same customer,
  program, and month scope, then review
  [`kpi_definitions.md`](kpi_definitions.md).

The dashboard remains a manual learning artifact. Production reporting would
need approved KPI ownership, access controls, refresh targets, and operational
support.
