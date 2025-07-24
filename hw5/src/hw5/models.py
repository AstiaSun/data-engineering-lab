from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


class CampaignPerformance(BaseDTO):
    campaign_id: int
    clicks: int
    impressions: int
    ctr: float
    ad_spend: float


class AdvertiserSpending(BaseDTO):
    advertiser_id: str
    total_spend: float


class UserEngagements(BaseDTO):
    user_id: int
    engagements: list[str]
