# Open Questions for the CTO

These questions separate the implemented local learning architecture from
decisions required for a real warehouse. They are prompts for discovery, not
assumptions about a production environment.

## Source systems and ownership

1. Which system is the authoritative source for customers, providers,
   patients, programs, enrollments, consents, activity time, device orders,
   coverage verification, and billing candidates?
2. When the same attribute appears in multiple systems, which source wins and
   who resolves conflicts?
3. Are source identifiers stable and globally unique, or do warehouse keys
   need to combine tenant, source system, and record identifier?
4. Do source systems retain status history and deletions, or only the latest
   record?
5. Who owns the source data contract for each system, including schema-change
   communication and correction of bad records?
6. Are the current file feeds official system outputs, temporary operational
   workarounds, or user-managed uploads?

## Refresh frequency and service expectations

1. How fresh must each domain be: near real time, hourly, daily, or monthly?
2. Which dashboards or operational decisions depend on intraday data?
3. What is the acceptable end-to-end delay from a source change to a visible
   warehouse update?
4. What are the recovery-time and recovery-point expectations after a failed
   load?
5. Are late-arriving records expected, and how far back should transformations
   recalculate?
6. Are there business cutoff times or time-zone rules for month-end billing?

## PHI and data boundaries

1. Which source fields are classified as PHI, personally identifiable
   information, financial information, or confidential business data?
2. Does the warehouse need patient-level identifiers, or can some use cases
   operate on tokenized, de-identified, or aggregated data?
3. Which fields are prohibited from raw storage, logs, error payloads,
   archives, development environments, and reporting tools?
4. What retention and deletion rules apply to source snapshots, warehouse
   tables, audit records, backups, and exported reports?
5. Is a formal data-classification review required before onboarding each
   source?
6. What environments may use production-like data, and what masking standard
   is required outside production?

## Access controls and auditability

1. Which roles need patient-level, customer-level, aggregate-only, operations,
   engineering, billing, and administrative access?
2. Is customer or tenant isolation required through separate databases,
   schemas, row-level security, or the reporting layer?
3. Which identity provider and single sign-on standard should database and
   reporting access use?
4. How should service accounts, password rotation, secrets, and emergency
   access be managed?
5. Which database queries, dashboard views, exports, and permission changes
   must be audited?
6. Who approves access, how often is access recertified, and who reviews audit
   logs?

## KPI governance

1. Who is the business owner and technical steward for each KPI?
2. Who approves definitions for Active Patients, Consented Patients,
   Enrollment Conversion, Timer Utilization, Device Fulfillment Delay,
   Billable Patient-Month, and Customer Performance?
3. Should Enrollment Conversion use all received enrollments, exclude
   declined records, or use a time-based cohort?
4. Which timer activity types count, and should utilization be capped at 100%?
5. What device fulfillment service level defines a delay?
6. Which program, payer, and contractual rules determine billability?
7. How should KPI definition changes be versioned and communicated?
8. What reconciliation threshold is acceptable between warehouse readiness and
   billing-system output?

See [`kpi_definitions.md`](kpi_definitions.md) for the current local
definitions and explicit assumptions.

## Data movement and future DMS use

1. Are the authoritative operational sources relational databases that Amazon
   Database Migration Service can access, or are they APIs, MongoDB, files, or
   vendor-managed systems?
2. Is log-based change data capture required, or would scheduled incremental
   extraction meet the freshness target?
3. Do source database owners permit replication settings, log retention,
   replication slots, and network access required by DMS?
4. How must inserts, updates, deletes, schema changes, and initial backfills be
   represented downstream?
5. What evidence would justify DMS complexity: data volume, freshness,
   reliability, source load, or operational support requirements?
6. If DMS is not suitable for a source, which ingestion pattern is preferred?

DMS should be selected only after source technology, change-capture needs,
networking, and operational ownership are known. The local Python extraction
jobs do not establish that DMS is required.

## Reporting platform

1. Is Metabase or Amazon QuickSight preferred for the target environment?
2. Who are the main audiences: operations teams, customer leaders, executives,
   analysts, or external customers?
3. Is embedded analytics required?
4. Are row-level customer restrictions, fine-grained permissions, scheduled
   delivery, alerts, or governed semantic definitions required?
5. What concurrency, dashboard-load time, export, and availability targets
   apply?
6. Are licensing, AWS integration, support ownership, or self-service
   exploration the deciding factors?
7. Should the reporting tool query marts directly, views, or a governed
   semantic layer?

## Amazon RDS sizing and networking

1. What are the expected starting and 12-to-24-month data volumes, daily
   changes, query concurrency, and peak load windows?
2. Is Amazon RDS for PostgreSQL the intended analytical store, or is it an
   interim choice before a dedicated warehouse?
3. Which instance class, storage type, storage autoscaling limit, IOPS, and
   connection limit fit the measured workload?
4. Are Multi-AZ deployment, read replicas, automated backups, point-in-time
   recovery, and cross-region recovery required?
5. Which VPC, subnets, security groups, routing, DNS, and private connectivity
   should be used?
6. Must the database be private-only, and where will ETL, dbt, reporting, and
   administrative clients run?
7. Is RDS Proxy or another connection-pooling layer needed?
8. Which encryption keys, certificate policies, parameter groups, maintenance
   windows, and monitoring standards apply?
9. Who owns capacity testing, cost review, patching, failover exercises, and
   incident response?

Sizing should follow measured ingestion and query tests. The local Docker
configuration is not evidence for a production instance size.

## Decision record

For each resolved question, record:

- decision and date
- business owner
- technical owner
- evidence or constraint
- affected data products
- follow-up work

Durable architecture choices should also be summarized in
[`DECISION_LOG.md`](DECISION_LOG.md).
