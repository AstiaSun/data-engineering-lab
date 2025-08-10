import uuid
from datetime import datetime
from typing_extensions import Any, Annotated

from pydantic import BaseModel, Field, BeforeValidator


def skip_empty_string(value: Any) -> Any | None:
    if isinstance(value, str) and len(value) == 0:
        return None
    return value


class AdEventRecord(BaseModel):
    event_id: uuid.UUID = Field(validation_alias="EventID")
    advertiser_name: str = Field(validation_alias="AdvertiserName")
    campaign_name: str = Field(validation_alias="CampaignName")
    campaign_start_date: datetime = Field(validation_alias="CampaignStartDate")
    campaign_end_date: datetime = Field(validation_alias="CampaignEndDate")
    campaign_targeting_criteria: str = Field(
        validation_alias="CampaignTargetingCriteria"
    )
    campaign_targeting_interest: str = Field(
        validation_alias="CampaignTargetingInterest"
    )
    campaign_targeting_country: str = Field(validation_alias="CampaignTargetingCountry")
    ad_slot_size: str = Field(validation_alias="AdSlotSize")
    user_id: int = Field(validation_alias="UserID")
    device: str = Field(validation_alias="Device")
    location: str = Field(validation_alias="Location")
    timestamp: datetime = Field(validation_alias="Timestamp")
    bid_amount: float = Field(validation_alias="BidAmount")
    ad_cost: float = Field(validation_alias="AdCost")
    was_clicked: bool = Field(validation_alias="WasClicked")
    click_timestamp: Annotated[datetime | None, BeforeValidator(skip_empty_string)] = (
        Field(default=None, validation_alias="ClickTimestamp")
    )
    ad_revenue: float = Field(validation_alias="AdRevenue")
    budget: float = Field(validation_alias="Budget")
    remaining_budget: float = Field(validation_alias="RemainingBudget")

    model_config = {"populate_by_name": True, "extra": "forbid"}
