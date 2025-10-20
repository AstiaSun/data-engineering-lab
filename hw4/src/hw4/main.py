import argparse
from datetime import datetime
from pathlib import Path

from .constants import MONTH_PARTITION_FORMAT


def ingest_dataset(args):
    from .pipelines import run_data_ingestion

    run_data_ingestion(args.dataset_path)


def update_tables(args):
    from .pipelines import run_tables_update

    run_tables_update(args.month)


def _varified_month_type(value: str):
    datetime.strptime(value, MONTH_PARTITION_FORMAT)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs monthly data ingestion from ad events dataset to Cassandra"
    )
    subparsers = parser.add_subparsers()

    ingestion_group = subparsers.add_parser(
        "ingest", help="Upload ad events from CSV files to DB"
    )
    ingestion_group.add_argument(
        "-d",
        "--dataset_path",
        type=Path,
        help="Path to the directory with CSV files",
        required=False,
        default=Path.cwd() / "dataset",
    )
    ingestion_group.set_defaults(func=ingest_dataset)

    update_group = subparsers.add_parser("update", help="Update periodical tables")
    update_group.add_argument(
        "month", type=_varified_month_type, help="Month in ISO format: yyyy-mm"
    )
    update_group.set_defaults(func=update_tables)

    cli_arguments = parser.parse_args()
    try:
        cli_arguments.func(cli_arguments)
    except argparse.ArgumentError as error:
        parser.error(str(error))
