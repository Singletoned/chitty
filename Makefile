.PHONY: install check test format build release

# Keep every checkout self-contained: direnv may export a shared environment,
# but `make` always creates and uses this worktree's disposable `.venv`.
export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv
export VIRTUAL_ENV := $(UV_PROJECT_ENVIRONMENT)
export PATH := $(VIRTUAL_ENV)/bin:$(PATH)

install: ## install Python and node dev dependencies
	uv sync --all-extras
	npm ci

check: ## lint, type-check and run the tests
	! git grep -nE '^(<<<<<<< |>>>>>>> |=======$$)'
	uv run ruff format --check .
	uv run ruff check --no-fix .
	uv run pyright
	TEST_TIER=check uv run unittest-parallel -s tests -t . --level test

test: ## run every test, drawing new random property-test examples
	TEST_TIER=thorough uv run unittest-parallel -s tests -t . --level test

format: ## format and auto-fix Python code
	uv run ruff check --exit-zero .
	uv run ruff format .

build: ## build the sdist and wheel into dist/
	rm -rf dist
	uv build

release: ## release from a temporary worktree, wait for PyPI, install it as the global chitty
	sh scripts/release.sh
