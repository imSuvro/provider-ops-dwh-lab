# Project One-Pager

## Business problem simulated

Healthcare operations teams often need a consistent view of activity spread
across operational applications and batch files. This lab simulates bringing
those sources together so teams could analyze operational trends from trusted,
documented datasets. All records are invented.

## Architecture summary

```text
Synthetic MongoDB + synthetic CSV
  -> Python jobs
  -> local raw_archive
  -> PostgreSQL raw/staging
  -> dbt Core
  -> PostgreSQL marts
  -> Metabase / SQL reports
```

PostgreSQL represents possible future Amazon RDS PostgreSQL, and
`raw_archive/` represents a controlled Amazon S3 archive. Python jobs represent
scheduled extraction/loading, while dbt owns transformation and testing.

## What this project demonstrates

- Separating source capture, raw storage, transformation, and reporting
- Combining document and file-based sources in a repeatable pipeline
- Organizing PostgreSQL into raw, staging, and analytics layers
- Applying dbt models and tests to improve analytical trust
- Explaining architecture and tradeoffs to technical and non-technical readers

## Why it is useful

The project provides a hands-on way to learn warehouse concepts and creates a
small portfolio artifact that can support conversations with managers,
technical leaders, recruiters, and beginner engineers. It also builds practice
in scoping, documenting, reviewing, and leading a future warehouse initiative.

## Intentional limits

The MVP avoids real PHI and company data, production AWS deployment, streaming,
Kafka, Redshift, Aurora, production CDC, frontend development, authentication,
and claims of production readiness. It favors a clear, inspectable learning
system over enterprise complexity.
