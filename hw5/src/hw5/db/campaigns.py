from typing import Any

from .client import db


async def get_first():
    return (
        await db.campaigns.find({}, {"_id": 0})
        .sort({"CampaignID": 1})
        .limit(1)
        .to_list(length=1)
    )


async def get(campaign_id: int) -> dict[str, Any]:
    return await db.campaigns.find_one({"CampaignID": campaign_id}, {"_id": 0})


async def get_by_advertiser(advertiser_id: str) -> list[int]:
    result = await db.campaigns.find(
        {"AdvertiserName": advertiser_id}, {"CampaignID": 1, "_id": 0}
    ).to_list()
    return [int(document["CampaignID"]) for document in result]
