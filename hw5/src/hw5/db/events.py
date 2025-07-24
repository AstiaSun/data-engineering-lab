from typing import Any

from .client import db


async def get_impressions_for_campaign(campaign_id: int) -> int:
    return await db.events.count_documents({"CampaignID": campaign_id})


async def get_clicks_for_campaign(campaign_id: int) -> int:
    return await db.events.count_documents(
        {"CampaignID": campaign_id, "WasClicked": True}
    )


async def get_ad_spend_for_campaign(campaign_id: int) -> float:
    result = await db.events.aggregate(
        [
            {"$match": {"CampaignID": campaign_id}},
            {"$group": {"_id": "", "total": {"$sum": "$AdCost"}}},
        ]
    ).to_list()
    return result[0]["total"]


async def get_ad_spend_for_campaigns(campaigns_ids: list[int]) -> float:
    result = await db.events.aggregate(
        [
            {"$match": {"CampaignID": {"$in": campaigns_ids}}},
            {"$group": {"_id": "", "total": {"$sum": "$AdCost"}}},
        ]
    ).to_list()
    return result[0]["total"] if result else 0.0


async def get_by_user(user_id: int) -> list[str]:
    result: list[dict[str, Any]] = await db.events.find(
        {"UserID": user_id}, {"EventID": 1, "_id": 0}
    ).to_list()
    return [document["EventID"] for document in result]
