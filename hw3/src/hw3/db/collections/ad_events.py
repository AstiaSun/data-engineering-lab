from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar

from pymongo import DESCENDING

from .abstract import BaseCollection

if TYPE_CHECKING:
    import pandas as pd


class AdEventCollection(BaseCollection):
    COLLECTION_NAME: ClassVar[str] = "events"

    def create_from_stream(self, stream: Iterator["pd.DataFrame"]):
        super().create_from_stream(stream=stream)
        print("Creating indexes for Events...")
        # Indexes below are created for the purpose of this homework.
        # In production such operation should be performed after evaluation of
        # impact on write operations. But since here we upload data only once,
        # it's OK from my perspective to do it.
        self.collection.create_index("CampaignID")
        self.collection.create_index("UserID")
        self.collection.create_index(
            [("UserID", 1), ("CampaignID", 1), ("WasClicked", 1)]
        )

    def get_interactions(
        self, user_id: int, *, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        """retrieves all ad interactions for a specific user"""
        return (
            self.collection.find({"UserID": user_id}, {"_id": 0}).limit(limit).to_list()
        )

    def get_last_user_sessions(
        self, user_id: int, *, session_duration_minutes: int = 30, limit: int = 5
    ) -> list:
        """retrieves a user’s last 5 ad sessions with timestamps and click behavior.

        :param user_id: UserID
        :param session_duration_minutes: the duration of a web session, 30 min by default
        :param limit: number of last sessions to return, 5 by default
        """
        match_user_stage = {"$match": {"UserID": user_id}}
        sort_by_timestamp_stage = {"$sort": {"Timestamp": 1}}
        shift_timestamp_stage = {
            "$setWindowFields": {
                "partitionBy": "$UserID",
                "sortBy": {"Timestamp": 1},
                "output": {
                    "PrevTimestamp": {"$shift": {"output": "$Timestamp", "by": -1}}
                },
            }
        }
        calculate_time_gaps_stage = {
            "$addFields": {
                "GapMinutes": {
                    "$divide": [
                        {"$subtract": ["$Timestamp", "$PrevTimestamp"]},
                        1000 * 60,
                    ]
                }
            }
        }
        determine_sessions_stage = {
            "$set": {
                "IsNewSession": {"$gte": ["$GapMinutes", session_duration_minutes]}
            }
        }
        create_session_ids_stage = {
            "$setWindowFields": {
                "partitionBy": "$UserID",
                "sortBy": {"Timestamp": 1},
                "output": {
                    "SessionId": {
                        "$sum": {"$cond": ["$IsNewSession", 1, 0]},
                        "window": {"documents": ["unbounded", "current"]},
                    }
                },
            }
        }
        group_by_session_id_stage = {
            "$group": {
                "_id": "$SessionId",
                "SessionStart": {"$min": "$Timestamp"},
                "SessionEnd": {"$max": "$Timestamp"},
                "Clicked": {"$max": {"$cond": ["$WasClicked", 1, 0]}},
                "Impressions": {"$sum": 1},
            }
        }
        sort_by_session_end_stage = {"$sort": {"SessionEnd": -1}}
        return self.collection.aggregate(
            [
                match_user_stage,
                sort_by_timestamp_stage,
                shift_timestamp_stage,
                calculate_time_gaps_stage,
                determine_sessions_stage,
                create_session_ids_stage,
                group_by_session_id_stage,
                sort_by_session_end_stage,
                {"$limit": limit},
            ]
        ).to_list()

    def get_clicks_per_hour_in_24h_for_campaign(
        self, campaign_id: int, to_time: datetime
    ) -> float:
        """retrieves the number of ad clicks per hour for a campaign in the 24 hours time segment

        :param campaign_id: CampaignID
        :param to_time: CPH will be calculated for a time span of [to_time - 24H, to_time]
        :returns average clicks per hour over tha 24 hour time frame
        """
        from_time = to_time - timedelta(hours=24)
        total_clicks = self.collection.count_documents(
            {
                "CampaignID": campaign_id,
                "Timestamp": {"$gte": from_time, "$lte": to_time},
                "WasClicked": True,
            }
        )
        return round(total_clicks / 24, 3)

    def get_clicks_per_hour_in_24h(
        self, campaigns_ids: list[int], to_time: datetime
    ) -> dict[int, float]:
        """calculates clicks per hour for a specific campaign during 24 hours"""
        return {
            campaign_id: self.get_clicks_per_hour_in_24h_for_campaign(
                campaign_id=campaign_id, to_time=to_time
            )
            for campaign_id in campaigns_ids
        }

    def get_users_with_ad_fatigue(self, *, min_views: int = 5) -> list[int]:
        """finds users who have seen the same ad 5+ times but never clicked"""
        # hack to make groupby execute faster
        sort_by_index_stage = {"$sort": {"UserID": 1, "CampaignID": 1, "WasClicked": 1}}
        group_by_user_and_ad_stage = {
            "$group": {
                "_id": {
                    "UserID": "$UserID",
                    "CampaignID": "$CampaignID",
                },
                "Views": {"$sum": 1},
                "Clicked": {"$sum": {"$cond": [{"$eq": ["$WasClicked", True]}, 1, 0]}},
            }
        }
        match_users_stage = {"$match": {"Views": {"$gte": min_views}, "Clicked": 0}}
        group_by_users = {"$group": {"_id": "$_id.UserID"}}
        pipeline = [
            sort_by_index_stage,
            group_by_user_and_ad_stage,
            match_users_stage,
            group_by_users,
        ]
        result = self.collection.aggregate(pipeline, allowDiskUse=True)
        return [group["_id"] for group in result]

    def get_top_ad_categories_for_user(self, user_id: int, limit: int = 3) -> list[str]:
        """retrieves a user’s top 3 most engaged ad categories based on past clicks"""
        match_clicked_events_stage = {"$match": {"UserID": user_id, "WasClicked": True}}
        lookup_campaign_stage = {
            "$lookup": {
                "from": "Campaigns",
                "localField": "CampaignID",
                "foreignField": "CampaignID",
                "as": "related_campaign",
            }
        }
        unwind_stage = {"$unwind": "$related_campaign"}
        group_by_campaign_target_category_stage = {
            "$group": {
                "_id": "$related_campaign.TargetingCriteria.Category",
                "category_click_count": {"$sum": 1},
            }
        }

        pipeline = [
            match_clicked_events_stage,
            lookup_campaign_stage,
            unwind_stage,
            group_by_campaign_target_category_stage,
            {"$sort": {"_id": DESCENDING}},
            {"$limit": limit},
        ]
        result = self.collection.aggregate(pipeline)
        return [ad_category["_id"] for ad_category in result]
