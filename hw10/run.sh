#!/bin/bash

docker-compose build pipeline

# setup kafka and create kafka topics
docker-compose up -d kafka
docker-compose exec kafka bash -c "kafka-topics.sh --bootstrap-server localhost:9092 --topic input --create --partitions 3 --replication-factor 1"
docker-compose exec kafka bash -c "kafka-topics.sh --bootstrap-server localhost:9092 --topic processed --create --partitions 3 --replication-factor 1"

docker-compose up -d spark spark-worker cassandra

# create tables in cassandra
docker-compose cp ./docker/init_table.sql cassandra:/tmp/init.sql
docker-compose exec cassandra bash -c 'cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD -f /tmp/init.sql'

# run pipeline
docker-compose up pipeline
