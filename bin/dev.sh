#!/usr/bin/env bash
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build

if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -U pip setuptools
    pip install -r requirements/dev.txt
fi