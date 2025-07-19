import csv
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from confluent_kafka import Consumer, Message

from .exceptions import FailedMessageException
from .models import Tweet, PartitionKey, TweetByKey

logger = logging.getLogger(__name__)


ENCODING = 'utf-8'


def _try_decode_message(message: Message) -> TweetByKey:
    """decodes, validates and verifies a message and a key"""
    if message.error():
        raise FailedMessageException(message.error())

    raw_tweet = json.loads(message.value().decode(ENCODING))
    tweet = Tweet.model_validate(raw_tweet)
    if message.key():
        raw_key = json.loads(message.key().decode(ENCODING))
        partition_key = PartitionKey.model_validate(raw_key).created_at
    else:
        partition_key = tweet.get_partition_key()
    return TweetByKey(key=partition_key, tweet=tweet)


def _decode_message(message: Message) -> TweetByKey | None:
    """decodes and validates the message, received from the kafka topic
    :param message: message from the kafka topic
    :returns: a pair of key and a message, in case of an error, returns None instead
    """
    try:
        return _try_decode_message(message)
    except Exception as e:
        logger.exception(e, exc_info=True)
    return None


class TweetConsumer:
    def __init__(self, config: dict[str, Any], storage_path: Path):
        """

        :param config: Kafka Consumer config
        :param storage_path: path to directory, where messages should be stored
        """
        self._consumer = Consumer(config)
        self._storage_path = storage_path

    def _export_tweets(self, tweets_by_key: dict[str, list[Tweet]]):
        """writes tweets to CSV files according to their key.
        Tweets with the same key will be written to the same file.

        """
        for key, tweets in tweets_by_key.items():
            file_path = self._storage_path / f"tweet_{key}.csv"
            file_exists = file_path.exists()

            with file_path.open("a", newline="") as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=Tweet.model_fields.keys())
                if not file_exists:
                    csv_writer.writeheader()
                for tweet in tweets:
                    csv_writer.writerow(tweet.model_dump())

    def _consume_tweets(self, *, poll_timeout: int = 1, batch_size: int = 15):
        self._storage_path.mkdir(exist_ok=True)
        while True:
            messages: list[Message] = self._consumer.consume(
                num_messages=batch_size, timeout=poll_timeout
            )
            if not messages:
                continue

            # the majority of the tweets should have the common key,
            # because we use the tweet creation time as a partition key
            tweets_by_key = defaultdict(list)
            for message in messages:
                if (tweet_by_key := _decode_message(message)) is not None:
                    tweets_by_key[tweet_by_key.key].append(tweet_by_key.tweet)

            if tweets_by_key:
                self._export_tweets(tweets_by_key)
                self._consumer.commit(messages[-1])

    def consume_tweets(self, *, poll_timeout: int = 1):
        """indefinitely reads messages from kafka topic and stores them on file system
        :param poll_timeout: how long to wait for a new batch of messages (seconds)
        """
        topic_names = ["tweets"]
        try:
            self._consumer.subscribe(topic_names)
            logger.info(f"Subscribed to topics: {','.join(topic_names)}")
            self._consume_tweets(poll_timeout=poll_timeout)
        finally:
            logger.info("Closing Kafka consumer...")
            self._consumer.close()


