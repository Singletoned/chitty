---
title: Stop autocommit repairing every ticket when it writes no ticket file
status: planning
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

A cold read on 2026-11-18 reproduced this in a scratch repository: `chitty archive TASK-3` with `archive = "delete"` rewrote another ticket's lower-case `depends_on: [task-1]` to `TASK-1` and left that file uncommitted. Cause: `Repo._commit` in `src/chitty/store.py` passes `fix` and `check` only the change's existing paths. When the only path was deleted, that list is empty. `fix` in `src/chitty/check.py` then treats an empty list as "every file" (`if problem or (wanted and ...)`) and repairs every ticket, and `check` with an empty list reports every problem in the repository, so a blocking problem elsewhere can also fail the write after the file is already deleted.

Decisions:

- `_commit` skips the fix-and-validate step when `task_paths` (the change's existing paths inside a configured context) is empty; it still formats and commits as today.
- `fix` and `check` keep their empty-means-all rule and signatures: changing them would ripple through the CLI, MCP and about ten existing tests for no gain, since `_commit` is the only caller that can pass an empty list by accident.

Tests: real-Git tests in a new `tests/test_commit_empty_paths.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`, `autocommit = true` and `archive = "delete"`. The other ticket's lower-case reference is written directly to its file and committed before the archive (`chitty add` or `edit` would correct it). No property: the bug is one empty-list case in `_commit`; existing `fix` tests cover path filtering.

## Acceptance Criteria

- [ ] With `archive = "delete"`, archiving a `done` ticket that no other ticket references, while another ticket holds `depends_on: [task-1]` in lower case, succeeds, leaves that other file byte-identical and `git status --porcelain` clean; this fails before the change
- [ ] Regression guard: `chitty fix` with no arguments still repairs that lower-case reference; `tests/test_check.py` passes unchanged; `make check` passes

## History

- 2026-11-18T17:54:12Z lively-quartz-crane → backlog
- 2026-11-18T17:55:03Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T17:55:03Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:20Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:58:15Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:58:15Z lively-quartz-crane cold-read → planning
