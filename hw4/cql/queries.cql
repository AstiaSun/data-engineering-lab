SELECT campaign_name, day, total_clicks * 100.0 / total_impressions AS CTR
FROM ad_events.ad_campaign_performance;

SELECT * FROM ad_events.monthly_advertiser_spending WHERE month='2024-12' LIMIT 5;

SELECT * FROM ad_events.user_impressions WHERE user_id=541198 LIMIT 10;

SELECT * FROM ad_events.monthly_user_clicks WHERE month='2024-12' LIMIT 10;

SELECT * FROM ad_events.monthly_advertiser_spending_by_region
WHERE region = 'Australia' AND month = '2024-12' LIMIT 5;
