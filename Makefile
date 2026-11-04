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
	uv run ruff format --check .
	uv run ruff check --no-fix .
	uv run pyright
	uv run python -m unittest discover -s tests -t .
	npm test

test: ## run the tests
	uv run python -m unittest discover -s tests -t .
	npm test

format: ## format and auto-fix Python code
	uv run ruff check --exit-zero .
	uv run ruff format .

build: ## build the sdist and wheel into dist/
	rm -rf dist
	uv build

release: ## tag this version and push it, so the workflow publishes it to PyPI
	@test "$$(git branch --show-current)" = main || { echo "release: not on main" >&2; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo "release: tree is not clean" >&2; exit 1; }
	git fetch origin
	@git merge-base --is-ancestor origin/main HEAD || { echo "release: behind origin/main" >&2; exit 1; }
	$(MAKE) check </dev/null
	version=$$(sed -n 's/^__version__ = "\(.*\)"$$/\1/p' src/chitty/__init__.py) && \
		pending="$${XDG_DATA_HOME:-$$HOME/.local/share}/chitty/pending-release" && \
		git tag "v$$version" && git push --atomic origin main "v$$version" && \
		mkdir -p "$$(dirname "$$pending")" && echo "$$version" > "$$pending"
