from pyspark.sql import SparkSession, functions as F, types as T

from .constants import KAFKA_BOOTSTRAP_SERVER, SPARK_MASTER_URL

APP_NAME = "WikiPagesFiltering"

KAFKA_CONSUMER_TOPIC = "input"
KAFKA_PRODUCER_TOPIC = "processed"

ALLOWED_DOMAINS = ["en.wikipedia.org", "www.wikidata.org", "commons.wikimedia.org"]


WIKI_PAGE_CREATE_INPUT_SCHEMA = T.StructType(
    [
        T.StructField("meta", T.StructType([T.StructField("domain", T.StringType())])),
        T.StructField(
            "performer",
            T.StructType(
                [
                    T.StructField("user_is_bot", T.BooleanType()),
                    T.StructField("user_id", T.IntegerType()),
                ]
            ),
        ),
        T.StructField("dt", T.TimestampType()),
        T.StructField("page_title", T.StringType()),
    ]
)

spark = (
    SparkSession.builder.master(SPARK_MASTER_URL)
    .appName(APP_NAME)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5")
    .config("spark.executor.memory", "2g")
    .config("spark.cores.max", "2")
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
    .select(F.from_json(F.col("json_str"), WIKI_PAGE_CREATE_INPUT_SCHEMA).alias("data"))
    .select("data.*")
)

filtered_df = json_df.filter(
    (F.col("meta.domain").isin(ALLOWED_DOMAINS))
    & (F.col("performer.user_is_bot") == False)
)
output_df = filtered_df.select(
    F.col("performer.user_id").alias("user_id"),
    F.col("meta.domain").alias("domain"),
    F.col("dt").alias("created_at"),
    F.col("page_title"),
)

query = (
    output_df.select(F.to_json(F.struct("*")).alias("value"))
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
    .option("topic", KAFKA_PRODUCER_TOPIC)
    .option("checkpointLocation", f"/tmp/{APP_NAME}")
    .start()
)
query.awaitTermination()
