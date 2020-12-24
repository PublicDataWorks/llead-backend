# Development

## Setup
- Install docker
- Install docker-compose 1.27.4
- Create .env file from .env.example template and update environment variables
- `docker-compose build` - build everything needed for local development.
- `docker-compose up web` - start Django development container. It should automatically reload when code change.
