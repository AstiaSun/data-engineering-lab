#!/bin/bash

docker-compose build pipeline
docker-compose up -d cassandra

CONTAINER_NAME=$(docker inspect --format '{{.Name}}' $(docker-compose ps -q cassandra) | sed 's|/||')

until [ "$(docker inspect -f '{{.State.Health.Status}}' $CONTAINER_NAME)" == "healthy" ]; do
  echo "Waiting for Cassandra to become healthy..."
  sleep 5
done

docker-compose cp ./cql/setup.cql cassandra:/tmp/setup.cql
docker-compose exec cassandra bash -c 'cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD -f /tmp/setup.cql'

docker-compose run --remove-orphans pipeline
docker-compose down
