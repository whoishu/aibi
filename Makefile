.PHONY: help install install-dev lint format test test-unit test-integration coverage clean pre-commit run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

lint:  ## Run all linters
	black --check app/ scripts/ examples/ tests/
	isort --check-only app/ scripts/ examples/ tests/
	flake8 app/ scripts/ examples/ tests/
	mypy app/ --ignore-missing-imports

format:  ## Format code with black and isort
	black app/ scripts/ examples/ tests/
	isort app/ scripts/ examples/ tests/

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v -m unit

test-integration:  ## Run integration tests only
	pytest tests/integration/ -v -m integration

coverage:  ## Run tests with coverage report
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ coverage.xml
	rm -rf build/ dist/

run:  ## Start the application
	python app/main.py

docker-up:  ## Start Docker dependencies
	docker-compose up -d

docker-down:  ## Stop Docker dependencies
	docker-compose down

init-data:  ## Initialize sample data
	python scripts/init_data.py

verify:  ## Verify installation
	python scripts/verify_installation.py

security:  ## Run security checks
	safety check --file requirements.txt || true
	bandit -r app/ || true
