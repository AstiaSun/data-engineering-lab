from typing import TYPE_CHECKING

from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

from .constants import MONGODB_URI, DATABASE_NAME, REDIS_HOST, REDIS_PORT


_mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URI)
_db: "AsyncIOMotorDatabase" = _mongo_client[DATABASE_NAME]


def get_db() -> "AsyncIOMotorDatabase":
    return _db


_redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_redis() -> Redis:
    return _redis_client
