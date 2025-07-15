#!/bin/bash

unzip adevents.sql.zip -d .

docker-compose build query-executor

docker-compose up -d database
docker-compose up database-dump-loader query-executor
