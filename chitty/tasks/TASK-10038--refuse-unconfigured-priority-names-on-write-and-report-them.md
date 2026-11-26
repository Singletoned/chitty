---
title: Refuse unconfigured priority names on write and report them in `chitty check`
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-10037
parent: TASK-607
created: 2026-11-26
---

## Description

Part of TASK-607. TASK-632 adds the `priorities` setting (`RepoConfig.priorities` in `src/chitty/config.py`, default `["high", "medium", "", "low"]`, with `""` placing tickets that have no priority). TASK-10037 lets `Frontmatter.priority` hold any non-empty name. This ticket makes writes accept only configured names, and makes `chitty check` report the others.

Writes (`src/chitty/store.py`, so the CLI and MCP share them): `Repo.add` and `Repo.edit` refuse a priority that is not a non-empty name in `self.config.priorities`. They raise `ChittyError` `priority '<value>' is not configured; choose from <the names, comma-separated, without "">` and write nothing. On `edit`, `""` still unsets.

- CLI (`src/chitty/cli.py`): `chitty add -p` and `chitty edit -p` become plain text options. Remove `click.Choice(PRIORITIES)` and the `_priority` callback; the store does the check. The `edit` help becomes `A configured priority; '' unsets.`
- MCP (`src/chitty/mcp.py`): the `Priority` type becomes `str`.
- `chitty check` (`src/chitty/check.py`) reports a ticket whose priority is not configured as `<absolute path>: priority '<value>' is not configured`.

Update the existing `-p urgent` error test in `tests/test_cli.py` (search for `urgent`) to expect `priority 'urgent' is not configured; choose from high, medium, low`.

Tests, in `tests/test_priorities_config.py`, with the custom config it already uses (`priorities = ["now", "soon", "", "later"]`):

- `chitty add T -d x -p now` writes `priority: now`. `chitty add T -d x -p high` exits non-zero, with `priority 'high' is not configured; choose from now, soon, later`, and creates no file. On an existing ticket, `chitty edit TASK-1 -p later` succeeds; `-p high` is refused with the same message, and the file stays byte-identical; `-p ""` removes the key.
- `chitty check` reports a hand-written `priority: high` ticket with the message above.
- The MCP add tool accepts `priority="now"` and fails for `"high"` with the configured-name message, asserted as `tests/test_mcp.py` asserts other tool errors.

Each fails on `main` with TASK-10037 landed (there, `-p` choices are the built-in names, and nothing checks the configuration).

Out of scope: `src/chitty/import_backlog.py`, which passes priorities through unchanged; `chitty check` then reports them.

## Acceptance Criteria

- [ ] The write, check and MCP tests in `tests/test_priorities_config.py` pass and fail before the change; record the failures in a note
- [ ] The `-p urgent` test expects the new message; `make check` passes

## History

- 2026-11-26T11:40:59Z brisk-bronze-adder → planning
