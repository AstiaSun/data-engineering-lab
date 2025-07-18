#!/bin/bash

if test -f .env; then
  docker-compose build pipeline
  docker-compose up -d mongodb
  docker-compose up pipeline --remove-orphans
else
  echo "Please, create .env from .env.template"
fi


