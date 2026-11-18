---
title: Stop autocommit repairing every ticket when it writes no ticket file
status: done
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

- [x] With `archive = "delete"`, archiving a `done` ticket that no other ticket references, while another ticket holds `depends_on: [task-1]` in lower case, succeeds, leaves that other file byte-identical and `git status --porcelain` clean; this fails before the change
- [x] Regression guard: `chitty fix` with no arguments still repairs that lower-case reference; `tests/test_check.py` passes unchanged; `make check` passes

## Plan

Add a real-Git regression test in tests/test_commit_empty_paths.py using CliTestCase: configure delete archiving/autocommit, create and commit a done ticket plus a lower-case dependency in another ticket, then verify archive succeeds, preserves the other file byte-for-byte, and leaves Git clean. Run that test first to demonstrate the failure. In Repo._commit, run fix/validation only when task_paths is non-empty; preserve formatting and commit behavior. Add/verify the no-argument chitty fix regression guard, then run focused tests and make check.

## Notes

Reviewed: The implementation preserves empty-means-all for direct fix calls and skips validation only for an empty changed-task set.
1: pass - The archive regression failed against main store.py with unrelated bytes changed from [task-1] to TASK-1; the focused suite passes with the fix and verifies a clean Git status.
2: pass - The no-argument fix guard fails when empty path filtering is mutated to select no files, reporting the lower-case dependency unresolved. The focused commit and check suites passed 16 tests; make check passed 676 tests, Ruff and Pyright.

## Summary

Skipped fix and validation when a change has no existing task paths; formatting and autocommit remain unchanged. Added regression coverage for delete-mode archiving with an unrelated lower-case dependency and for no-argument `chitty fix`. Verified the regression failed before the fix because it rewrote the unrelated ticket. `make check` passed (671 tests); focused `tests.test_commit_empty_paths` and `tests.test_check` passed. No follow-ups.

## History

- 2026-11-18T17:54:12Z lively-quartz-crane → backlog
- 2026-11-18T17:55:03Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T17:55:03Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:20Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:58:15Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:58:15Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:58:17Z lively-quartz-crane planning → todo
- 2026-11-18T23:09:38Z open-quartz-jay todo → doing
- 2026-11-18T23:10:47Z open-quartz-jay: wrote the plan
- 2026-11-18T23:12:42Z open-quartz-jay: ticked acceptance criteria
- 2026-11-18T23:12:49Z open-quartz-jay: changed summary
- 2026-11-18T23:12:49Z open-quartz-jay doing → review
- 2026-11-18T23:15:20Z zesty-amber-eel: changed notes
- 2026-11-18T23:15:20Z zesty-amber-eel review → done
