from abc import ABC
from typing import TYPE_CHECKING, Iterator, ClassVar

from pymongo import ASCENDING
from pymongo.errors import BulkWriteError

if TYPE_CHECKING:
    import pandas as pd
    from pymongo.database import Database


class BaseCollection(ABC):
    COLLECTION_NAME: ClassVar[str]

    def __init__(self, db: "Database"):
        self.collection = db[self.COLLECTION_NAME]

    def create_from_stream(self, stream: Iterator["pd.DataFrame"]):
        self.collection.drop()
        self._bulk_insert_from_stream(stream)

    def _create_collection_with_index(self, index: str):
        self.collection.drop()
        self.collection.create_index([(index, ASCENDING)], name=index, unique=True)

    def _bulk_insert_from_stream(self, stream: Iterator["pd.DataFrame"]):
        for df_chunk in stream:
            self._insert_dataframe(df=df_chunk)

    def _insert_dataframe(self, df: "pd.DataFrame"):
        if not (records := df.to_dict("records")):
            return
        try:
            self.collection.insert_many(records, ordered=False)
        except BulkWriteError as bwe:
            print("Bulk write error:", bwe.details)
