.DEFAULT_GOAL := help

.PHONY: help setup up down reset ps logs build-tools dbt-debug

help:
	@echo "Available commands:"
	@echo "  make setup       Create .env from .env.example if needed"
	@echo "  make up          Start PostgreSQL, MongoDB, and Metabase"
	@echo "  make down        Stop the local stack"
	@echo "  make reset       Stop the stack and delete local volumes"
	@echo "  make ps          Show service status"
	@echo "  make logs        Follow service logs"
	@echo "  make build-tools Build the Python/dbt tools image"
	@echo "  make dbt-debug   Check dbt's PostgreSQL connection"

setup:
	@test -f .env || cp .env.example .env

up:
	docker compose up -d postgres mongodb metabase

down:
	docker compose down

reset:
	docker compose down --volumes

ps:
	docker compose ps

logs:
	docker compose logs --follow

build-tools:
	docker compose --profile tools build tools

dbt-debug:
	docker compose --profile tools run --rm tools dbt debug --project-dir dbt --profiles-dir dbt
