import os

DATABASE_NAME = "AdEvents"

MONGODB_USERNAME = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGODB_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")

MONGODB_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:27017/?authSource=admin"

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
