from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from .db.collections import users, ad_events, campaigns
from .db.queries import create_collection_from_stream
from ..constants import CHUNK_SIZE

if TYPE_CHECKING:
    from pymongo.collection import Collection


CAMPAIGNS_COLUMNS = [
    "AdvertiserName",
    "CampaignName",
    "CampaignStartDate",
    "CampaignEndDate",
    "CampaignTargetingCriteria",
    "CampaignTargetingInterest",
    "CampaignTargetingCountry",
]


def stream_ad_events(csv_path: Path) -> Iterator[pd.DataFrame]:
    for df_chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
        df_chunk["CampaignID"] = (
            df_chunk["CampaignName"].str.split("_").str[1].astype(int)
        )
        df_chunk.drop(columns=CAMPAIGNS_COLUMNS, inplace=True)
        yield df_chunk


def create_events_collection(csv_path: Path):
    stream = stream_ad_events(csv_path)
    create_collection_from_stream(stream=stream, collection=ad_events, index="EventID")


def create_collection_from_csv(collection: "Collection", csv_path: Path, index: str):
    stream = pd.read_csv(csv_path, chunksize=CHUNK_SIZE)
    create_collection_from_stream(stream=stream, collection=collection, index=index)


def load_dataset(dataset_path: Path):
    create_collection_from_csv(
        collection=users, csv_path=dataset_path / "users.csv", index="UserID"
    )
    create_collection_from_csv(
        collection=campaigns,
        csv_path=dataset_path / "campaigns.csv",
        index="CampaignID",
    )
    create_events_collection(dataset_path / "ad_events.csv")
