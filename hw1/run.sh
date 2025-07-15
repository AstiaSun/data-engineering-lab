#!/bin/bash

if test -f .env; then
  docker-compose build data-loader

  docker-compose up -d database
  docker-compose up data-loader
else
  echo "Please, create .env from .env.template"
fi
