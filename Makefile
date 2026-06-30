.DEFAULT_GOAL := help

DBT_PROJECT_DIR := dbt/provider_ops_dwh
DBT_ARGS := --project-dir $(DBT_PROJECT_DIR) --profiles-dir $(DBT_PROJECT_DIR)

.PHONY: help setup up down seed etl reset ps logs build-tools dbt-deps dbt-debug dbt-run dbt-test

help:
	@echo "Available commands:"
	@echo "  make setup       Create .env from .env.example if needed"
	@echo "  make up          Start PostgreSQL, MongoDB, and Metabase"
	@echo "  make down        Stop the local stack"
	@echo "  make seed        Load the synthetic MongoDB demo records"
	@echo "  make etl         Extract sources and load PostgreSQL raw tables"
	@echo "  make reset       Stop the stack and delete local volumes"
	@echo "  make ps          Show service status"
	@echo "  make logs        Follow service logs"
	@echo "  make build-tools Build the Python/dbt tools image"
	@echo "  make dbt-deps    Install dbt project dependencies"
	@echo "  make dbt-debug   Check dbt's PostgreSQL connection"
	@echo "  make dbt-run     Build dbt staging models"
	@echo "  make dbt-test    Run dbt data tests"

setup:
	@test -f .env || cp .env.example .env

up:
	docker compose up -d postgres mongodb metabase

down:
	docker compose down

seed: build-tools
	docker compose --profile tools run --rm tools python scripts/seed_mongo.py

etl: build-tools
	docker compose --profile tools run --rm tools python scripts/run_etl.py

reset:
	docker compose down --volumes

ps:
	docker compose ps

logs:
	docker compose logs --follow

build-tools:
	docker compose --profile tools build tools

dbt-deps: build-tools
	docker compose --profile tools run --rm tools dbt deps $(DBT_ARGS)

dbt-debug: build-tools
	docker compose --profile tools run --rm tools dbt debug $(DBT_ARGS)

dbt-run: build-tools
	docker compose --profile tools run --rm tools dbt run $(DBT_ARGS)

dbt-test: build-tools
	docker compose --profile tools run --rm tools dbt test $(DBT_ARGS)
