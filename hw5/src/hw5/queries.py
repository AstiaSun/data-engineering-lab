from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorCollection


async def get_ad_spend_for_campaign(
    events: "AsyncIOMotorCollection", campaign_id: int
) -> float:
    result = await events.aggregate(
        [
            {"$match": {"CampaignID": campaign_id}},
            {"$group": {"_id": "", "total": {"$sum": "$AdCost"}}},
        ]
    ).to_list(length=1)
    return result[0]["total"] if result else 0.0


async def get_ad_spend_for_campaigns(
    events: "AsyncIOMotorCollection", campaigns: list[dict[str, Any]]
) -> float:
    campaigns_ids = [campaign["CampaignID"] for campaign in campaigns]
    result = await events.aggregate(
        [
            {"$match": {"CampaignID": {"$in": campaigns_ids}}},
            {"$group": {"_id": "", "total": {"$sum": "$AdCost"}}},
        ]
    ).to_list(length=1)
    return result[0]["total"] if result else 0.0
