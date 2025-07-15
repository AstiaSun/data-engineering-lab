from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from .db.client import get_db
from .db.collections import AdEventCollection, UsersCollection, CampaignsCollection
from ..constants import CHUNK_SIZE


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
        df_chunk["Timestamp"] = pd.to_datetime(df_chunk["Timestamp"])
        df_chunk.drop(columns=CAMPAIGNS_COLUMNS, inplace=True)
        yield df_chunk


def stream_campaigns(csv_path: Path) -> Iterator[pd.DataFrame]:
    targeting_criteria_header = ("Age", "Category", "Country")

    def _parse_targeting_criteria(line: str) -> dict[str, str]:
        return dict(zip(targeting_criteria_header, line.split(", ")))

    for df_chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
        df_chunk["TargetingCriteria"] = df_chunk["TargetingCriteria"].apply(
            _parse_targeting_criteria
        )
        yield df_chunk


def load_dataset(dataset_path: Path):
    db = get_db()
    print("Loading Users...")
    stream = pd.read_csv(dataset_path / "users.csv", chunksize=CHUNK_SIZE)
    UsersCollection(db).create_from_stream(stream)
    print("Loading Campaigns...")
    stream = stream_campaigns(dataset_path / "campaigns.csv")
    CampaignsCollection(db).create_from_stream(stream)
    print("Loading Events...")
    stream = stream_ad_events(dataset_path / "ad_events.csv")
    AdEventCollection(db).create_from_stream(stream)
    print("Done!")
