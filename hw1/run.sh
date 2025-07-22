#!/bin/bash

docker-compose down

if test -d db; then
  echo "Cleaning up volumes..."
  rm -rf db/
fi

if test -f .env; then
  docker-compose build data-loader

  docker-compose up -d database
  docker-compose run data-loader
  docker-compose down
else
  echo "Please, create .env from .env.template"
fi
