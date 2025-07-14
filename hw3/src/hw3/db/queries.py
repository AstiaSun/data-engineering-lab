from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pandas as pd
from pymongo import ASCENDING
from pymongo.errors import BulkWriteError

from .collections import ad_events

if TYPE_CHECKING:
    from pymongo.collection import Collection


def create_collection_with_index(collection: "Collection", index: str):
    collection.drop()
    collection.create_index([(index, ASCENDING)], name=index, background=True)


def create_collection_from_stream(
    stream: Iterator[pd.DataFrame], collection: "Collection", index: str
):
    create_collection_with_index(collection=collection, index=index)
    for df_chunk in stream:
        insert_dataframe(collection=collection, df=df_chunk)


def insert_dataframe(collection: "Collection", df: pd.DataFrame):
    if not (records := df.to_dict("records")):
        return
    try:
        collection.insert_many(records, ordered=False)
    except BulkWriteError as bwe:
        print("Bulk write error:", bwe.details)


def get_interactions(user_id: int, *, limit: int = 100000) -> list[dict[str, Any]]:
    return list(ad_events.find({"UserID": user_id}, {"_id": 0}).limit(limit))


def get_the_most_active_users(limit: int = 10) -> list[int]:
    pipeline = [
        {"$group": {"_id": "$UserID", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return [event["_id"] for event in ad_events.aggregate(pipeline)]
