### How to run:

1. Open terminal and change the current working directory to `hw4`
2. Create a .env file from .env.template and set values to env variables
3. Run bash script:
    ```commandline
    $ chmod +x run.sh && ./run.sh
    ```

### Results

1. Cassandra schema design is described in [models.py](src/hw4/db/models.py). 
2. CQL queries to answer key business questions are implemented in [queries.cql](cql/queries.cql).
3. Screenshots with queries results are located in [screenshots](screenshots) directory.


### Comments
Cassandra needs about 1-2 minutes to become healthy.

Data ingestion is taking quite a long time for Ad Events dataset (about 30 min on Apple M3 16G RAM).
Minimal requirements for a successful ingestion of the whole dataset is 12 GB of free RAM.
The User may need to additionally manually increase memory limit for docker. If the execution is failing 
in the middle because of resources, this may be a possible cause.
Due to limited resources, node replication is not enabled (replication factor=1), so some warnings are possible because of that. 

You can connect to cassandra cql by running the following command:
```
$ docker compose exec -it cassandra bash -c 'cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD'
```
