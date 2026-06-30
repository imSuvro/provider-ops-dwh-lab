"""Load committed synthetic CSV source files into PostgreSQL raw tables."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Iterable

import psycopg
from psycopg import sql

from etl_common import (
    DATA_INPUT_ROOT,
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


LOGGER = logging.getLogger("load_csv")
Converter = Callable[[str], Any]


@dataclass(frozen=True)
class CsvSource:
    file_name: str
    table_name: str
    id_column: str
    columns: tuple[str, ...]
    converters: dict[str, Converter] = field(default_factory=dict)


def parse_boolean(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected true or false, received {value!r}.")


CSV_SOURCES = (
    CsvSource(
        file_name="vob_files.csv",
        table_name="csv_vob_files",
        id_column="vob_id",
        columns=(
            "vob_id",
            "patient_id",
            "customer_id",
            "payer_name",
            "member_reference",
            "coverage_status",
            "verified_on",
            "program",
            "estimated_copay",
        ),
        converters={
            "verified_on": date.fromisoformat,
            "estimated_copay": Decimal,
        },
    ),
    CsvSource(
        file_name="billing_exports.csv",
        table_name="csv_billing_exports",
        id_column="export_id",
        columns=(
            "export_id",
            "patient_id",
            "customer_id",
            "patient_month",
            "program",
            "billable_candidate",
            "amount",
            "currency",
            "exported_at",
        ),
        converters={
            "patient_month": date.fromisoformat,
            "billable_candidate": parse_boolean,
            "amount": Decimal,
            "exported_at": parse_timestamp,
        },
    ),
    CsvSource(
        file_name="customer_roster_upload.csv",
        table_name="csv_customer_roster_uploads",
        id_column="roster_record_id",
        columns=(
            "roster_record_id",
            "customer_id",
            "patient_id",
            "provider_id",
            "first_name",
            "last_name",
            "date_of_birth",
            "state",
            "phone",
            "program_interest",
            "uploaded_at",
        ),
        converters={
            "date_of_birth": date.fromisoformat,
            "uploaded_at": parse_timestamp,
        },
    ),
)
CSV_SOURCE_BY_NAME = {source.file_name: source for source in CSV_SOURCES}


def convert_csv_row(source: CsvSource, row: dict[str, str]) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for column_name in source.columns:
        raw_value = row.get(column_name)
        if raw_value is None:
            raise ValueError(f"Missing required column {column_name!r}.")
        if raw_value == "":
            converted[column_name] = None
            continue
        converter = source.converters.get(column_name)
        converted[column_name] = converter(raw_value) if converter else raw_value

    if not converted[source.id_column]:
        raise ValueError(f"{source.id_column} must not be empty.")
    return converted


def upsert_csv_row(
    cursor: psycopg.Cursor,
    *,
    source: CsvSource,
    row: dict[str, Any],
    source_file_name: str,
    source_row_number: int,
) -> None:
    update_columns = [
        column_name
        for column_name in source.columns
        if column_name != source.id_column
    ]
    assignments = [
        sql.SQL("{} = %s").format(sql.Identifier(column_name))
        for column_name in update_columns
    ]
    assignments.extend(
        (
            sql.SQL("source_file_name = %s"),
            sql.SQL("source_row_number = %s"),
            sql.SQL("loaded_at = CURRENT_TIMESTAMP"),
        )
    )
    update_statement = sql.SQL(
        "UPDATE raw.{} SET {} WHERE {} = %s"
    ).format(
        sql.Identifier(source.table_name),
        sql.SQL(", ").join(assignments),
        sql.Identifier(source.id_column),
    )
    update_values = [row[column_name] for column_name in update_columns]
    update_values.extend(
        (
            source_file_name,
            source_row_number,
            row[source.id_column],
        )
    )
    cursor.execute(update_statement, update_values)
    if cursor.rowcount > 0:
        return

    insert_columns = list(source.columns) + [
        "source_file_name",
        "source_row_number",
    ]
    insert_statement = sql.SQL(
        "INSERT INTO raw.{} ({}) VALUES ({})"
    ).format(
        sql.Identifier(source.table_name),
        sql.SQL(", ").join(map(sql.Identifier, insert_columns)),
        sql.SQL(", ").join(sql.Placeholder() * len(insert_columns)),
    )
    insert_values = [row[column_name] for column_name in source.columns]
    insert_values.extend((source_file_name, source_row_number))
    cursor.execute(insert_statement, insert_values)


def load_csv_file(
    connection: psycopg.Connection,
    *,
    path: Path,
    source: CsvSource,
) -> int:
    row_count = 0
    with path.open("r", encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        missing_columns = set(source.columns) - set(reader.fieldnames or ())
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{path} is missing columns: {missing}")

        with connection.cursor() as cursor:
            for source_row_number, row in enumerate(reader, start=2):
                try:
                    converted_row = convert_csv_row(source, row)
                    upsert_csv_row(
                        cursor,
                        source=source,
                        row=converted_row,
                        source_file_name=path.name,
                        source_row_number=source_row_number,
                    )
                except Exception as error:
                    raise ValueError(
                        f"{path}:{source_row_number}: {error}"
                    ) from error
                row_count += 1
    connection.commit()
    return row_count


def load_csv_sources(
    *,
    input_directory: Path = DATA_INPUT_ROOT,
    file_names: Iterable[str] | None = None,
) -> int:
    selected_names = (
        list(file_names)
        if file_names is not None
        else [source.file_name for source in CSV_SOURCES]
    )
    unsupported = set(selected_names) - set(CSV_SOURCE_BY_NAME)
    if unsupported:
        raise ValueError(f"Unsupported CSV sources: {sorted(unsupported)}")

    paths = [input_directory / file_name for file_name in selected_names]
    missing_paths = [path for path in paths if not path.is_file()]
    if missing_paths:
        raise FileNotFoundError(
            "Missing CSV source files: "
            + ", ".join(str(path) for path in missing_paths)
        )

    connection = create_postgres_connection()
    records_read = 0
    records_loaded = 0
    records_rejected = 0
    load_run_id = create_load_run(
        connection,
        pipeline_name="load_csv_to_postgres",
        source_type="CSV",
        source_name="data/input",
        metadata={"file_count": len(paths)},
    )

    try:
        for path in paths:
            source = CSV_SOURCE_BY_NAME[path.name]
            file_history_id = create_file_history(
                connection,
                load_run_id=load_run_id,
                path=path,
            )
            try:
                row_count = load_csv_file(
                    connection,
                    path=path,
                    source=source,
                )
            except Exception as error:
                connection.rollback()
                records_rejected += 1
                finish_file_history(
                    connection,
                    file_history_id=file_history_id,
                    status="FAILED",
                    row_count=None,
                    metadata={"table": f"raw.{source.table_name}"},
                )
                record_load_error(
                    connection,
                    load_run_id=load_run_id,
                    error_stage="LOAD_CSV",
                    error_message=str(error),
                    source_file_name=path.name,
                    raw_payload={
                        "file_path": project_relative_path(path),
                        "table": f"raw.{source.table_name}",
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
                metadata={"table": f"raw.{source.table_name}"},
            )
            LOGGER.info(
                "Loaded %s records from %s into raw.%s",
                row_count,
                path,
                source.table_name,
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
        description="Load synthetic CSV source files into PostgreSQL raw tables.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DATA_INPUT_ROOT,
        help="Directory containing the configured CSV sources.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        choices=tuple(CSV_SOURCE_BY_NAME),
        help="CSV files to load (default: all configured source files).",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    try:
        record_count = load_csv_sources(
            input_directory=args.input_dir,
            file_names=args.files,
        )
    except Exception:
        LOGGER.exception("CSV load failed")
        return 1

    LOGGER.info("CSV load completed with %s records", record_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
