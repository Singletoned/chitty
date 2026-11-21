---
title: Guard provisional renumbering preflight and report bad paths
status: planning
depends_on:
  - TASK-391
parent: TASK-391
created: 2026-11-21
---

## Description

Add explicit rejection paths to the read-only preflight from `TASK-391`. Verify the landed interface before cold-reading this ticket. Before discovery use fresh `git.is_repository` and `git.current_branch`; in Git only `Repo._main_branch()` may proceed. Detached HEAD is off main. Raise new `ProvisionalOffMain(ChittyError)` in `src/chitty/errors.py` saying provisional tickets are renumbered on main. Outside Git retain preflight behavior. Do not call `_prepare_write` or change allocation. Reject any duplicate on-disk ID involving a candidate before the allocator, naming both paths. Keep path-bearing parse errors.

Test using `RepoTestCase` and real Git in `tests/test_provisional_preflight_errors.py`: `git init -b main`, set local author, commit valid `TASK-AAAAAA` and remove and commit `chitty_version` to create stale setup. Test a branch off main and detached HEAD; return to main and separately plant a malformed validly named path and two distinct valid paths carrying the same candidate ID. Snapshot HEAD, index and file bytes after each setup, before the call. These fixed integration cases verify Git state and diagnostic paths. Show that branch/detached and duplicate diagnostics fail on the unguarded preflight; the malformed fixture is a regression guard if it already passes. Run the new tests and `make check`.

## Acceptance Criteria

- [ ] With stale setup and eligible work, a branch off configured main and detached HEAD each raise `ProvisionalOffMain`, before any writes; compare HEAD, index and file bytes.
- [ ] On main, an unparseable ticket or duplicate provisional candidate each refuses the whole plan with the bad path or both duplicate paths respectively, with HEAD, index and files unchanged.

## History

- 2026-11-21T18:44:40Z eager-ginger-adder → backlog
- 2026-11-21T18:45:14Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:45:14Z eager-ginger-adder backlog → planning
