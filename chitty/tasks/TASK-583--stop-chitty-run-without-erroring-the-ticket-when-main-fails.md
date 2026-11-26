---
title: Stop `chitty run` without erroring the ticket when `main` fails its check
status: doing
created: 2026-11-22
---

## Description

### Why

In echonomicon, 2026-11-25 23:49 to 2026-11-26 00:01, four tickets in a row went to `error` with "check exited with status 2 ... the branch has no work yet, so `main` fails this check". One flaky test on `main` caused all four, and cleaning up meant resetting four statuses and rebasing four branches by hand. The runner knew `main` was failing and still errored each ticket in turn. Decided (the person, 2026-11-26): leave the ticket's status alone, report once, and stop the loop.

### Change

In `_run_check` (`src/chitty/run.py`), the branch that adds "; the branch has no work yet, so `main` fails this check" (check exited non-zero, `work` mode, selected status `todo`, no uncommitted changes, `_branch_has_work` false) no longer calls `_handle_check_failure`. Instead it:

1. Moves the branch copy of the ticket back from `doing` (the runner's claim earlier in `run`) to `todo`, with a note ``Not started: `main` fails the check: <detail>``, using the same `Edit` flags as the claim (`skip_verdicts=True, skip_current_version=True`).
2. Raises a new `MainCheckFailed(ChittyError)`, defined in `run.py`, with the message ``main fails the check (<detail>); fix `main`, then restart `chitty run` ``. Drop the "; the branch has no work yet, so `main` fails this check" suffix from `<detail>` here, since the message says it.

The check runs outside the agent phase's `try`, so nothing records it as a ticket error. `chitty run` then prints `Error: <message>` once and exits 1, which already stops `chitty run --loop` (`loop_step`); the configured error reporter fires as for any run error, which is wanted. The run lock is released on exit, and `next_action` reads `main`'s copy (still `todo`), so the ticket is picked again once `main` is fixed.

### Out of scope

Rerunning a flaky check (TASK-496); timeouts, missing check commands, review tickets, and tickets whose branch has work, which keep today's handling.

## Acceptance Criteria

- [ ] Rewrite `test_run_check_failure_on_todo_ticket_records_error_on_branch` in `tests/test_next.py` (rename it to say the run stops) for the new behaviour, using `self.run_cli("run", exit_code=1)`: stderr contains the message text ``main fails the check`` once; the agent did not start; the branch copy of `TASK-1` has `status: todo` and a note containing ``Not started: `main` fails the check`` and the check detail; it has no `Runner error (check)`; `main` is unchanged; and `next_action` with no modes picks `TASK-1` again. Keep its existing assertions on the check arguments, log and worktree status. Rewrite `test_run_check_failure_on_todo_ticket_with_only_ticket_commits_errors` (around line 1513) the same way, since a branch with only ticket-file commits has no work. Fails without the change.
- [ ] Regression tests: a `todo` ticket whose branch already has a work commit, and `doing`/`error` tickets whose check fails, behave as today (their existing tests in `tests/test_next.py` pass unchanged), and `test_todo_check_timeout` in `tests/test_command_timeout.py` passes unchanged. `make check` passes.

## History

- 2026-11-22T13:19:33Z friendly-jade-stoat → todo
- 2026-11-22T13:19:39Z friendly-jade-stoat todo → backlog
- 2026-11-26T10:56:36Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:22Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:22Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:19:32Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:19:32Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:21:11Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T11:21:11Z calm-ochre-quail cold-read → todo
- 2026-11-26T12:47:15Z friendly-white-raven todo → doing
