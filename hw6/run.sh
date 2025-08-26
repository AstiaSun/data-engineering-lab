#!/bin/bash

if test -f .env; then
  docker-compose build pipeline
  docker-compose up -d mongodb
  docker-compose up pipeline
else
  echo "Please, create .env from .env.template"
fi


