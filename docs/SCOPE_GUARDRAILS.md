# Scope Guardrails

## MVP includes

- Synthetic MongoDB operational data
- Synthetic CSV source files
- Python extraction and loading jobs
- A local raw archive folder
- PostgreSQL raw, staging, and marts schemas
- dbt Core transformations and tests
- SQL reporting queries
- A Metabase dashboard guide
- Clear setup, architecture, and learning documentation

## MVP excludes

- Real PHI, patient data, company data, or production exports
- Production AWS deployment
- Real-time streaming or Kafka
- Redshift or Aurora
- Production change data capture (CDC)
- A frontend application
- Authentication

## Possible later extensions

Only after the MVP is complete and explicitly approved:

- Deploying selected components to AWS
- Using S3 and Amazon RDS PostgreSQL
- Orchestration, monitoring, and alerting
- Incremental loading or a controlled CDC experiment
- QuickSight reporting
- Additional synthetic source domains and data-quality checks

## Change rule

Do not expand scope without explicit human approval. Record an approved
long-lived scope or architecture change in
[`DECISION_LOG.md`](DECISION_LOG.md), then update the README and related docs.
