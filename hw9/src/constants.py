import os
from pathlib import Path

KAFKA_HOST = os.environ.get("KAFKA_HOST", "localhost")
KAFKA_PORT = os.environ.get("KAFKA_PORT", 9092)
OUTPUT_PATH = Path.cwd() / Path(os.environ["OUTPUT_PATH"])
