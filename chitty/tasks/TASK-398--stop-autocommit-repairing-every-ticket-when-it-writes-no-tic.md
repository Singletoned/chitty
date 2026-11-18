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

- `_commit` skips the fix-and-validate step when the change has no existing ticket path; it still formats and commits as today.
- `fix(repo, paths: Sequence[Path] | None)`: `None` means every ticket file; a sequence, even empty, means only those. CLI `fix` with no arguments and MCP `fix` with no paths (`src/chitty/mcp.py`, today `paths or []`) pass `None`. Apply the same to `check` if it has the same empty-means-all rule, and say so in the commit.

Tests: real-Git tests in a new `tests/test_commit_empty_paths.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`, `autocommit = true` and `archive = "delete"`. No property: one empty-list case through each caller, each in the criteria.

## Acceptance Criteria

- [ ] With `archive = "delete"`, archiving a `done` ticket that no other ticket references, while another ticket holds `depends_on: [task-1]` in lower case, succeeds, leaves that other file byte-identical and `git status --porcelain` clean; this fails before the change
- [ ] `chitty fix` with no arguments, and MCP `fix` with no paths, still repair that lower-case reference in every ticket; `fix` given an explicitly empty list repairs nothing; `make check` passes

## History

- 2026-11-18T17:54:12Z lively-quartz-crane → backlog
- 2026-11-18T17:55:03Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T17:55:03Z lively-quartz-crane backlog → planning
