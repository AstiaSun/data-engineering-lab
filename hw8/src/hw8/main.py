import csv
import logging
import random
import socket
import time
from collections.abc import Iterator
from pathlib import Path

from confluent_kafka import Producer

from .models import ReviewMessage
from ..constants import KAFKA_HOST, KAFKA_PORT, DATASET_PATH

logger = logging.getLogger(__file__)

config = {
    'bootstrap.servers': f"{KAFKA_HOST}:{KAFKA_PORT}",
    'client.id': socket.gethostname()
}

producer = Producer(config)


def produce_reviews_from_file(csv_path: Path) -> Iterator[ReviewMessage]:
    with csv_path.open() as file_stream:
        reader = csv.DictReader(file_stream)
        for record in reader:
            message = ReviewMessage(
                customer_id=record["customer_id"],
                review_id=record["review_id"],
                message=record["review_body"]
            )
            yield message


def send_messages_to_kafka(stream: Iterator[ReviewMessage], topic: str):
    for message in stream:
        try:
            producer.produce(topic, message.model_dump_json().encode('utf-8'))
            producer.flush()
        except Exception as e:
            logger.exception(e)
        time.sleep(random.uniform(0.066, 0.1))


def main():
    review_stream = produce_reviews_from_file(DATASET_PATH)
    send_messages_to_kafka(review_stream, "reviews")


if __name__ == "__main__":
    main()
