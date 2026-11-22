---
title: Say when a run fails because the checks already fail on `main`
status: done
created: 2026-11-22
---

## Description

When `chitty run` starts a `todo` ticket, it runs the configured check in the
fresh worktree before any work is done. If `main` itself fails that check,
the ticket goes to `error` with only `check exited with status 2; output in
.chitty/check.log`, and every later ticket does the same, with nothing saying
that `main` is the cause. Seen in taidy, 2026-11-22 (taidy `TASK-21`).

Change: in `_run_check` (`src/chitty/run.py` around line 1458), only on the
non-zero exit path where `detail = f"check exited with status ..."` is built
(not on timeout or a missing command), when `action.mode == "work"`,
`selected_status == "todo"` and
`not _branch_has_work(branch_repo.root, branch_repo.config.main_branch)`
(the branch has only ticket-file changes, so its code is `main`'s), append
this sentence to `detail` before calling `_handle_check_failure`:

    ; the branch has no work yet, so `main` fails this check

Other check failures keep today's text. The ticket still goes to `error`
as today. Stopping the run in this case is TASK-583, not this ticket.

Test: in `tests/test_next.py`,
`test_run_check_failure_on_todo_ticket_records_error_on_branch` (around line
1301) is this exact case. Add assertions there that `task.section("Notes")`
(the test's existing `repo.find(...)` view) and `branch_ticket` (the test's
existing `git show task-1:...` text) both contain "the branch has no work yet, so `main` fails this check". Record that
they fail before the change. The existing `assertIn(detail, ...)` lines keep
passing, since the old text is a prefix.

## Acceptance Criteria

- [x] A runner check failure on a `todo` ticket whose branch has no work says the branch has no work yet, so `main` fails the check; shown by the new assertions in `test_run_check_failure_on_todo_ticket_records_error_on_branch`, which fail before the change.
- [x] `make check` passes.

## Plan

Extend the existing regression test, verify it fails, then annotate the specified nonzero check failure and run the full checks.

## Notes

Suggestion origin: taidy

Cold read: limited to the non-zero exit path (not timeout or missing command); test targets named.

The targeted regression test fails before the fix: the explanation is absent from the recorded Notes.

Reviewed: implementation matches the specified nonzero check path.
1: pass - The targeted test passes in make check. Running the new test against 28527a4e^ failed with AssertionError because the explanation was absent from Notes; the worker also recorded the pre-fix failure.
2: pass - make check reported 1130 tests OK, ruff passed, and pyright reported 0 errors.

## Summary

Added the main-branch check failure explanation and regression assertions. The targeted test failed before the fix; make check passed all 1128 tests.

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:26Z friendly-jade-stoat: changed notes
- 2026-11-22T13:19:32Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:19:32Z friendly-jade-stoat backlog → planning
- 2026-11-22T13:21:10Z friendly-jade-stoat: changed description, notes
- 2026-11-22T13:21:10Z friendly-jade-stoat planning → todo
- 2026-11-22T15:45:35Z quick-ebony-lapwing todo → doing
- 2026-11-22T15:49:26Z quick-ebony-lapwing: wrote the plan
- 2026-11-22T15:49:56Z quick-ebony-lapwing: changed notes
- 2026-11-22T15:53:11Z quick-ebony-lapwing: changed summary
- 2026-11-22T15:57:05Z quick-ebony-lapwing doing → review
- 2026-11-22T16:05:07Z able-zinc-zander: changed notes; ticked acceptance criteria
- 2026-11-22T16:05:07Z able-zinc-zander review → done
