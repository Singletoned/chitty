---
title: Explain the `setup` and `autocommit` errors from `chitty run`
status: doing
priority: medium
created: 2026-11-06
---

## Description

`_preflight` in `src/chitty/run.py` fails with ``chitty run` requires setup to be configured`. That doesn't say what `setup` is, where it goes, or what to write. The `autocommit` error next to it has the same problem.

Change both messages to name the config file and give an example, following the `agent_command` error in `_agent_command`:

- ``chitty run` requires `setup` in <file>: the command that installs a new ticket worktree's environment before the agent starts, for example `setup = "make install"``
- ``chitty run` requires `autocommit = true` in <file>, so ticket changes reach every branch; `chitty init --autocommit` sets it`

`<file>` is the file holding this repo's Chitty config, either `chitty.toml` or `pyproject.toml`. Get it from `_config_source` in `src/chitty/config.py`, renamed to `config_source`, with its callers updated. Print the path relative to the repository root. It can't return `None` here, because `Repo.open` already refused a repository without config, so `assert` that with a comment.

Update the expected strings in the `_preflight` table test in `tests/test_next.py` (the `"autocommit"` and `"setup"` entries). For the `pyproject.toml` test, build the config the way `PYPROJECT_CONFIG` in `tests/test_config.py` does. No `__version__` bump: nothing `chitty init` writes changes.

## Acceptance Criteria

- [ ] Tests assert both full messages, with `chitty.toml` as the file. One more test asserts `pyproject.toml` when the config is in `[tool.chitty]`.

## Plan

Rename _config_source to config_source and use it in _preflight to render repository-relative config paths in actionable setup/autocommit errors. Add/update table coverage for chitty.toml and pyproject.toml using the existing PYPROJECT_CONFIG fixture, then run format/check.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-208/1`; 3 tests failed before and passed after; `make check` OK). Outcomes:
- `config_source` returning `None`: fixed, the ticket now says to assert it can't.
- How to build a `pyproject.toml` repo in the test: fixed, the ticket points to `PYPROJECT_CONFIG`.
- No version bump: confirmed, and the ticket now says so.
- `chitty init --autocommit` needs a clean tree: rejected, its own error says so when it applies.
- "Reach every branch": accepted as written. Autocommit is what lets other branches see ticket state.

## History

- 2026-11-06T13:37:47Z youthful-toad → backlog
- 2026-11-06T13:46:44Z youthful-toad: changed description, notes
- 2026-11-06T13:46:44Z youthful-toad backlog → todo
- 2026-11-06T20:36:53Z sunny-kestrel todo → doing
- 2026-11-06T20:37:10Z sunny-kestrel: wrote the plan
