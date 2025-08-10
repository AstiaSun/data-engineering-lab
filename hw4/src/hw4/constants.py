import os
from pathlib import Path

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "127.0.0.1")
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PASSWORD = os.environ.get("CASSANDRA_PASSWORD")

CASSANDRA_KEYSPACE = "ad_events"

DATASET_PATH = Path.cwd() / "dataset"
