#!/usr/bin/env bash

if [ "$1" == "--fix" ]; then
  python -m isort . && python -m black ./ipno/ && python -m flake8 ./ipno
else
  python -m isort . --check-only && \
  python -m black ./ipno/ --check &&
  python -m flake8 ./ipno
fi