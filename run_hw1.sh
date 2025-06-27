#!/bin/bash

docker-compose --env-file hw1/.env build mysql-db
docker-compose --env-file hw1/.env build data-loader

docker-compose --env-file hw1/.env up -d mysql-db
docker-compose --env-file hw1/.env up data-loader
