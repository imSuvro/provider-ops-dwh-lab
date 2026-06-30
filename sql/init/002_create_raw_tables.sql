BEGIN;

CREATE TABLE IF NOT EXISTS raw.mongo_customers (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'customers',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_customers_source_collection_check
        CHECK (source_collection = 'customers')
);

CREATE TABLE IF NOT EXISTS raw.mongo_providers (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'providers',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_providers_source_collection_check
        CHECK (source_collection = 'providers')
);

CREATE TABLE IF NOT EXISTS raw.mongo_patients (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'patients',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_patients_source_collection_check
        CHECK (source_collection = 'patients')
);

CREATE TABLE IF NOT EXISTS raw.mongo_programs (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'programs',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_programs_source_collection_check
        CHECK (source_collection = 'programs')
);

CREATE TABLE IF NOT EXISTS raw.mongo_enrollments (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'enrollments',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_enrollments_source_collection_check
        CHECK (source_collection = 'enrollments')
);

CREATE TABLE IF NOT EXISTS raw.mongo_consents (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'consents',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_consents_source_collection_check
        CHECK (source_collection = 'consents')
);

CREATE TABLE IF NOT EXISTS raw.mongo_timer_sessions (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'timer_sessions',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_timer_sessions_source_collection_check
        CHECK (source_collection = 'timer_sessions')
);

CREATE TABLE IF NOT EXISTS raw.mongo_device_orders (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'device_orders',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_device_orders_source_collection_check
        CHECK (source_collection = 'device_orders')
);

CREATE TABLE IF NOT EXISTS raw.mongo_coordinator_notes (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id text NOT NULL,
    raw_doc jsonb NOT NULL,
    source_collection text NOT NULL DEFAULT 'coordinator_notes',
    extracted_at timestamp with time zone NOT NULL,
    source_updated_at timestamp with time zone NULL,
    CONSTRAINT mongo_coordinator_notes_source_collection_check
        CHECK (source_collection = 'coordinator_notes')
);

CREATE INDEX IF NOT EXISTS mongo_customers_source_snapshot_idx
    ON raw.mongo_customers (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_providers_source_snapshot_idx
    ON raw.mongo_providers (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_patients_source_snapshot_idx
    ON raw.mongo_patients (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_programs_source_snapshot_idx
    ON raw.mongo_programs (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_enrollments_source_snapshot_idx
    ON raw.mongo_enrollments (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_consents_source_snapshot_idx
    ON raw.mongo_consents (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_timer_sessions_source_snapshot_idx
    ON raw.mongo_timer_sessions (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_device_orders_source_snapshot_idx
    ON raw.mongo_device_orders (source_id, extracted_at DESC);
CREATE INDEX IF NOT EXISTS mongo_coordinator_notes_source_snapshot_idx
    ON raw.mongo_coordinator_notes (source_id, extracted_at DESC);

CREATE TABLE IF NOT EXISTS raw.csv_vob_files (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vob_id text,
    patient_id text,
    customer_id text,
    payer_name text,
    member_reference text,
    coverage_status text,
    verified_on date,
    program text,
    estimated_copay numeric(12, 2),
    source_file_name text NOT NULL,
    source_row_number integer NOT NULL,
    loaded_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.csv_billing_exports (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    export_id text,
    patient_id text,
    customer_id text,
    patient_month date,
    program text,
    billable_candidate boolean,
    amount numeric(12, 2),
    currency character(3),
    exported_at timestamp with time zone,
    source_file_name text NOT NULL,
    source_row_number integer NOT NULL,
    loaded_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.csv_customer_roster_uploads (
    raw_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    roster_record_id text,
    customer_id text,
    patient_id text,
    provider_id text,
    first_name text,
    last_name text,
    date_of_birth date,
    state character(2),
    phone text,
    program_interest text,
    uploaded_at timestamp with time zone,
    source_file_name text NOT NULL,
    source_row_number integer NOT NULL,
    loaded_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS csv_vob_files_source_file_idx
    ON raw.csv_vob_files (source_file_name, source_row_number);
CREATE INDEX IF NOT EXISTS csv_billing_exports_source_file_idx
    ON raw.csv_billing_exports (source_file_name, source_row_number);
CREATE INDEX IF NOT EXISTS csv_customer_roster_uploads_source_file_idx
    ON raw.csv_customer_roster_uploads (source_file_name, source_row_number);

COMMENT ON TABLE raw.mongo_customers IS
    'Latest raw records from the MongoDB customers collection.';
COMMENT ON TABLE raw.mongo_providers IS
    'Latest raw records from the MongoDB providers collection.';
COMMENT ON TABLE raw.mongo_patients IS
    'Latest raw records from the MongoDB patients collection.';
COMMENT ON TABLE raw.mongo_programs IS
    'Latest raw records from the MongoDB programs collection.';
COMMENT ON TABLE raw.mongo_enrollments IS
    'Latest raw records from the MongoDB enrollments collection.';
COMMENT ON TABLE raw.mongo_consents IS
    'Latest raw records from the MongoDB consents collection.';
COMMENT ON TABLE raw.mongo_timer_sessions IS
    'Latest raw records from the MongoDB timer_sessions collection.';
COMMENT ON TABLE raw.mongo_device_orders IS
    'Latest raw records from the MongoDB device_orders collection.';
COMMENT ON TABLE raw.mongo_coordinator_notes IS
    'Latest raw records from the MongoDB coordinator_notes collection.';
COMMENT ON TABLE raw.csv_vob_files IS
    'Typed raw rows loaded from synthetic VOB CSV files.';
COMMENT ON TABLE raw.csv_billing_exports IS
    'Typed raw rows loaded from synthetic billing export CSV files.';
COMMENT ON TABLE raw.csv_customer_roster_uploads IS
    'Typed raw rows loaded from synthetic customer roster CSV files.';

COMMIT;
