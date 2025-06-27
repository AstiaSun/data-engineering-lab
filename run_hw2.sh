#!/bin/bash

unzip hw2/adevents.sql.zip -d hw2

docker-compose --env-file hw2/.env build query-executor

docker-compose --env-file hw2/.env up -d db-monthly

docker-compose --env-file hw2/.env up db-monthly-dump-loader
docker-compose --env-file hw2/.env up query-executor
