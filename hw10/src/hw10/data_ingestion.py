import asyncio
import logging.config
import time

import aiohttp
from aiokafka import AIOKafkaProducer

from .constants import WIKIMEDIA_STREAM_URL, KAFKA_BOOTSTRAP_SERVER

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("data-ingestor")


KAFKA_TOPIC = "input"
NEW_MSG_HEADER = "data: "


class MessageProgressReporter:
    def __init__(self, report_interval: int = 10):
        self.ts = time.monotonic()
        self.counter = 0
        self.report_interval = report_interval

    def reset(self):
        self.ts = time.monotonic()
        self.counter = 0

    def record(self):
        self.counter += 1

    def try_report(self):
        if time.monotonic() > self.ts + self.report_interval:
            logger.info(f"Processed {self.counter} messages")
            self.reset()


async def _read_from_stream(
    response: aiohttp.ClientResponse, producer: AIOKafkaProducer
):
    msg_progress = MessageProgressReporter()
    async for raw_message in response.content:
        message = raw_message.decode("utf-8").strip()
        if message.startswith(NEW_MSG_HEADER):
            event = message.removeprefix(NEW_MSG_HEADER)
            try:
                await producer.send(KAFKA_TOPIC, event.encode("utf-8"))
            except Exception:
                logger.exception("Error sending message:")
            msg_progress.record()
        msg_progress.try_report()


async def listen_wiki_stream():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER)
    await producer.start()
    logger.info(f"Connected to kafka on {KAFKA_BOOTSTRAP_SERVER}...")
    async with aiohttp.ClientSession() as session:
        async with session.get(WIKIMEDIA_STREAM_URL) as response:
            if response.status != 200:
                logger.error(f"Failed to connect to wiki stream: {response.status}")
                return
            logger.info("Connected to Wikimedia stream...")
            try:
                await _read_from_stream(response, producer)
            except Exception:
                logger.exception("Data ingestion from wiki stream has failed:")
            finally:
                await producer.stop()


if __name__ == "__main__":
    asyncio.run(listen_wiki_stream())
