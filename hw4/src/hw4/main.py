import atexit
import csv
import logging

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, EXEC_PROFILE_DEFAULT, ExecutionProfile, Session
from cassandra.cqlengine import connection
from cassandra.policies import DCAwareRoundRobinPolicy

from .constants import (
    CASSANDRA_HOST,
    CASSANDRA_USER,
    CASSANDRA_PASSWORD,
    DATASET_PATH,
    CASSANDRA_KEYSPACE,
)
from .db import (
    InsertUserImpressions,
    InsertAdvertiserSpending,
    init_tables,
    UpdateAdCampaignClicks,
    UpdateAdCampaignImpressions,
)
from .loader import AdEventsLoader
from .models import AdEventRecord

logger = logging.getLogger(__file__)

cluster = Cluster(
    [CASSANDRA_HOST],
    auth_provider=PlainTextAuthProvider(
        username=CASSANDRA_USER, password=CASSANDRA_PASSWORD
    ),
    execution_profiles={
        EXEC_PROFILE_DEFAULT: ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(), request_timeout=10
        ),
    },
    idle_heartbeat_interval=30,
)
session: Session = cluster.connect(CASSANDRA_KEYSPACE)

connection.set_session(session)


@atexit.register
def shutdown_cassandra():
    session.shutdown()
    cluster.shutdown()


def run_data_ingestion():
    source_path = DATASET_PATH / "ad_events.csv"
    statements = [
        InsertUserImpressions(session),
        InsertAdvertiserSpending(session),
        UpdateAdCampaignClicks(session),
        UpdateAdCampaignImpressions(session),
    ]
    loader = AdEventsLoader(session, statements)
    with source_path.open() as csv_file:
        stream_reader = csv.DictReader(csv_file)
        for row in stream_reader:
            ad_event = AdEventRecord.model_validate(row)
            loader.insert_async(ad_event)
    loader.flush()
    logger.info(
        "Ingestion complete. Success: %d, Failed: %d",
        loader.success_count,
        loader.fail_count,
    )


def main():
    init_tables()
    run_data_ingestion()


if __name__ == "__main__":
    main()
