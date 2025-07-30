#!/bin/bash

docker-compose build producer

docker-compose up -d kafka
docker-compose up producer
