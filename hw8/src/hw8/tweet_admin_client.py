import logging
from concurrent.futures import Future, CancelledError
from typing import Any

from confluent_kafka.admin import ClusterMetadata, AdminClient
from confluent_kafka.cimpl import NewTopic


logger = logging.getLogger(__name__)


class TweetAdminClient:
    def __init__(self, config: dict[str, Any]):
        self._admin_client = AdminClient(config)

    def create_topics(self):
        metadata: ClusterMetadata = self._admin_client.list_topics(timeout=10)
        if "tweets" in metadata.topics:
            logger.info("Topics already exist, skipping...")
            return
        creation_timeout = 10
        topics = [NewTopic("tweets", num_partitions=3, replication_factor=1),]
        futures: dict[str, Future] = self._admin_client.create_topics(topics)
        for topic_name, create_topic_future in futures.items():
            try:
                create_topic_future.result(timeout=creation_timeout)
                logger.info(f"Topic is created: {topic_name}")
            except CancelledError:
                logger.error(f"Failed to create a topic={topic_name}. Task was cancelled.")
            except TimeoutError:
                logger.error(
                    f"Failed to create a topic={topic_name}. Task did not finish in {creation_timeout} seconds"
                )
