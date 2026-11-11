# Agents

Chitty is a markdown-native task tracker. `PLAN.md` is the design; before
changing behaviour, find the relevant section with `grep -n '^## ' PLAN.md` and
read only that section. Update it when a decision changes.

- `make install` once (Python deps including the `mcp` extra, and the pinned
  prettier used by the round-trip tests).
- In this repository run `main`'s Chitty, `.venv/bin/chitty` in the main
  checkout, not the global PyPI `chitty`: `main` is usually ahead of PyPI.
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
- Other agents commit in this checkout at the same time. Stage only the paths
  you changed; never `git add -A` or all of `chitty/`.
- Writing tickets with the human? Cold-read them, as `PLAN.md` describes. If you
  were given a ticket to work on or review, skip this: it is not your step.
- Releases: `make release` tags the version in `src/chitty/__init__.py` and pushes
  it. `.github/workflows/release.yml` checks, builds and publishes to PyPI by
  trusted publishing (environment `pypi`). `make release` then waits for that
  run (`scripts/watch_release.py`): on success it upgrades the global `chitty`;
  on failure it records the failure with `sump capture chitty` and exits
  non-zero.
- Branches never change `__version__` in `src/chitty/__init__.py`; `make release`
  chooses the published bump. Never edit `chitty.toml` or the managed block below,
  or run `chitty init`, on a ticket branch. The main checkout's `chitty` upgrades
  setup files after the work lands (TASK-212).
- Whoever writes, works or reviews a ticket may add `needs-minor` when users must
  notice or act on the change: a new required setting, changed default or
  selection rule, something needing `chitty init` re-run, or a removed command or
  option.

<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->

## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks. When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.
Backticks run commands inside double-quoted shell arguments, so pass such text in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
Run `chitty --help` for the command reference.

A passing review lands through `chitty run`: it fast-forwards `main` only after
merging `main` into the ticket branch and running the configured setup and
checks. Agents started without `chitty run` should first merge `main` into the
branch in its worktree and run the configured checks; after they pass, only
fast-forward `main`. Do not merge or remove branches or worktrees as a reviewer.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

Every review note, whether passing or failing, has one line per criterion below
its `Reviewed:` or `Review failed (<cause>):` first line: `<number>: pass -
<evidence>` or `<number>: fail - <reason>`. Evidence is the command or test that
shows it. A test criterion passes only with evidence that the test fails without
the change.

<!-- chitty:end -->
