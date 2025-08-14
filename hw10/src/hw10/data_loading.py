from pyspark.sql import SparkSession, functions as F, types as T

from .constants import (
    SPARK_MASTER_URL,
    CASSANDRA_HOST,
    CASSANDRA_USER,
    CASSANDRA_PASSWORD,
    KAFKA_BOOTSTRAP_SERVER,
)

APP_NAME = "WikiPagesLoading"

KAFKA_CONSUMER_TOPIC = "processed"
CASSANDRA_KEYSPACE = "wikimedia"

WIKI_PAGE_CREATE_SCHEMA = (
    T.StructType()
    .add("user_id", T.IntegerType())
    .add("domain", T.StringType())
    .add("created_at", T.TimestampType())
    .add("page_title", T.StringType())
)

spark = (
    SparkSession.builder.master(SPARK_MASTER_URL)
    .appName(APP_NAME)
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1",
    )
    .config("spark.executor.memory", "2g")
    .config("spark.cores.max", "2")
    .config("spark.cassandra.connection.host", CASSANDRA_HOST)
    .config("spark.cassandra.connection.port", "9042")
    .config("spark.cassandra.auth.username", CASSANDRA_USER)
    .config("spark.cassandra.auth.password", CASSANDRA_PASSWORD)
    .getOrCreate()
)

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
    .option("subscribe", KAFKA_CONSUMER_TOPIC)
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")
    .load()
)

json_df = (
    raw.selectExpr("CAST(value AS STRING) as json_str")
    .select(F.from_json(F.col("json_str"), WIKI_PAGE_CREATE_SCHEMA).alias("data"))
    .select("data.*")
)

query = (
    json_df.writeStream.format("org.apache.spark.sql.cassandra")
    .option("keyspace", CASSANDRA_KEYSPACE)
    .option("table", "page_create")
    .option("checkpointLocation", f"/tmp/{APP_NAME}")
    .outputMode("append")
    .start()
)
query.awaitTermination()
