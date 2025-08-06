from collections.abc import Iterator
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from pymongo import ASCENDING

from .abstract import BaseCollection

if TYPE_CHECKING:
    import pandas as pd


class CampaignsCollection(BaseCollection):
    COLLECTION_NAME: ClassVar[str] = "Campaigns"

    def create_from_stream(self, stream: Iterator["pd.DataFrame"]):
        super().create_from_stream(stream=stream)
        self.collection.create_index(
            [("CampaignID", ASCENDING)], name="CampaignID", unique=True
        )

    def get_active_campaigns(
        self, advertiser_name: str, from_time: datetime
    ) -> list[int]:
        campaign_filter = {
            "AdvertiserName": advertiser_name,
            "CampaignEndDate": {"$gte": from_time.isoformat()},
        }
        advertiser_campaigns = self.collection.find(campaign_filter, {"CampaignID": 1})
        return [campaign["CampaignID"] for campaign in advertiser_campaigns]
