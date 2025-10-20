#!/bin/bash
set -e

rm -rf ./.volumes

docker-compose build pipeline
docker-compose up -d cassandra

CONTAINER_NAME=$(docker inspect --format '{{.Name}}' $(docker-compose ps -q cassandra) | sed 's|/||')

until [ "$(docker inspect -f '{{.State.Health.Status}}' $CONTAINER_NAME)" == "healthy" ]; do
  echo "Waiting for Cassandra to become healthy..."
  sleep 5
done

docker-compose cp ./cql/setup.cql cassandra:/tmp/setup.cql
docker-compose exec cassandra bash -c 'cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD -f /tmp/setup.cql'

docker-compose run pipeline bash -c "poetry run python -m src.hw4.main ingest -d /data-engineering-lab/dataset"

current_month="2024-12"   # the last month in the dataset
docker-compose run pipeline bash -c "poetry run python -m src.hw4.main update ${current_month}"
docker-compose run pipeline bash -c "poetry run python -m src.hw4.main test_queries --user_id=541198 --month=${current_month} --region=Australia"

docker-compose down
