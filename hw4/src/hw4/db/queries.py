import abc
from typing import Any

from cassandra.cluster import Session, PreparedStatement
from cassandra.cqlengine.management import sync_table

from .models import (
    UserImpressions,
    AdvertiserSpending,
    AdCampaignPerformance,
    MonthlyAdvertiserSpending,
    MonthlyAdvertiserSpendingByRegion,
    MonthlyUserClicks,
)
from ..models import AdEventRecord


def init_tables():
    sync_table(UserImpressions)
    sync_table(AdCampaignPerformance)
    sync_table(AdvertiserSpending)
    sync_table(MonthlyUserClicks)
    sync_table(MonthlyAdvertiserSpending)
    sync_table(MonthlyAdvertiserSpendingByRegion)


class QueryHandler(abc.ABC):
    @property
    @abc.abstractmethod
    def statement(self) -> PreparedStatement: ...

    @abc.abstractmethod
    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None: ...


class InsertUserImpressions(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            INSERT INTO {UserImpressions.__table_name__} (user_id, event_id, event_ts, campaign_name, is_clicked) 
            VALUES (?, ?, ?, ?, ?)
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        return (
            ad_event.user_id,
            ad_event.event_id,
            ad_event.timestamp,
            ad_event.campaign_name,
            ad_event.was_clicked,
        )


class InsertAdvertiserSpending(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            INSERT INTO {AdvertiserSpending.__table_name__} (advertiser_name, event_ts, event_id, region, ad_cost) 
            VALUES (?, ?, ?, ?, ?)
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        return (
            ad_event.advertiser_name,
            ad_event.timestamp,
            ad_event.event_id,
            ad_event.campaign_targeting_country,
            ad_event.ad_cost,
        )


class UpdateAdCampaignClicks(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            UPDATE {AdCampaignPerformance.__table_name__}
            SET total_clicks = total_clicks + 1
            WHERE campaign_name = ? AND day = ?
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        if ad_event.was_clicked:
            return ad_event.campaign_name, ad_event.timestamp.date()
        return None


class UpdateAdCampaignImpressions(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            UPDATE {AdCampaignPerformance.__table_name__}
            SET total_impressions = total_impressions + 1
            WHERE campaign_name = ? AND day = ?
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        return ad_event.campaign_name, ad_event.timestamp.date()
