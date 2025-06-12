from typing import Any

from hw1 import DBSession


QUERY_CREATE_TEMP_AD_EVENTS_LATEST = """
CREATE TABLE ad_events_latest AS
SELECT *
FROM AdEvents
WHERE Timestamp >= (STR_TO_DATE('2024-12-30 23:47:12', '%Y-%m-%d %H:%i:%s') - INTERVAL 1 MONTH );
"""

QUERY_DROP_TEMP_AD_EVENTS_LATEST = "DROP TABLE ad_events_latest;"


QUERY_CAMPAIGN_PERFORMANCE = """
WITH total_clicks AS (
    SELECT CampaignID, COUNT(*) as TotalClicks
    FROM ad_events_latest
    WHERE WasClicked = true
    GROUP BY CampaignID
), 
    total_impressions AS (
    SELECT CampaignID, COUNT(*) as TotalImpressions
    FROM ad_events_latest
    GROUP BY CampaignID
)
SELECT total_clicks.CampaignID, (total_clicks.TotalClicks / total_impressions.TotalImpressions * 100) AS ClickThroughRate
FROM (
    total_clicks 
    INNER JOIN total_impressions 
    ON total_clicks.CampaignID = total_impressions.CampaignID
)
ORDER BY ClickThroughRate DESC
LIMIT 5;
"""

QUERY_ADVERTISER_SPENDING = """
SELECT Campaigns.AdvertiserName, SUM(ad_events_latest.AdCost) as TotalSpending
FROM ad_events_latest INNER JOIN Campaigns ON ad_events_latest.CampaignID = Campaigns.CampaignID
GROUP BY Campaigns.AdvertiserName
ORDER BY TotalSpending DESC
LIMIT 5;
"""

QUERY_COST_EFFICIENCY = """
WITH total_ad_spend AS (
    SELECT CampaignID, SUM(AdCost) AS TotalSpending
    FROM ad_events_latest
    GROUP BY CampaignID
),
    total_clicks AS (
    SELECT CampaignID, COUNT(*) AS TotalClicks
    FROM ad_events_latest
    WHERE WasClicked = true
    GROUP BY CampaignID
),
    total_impressions AS (
    SELECT CampaignID, COUNT(*) AS TotalImpressions
    FROM ad_events_latest
    GROUP BY CampaignID
), 
    cost_per_click AS (
    SELECT total_ad_spend.CampaignID, (total_ad_spend.TotalSpending / total_clicks.TotalClicks) AS CPC
    FROM total_ad_spend
    INNER JOIN total_clicks 
    ON total_ad_spend.CampaignID = total_clicks.CampaignID
), cost_per_mille AS (
    SELECT total_ad_spend.CampaignID, (total_ad_spend.TotalSpending / total_impressions.TotalImpressions * 1000) AS CPM
    FROM total_ad_spend
    INNER JOIN total_impressions 
    ON total_ad_spend.CampaignID = total_impressions.CampaignID
),
    campaign_cpc_cpm AS (
    SELECT cost_per_click.CampaignID, cost_per_click.CPC, cost_per_mille.CPM
    FROM cost_per_click
    INNER JOIN cost_per_mille
    ON cost_per_click.CampaignID = cost_per_mille.CampaignID
)
SELECT Campaigns.TargetLocation, AVG(campaign_cpc_cpm.CPC) AS AVG_CPC, AVG(campaign_cpc_cpm.CPM) AS AVG_CPM
FROM campaign_cpc_cpm
INNER JOIN Campaigns
ON campaign_cpc_cpm.CampaignID = Campaigns.CampaignID
GROUP BY Campaigns.TargetLocation
ORDER BY AVG_CPC, AVG_CPM DESC;
"""

QUERY_REGIONAL_ANALYSIS = """
SELECT Users.Location, SUM(AdRevenue) AS TotalRevenue
FROM ad_events_latest
INNER JOIN Users
ON ad_events_latest.UserID = Users.UserID
GROUP BY Users.Location
ORDER BY TotalRevenue DESC;
"""

QUERY_USER_ENGAGEMENT = """
SELECT UserID, COUNT(*) AS TotalClicks
FROM ad_events_latest
WHERE WasClicked = true
GROUP BY UserID
ORDER BY TotalClicks DESC
LIMIT 10;
"""

QUERY_BUDGET_CONSUMPTION = """
WITH total_ad_spend AS (
    SELECT CampaignID, SUM(AdCost) AS TotalSpending
    FROM ad_events_latest
    GROUP BY CampaignID
)
SELECT Campaigns.CampaignID, total_ad_spend.TotalSpending, Campaigns.Budget
FROM total_ad_spend
INNER JOIN Campaigns
ON total_ad_spend.CampaignID = Campaigns.CampaignID
WHERE total_ad_spend.TotalSpending > (Campaigns.Budget * 0.8);
"""

QUERY_DEVICE_PERFORMANCE_COMPARISON = """
WITH total_clicks AS (
    SELECT Device, COUNT(*) as TotalClicks
    FROM ad_events_latest
    WHERE WasClicked = true
    GROUP BY Device
), 
    total_impressions AS (
    SELECT Device, COUNT(*) as TotalImpressions
    FROM ad_events_latest
    GROUP BY Device
)
SELECT total_clicks.Device, (total_clicks.TotalClicks / total_impressions.TotalImpressions * 100) AS ClickThroughRate
FROM (
    total_clicks 
    INNER JOIN total_impressions 
    ON total_clicks.Device = total_impressions.Device
)
"""

def report(result: Any):
    if not result:
        print("empty")
    else:
        header = "\t| ".join(result.keys())
        print(header)
        print("-" * len(header))
        print("\n".join(
            "\t| ".join(map(str, row)) for row in result)
        )
        print("-" * len(header) + "\n")


QUERIES = {
    "CAMPAIGN_PERFORMANCE" : QUERY_CAMPAIGN_PERFORMANCE,
    "COST_EFFICIENCY" : QUERY_COST_EFFICIENCY,
    "ADVERTISER_SPENDING" : QUERY_ADVERTISER_SPENDING,
    "REGIONAL_ANALYSIS" : QUERY_REGIONAL_ANALYSIS,
    "USER_ENGAGEMENT": QUERY_USER_ENGAGEMENT,
    "BUDGET_CONSUMPTION": QUERY_BUDGET_CONSUMPTION,
    "DEVICE_PERFORMANCE_COMPARISON": QUERY_DEVICE_PERFORMANCE_COMPARISON,
}

def execute_queries():
    with DBSession() as db:
        db.execute(QUERY_CREATE_TEMP_AD_EVENTS_LATEST)
        for query_name, query in QUERIES.items():
            print(query_name)
            result = db.execute(query)
            report(result)
        db.execute(QUERY_DROP_TEMP_AD_EVENTS_LATEST)



if __name__ == "__main__":
    execute_queries()
