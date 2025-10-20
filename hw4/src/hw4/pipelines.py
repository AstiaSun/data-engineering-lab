import atexit
import csv
import logging.config
from pathlib import Path

from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile, Session
from cassandra.cqlengine import connection
from cassandra.policies import (
    DCAwareRoundRobinPolicy,
    DowngradingConsistencyRetryPolicy,
)
from tqdm import tqdm

from .constants import (
    CASSANDRA_HOST,
    CASSANDRA_PASSWORD,
    CASSANDRA_USER,
    MAX_BATCH_SIZE,
)
from .db import (
    InsertAdvertiserSpending,
    InsertUserImpressions,
    UpdateAdCampaignPerformance,
    init_tables,
    update_monthly_advertiser_spending,
    update_monthly_advertiser_spending_by_region,
    update_monthly_user_clicks,
)
from .loader import AdEventsLoader
from .models import AdEventRecord

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("pipeline")

cluster = Cluster(
    [CASSANDRA_HOST],
    auth_provider=PlainTextAuthProvider(
        username=CASSANDRA_USER, password=CASSANDRA_PASSWORD
    ),
    execution_profiles={
        EXEC_PROFILE_DEFAULT: ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            retry_policy=DowngradingConsistencyRetryPolicy(),
            consistency_level=ConsistencyLevel.LOCAL_ONE,
        ),
    },
    idle_heartbeat_interval=30,
    protocol_version=5,
)
session: Session = cluster.connect()
connection.set_session(session)


@atexit.register
def shutdown_cassandra():
    session.shutdown()
    cluster.shutdown()


def run_data_ingestion(dataset_path: Path):
    source_path = dataset_path / "ad_events.csv"
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    init_tables()

    line_count = sum(1 for _ in source_path.open()) - 1
    statements = [
        InsertUserImpressions(session),
        InsertAdvertiserSpending(session),
        UpdateAdCampaignPerformance(session),
    ]
    loader = AdEventsLoader(session, statements)
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
        lines_processed = 0
        for row in stream_reader:
            ad_event = AdEventRecord.model_validate(row)
            loader.save_statement_params(ad_event)
            lines_processed += 1
            if loader.batch_size >= MAX_BATCH_SIZE:
                loader.execute_statements()
                progress_bar.update(lines_processed)
                lines_processed = 0
        loader.execute_statements()
        progress_bar.update(lines_processed)
    logger.info(
        f"Ingestion complete. Success: {loader.success_count}, Failed: {loader.fail_count}"
    )


def run_tables_update(month: str):
    logger.info("Running updates for monthly aggregation tables")
    update_monthly_advertiser_spending(session, month=month)
    update_monthly_advertiser_spending_by_region(session, month=month)
    update_monthly_user_clicks(session, month=month)
    logger.info("Success!")
