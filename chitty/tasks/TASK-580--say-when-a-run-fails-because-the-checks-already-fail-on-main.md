---
title: Say when a run fails because the checks already fail on `main`
status: planning
created: 2026-11-22
---

## Description

When `chitty run` starts a `todo` ticket, it runs the configured check in the
fresh worktree before any work is done. If `main` itself fails that check,
the ticket goes to `error` with only `check exited with status 2; output in
.chitty/check.log`, and every later ticket does the same, with nothing saying
that `main` is the cause. Seen in taidy, 2026-11-22 (taidy `TASK-21`).

Change: in `_handle_check_failure` (`src/chitty/run.py` around line 1470),
when it is about to call `_record_ticket_error` for a ticket with
`action.mode == "work"`, `selected_status == "todo"` and
`not _branch_has_work(branch_repo.root, branch_repo.config.main_branch)`
(the branch has only ticket-file changes, so its code is `main`'s), append
this sentence to `detail` before recording it:

    ; the branch has no work yet, so `main` fails this check

Other check failures keep today's text. The ticket still goes to `error`
as today. Stopping the run in this case is TASK-583, not this ticket.

Test: in `tests/test_next.py`,
`test_run_check_failure_on_todo_ticket_records_error_on_branch` (around line
1301) is this exact case. Add assertions there that the ticket's Notes on
`main`'s view (`task.section("Notes")`) and the `task-1` branch ticket both
contain "the branch has no work yet, so `main` fails this check". Record that
they fail before the change. The existing `assertIn(detail, ...)` lines keep
passing, since the old text is a prefix.

## Acceptance Criteria

- [ ] A runner check failure on a `todo` ticket whose branch has no work says the branch has no work yet, so `main` fails the check; shown by the new assertions in `test_run_check_failure_on_todo_ticket_records_error_on_branch`, which fail before the change.
- [ ] `make check` passes.

## Notes

Suggestion origin: taidy

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:26Z friendly-jade-stoat: changed notes
- 2026-11-22T13:19:32Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:19:32Z friendly-jade-stoat backlog → planning
