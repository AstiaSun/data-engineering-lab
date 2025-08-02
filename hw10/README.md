### How to run:

1. Open terminal and change the current working directory to `hw10`
2. Create an `.env` file from `.env.template`
3. Run bash script, it will build image and will start all containers:
    ```commandline
    $ chmod +x run.sh && ./run.sh
    ```
4. Run next commands in separate terminals:
```commandline
docker-compose exec pipeline bash -c 'poetry run python -m src.hw10.data_filtering'
docker-compose exec pipeline bash -c 'poetry run python -m src.hw10.data_loading'
```

To stop the execution, press Ctrl+C on active containers and then run `docker compose down`.

### Comments
Script requires a Unix OS, if you're using Windows, run it from Bash for Windows.

When kafka container will be starting, you may see warnings like:
```commandline
WARN [AdminClient clientId=adminclient-1] Connection to node -1 (localhost/127.0.0.1:9092) could not be established. Node may not be available. (org.apache.kafka.clients.NetworkClient)
```

This means that the container is starting, kafka will be fully up in a minute.

Cassandra needs about 1-2 minutes to become healthy.
