"""Remove only the tagged synthetic demo records created by seed_mongo.py."""

from __future__ import annotations

import argparse

from seed_mongo import (
    COLLECTIONS,
    SEED_BATCH,
    create_mongo_client,
    mongo_database_name,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove the tagged synthetic demo batch from MongoDB.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt.",
    )
    return parser.parse_args()


def confirm_reset(database_name: str) -> bool:
    response = input(
        f"Remove demo batch '{SEED_BATCH}' from MongoDB database "
        f"'{database_name}'? [y/N]: "
    )
    return response.strip().lower() in {"y", "yes"}


def main() -> None:
    args = parse_args()
    database_name = mongo_database_name()
    if not args.yes and not confirm_reset(database_name):
        print("Reset cancelled.")
        return

    client = create_mongo_client()
    try:
        client.admin.command("ping")
        database = client[database_name]
        deleted_counts = {
            collection_name: database[collection_name]
            .delete_many({"seed_batch": SEED_BATCH})
            .deleted_count
            for collection_name in COLLECTIONS
        }
    finally:
        client.close()

    print(f"Removed demo batch '{SEED_BATCH}' from '{database_name}':")
    for collection_name, deleted_count in deleted_counts.items():
        print(f"  {collection_name}: {deleted_count}")


if __name__ == "__main__":
    main()
