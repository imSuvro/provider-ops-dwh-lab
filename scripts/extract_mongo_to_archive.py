"""Extract configured MongoDB collections into dated JSONL archive files."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from bson import json_util

from etl_common import (
    MONGO_COLLECTIONS,
    RAW_ARCHIVE_ROOT,
    configure_logging,
    create_mongo_client,
    mongo_database_name,
    utc_now,
)


LOGGER = logging.getLogger("extract_mongo")
SOURCE_UPDATED_FIELDS = (
    "source_updated_at",
    "updated_at",
    "status_updated_at",
)


def source_updated_at(document: dict[str, Any]) -> str | None:
    for field_name in SOURCE_UPDATED_FIELDS:
        value = document.get(field_name)
        if isinstance(value, datetime):
            return value.isoformat()
    return None


def archive_record(
    document: dict[str, Any],
    *,
    collection_name: str,
    extracted_at: datetime,
) -> dict[str, Any]:
    raw_doc = json.loads(json_util.dumps(document))
    return {
        "source_id": str(document["_id"]),
        "source_collection": collection_name,
        "extracted_at": extracted_at.isoformat(),
        "source_updated_at": source_updated_at(document),
        "raw_doc": raw_doc,
    }


def extract_collections(
    *,
    archive_date: date,
    collection_names: tuple[str, ...] = MONGO_COLLECTIONS,
    archive_root: Path = RAW_ARCHIVE_ROOT,
) -> list[Path]:
    extracted_at = utc_now()
    archive_paths: list[Path] = []
    client = create_mongo_client()
    try:
        client.admin.command("ping")
        database = client[mongo_database_name()]
        for collection_name in collection_names:
            output_directory = (
                archive_root
                / "mongo"
                / collection_name
                / f"date={archive_date.isoformat()}"
            )
            output_directory.mkdir(parents=True, exist_ok=True)
            output_path = output_directory / "data.jsonl"
            temporary_path = output_directory / "data.jsonl.tmp"

            record_count = 0
            try:
                with temporary_path.open(
                    "w",
                    encoding="utf-8",
                    newline="\n",
                ) as output:
                    cursor = database[collection_name].find({}).sort("_id", 1)
                    for document in cursor:
                        record = archive_record(
                            document,
                            collection_name=collection_name,
                            extracted_at=extracted_at,
                        )
                        output.write(json.dumps(record, separators=(",", ":")))
                        output.write("\n")
                        record_count += 1

                temporary_path.replace(output_path)
            except Exception:
                temporary_path.unlink(missing_ok=True)
                raise
            archive_paths.append(output_path)
            LOGGER.info(
                "Archived %s records from %s to %s",
                record_count,
                collection_name,
                output_path,
            )
    finally:
        client.close()

    return archive_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract MongoDB source collections into dated JSONL files.",
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=utc_now().date(),
        help="Archive partition date in YYYY-MM-DD format (default: today UTC).",
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        choices=MONGO_COLLECTIONS,
        default=list(MONGO_COLLECTIONS),
        help="Collections to extract (default: all configured collections).",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    try:
        paths = extract_collections(
            archive_date=args.date,
            collection_names=tuple(args.collections),
        )
    except Exception:
        LOGGER.exception("MongoDB extraction failed")
        return 1

    LOGGER.info("MongoDB extraction completed with %s archive files", len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
