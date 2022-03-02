# Development

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop): Development environment, better install latest version.
- (Optional) Pycharm and virtual environment `venv`

## Local run
- Create .env file from .env.example template and update environment variables.
- `bin/dev.sh` - build package inside Docker environment (and for your `venv` as well).
- `bin/manage.sh migrate` migrate your database migrations.
- `bin/manage.sh createsuperuser` create admin user.
- `bin/manage.sh init_project_config` create initial project configuration.
- `docker-compose up` - start Django development container. It should automatically reload when code change.

## Useful command
- `bin/manage.sh` - run any and all of your Django command.
- `bin/manage.sh createsuperuser` create admin user.
- `bin/manage.sh migrate` migrate your database migrations.
- `bin/manage.sh init_project_config` create initial project configuration.
- `bin/manage.sh run_daily_tasks` run daily tasks.

## Package install
- Put your packages & version inside [requirements/base.txt](requirements/base.txt) if they're dependencies or [requirements/dev.txt](requirements/dev.txt) if they're dev-dependencies.
- Run `bin/dev.sh` to install them.

## Testing
- Run test `bin/test.sh`
  - Run all tests: `bin/test.sh`
  - Run a test file:  `bin/test.sh file_path`
  - Run a specific test  `bin/test.sh file_path::class_name::function_name`
    - ex: `bin/test.sh ipno/documents/tests/test_views.py::DocumentsViewSetTestCase::test_retrieve`

## Local running with Fluent bit logging:
- Follow the step in local run with option `--logging`: `bin/manage.sh --logging`
- Run `docker-compose -f docker-compose-logging.yml up `

## Automatically push code to `llead-backend` repository
- The pushing code process is performed by `CircleCI` which is setup in `config.yml` file  

## Docs
- [Set up ingress tls](docs/setup-ingress-tls.md)
- [Circleci](docs/circleci.md)
- [Set up logging](docs/logging.md)
