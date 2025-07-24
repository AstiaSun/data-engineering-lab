from fastapi import FastAPI, HTTPException

from .db import events, campaigns, users
from .models import CampaignPerformance, AdvertiserSpending, UserEngagements

app = FastAPI()


@app.get("/campaign/{campaign_id}/performance", response_model=CampaignPerformance)
async def get_campaign_performance(campaign_id: int):
    if not await campaigns.get(campaign_id):
        raise HTTPException(status_code=404, detail=f"{campaign_id=!r} not found")
    total_impressions = await events.get_impressions_for_campaign(campaign_id)
    total_clicks = await events.get_clicks_for_campaign(campaign_id)
    total_ad_spend = await events.get_ad_spend_for_campaign(campaign_id)
    ctr = total_clicks / total_impressions * 100
    return CampaignPerformance(
        campaign_id=campaign_id,
        clicks=total_clicks,
        impressions=total_impressions,
        ctr=ctr,
        ad_spend=total_ad_spend,
    )


@app.get("/advertiser/{advertiser_id}/spending", response_model=AdvertiserSpending)
async def get_advertiser_spending(advertiser_id: str):
    campaigns_ids = await campaigns.get_by_advertiser(advertiser_id)
    if not campaigns_ids:
        raise HTTPException(
            status_code=404, detail=f"No campaigns of {advertiser_id=!r} are found"
        )
    total = await events.get_ad_spend_for_campaigns(campaigns_ids)
    return AdvertiserSpending(advertiser_id=advertiser_id, total_spend=total)


@app.get("/user/{user_id}/engagements", response_model=UserEngagements)
async def get_user_engagements(user_id: int):
    if not await users.get(user_id):
        raise HTTPException(status_code=404, detail=f"{user_id=!r} not found")
    engagements = await events.get_by_user(user_id)
    return UserEngagements(user_id=user_id, engagements=engagements)
