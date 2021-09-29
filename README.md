# Development

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop): Development environment, better install latest version.
- (Optional) Pycharm and virtual environment `venv`

## Local run
- Create .env file from .env.example template and update environment variables.
- `bin/dev.sh` - build package inside Docker environment (and for your `venv` as well).
- `docker-compose up` - start Django development container. It should automatically reload when code change.
- `bin/manage.sh` - run any and all of your Django command.

## Useful command
- `bin/manage.sh createsuperuser` create admin user.
- `bin/manage.sh migrate` migrate your database migrations.
- `bin/manage.sh create_initial_app_config` create app configs.
- `./bin/manage.sh create_initial_wrgl_repos` init wrgl repos.

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


## Docs
- [Set up ingress tls](docs/setup-ingress-tls.md)
- [Circleci](docs/circleci.md)
- [Set up logging](docs/logging.md)
