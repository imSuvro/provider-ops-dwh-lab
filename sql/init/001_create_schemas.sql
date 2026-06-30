BEGIN;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS audit;

COMMENT ON SCHEMA raw IS
    'Latest extracted source records before transformation.';
COMMENT ON SCHEMA staging IS
    'Cleaned and standardized intermediate warehouse models.';
COMMENT ON SCHEMA marts IS
    'Business-facing analytical models and reporting tables.';
COMMENT ON SCHEMA audit IS
    'Pipeline run, load error, and source file processing history.';

COMMIT;
