#!/bin/bash

docker-compose build
docker-compose up -d mysql-db
docker-compose up data-loader


# docker exec CONTAINER /usr/bin/mysqldump -u root DATABASE > backup.sql