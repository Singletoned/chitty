# Agents

Chitty is a markdown-native task tracker. `PLAN.md` is the design; before
changing behaviour, find the relevant section with `grep -n '^## ' PLAN.md` and
read only that section. Update it when a decision changes.

- `make install` once (Python deps including the `mcp` extra, and the pinned
  prettier used by the round-trip tests).
- `make check` (ruff, pyright, unittest, Node tests) before every commit. `make
  format` to fix formatting.
- Tests use `unittest` and write real files in temp dirs; no filesystem
  mocking. Tests that use the inbox must inherit `RepoTestCase`, which assigns
  a temporary `XDG_DATA_HOME` so they never touch the real inbox. The formatter
  tests fail, never skip, if prettier or mdformat is missing.
- Put a ticket's new guide tests in their own file, `tests/test_guide_<topic>.py`,
  not at the end of `TestGuide` in `tests/test_cli.py`, where every guide
  ticket's tests collide.
- `cli.py` and `mcp.py` stay thin: behaviour lives in `store.py` and
  `model.py` so the two front ends cannot diverge.
- Writing tickets with the human? Cold-read them, as `PLAN.md` describes. If you
  were given a ticket to work on or review, skip this: it is not your step.
- Releases: `make release` tags the version in `src/chitty/__init__.py` and pushes
  it. `.github/workflows/release.yml` checks, builds and publishes to PyPI by
  trusted publishing (environment `pypi`).
- Any change that existing repos only pick up by re-running `chitty init`
  (the managed guide block, `chitty.toml` template or upgrades, inbox
  registration) must bump `__version__` in `src/chitty/__init__.py`, at least at patch
  level, in the same change. The version recorded in `chitty.toml` is how
  other repos learn that `init` needs re-running (TASK-52). Bump only
  `__version__`: never edit `chitty.toml` or the managed block below, or run
  `chitty init`, on a ticket branch. The main checkout's `chitty` upgrades
  both after the work lands (TASK-212).

<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->

## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks.
Run `chitty --help` for the command reference.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

<!-- chitty:end -->
