import csv
import logging.config
from pathlib import Path

from tqdm import tqdm

from .constants import MAX_BATCH_SIZE
from .db.queries import (
    InsertAdvertiserSpending,
    InsertUserClicks,
    InsertUserImpressions,
    UpdateAdCampaignPerformance,
    update_monthly_advertiser_spending,
    update_monthly_advertiser_spending_by_region,
    update_monthly_user_clicks,
)
from .loader import AdEventsLoader
from .models import AdEventRecord

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("pipeline")


def run_data_ingestion(dataset_path: Path):
    source_path = dataset_path / "ad_events.csv"
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    line_count = sum(1 for _ in source_path.open()) - 1
    statements = [
        InsertUserImpressions(),
        InsertUserClicks(),
        InsertAdvertiserSpending(),
        UpdateAdCampaignPerformance(),
    ]
    loader = AdEventsLoader(statements)
    logger.info(f"Starting data ingestion from {source_path.name}")
    with (
        tqdm(
            mininterval=5,
            maxinterval=60,
            desc=f"Loading {source_path.name}",
            total=line_count,
            leave=True,
        ) as progress_bar,
        source_path.open() as csv_file,
    ):
        stream_reader = csv.DictReader(csv_file)
        for row in stream_reader:
            ad_event = AdEventRecord.model_validate(row)
            loader.add_statement_params(ad_event)
            for statement_id, batch_size in enumerate(loader.batch_sizes):
                if batch_size >= MAX_BATCH_SIZE:
                    loader.execute_statement(statement_id)
            progress_bar.update()
        logger.info("Syncing with database...")
        loader.execute_statements()
    logger.info(
        f"Ingestion complete. Success: {loader.success_count}, Failed: {loader.fail_count}"
    )


def run_tables_update(month: str):
    logger.info("Running updates for monthly aggregation tables")
    update_monthly_advertiser_spending(month=month)
    update_monthly_advertiser_spending_by_region(month=month)
    update_monthly_user_clicks(month=month)
    logger.info("Success!")
