### How to run:

1. Open terminal and change the current working directory to `hw4`
2. Create a .env file from .env.template and set values to env variables
3. Run bash script:
    ```commandline
    $ chmod +x run.sh && ./run.sh
    ```

### Comments
Cassandra needs about 1-2 minutes to become healthy.

Data ingestion is taking quite a long time for Ad Events dataset (about 1 hour on Apple M3 16G RAM).
Minimal requirements for a successful ingestion of the whole dataset is 12 GB of free RAM.
The User may need to additionally manually increase memory limit for docker. If the execution is failing 
in the middle because of resources, this may be a possible cause.
Due to limited resources, node replication is not enabled (replication factor=1), so some warnings are possible because of that. 

Note, there's no queries that provide the results of data ingestion. 
Please, connect to the cassandra docker and query respective table contents. Example:

```
$ docker compose exec -it cassandra bash 'cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD'
cql> select * from ad_events.ad_campaign_performance limit 10;
cql> select * from ad_events.monthly_advertiser_spending where month = '2024-10' limit 10;
```
