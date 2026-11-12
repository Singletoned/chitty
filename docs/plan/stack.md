# Stack

- Python ≥ 3.12, packaged with `uv`. Install with `uv tool install chitty`; try
  with `uvx chitty`.
- Runtime: `click`, `pydantic`, `pyyaml`, `markdown-it-py`. Optional extra
  `mcp`.
- Frontmatter is split on `---` by our own code. YAML loads every scalar as a
  string.
- Dev: `ruff`, `pyright` (strict for `src/`, standard for tests), `unittest`
  (real files in temp dirs, CLI through `click.testing.CliRunner`, no
  filesystem mocking), pinned `prettier` and `mdformat` for the round-trip
  tests.
- `Makefile` with mate conventions: `make check` (ruff, pyright, tests),
  `make format`.
- Developing Chitty: the global `chitty` comes from PyPI; each checkout has its
  own `.venv`, and this repository runs `.venv/bin/chitty`, because `main` is
  usually ahead of PyPI.

## Git

- `subprocess.run(..., check=True)`; failures are loud errors.
- `chitty init --autocommit` needs a clean tree, enables `autocommit`, and
  commits only the setup files it changed (`chitty: initialize and enable
  autocommit`).
- With `autocommit` on, each write runs
  `git add -- <paths> && git commit --only -m "chitty: <verb> <ID> <title>" -- <paths>`,
  with a `Task: <ID>` trailer per ticket written. Every affected path is listed
  (two for `move`/`archive`, more when `move` rewrites references), so nothing
  the user staged is swept in.
