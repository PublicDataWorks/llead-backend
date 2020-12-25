#!/usr/bin/env bash

if [ -z "$1" ]; then
  docker-compose run web python -m pytest --cov-report term  --cov=ipno ipno/
else
  docker-compose run web python -m pytest $1
fi
