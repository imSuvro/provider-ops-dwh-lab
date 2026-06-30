.DEFAULT_GOAL := help

DBT_PROJECT_DIR := dbt/provider_ops_dwh
DBT_ARGS := --project-dir $(DBT_PROJECT_DIR) --profiles-dir $(DBT_PROJECT_DIR)
DOCKER ?= docker

.PHONY: help setup up down seed etl demo report-locations reset ps logs build-tools dbt-deps dbt-debug dbt-run dbt-test

help:
	@echo "Available commands:"
	@echo "  make setup       Create .env from .env.example if needed"
	@echo "  make up          Start PostgreSQL, MongoDB, and Metabase"
	@echo "  make down        Stop the local stack"
	@echo "  make seed        Load the synthetic MongoDB demo records"
	@echo "  make etl         Extract sources and load PostgreSQL raw tables"
	@echo "  make demo        Run the complete local learning demo"
	@echo "  make report-locations  Print the available report query paths"
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
	$(DOCKER) compose up -d postgres mongodb metabase

down:
	$(DOCKER) compose down

seed: build-tools
	$(DOCKER) compose --profile tools run --rm tools python scripts/seed_mongo.py

etl: build-tools
	$(DOCKER) compose --profile tools run --rm tools python scripts/run_etl.py

demo: setup
	$(DOCKER) compose up -d postgres mongodb metabase
	$(DOCKER) compose --profile tools build tools
	$(DOCKER) compose --profile tools run --rm tools python scripts/seed_mongo.py
	$(DOCKER) compose --profile tools run --rm tools python scripts/run_etl.py
	$(DOCKER) compose --profile tools run --rm tools dbt deps $(DBT_ARGS)
	$(DOCKER) compose --profile tools run --rm tools dbt run $(DBT_ARGS)
	$(DOCKER) compose --profile tools run --rm tools dbt test $(DBT_ARGS)
	@$(MAKE) --no-print-directory report-locations

report-locations:
	@echo "Demo complete. Reporting queries:"
	@echo "  sql/reports/enrollment_funnel_by_customer.sql"
	@echo "  sql/reports/consent_conversion_by_program.sql"
	@echo "  sql/reports/timer_utilization_by_provider.sql"
	@echo "  sql/reports/billable_patient_months.sql"
	@echo "  sql/reports/customer_performance_summary.sql"
	@echo "  sql/reports/data_quality_issues.sql"
	@echo "Dashboard setup guide: docs/metabase_dashboard_guide.md"

reset:
	$(DOCKER) compose down --volumes

ps:
	$(DOCKER) compose ps

logs:
	$(DOCKER) compose logs --follow

build-tools:
	$(DOCKER) compose --profile tools build tools

dbt-deps: build-tools
	$(DOCKER) compose --profile tools run --rm tools dbt deps $(DBT_ARGS)

dbt-debug: build-tools
	$(DOCKER) compose --profile tools run --rm tools dbt debug $(DBT_ARGS)

dbt-run: build-tools
	$(DOCKER) compose --profile tools run --rm tools dbt run $(DBT_ARGS)

dbt-test: build-tools
	$(DOCKER) compose --profile tools run --rm tools dbt test $(DBT_ARGS)
