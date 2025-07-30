import os
from pathlib import Path

KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", 9092)

DATASET_PATH = Path(os.getenv("DATASET_PATH"))
