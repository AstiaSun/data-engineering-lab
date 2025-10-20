from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from ..constants import CASSANDRA_KEYSPACE


class AdCampaignPerformance(Model):
    """Used to fetch the CTR per campaign per day"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "ad_campaign_performance"

    campaign_name = columns.Text(min_length=10, max_length=16, partition_key=True)
    month_partition = columns.Text(min_length=7, max_length=7, partition_key=True)
    day = columns.Date(primary_key=True)
    total_clicks = columns.Counter()
    total_impressions = columns.Counter()


class UserImpressions(Model):
    """Used to retrieve the last 10 ads the user saw and whether they were clicked"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "user_impressions"

    user_id = columns.Integer(partition_key=True)

    event_id = columns.UUID(primary_key=True)
    event_ts = columns.DateTime(clustering_order="DESC", primary_key=True)
    month = columns.Text(min_length=7, max_length=7)
    campaign_name = columns.Text(min_length=10, max_length=16)
    is_clicked = columns.Boolean()


class UserClicks(Model):
    """Used to aggregate monthly user clicks"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "user_clicks"

    month_partition = columns.Text(min_length=7, max_length=7, partition_key=True)
    user_id = columns.Integer(primary_key=True)


class AdvertiserSpending(Model):
    """historical spending by advertiser, used to calculate cumulative spending"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "advertiser_spending"

    day_partition = columns.Date(partition_key=True)
    event_ts = columns.DateTime(primary_key=True)
    advertiser_name = columns.Text(min_length=12, max_length=16)
    region = columns.Text(min_length=2, max_length=30)
    ad_cost = columns.Float()


class MonthlyAdvertiserSpending(Model):
    """used to retrieve advertisers by total ad spend in the past 30 days"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "monthly_advertiser_spending"

    month = columns.Text(min_length=7, max_length=7, partition_key=True)
    rank = columns.Integer(primary_key=True)
    advertiser_name = columns.Text(primary_key=True, min_length=12, max_length=16)
    total_spending = columns.Float()


class MonthlyUserClicks(Model):
    """Used to retrieve users with the highest number of ad clicks in the past 30 days"""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "monthly_user_clicks"

    month = columns.Text(min_length=7, max_length=7, partition_key=True)
    rank = columns.Integer(primary_key=True)
    user_id = columns.Integer()
    clicks = columns.Integer()


class MonthlyAdvertiserSpendingByRegion(Model):
    """Used to retrieve advertisers who spent the most in a specific region over the last 30 days."""

    __keyspace__ = CASSANDRA_KEYSPACE
    __table_name__ = "monthly_advertiser_spending_by_region"

    region = columns.Text(min_length=2, max_length=30, partition_key=True)
    month = columns.Text(min_length=7, max_length=7, partition_key=True)
    rank = columns.Integer(primary_key=True)
    advertiser_name = columns.Text(min_length=12, max_length=16)
    total_spending = columns.Float()
