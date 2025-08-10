from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, Depends

from .queries import get_ad_spend_for_campaign, get_ad_spend_for_campaigns
from .dependencies import get_db, get_redis
from .models import CampaignPerformance, AdvertiserSpending, UserEngagements

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase
    from redis.asyncio import Redis


app = FastAPI()


@app.get("/campaign/{campaign_id}/performance", response_model=CampaignPerformance)
async def get_campaign_performance(
    campaign_id: int,
    db: "AsyncIOMotorDatabase" = Depends(get_db),
    redis_client: "Redis" = Depends(get_redis),
) -> CampaignPerformance:
    cache_key = f"campaign:{campaign_id}:performance"
    if cached := await redis_client.get(cache_key):
        return CampaignPerformance.model_validate_json(cached)

    if not await db.campaigns.find_one({"CampaignID": campaign_id}):
        raise HTTPException(status_code=404, detail=f"{campaign_id=!r} not found")

    total_impressions = await db.events.count_documents({"CampaignID": campaign_id})
    total_clicks = await db.events.count_documents(
        {"CampaignID": campaign_id, "WasClicked": True}
    )
    total_ad_spend = await get_ad_spend_for_campaign(db.events, campaign_id)
    ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions else 0.0
    campaign_performance = CampaignPerformance(
        campaign_id=campaign_id,
        clicks=total_clicks,
        impressions=total_impressions,
        ctr=ctr,
        ad_spend=total_ad_spend,
    )
    await redis_client.set(cache_key, campaign_performance.model_dump_json(), ex=30)
    return campaign_performance


@app.get("/advertiser/{advertiser_id}/spending", response_model=AdvertiserSpending)
async def get_advertiser_spending(
    advertiser_id: str,
    db: "AsyncIOMotorDatabase" = Depends(get_db),
    redis_client: "Redis" = Depends(get_redis),
) -> AdvertiserSpending:
    cache_key = f"advertiser:{advertiser_id}:spending"
    if cached := await redis_client.get(cache_key):
        return AdvertiserSpending.model_validate_json(cached)

    campaigns = await db.campaigns.find(
        {"AdvertiserName": advertiser_id}, {"CampaignID": 1, "_id": 0}
    ).to_list()
    if not campaigns:
        raise HTTPException(
            status_code=404, detail=f"No campaigns of {advertiser_id=!r} are found"
        )

    total_spend = await get_ad_spend_for_campaigns(db.events, campaigns)
    ad_spending = AdvertiserSpending(
        advertiser_id=advertiser_id, total_spend=total_spend
    )
    await redis_client.set(cache_key, ad_spending.model_dump_json(), ex=300)
    return ad_spending


@app.get("/user/{user_id}/engagements", response_model=UserEngagements)
async def get_user_engagements(
    user_id: int,
    db: "AsyncIOMotorDatabase" = Depends(get_db),
) -> UserEngagements:
    if not await db.users.find_one({"UserID": user_id}):
        raise HTTPException(status_code=404, detail=f"{user_id=!r} not found")

    engagements = await db.events.find(
        {"UserID": user_id}, {"EventID": 1, "_id": 0}
    ).to_list()
    return UserEngagements(
        user_id=user_id, engagements=[event["EventID"] for event in engagements]
    )
