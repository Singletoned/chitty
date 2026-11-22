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
	TEST_TIER=check uv run pytest -q -n auto tests

test: ## run every test, drawing new random property-test examples
	COVERAGE_ROOT=$(CURDIR) TEST_TIER=thorough uv run coverage run -m pytest -q -n auto tests
	uv run coverage combine -q
	uv run coverage report
	uv run coverage html -q -d tmp/coverage

format: ## format and auto-fix Python code
	uv run ruff check --exit-zero .
	uv run ruff format .

build: ## build the sdist and wheel into dist/
	rm -rf dist
	uv build

release: ## release from a temporary worktree, wait for PyPI, install it as the global chitty
	sh scripts/release.sh
