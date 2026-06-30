BEGIN;

CREATE TABLE IF NOT EXISTS audit.load_runs (
    load_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pipeline_name text NOT NULL,
    source_type text NOT NULL,
    source_name text NOT NULL,
    status text NOT NULL,
    started_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp with time zone,
    records_read bigint NOT NULL DEFAULT 0,
    records_loaded bigint NOT NULL DEFAULT 0,
    records_rejected bigint NOT NULL DEFAULT 0,
    error_message text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT load_runs_status_check
        CHECK (status IN ('RUNNING', 'SUCCEEDED', 'FAILED', 'PARTIAL')),
    CONSTRAINT load_runs_record_counts_check
        CHECK (
            records_read >= 0
            AND records_loaded >= 0
            AND records_rejected >= 0
        ),
    CONSTRAINT load_runs_completion_check
        CHECK (completed_at IS NULL OR completed_at >= started_at)
);

CREATE TABLE IF NOT EXISTS audit.load_errors (
    load_error_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    load_run_id bigint NOT NULL,
    source_record_id text,
    source_file_name text,
    source_row_number integer,
    error_stage text NOT NULL,
    error_code text,
    error_message text NOT NULL,
    raw_payload jsonb,
    occurred_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT load_errors_load_run_fk
        FOREIGN KEY (load_run_id)
        REFERENCES audit.load_runs (load_run_id),
    CONSTRAINT load_errors_source_row_number_check
        CHECK (source_row_number IS NULL OR source_row_number > 0)
);

CREATE TABLE IF NOT EXISTS audit.file_load_history (
    file_load_history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    load_run_id bigint NOT NULL,
    file_name text NOT NULL,
    file_path text NOT NULL,
    file_checksum text,
    file_size_bytes bigint,
    row_count bigint,
    status text NOT NULL,
    discovered_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    loaded_at timestamp with time zone,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT file_load_history_load_run_fk
        FOREIGN KEY (load_run_id)
        REFERENCES audit.load_runs (load_run_id),
    CONSTRAINT file_load_history_status_check
        CHECK (
            status IN (
                'DISCOVERED',
                'LOADING',
                'LOADED',
                'FAILED',
                'SKIPPED'
            )
        ),
    CONSTRAINT file_load_history_file_size_check
        CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0),
    CONSTRAINT file_load_history_row_count_check
        CHECK (row_count IS NULL OR row_count >= 0),
    CONSTRAINT file_load_history_loaded_at_check
        CHECK (loaded_at IS NULL OR loaded_at >= discovered_at)
);

CREATE INDEX IF NOT EXISTS load_runs_status_started_at_idx
    ON audit.load_runs (status, started_at DESC);
CREATE INDEX IF NOT EXISTS load_errors_load_run_id_idx
    ON audit.load_errors (load_run_id);
CREATE INDEX IF NOT EXISTS file_load_history_load_run_id_idx
    ON audit.file_load_history (load_run_id);
CREATE INDEX IF NOT EXISTS file_load_history_checksum_idx
    ON audit.file_load_history (file_checksum)
    WHERE file_checksum IS NOT NULL;

COMMENT ON TABLE audit.load_runs IS
    'One row per extraction or loading pipeline execution.';
COMMENT ON TABLE audit.load_errors IS
    'Record-level or file-level errors associated with a load run.';
COMMENT ON TABLE audit.file_load_history IS
    'Discovery and processing history for source files.';

COMMIT;
