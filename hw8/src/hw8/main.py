import csv
import socket
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from .tweet_admin_client import TweetAdminClient
from .tweet_producer import TweetProducer
from .logging import setup_logging
from .models import Tweet
from ..constants import KAFKA_HOST, KAFKA_PORT, DATASET_PATH


logger = setup_logging()

KAFKA_CONFIG = {
    "bootstrap.servers": f"{KAFKA_HOST}:{KAFKA_PORT}",
    "client.id": socket.gethostname(),
}


def produce_tweets_from_file(csv_path: Path) -> Iterator[Tweet]:
    with csv_path.open() as file_stream:
        reader = csv.DictReader(file_stream)
        for row_count, record in enumerate(reader, start=1):
            try:
                yield Tweet.model_validate(record)
            except ValidationError as e:
                logger.exception(e, extra={"row_count": row_count})
                continue


def setup_kafka():
    TweetAdminClient(config=KAFKA_CONFIG).create_topics()


def produce_messages():
    producer = TweetProducer(config=KAFKA_CONFIG)
    producer.register_shutdown_signals()

    review_stream = produce_tweets_from_file(DATASET_PATH)
    producer.send_tweets_from_steam(stream=review_stream)


def main():
    try:
        setup_kafka()
        produce_messages()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
