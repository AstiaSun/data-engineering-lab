import os

WIKIMEDIA_STREAM_URL = "https://stream.wikimedia.org/v2/stream/page-create"

# kafka
KAFKA_HOST = os.environ.get("KAFKA_HOST", "localhost")
KAFKA_BOOTSTRAP_SERVER = f"{KAFKA_HOST}:9092"

# spark
SPARK_MASTER_HOST = os.environ.get("SPARK_MASTER_HOST", "localhost")
SPARK_MASTER_URL = f"spark://{SPARK_MASTER_HOST}:7077"

# cassandra
CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
CASSANDRA_USER = os.environ["CASSANDRA_USER"]
CASSANDRA_PASSWORD = os.environ["CASSANDRA_PASSWORD"]
