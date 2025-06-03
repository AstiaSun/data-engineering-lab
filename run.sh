#!/bin/bash

docker-compose build
docker-compose up -d mysql-db
docker-compose up data-loader
