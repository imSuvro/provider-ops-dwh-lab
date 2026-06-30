"""Shared configuration, logging, database, and audit helpers for local ETL."""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from pymongo import MongoClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ARCHIVE_ROOT = PROJECT_ROOT / "raw_archive"
DATA_INPUT_ROOT = PROJECT_ROOT / "data" / "input"

MONGO_COLLECTIONS = (
    "customers",
    "providers",
    "patients",
    "programs",
    "enrollments",
    "consents",
    "timer_sessions",
    "device_orders",
    "coordinator_notes",
)
MONGO_TABLES = {
    collection_name: f"mongo_{collection_name}"
    for collection_name in MONGO_COLLECTIONS
}


def configure_logging() -> None:
    """Configure concise console logging once per process."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: str | datetime | None) -> datetime | None:
    if value is None:
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def mongo_uri_from_environment() -> str:
    load_environment()
    configured_uri = os.getenv("MONGO_URI")
    if configured_uri:
        return configured_uri

    username = quote_plus(os.getenv("MONGO_USER", "mongo"))
    password = quote_plus(os.getenv("MONGO_PASSWORD", "mongo"))
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    database_name = os.getenv("MONGO_DATABASE", "provider_ops")
    auth_source = quote_plus(os.getenv("MONGO_AUTH_SOURCE", "admin"))
    return (
        f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
        f"?authSource={auth_source}"
    )


def mongo_database_name() -> str:
    load_environment()
    return os.getenv("MONGO_DATABASE", "provider_ops")


def create_mongo_client() -> MongoClient:
    return MongoClient(
        mongo_uri_from_environment(),
        serverSelectionTimeoutMS=5_000,
    )


def create_postgres_connection() -> psycopg.Connection:
    load_environment()
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "warehouse"),
        password=os.getenv("POSTGRES_PASSWORD", "warehouse"),
        dbname=os.getenv("POSTGRES_DB", "provider_ops_dwh"),
        connect_timeout=5,
    )


def project_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_load_run(
    connection: psycopg.Connection,
    *,
    pipeline_name: str,
    source_type: str,
    source_name: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO audit.load_runs (
                pipeline_name,
                source_type,
                source_name,
                status,
                metadata
            )
            VALUES (%s, %s, %s, 'RUNNING', %s)
            RETURNING load_run_id
            """,
            (
                pipeline_name,
                source_type,
                source_name,
                Jsonb(metadata or {}),
            ),
        )
        load_run_id = cursor.fetchone()[0]
    connection.commit()
    return load_run_id


def finish_load_run(
    connection: psycopg.Connection,
    *,
    load_run_id: int,
    status: str,
    records_read: int,
    records_loaded: int,
    records_rejected: int,
    error_message: str | None = None,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE audit.load_runs
            SET
                status = %s,
                completed_at = CURRENT_TIMESTAMP,
                records_read = %s,
                records_loaded = %s,
                records_rejected = %s,
                error_message = %s
            WHERE load_run_id = %s
            """,
            (
                status,
                records_read,
                records_loaded,
                records_rejected,
                error_message,
                load_run_id,
            ),
        )
    connection.commit()


def create_file_history(
    connection: psycopg.Connection,
    *,
    load_run_id: int,
    path: Path,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO audit.file_load_history (
                load_run_id,
                file_name,
                file_path,
                file_checksum,
                file_size_bytes,
                status
            )
            VALUES (%s, %s, %s, %s, %s, 'LOADING')
            RETURNING file_load_history_id
            """,
            (
                load_run_id,
                path.name,
                project_relative_path(path),
                file_sha256(path),
                path.stat().st_size,
            ),
        )
        file_history_id = cursor.fetchone()[0]
    connection.commit()
    return file_history_id


def finish_file_history(
    connection: psycopg.Connection,
    *,
    file_history_id: int,
    status: str,
    row_count: int | None,
    metadata: dict[str, Any] | None = None,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE audit.file_load_history
            SET
                status = %s,
                row_count = %s,
                loaded_at = CASE
                    WHEN %s = 'LOADED' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END,
                metadata = %s
            WHERE file_load_history_id = %s
            """,
            (
                status,
                row_count,
                status,
                Jsonb(metadata or {}),
                file_history_id,
            ),
        )
    connection.commit()


def record_load_error(
    connection: psycopg.Connection,
    *,
    load_run_id: int,
    error_stage: str,
    error_message: str,
    source_record_id: str | None = None,
    source_file_name: str | None = None,
    source_row_number: int | None = None,
    raw_payload: dict[str, Any] | None = None,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO audit.load_errors (
                load_run_id,
                source_record_id,
                source_file_name,
                source_row_number,
                error_stage,
                error_message,
                raw_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                load_run_id,
                source_record_id,
                source_file_name,
                source_row_number,
                error_stage,
                error_message,
                Jsonb(raw_payload) if raw_payload is not None else None,
            ),
        )
    connection.commit()
