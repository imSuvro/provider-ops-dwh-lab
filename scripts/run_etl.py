"""Run the local MongoDB extraction and PostgreSQL raw loading workflow."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from etl_common import configure_logging, utc_now
from extract_mongo_to_archive import extract_collections
from load_csv_to_postgres import load_csv_sources
from load_mongo_archive_to_postgres import load_mongo_archives


LOGGER = logging.getLogger("run_etl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract local sources and load PostgreSQL raw tables.",
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=utc_now().date(),
        help="MongoDB archive partition date in YYYY-MM-DD format.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    try:
        LOGGER.info("Starting local ETL for archive date %s", args.date)
        archive_paths = extract_collections(archive_date=args.date)
        mongo_count = load_mongo_archives(
            archive_paths=archive_paths,
            archive_date=args.date,
        )
        csv_count = load_csv_sources()
    except Exception:
        LOGGER.exception("Local ETL failed")
        return 1

    LOGGER.info(
        "Local ETL completed: %s MongoDB records and %s CSV rows loaded",
        mongo_count,
        csv_count,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
