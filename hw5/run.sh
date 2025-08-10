# !/bin/bash

if test -f .env; then
  docker-compose build app
  docker-compose up -d
else
  echo "Please, create .env from .env.template"
fi