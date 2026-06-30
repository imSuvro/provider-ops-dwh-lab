# Synthetic source data

`data/input/` contains committed, clearly synthetic source fixtures:

- `vob_files.csv` contains demo verification-of-benefits results.
- `billing_exports.csv` contains monthly program billing candidates and
  amounts.
- `customer_roster_upload.csv` contains a demo customer roster.

The patient, customer, provider, and program identifiers align with the
MongoDB records created by `scripts/seed_mongo.py`.

Future generated CSV files belong in `data/csv/` and are ignored by Git.
