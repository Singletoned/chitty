# Stack

- Python ≥ 3.12, packaged with `uv`; installed as `uv tool install chitty`,
  tried with `uvx chitty`.
- On a machine developing Chitty, the global `chitty` is an editable install of
  the main checkout (reverses `TASK-81`, see `TASK-118`). Work happens in
  worktrees, so `main` should always be safe, and if it is not that needs fixing
  anyway. It also means a version bump on `main` needs no release before `chitty`
  can write to this repository. There is no shared virtual environment: each
  checkout has its own `.venv`, used through `make` and `uv run`.
- Runtime: `click`, `pydantic`, `pyyaml`. Frontmatter is split on `---` by
  our own code; YAML is loaded with a loader that resolves every scalar as a
  string. Optional extra `mcp`.
- Dev: `ruff`, `pyright` (strict for `src/`, standard for tests; with
  `types-PyYAML`), `unittest` (stdlib;
  tests write real files in a temp dir and drive the CLI through
  `click.testing.CliRunner`; no filesystem mocking), `prettier` and `mdformat`
  with the plugins above for the round-trip tests.
- `Makefile` following the mate conventions (`.PHONY` targets with `##`
  descriptions): `make check` (ruff + pyright + tests), `make format`.
- Git via `subprocess.run(..., check=True)`. `chitty init --autocommit` first
  requires a clean tree, enables `autocommit`, then commits only setup files it
  changed with `chitty: initialize and enable autocommit`. For task writes when
  `autocommit` is on: `git add -- <paths> && git commit --only -m "chitty: <verb> <ID> <title>\n\nTask: <ID>" -- <paths>`,
  with one `Task: <ID>` trailer for every task the commit writes. All affected
  paths are listed (two for `move`/`archive`, more when `move` rewrites
  references), so nothing the user had staged is swept in. Failure is a loud
  error.
