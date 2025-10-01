.PHONY: help install sync format lint check test clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install uv and sync dependencies"
	@echo "  make sync       - Sync dependencies with uv"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Lint code with ruff"
	@echo "  make check      - Run both format and lint checks"
	@echo "  make test       - Run tests with pytest"
	@echo "  make clean      - Remove build artifacts and cache"

install:
	pip install uv
	uv sync --all-extras

sync:
	uv sync --all-extras

format:
	uv run black app/ scripts/ examples/

lint:
	uv run ruff check app/ scripts/ examples/

check: format lint
	@echo "✓ All quality checks passed!"

test:
	uv run pytest tests/ -v

clean:
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
