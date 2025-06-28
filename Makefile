# Mindbridge Development Makefile

.PHONY: help install install-dev test test-cov lint format type-check security-check clean build docker-build docker-up docker-down pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  test           Run tests"
	@echo "  test-cov       Run tests with coverage report"
	@echo "  lint           Run linting (ruff)"
	@echo "  format         Format code (black, ruff)"
	@echo "  type-check     Run type checking (mypy)"
	@echo "  security-check Run security checks (bandit, safety)"
	@echo "  clean          Clean build artifacts"
	@echo "  build          Build package"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-up      Start Docker services"
	@echo "  docker-down    Stop Docker services"
	@echo "  pre-commit     Run pre-commit hooks"

# Installation
install:
	poetry install --only=main

install-dev:
	poetry install --with dev,test
	poetry run pre-commit install

# Testing
test:
	poetry run pytest

test-cov:
	poetry run pytest --cov --cov-report=html --cov-report=term

# Code quality
lint:
	poetry run ruff check src/ tests/

format:
	poetry run black src/ tests/
	poetry run ruff format src/ tests/

type-check:
	poetry run mypy src/

security-check:
	poetry run bandit -r src/
	poetry run safety check

# Quality gates (run all checks)
quality-check: lint type-check security-check
	@echo "All quality checks passed!"

# Build
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	poetry build

# Docker
docker-build:
	docker build -t mindbridge:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development
pre-commit:
	poetry run pre-commit run --all-files

# Database migrations (placeholder for future)
migrate:
	@echo "Database migration commands will be added when implementing R-005"

# Start development server (placeholder for future)
dev:
	@echo "Development server command will be added when implementing R-004"
