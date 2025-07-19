from .logging import setup_logging
from ..constants import OUTPUT_PATH, KAFKA_HOST, KAFKA_PORT
from .tweet_consumer import TweetConsumer


logger = setup_logging()


KAFKA_CONFIG = {
    "bootstrap.servers": f"{KAFKA_HOST}:{KAFKA_PORT}",
    "group.id": "tweet-consumer-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
}


def main():
    try:
        consumer = TweetConsumer(config=KAFKA_CONFIG, storage_path=OUTPUT_PATH / "storage")
        consumer.consume_tweets()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()