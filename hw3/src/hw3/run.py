from datetime import datetime, timedelta
from pathlib import Path

from ..constants import DATASET_PATH
from .loader import load_dataset
from .db.collections import AdEventCollection, CampaignsCollection
from .db import get_db
from .reporter import CSVReporter


def get_clicks_per_hour_per_campaign_for_advertiser(db, advertiser_name: str, time_now: datetime):
    campaigns = CampaignsCollection(db)
    campaigns_ids = campaigns.get_active_campaigns(
        advertiser_name=advertiser_name,
        from_time=time_now - timedelta(hours=24),
    )
    events = AdEventCollection(db)
    return events.get_clicks_per_hour_in_24h(
        campaigns_ids=campaigns_ids,
        to_time=time_now,
    )


def execute_queries():
    reporter = CSVReporter()
    db = get_db()
    events = AdEventCollection(db)

    user_interactions = events.get_interactions(user_id=399752)
    reporter.report(user_interactions, file_name="1_user_interactions")
    print(user_interactions[:5])

    user_sessions = events.get_last_user_sessions(user_id=399752, limit=5)
    reporter.report(user_sessions, file_name="2_user_sessions")
    print(user_sessions)

    last_24h_cph = get_clicks_per_hour_per_campaign_for_advertiser(
        db=db,
        advertiser_name="Advertiser_1",
        time_now=datetime.fromisoformat("2024-10-29")
    )
    reporter.report(last_24h_cph, file_name="3_clicks_per_campaign", index=[0])
    print(last_24h_cph)

    users_with_fatigue = events.get_users_with_ad_fatigue()
    reporter.report(users_with_fatigue, file_name="4_users_with_fatigue")
    print(users_with_fatigue)

    top_3_categories = events.get_top_ad_categories_for_user(user_id=101187)
    reporter.report(top_3_categories, file_name="5_top_categories")
    print(top_3_categories)


def main():
    load_dataset(dataset_path=Path(DATASET_PATH))
    execute_queries()


if __name__ == "__main__":
    main()
