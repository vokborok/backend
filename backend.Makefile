define BACKEND_HELP
Available backend <target>:
	backend/init           - Initialize the environment for local development

	Migrations:
	backend/gen_auto_migration - Generate auto migration based on SQLModel definitions
	backend/gen_migration      - Generate empty migration
	backend/migrate            - Run migrations
	backend/migrate/test       - Run migrations for test environment
	backend/rollback           - Rollback last migration

	Tests:
	backend/test               - Run tests

	Code quality:
	backend/lint              - Run Ruff linter
	backend/lint-fix          - Run Ruff linter with auto-fix
	backend/typecheck         - Run Mypy type checker
	backend/check             - Run all code quality checks

	Other:
	backend/bash               - Run bash in container

endef
export BACKEND_HELP

backend/help:
	@echo "$$BACKEND_HELP"

# env
backend/init:
	test -f backend/.env.secret || cp backend/.env.secret.example backend/.env.secret && \
	test -d backend/.venv || mkdir -p backend/.venv

# DB migrations
backend/gen_auto_migration:
	docker compose run --rm backend alembic revision --autogenerate -m "$(name)"

backend/gen_migration:
	docker compose run --rm backend alembic revision -m "$(name)"

backend/migrate:
	docker compose run --rm backend alembic upgrade head

backend/migrate/test:
	docker compose --profile test run --rm backend-test alembic upgrade head

backend/rollback:
	docker compose run --rm backend alembic downgrade -1

# tests
backend/test:
	docker compose --profile test run --rm backend-test pytest

backend/bash:
	docker compose run --rm backend bash

# code quality
backend/lint:
	docker compose run --rm backend ruff check .
	docker compose run --rm backend ruff format --check .

backend/lint-fix:
	docker compose run --rm backend ruff format .
	docker compose run --rm backend ruff check --fix .

backend/typecheck:
	docker compose run --rm backend mypy app

backend/check: backend/lint backend/typecheck
