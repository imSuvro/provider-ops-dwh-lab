"""Load MongoDB JSONL archive files into PostgreSQL raw tables."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from etl_common import (
    MONGO_TABLES,
    RAW_ARCHIVE_ROOT,
    configure_logging,
    create_file_history,
    create_load_run,
    create_postgres_connection,
    finish_file_history,
    finish_load_run,
    parse_timestamp,
    project_relative_path,
    record_load_error,
)


LOGGER = logging.getLogger("load_mongo_archive")


def discover_archive_paths(
    *,
    archive_root: Path = RAW_ARCHIVE_ROOT,
    archive_date: date | None = None,
) -> list[Path]:
    paths = sorted((archive_root / "mongo").glob("*/date=*/data.jsonl"))
    if archive_date is not None:
        partition_name = f"date={archive_date.isoformat()}"
        paths = [path for path in paths if path.parent.name == partition_name]
    return paths


def archive_collection_name(path: Path) -> str:
    collection_name = path.parents[1].name
    if collection_name not in MONGO_TABLES:
        raise ValueError(f"Unsupported MongoDB archive collection: {collection_name}")
    return collection_name


def upsert_mongo_record(
    cursor: psycopg.Cursor,
    *,
    table_name: str,
    record: dict[str, Any],
) -> None:
    source_id = str(record["source_id"])
    raw_doc = record["raw_doc"]
    source_collection = str(record["source_collection"])
    extracted_at = parse_timestamp(record["extracted_at"])
    source_updated_at = parse_timestamp(record.get("source_updated_at"))

    update_statement = sql.SQL(
        """
        UPDATE raw.{}
        SET
            raw_doc = %s,
            source_collection = %s,
            extracted_at = %s,
            source_updated_at = %s
        WHERE source_id = %s
        """
    ).format(sql.Identifier(table_name))
    cursor.execute(
        update_statement,
        (
            Jsonb(raw_doc),
            source_collection,
            extracted_at,
            source_updated_at,
            source_id,
        ),
    )
    if cursor.rowcount > 0:
        return

    insert_statement = sql.SQL(
        """
        INSERT INTO raw.{} (
            source_id,
            raw_doc,
            source_collection,
            extracted_at,
            source_updated_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """
    ).format(sql.Identifier(table_name))
    cursor.execute(
        insert_statement,
        (
            source_id,
            Jsonb(raw_doc),
            source_collection,
            extracted_at,
            source_updated_at,
        ),
    )


def load_archive_file(
    connection: psycopg.Connection,
    *,
    path: Path,
    collection_name: str,
) -> int:
    table_name = MONGO_TABLES[collection_name]
    row_count = 0
    with path.open("r", encoding="utf-8") as source_file:
        with connection.cursor() as cursor:
            for line_number, line in enumerate(source_file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if record.get("source_collection") != collection_name:
                        raise ValueError(
                            "collection does not match its archive path"
                        )
                    upsert_mongo_record(
                        cursor,
                        table_name=table_name,
                        record=record,
                    )
                except Exception as error:
                    raise ValueError(
                        f"{path}:{line_number}: {error}"
                    ) from error
                row_count += 1
    connection.commit()
    return row_count


def load_mongo_archives(
    *,
    archive_paths: Iterable[Path] | None = None,
    archive_date: date | None = None,
) -> int:
    paths = (
        list(archive_paths)
        if archive_paths is not None
        else discover_archive_paths(archive_date=archive_date)
    )
    if not paths:
        date_description = archive_date.isoformat() if archive_date else "any date"
        raise FileNotFoundError(
            f"No MongoDB archive files found for {date_description}."
        )

    connection = create_postgres_connection()
    records_read = 0
    records_loaded = 0
    records_rejected = 0
    load_run_id = create_load_run(
        connection,
        pipeline_name="load_mongo_archive_to_postgres",
        source_type="MONGO_ARCHIVE",
        source_name="raw_archive/mongo",
        metadata={
            "archive_date": archive_date.isoformat() if archive_date else None,
            "file_count": len(paths),
        },
    )

    try:
        for path in paths:
            collection_name = archive_collection_name(path)
            file_history_id = create_file_history(
                connection,
                load_run_id=load_run_id,
                path=path,
            )
            try:
                row_count = load_archive_file(
                    connection,
                    path=path,
                    collection_name=collection_name,
                )
            except Exception as error:
                connection.rollback()
                records_rejected += 1
                finish_file_history(
                    connection,
                    file_history_id=file_history_id,
                    status="FAILED",
                    row_count=None,
                    metadata={"collection": collection_name},
                )
                record_load_error(
                    connection,
                    load_run_id=load_run_id,
                    error_stage="LOAD_MONGO_ARCHIVE",
                    error_message=str(error),
                    source_file_name=path.name,
                    raw_payload={
                        "file_path": project_relative_path(path),
                        "collection": collection_name,
                    },
                )
                raise

            records_read += row_count
            records_loaded += row_count
            finish_file_history(
                connection,
                file_history_id=file_history_id,
                status="LOADED",
                row_count=row_count,
                metadata={"collection": collection_name},
            )
            LOGGER.info(
                "Loaded %s records from %s into raw.%s",
                row_count,
                path,
                MONGO_TABLES[collection_name],
            )

        finish_load_run(
            connection,
            load_run_id=load_run_id,
            status="SUCCEEDED",
            records_read=records_read,
            records_loaded=records_loaded,
            records_rejected=records_rejected,
        )
    except Exception as error:
        finish_load_run(
            connection,
            load_run_id=load_run_id,
            status="FAILED",
            records_read=records_read,
            records_loaded=records_loaded,
            records_rejected=records_rejected,
            error_message=str(error),
        )
        raise
    finally:
        connection.close()

    return records_loaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load MongoDB JSONL archives into PostgreSQL raw tables.",
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        help="Load only archive files in the specified YYYY-MM-DD partition.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    try:
        record_count = load_mongo_archives(archive_date=args.date)
    except Exception:
        LOGGER.exception("MongoDB archive load failed")
        return 1

    LOGGER.info("MongoDB archive load completed with %s records", record_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
