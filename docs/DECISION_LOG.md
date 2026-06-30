# Decision Log

Record durable project decisions here. Keep entries short and update related
documentation when a decision changes.

## Initial decisions

| Decision | Rationale | Status |
| --- | --- | --- |
| Use local PostgreSQL to represent possible future Amazon RDS PostgreSQL. | Learn on an accessible relational warehouse while preserving a clear production mapping. | Accepted |
| Use local `raw_archive/` to represent a possible future controlled S3 archive. | Practice retaining source snapshots without requiring cloud deployment. | Accepted |
| Use Python jobs first for extraction and loading. | Keep source handling explicit, approachable, and portable to later schedulers or Lambda. | Accepted |
| Use dbt Core for transformations and tests. | Separate analytical transformation from ingestion and keep models reviewable. | Accepted |
| Separate PostgreSQL into `raw`, `staging`, `marts`, and `audit` schemas. | Keep source capture, transformation layers, reporting models, and load history logically distinct. | Accepted |
| Update or insert local raw rows by source record ID. | Keep reruns approachable and duplicate-free while the dated archive and audit tables retain execution history. | Accepted |
| Use synthetic data only. | Protect privacy and make the repository safe for learning and portfolio use. | Accepted |
| Keep AWS deployment out of the MVP. | Prioritize warehouse fundamentals before infrastructure complexity. | Accepted |

## New decision template

### YYYY-MM-DD — Decision title

- **Decision:** <!-- State the choice. -->
- **Why:** <!-- State the reason. -->
- **Consequences:** <!-- State the tradeoffs and follow-up work. -->
- **Status:** Proposed / Accepted / Superseded
