from typing import TYPE_CHECKING

from pymongo import MongoClient

from ...constants import DATABASE_NAME, MONGODB_URI

if TYPE_CHECKING:
    from pymongo.database import Database


def get_db() -> "Database":
    client = MongoClient(MONGODB_URI)
    return client[DATABASE_NAME]
