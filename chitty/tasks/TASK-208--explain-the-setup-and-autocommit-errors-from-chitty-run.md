---
title: Explain the `setup` and `autocommit` errors from `chitty run`
status: backlog
priority: medium
created: 2026-11-06
---

## Description

`_preflight` in `src/chitty/run.py` fails with ``chitty run` requires setup to be configured`. That doesn't say what `setup` is, where it goes, or what to write. The `autocommit` error next to it has the same problem.

Change both messages to name the config file and give an example, following the `agent_command` error in `_agent_command`:

- ``chitty run` requires `setup` in <file>: the command that installs a new ticket worktree's environment before the agent starts, for example `setup = "make install"``
- ``chitty run` requires `autocommit = true` in <file>, so ticket changes reach every branch; `chitty init --autocommit` sets it`

`<file>` is the file holding this repo's Chitty config, either `chitty.toml` or `pyproject.toml`. Get it from `_config_source` in `src/chitty/config.py`, renamed to `config_source`, with its callers updated. Print the path relative to the repository root.

Update the expected strings in the `_preflight` table test in `tests/test_next.py` (the `"autocommit"` and `"setup"` entries).

## Acceptance Criteria

- [ ] Tests assert both full messages, with `chitty.toml` as the file. One more test asserts `pyproject.toml` when the config is in `[tool.chitty]`.

## History

- 2026-11-06T13:37:47Z youthful-toad → backlog
