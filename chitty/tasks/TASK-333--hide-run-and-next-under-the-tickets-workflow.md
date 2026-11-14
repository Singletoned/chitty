---
title: Hide run and next under the tickets workflow
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-330
  - TASK-332
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), hide the runner commands `run` and `next`.

- CLI (`src/chitty/cli.py`): when the current directory is in a Chitty repository whose config loads with workflow `tickets`, `chitty --help` does not list `run` or `next`. Invoking either exits 1 with `chitty <command> needs workflow = "runner" in the Chitty config` on stderr, not click's "No such command". A custom `click.Group` overriding `list_commands` and `get_command` is one way.
- When no config is found, or it fails to load, `--help` lists every command, so help still works while diagnosing a broken config; running `run` or `next` then reports the config error as today.
- MCP (`src/chitty/mcp.py`): in `create_server(start_dir)` (added by TASK-332), register the `next` tool only when the workflow of the config found from `start_dir` is `runner`, or when no config is found. Under `tickets`, the tool list has no `next`.
- Under `runner`, and outside a repository, nothing changes.
- Keep the check in one place in `store.py` or `config.py` (for example `require_runner(config, command)`), so the CLI and MCP cannot diverge.
- No property test: a small fixed set (two workflows, plus no repository, times two commands), each case tested. Tests go in `tests/test_workflow_commands.py`, and set `workflow` explicitly in every config they write.

## Acceptance Criteria

- [ ] In a temp repository with `workflow = "tickets"`, `chitty --help` lists neither `run` nor `next` but still lists `list` and `add`; `chitty run` and `chitty next` each exit 1 with the message naming the command and `workflow = "runner"`. Both fail today.
- [ ] With `workflow = "runner"`, and in a directory with no Chitty config, `chitty --help` lists `run` and `next` and both commands behave as before (existing `tests/test_next.py` passes unchanged).
- [ ] An MCP server started in a `tickets` repository lists no `next` tool, and one started in a `runner` repository lists it; use the existing pattern in `tests/test_mcp.py`. `make check` passes.

## History

- 2026-11-14T18:21:57Z friendly-ginger-adder → planning
- 2026-11-14T18:23:30Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:48Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:29:59Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:47:00Z friendly-ginger-adder: changed description
