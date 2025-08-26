from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import DateType
from pyspark.sql.functions import col, count, month, avg

from .constants import (
    DATASET_PATH,
    MONGODB_URI,
    DATABASE_NAME,
    SPARK_MASTER_URL,
    SPARK_MONGO_CONNECTOR,
)


def pipeline():
    if not Path(DATASET_PATH).exists():
        raise FileNotFoundError(f"{DATASET_PATH=} is not found")

    if not SPARK_MONGO_CONNECTOR:
        raise ValueError(
            "Environment variable SPARK_MONGO_CONNECTOR should be defined."
        )

    spark = (
        SparkSession.builder.master(SPARK_MASTER_URL)
        .appName("AmazonReviewsIngestion")
        .config("spark.jars.packages", SPARK_MONGO_CONNECTOR)
        .config("spark.mongodb.connection.uri", MONGODB_URI)
        .config("spark.mongodb.database", DATABASE_NAME)
        .getOrCreate()
    )

    df = spark.read.csv(DATASET_PATH, header=True)

    critical_columns = ["review_id", "product_id", "star_rating", "review_date"]
    df_clean = df.dropna(subset=critical_columns)

    df_clean = (
        df_clean.withColumn("review_date", col("review_date")
            .cast(DateType()))
    )
    df_clean = df_clean.filter(col("verified_purchase") == "1")

    df_clean.write.format("mongodb").mode("append").option(
        "collection", "reviews"
    ).save()

    reviews_per_product = (
        df_clean.groupBy("product_id")
        .agg(avg("star_rating").alias("average_rating"))
    )

    reviews_per_product.write.format("mongodb").mode("append").option(
        "collection", "reviews_per_product"
    ).save()

    customer_reviews = (
        df_clean.filter(col("verified_purchase") == "1")
        .groupBy("customer_id")
        .agg(count("review_id").alias("total_reviews"))
    )

    customer_reviews.write.format("mongodb").mode("append").option(
        "collection", "customer_reviews"
    ).save()

    monthly_reviews = (
        df_clean.withColumn("month", month("review_date"))
        .groupBy("product_id", "month")
        .agg(count("review_id").alias("monthly_reviews"))
    )

    monthly_reviews.write.format("mongodb").mode("append").option(
        "collection", "monthly_reviews"
    ).save()

    spark.stop()


if __name__ == "__main__":
    pipeline()
