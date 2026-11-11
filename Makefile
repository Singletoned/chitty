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
	uv run unittest-parallel -s tests -t . --level test
	npm test

test: ## run the tests
	uv run unittest-parallel -s tests -t . --level test
	npm test

format: ## format and auto-fix Python code
	uv run ruff check --exit-zero .
	uv run ruff format .

build: ## build the sdist and wheel into dist/
	rm -rf dist
	uv build

release: ## tag and push this version, wait for PyPI, upgrade the global chitty
	@test "$$(git branch --show-current)" = main || { echo "release: not on main" >&2; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo "release: tree is not clean" >&2; exit 1; }
	git fetch origin
	@git merge-base --is-ancestor origin/main HEAD || { echo "release: behind origin/main" >&2; exit 1; }
	version=$$(uv run python scripts/release_version.py) && \
		uv run python -c "from pathlib import Path; import re, sys; p=Path('src/chitty/__init__.py'); p.write_text(re.sub(r'__version__ = \"[^\"]+\"', f'__version__ = \"{sys.argv[1]}\"', p.read_text()))" "$$version" && \
		git add src/chitty/__init__.py && git commit -m "Release $$version" && \
		git tag "v$$version" && \
		if ! git push --atomic origin main "v$$version"; then \
			echo "release: push failed; undo with git tag -d v$$version && git reset --hard HEAD~1" >&2; \
			exit 1; \
		fi && \
		pending="$${XDG_DATA_HOME:-$$HOME/.local/share}/chitty/pending-release" && \
		mkdir -p "$$(dirname "$$pending")" && echo "$$version" > "$$pending" && \
		python3 scripts/watch_release.py "$$version"
