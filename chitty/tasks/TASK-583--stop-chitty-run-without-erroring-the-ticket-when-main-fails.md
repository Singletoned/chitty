---
title: Stop `chitty run` without erroring the ticket when `main` fails its check
status: cold-read
created: 2026-11-22
---

## Description

### Why

In echonomicon, 2026-11-25 23:49 to 2026-11-26 00:01, four tickets in a row went to `error` with "check exited with status 2 ... the branch has no work yet, so `main` fails this check". One flaky test on `main` caused all four, and cleaning up meant resetting four statuses and rebasing four branches by hand. The runner knew `main` was failing and still errored each ticket in turn. Decided (the person, 2026-11-26): leave the ticket's status alone, report once, and stop the loop.

### Change

In `_run_check` (`src/chitty/run.py`), the branch that adds "; the branch has no work yet, so `main` fails this check" (check exited non-zero, `work` mode, selected status `todo`, no uncommitted changes, `_branch_has_work` false) no longer calls `_handle_check_failure`. Instead it:

1. Moves the branch copy of the ticket back from `doing` (the runner's claim earlier in `run`) to `todo`, with a note ``Not started: `main` fails the check: <detail>``, using the same `Edit` flags as the claim (`skip_verdicts=True, skip_current_version=True`).
2. Raises a new `MainCheckFailed(ChittyError)`, defined in `run.py`, with the message ``main fails the check (<detail>); fix `main`, then restart `chitty run` ``.

`chitty run` then exits 1, which already stops `chitty run --loop` (`loop_step`), and prints the message once. The ticket is picked again once `main` is fixed.

### Out of scope

Rerunning a flaky check (TASK-496); timeouts, missing check commands, review tickets, and tickets whose branch has work, which keep today's handling.

## Acceptance Criteria

- [ ] Rewrite `test_run_check_failure_on_todo_ticket_records_error_on_branch` in `tests/test_next.py` (rename it to say the run stops) for the new behaviour: `chitty run` exits 1 and its output contains the `MainCheckFailed` message once; the agent did not start; the branch copy of `TASK-1` has `status: todo` and a note containing `main` fails the check and the check detail; it has no `Runner error (check)`; `main` is unchanged; and `next_action` (as the test calls it) with no modes picks `TASK-1` again. Keep its existing assertions on the check arguments, log and worktree status. Fails without the change.
- [ ] A ticket in `todo` whose branch already has a work commit, and a `todo` ticket whose check times out, behave as today (the existing tests for these, and for `doing`/`error` tickets whose check fails, pass unchanged as regression tests). `make check` passes.

## History

- 2026-11-22T13:19:33Z friendly-jade-stoat → todo
- 2026-11-22T13:19:39Z friendly-jade-stoat todo → backlog
- 2026-11-26T10:56:36Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:22Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:22Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:19:32Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:19:32Z calm-ochre-quail to-plan → cold-read
