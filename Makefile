.PHONY: install check test format

install: ## install Python and node dev dependencies
	uv sync
	npm ci

check: ## lint, type-check and run the tests
	uv run ruff format --check .
	uv run ruff check --no-fix .
	uv run pyright
	uv run python -m unittest discover -s tests -t .

test: ## run the tests
	uv run python -m unittest discover -s tests -t .

format: ## format and auto-fix Python code
	uv run ruff check --exit-zero .
	uv run ruff format .
