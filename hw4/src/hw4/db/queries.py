import abc
import operator
from collections import defaultdict
from typing import Any, Iterator

from cassandra.cluster import PreparedStatement, ResultSet, Session
from cassandra.concurrent import execute_concurrent_with_args
from cassandra.cqlengine.management import sync_table

from ..constants import CASSANDRA_CONCURRENT_REQUESTS, MONTH_BUCKET_FORMAT
from ..models import AdEventRecord
from .models import (
    AdCampaignPerformance,
    AdvertiserSpending,
    MonthlyAdvertiserSpending,
    MonthlyAdvertiserSpendingByRegion,
    MonthlyUserClicks,
    UserImpressions,
)


def init_tables():
    sync_table(UserImpressions)
    sync_table(AdCampaignPerformance)
    sync_table(AdvertiserSpending)


class QueryHandler(abc.ABC):
    @property
    @abc.abstractmethod
    def statement(self) -> PreparedStatement:
        """prepared insert statement for a corresponding table"""

    @abc.abstractmethod
    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        """returns extracted from input and transformed parameters, used to execute the CQL statement"""


class InsertUserImpressions(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            INSERT INTO {UserImpressions.column_family_name()} 
            (user_id, month_bucket, event_id, event_ts, campaign_name, is_clicked) 
            VALUES (?, ?, ?, ?, ?, ?)
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        return (
            ad_event.user_id,
            ad_event.timestamp.strftime(MONTH_BUCKET_FORMAT),
            ad_event.event_id,
            ad_event.timestamp,
            ad_event.campaign_name,
            ad_event.was_clicked,
        )


class InsertAdvertiserSpending(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            INSERT INTO {AdvertiserSpending.column_family_name()} 
            (advertiser_name, month_bucket, event_ts, event_id, region, ad_cost) 
            VALUES (?, ?, ?, ?, ?, ?)
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        return (
            ad_event.advertiser_name,
            ad_event.timestamp.strftime(MONTH_BUCKET_FORMAT),
            ad_event.timestamp,
            ad_event.event_id,
            ad_event.campaign_targeting_country,
            ad_event.ad_cost,
        )


class UpdateAdCampaignPerformance(QueryHandler):
    def __init__(self, session: Session):
        self._statement = session.prepare(f"""
            UPDATE {AdCampaignPerformance.column_family_name()}
            SET total_clicks = total_clicks + ?, total_impressions = total_impressions + 1
            WHERE campaign_name = ? AND month_bucket = ? AND day = ?;
        """)

    @property
    def statement(self) -> PreparedStatement:
        return self._statement

    def bind_from_event(self, ad_event: AdEventRecord) -> tuple[Any, ...] | None:
        event_date = ad_event.timestamp.date()
        month_bucket = event_date.strftime(MONTH_BUCKET_FORMAT)
        return (
            int(ad_event.was_clicked),
            ad_event.campaign_name,
            month_bucket,
            event_date,
        )


def get_advertisers_spending(session: Session, *, month_bucket: str):
    return session.execute(
        f"SELECT * FROM {AdvertiserSpending.column_family_name()} "
        f"WHERE month_bucket = '{month_bucket}' ALLOW FILTERING"
    )


def update_monthly_advertiser_spending(session: Session, *, month: str):
    """
    Aggregates spending for each advertiser in the specified month.
    Advertisers are sorted in the output table by their total spending
    from the biggest to the smallest.
    """
    sync_table(MonthlyAdvertiserSpending)
    results = get_advertisers_spending(session, month_bucket=month)

    advertiser_spending = _aggregate_spending(results, key=("advertiser_name",))

    sorted_advertisers = sorted(
        advertiser_spending.items(), key=operator.itemgetter(1), reverse=True
    )
    ranked_advertisers = [
        (month, rank, advertiser_name, spending)
        for rank, (advertiser_name,), spending in _rank_sorted_items(sorted_advertisers)
    ]

    monthly_advertiser_spending_statement = session.prepare(f"""
        INSERT INTO {MonthlyAdvertiserSpending.column_family_name()}
        (month, rank, advertiser_name, total_spending)
        VALUES (?, ?, ?, ?)
    """)
    execute_concurrent_with_args(
        session,
        monthly_advertiser_spending_statement,
        ranked_advertisers,
        concurrency=CASSANDRA_CONCURRENT_REQUESTS,
    )


def update_monthly_advertiser_spending_by_region(session: Session, *, month: str):
    """
    Aggregates spending for each advertiser in each region in the specified month.
    Advertisers are sorted in the output table by their total spending
    from the biggest to the smallest for each region.
    """
    sync_table(MonthlyAdvertiserSpendingByRegion)
    results = get_advertisers_spending(session, month_bucket=month)

    advertiser_spending = _aggregate_spending(
        results, key=("advertiser_name", "region")
    )
    advertisers_by_regions = defaultdict(list)
    for (advertiser_name, region), spending in advertiser_spending.items():
        advertisers_by_regions[region].append((advertiser_name, spending))
    for region in advertisers_by_regions:
        advertisers_by_regions[region] = sorted(
            advertisers_by_regions[region], key=operator.itemgetter(1), reverse=True
        )

    statement_params = [
        (region, month, rank, advertiser_name, spending)
        for region, region_spending in advertisers_by_regions.items()
        for rank, advertiser_name, spending in _rank_sorted_items(region_spending)
    ]

    monthly_advertiser_spending_statement = session.prepare(f"""
        INSERT INTO {MonthlyAdvertiserSpendingByRegion.column_family_name()}
        (region, month, rank, advertiser_name, total_spending)
        VALUES (?, ?, ?, ?, ?)
    """)
    execute_concurrent_with_args(
        session,
        monthly_advertiser_spending_statement,
        statement_params,
        concurrency=CASSANDRA_CONCURRENT_REQUESTS,
    )


def update_monthly_user_clicks(session: Session, *, month: str):
    """
    Counts how many times each User clicked on any ad in the specified month.
    Users are sorted from the most active in the output table.
    """
    sync_table(MonthlyUserClicks)
    results = session.execute(
        f"SELECT user_id FROM {UserImpressions.column_family_name()} "
        f"WHERE is_clicked = True AND month_bucket = '{month}' ALLOW FILTERING",
    )
    user_clicks = {}
    for row in results:
        if row["user_id"] not in user_clicks:
            user_clicks[row["user_id"]] = 0
        user_clicks[row["user_id"]] += 1

    sorted_user_clicks = sorted(
        user_clicks.items(), key=operator.itemgetter(1), reverse=True
    )
    statement_params = [
        (month, rank, user_id, clicks)
        for rank, user_id, clicks in _rank_sorted_items(sorted_user_clicks)
    ]

    monthly_user_clicks_statement = session.prepare(f"""
        INSERT INTO {MonthlyUserClicks.column_family_name()}
        (month, rank, user_id, clicks)
        VALUES (?, ?, ?, ?)
    """)
    execute_concurrent_with_args(
        session,
        monthly_user_clicks_statement,
        statement_params,
        concurrency=CASSANDRA_CONCURRENT_REQUESTS,
    )


def _rank_sorted_items(
    items: list[tuple[Any, float]],
) -> Iterator[tuple[int, Any, float]]:
    last_value = -1
    rank = 0
    for key, value in items:
        if value != last_value:
            rank += 1
            last_value = value
        yield rank, key, value


def _aggregate_spending(items: ResultSet, *, key: tuple[str, ...]) -> dict[Any, Any]:
    aggregated = {}
    for row in items:
        _key = tuple(row[key_name] for key_name in key)
        _value = row["ad_cost"]
        if _key not in aggregated:
            aggregated[_key] = _value
        else:
            aggregated[_key] += _value
    return aggregated
