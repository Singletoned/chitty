---
title: Refuse unconfigured priority names on write and report them in `chitty check`
status: doing
labels:
  - needs-minor
depends_on:
  - TASK-10037
  - TASK-10039
parent: TASK-607
created: 2026-11-26
---

## Description

Part of TASK-607. TASK-632 adds the `priorities` setting (`RepoConfig.priorities` in `src/chitty/config.py`, default `["high", "medium", "", "low"]`, with `""` placing tickets that have no priority). TASK-10039 lets `Frontmatter.priority` hold any non-empty name. This ticket makes writes accept only configured names, and makes `chitty check` report the others.

Writes (`src/chitty/store.py`, so the CLI and MCP share them): `Repo.add` and `Repo.edit` refuse a priority that is not a non-empty name in `self.config.priorities`. They raise `ChittyError` `priority '<value>' is not configured; choose from <the names, comma-separated, without "">` and write nothing. On `edit`, `""` still unsets.

- CLI (`src/chitty/cli.py`): `chitty add -p` and `chitty edit -p` become plain text options. Remove `click.Choice(PRIORITIES)` and the `_priority` callback; the store does the check. The `edit` help becomes `A configured priority; '' unsets.`
- MCP (`src/chitty/mcp.py`): the `Priority` type becomes `str`.
- `chitty check` (`src/chitty/check.py`) reports a ticket whose priority is not configured as `<absolute path>: priority '<value>' is not configured`.

Update the existing `-p urgent` error test in `tests/test_cli.py` (search for `urgent`) to expect `priority 'urgent' is not configured; choose from high, medium, low`.

Tests, in `tests/test_priorities_config.py`, with the custom config it already uses (`priorities = ["now", "soon", "", "later"]`):

- `chitty add T -d x -p now` writes `priority: now`. `chitty add T -d x -p high` exits non-zero, with `priority 'high' is not configured; choose from now, soon, later`, and creates no file. On an existing ticket, `chitty edit TASK-1 -p later` succeeds; `-p high` is refused with the same message, and the file stays byte-identical; `-p ""` removes the key.
- `chitty check` reports a hand-written `priority: high` ticket with the message above.
- The MCP add tool accepts `priority="now"` and fails for `"high"` with the configured-name message, asserted as `tests/test_mcp.py` asserts other tool errors.

Record the before-change failures only once TASK-632, TASK-10037 and TASK-10039 are on `main`. Then the `-p` choices are still the built-in names, and nothing checks the configuration. `add -p ""` and `edit -p` with a name are checked by the store; `add -p ""` giving the not-configured message is intended. The MCP change has no existing test to update. `check()` already has `repo.config`.

Out of scope: `src/chitty/import_backlog.py`, which passes priorities through unchanged; `chitty check` then reports them.

## Acceptance Criteria

- [ ] The write, check and MCP tests in `tests/test_priorities_config.py` pass and fail before the change; record the failures in a note
- [ ] The `-p urgent` test expects the new message; `make check` passes

## Plan

Add CLI, check and MCP regression tests and record their pre-fix failures; validate priorities centrally in store writes, report unconfigured values in check, remove frontend restrictions, then format and run make check.

## Notes

Before the fix, the three new priority tests failed: CLI accepted high, check returned success for high, and MCP rejected now as a literal validation error.

## Summary

Store writes validate configured priority names; CLI and MCP accept custom names, and check reports unconfigured values. Added regression tests; make check passes.

## History

- 2026-11-26T11:40:59Z brisk-bronze-adder → planning
- 2026-11-26T11:43:08Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:46:06Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:46:15Z brisk-bronze-adder: changed dependencies, description
- 2026-11-26T11:46:15Z brisk-bronze-adder planning → todo
- 2026-11-26T15:01:18Z intrepid-teal-yellowhammer todo → doing
- 2026-11-26T15:05:33Z intrepid-teal-yellowhammer: wrote the plan
- 2026-11-26T15:06:08Z intrepid-teal-yellowhammer: changed notes
- 2026-11-26T15:10:35Z intrepid-teal-yellowhammer: changed summary
