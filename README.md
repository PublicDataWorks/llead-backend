# Development

## Setup
- Install docker
- Install docker-compose 1.27.4
- Create .env file from .env.example template and update environment variables
- `docker-compose build` - build everything needed for local development.
- `docker-compose up web` - start Django development container. It should automatically reload when code change.
- Run test `bin/test.sh`
  - Run all tests: `bin/test.sh`
  - Run a test file:  `bin/test.sh file_path`
  - Run a specific test  `bin/test.sh file_path::class_name::function_name`
    - ex: `bin/test.sh ipno/documents/tests/test_views.py::DocumentsViewSetTestCase::test_retrieve`
- `bin/manage.sh` - run any and all of your Django command.

## Docs
- [Set up ingress tls](docs/setup-ingress-tls.md)
