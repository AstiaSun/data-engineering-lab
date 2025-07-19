import logging
import random
import signal
import time
from collections.abc import Iterable
from typing import Any

from confluent_kafka import Producer, Message as KafkaMessage

from .models import Tweet


logger = logging.getLogger(__name__)
KAFKA_FLUSH_TIMEOUT = 10 # seconds


def _message_sent_callback(error: Any, message: KafkaMessage):
    if error is not None:
        logger.error(f"Message delivery failed: {error}")
    else:
        logger.debug(f"Message delivered to {message.topic()} [{message.partition()}] @ offset {message.offset()}")

class TweetProducer:
    def __init__(self, config: dict[str, Any]):
        self._active: bool = False
        self._producer = Producer(config)

    def register_shutdown_signals(self):
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        self._active = True

    def handle_shutdown(self, signum: int, _: Any):
        logger.info(f"Shutdown signal={signum} received. Flushing producer...")
        self._active = False
        not_delivered_messages = self._producer.flush(timeout=60)
        if not_delivered_messages:
            logger.error(f"Failed to deliver messages to kafka: number={not_delivered_messages}")


    def _send_message(self, tweet: Tweet):
        self._producer.produce(
            topic="tweets",
            value=tweet.model_dump_json().encode('utf-8'),
            callback=_message_sent_callback
        )

    def send_tweets_from_steam(self, stream: Iterable[Tweet], *, max_batch_size: int = 15):
        while True:
            if not self._active:
                return

            for batch_size, tweet in enumerate(stream):
                try:
                    self._send_message(tweet)
                    time.sleep(random.uniform(0.066, 0.1))
                except BufferError:
                    logger.warning("Producer queue is full, waiting...")
                    self._producer.flush(timeout=KAFKA_FLUSH_TIMEOUT)
                    self._send_message(tweet=tweet)
                    break
                if batch_size >= max_batch_size:
                    break
            else:
                break

            self._producer.poll(timeout=1)
        self._producer.flush(timeout=KAFKA_FLUSH_TIMEOUT)