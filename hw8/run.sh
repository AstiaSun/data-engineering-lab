#!/bin/bash

docker-compose build app

docker-compose up -d kafka
docker-compose up app
