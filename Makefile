.PHONY: help setup test lint format typecheck check demo demo-json sample build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

setup: ## Create the venv and install the package with dev extras
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -e ".[dev]"

test: ## Run the test suite with coverage
	$(BIN)/pytest --cov --cov-report=term-missing

lint: ## Ruff lint + format check
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

format: ## Auto-format with ruff
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

typecheck: ## mypy --strict on the package
	$(BIN)/mypy

check: lint typecheck test ## Everything CI runs

demo: ## Print the inventory three ways
	$(BIN)/e-shop-ltap

demo-json: ## Machine-readable report only
	$(BIN)/e-shop-ltap --json

sample: ## Refresh docs/sample_output.txt from a real run
	$(BIN)/e-shop-ltap > docs/sample_output.txt

build: ## Build sdist + wheel and check them
	$(BIN)/python -m build
	$(BIN)/twine check dist/*

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov build dist src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
