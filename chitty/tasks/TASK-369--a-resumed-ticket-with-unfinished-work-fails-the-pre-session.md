---
title: A resumed ticket with unfinished work fails the pre-session check and goes to error
status: done
labels:
  - bug
created: 2026-11-17
---

## Description

Seen 2026-11-17 on `TASK-343` and `TASK-364`. Each had been returned to planning with partial work preserved in its worktree, as `work.md` tells workers to do, and was then put back in `todo`. `chitty run` runs the configured check in the worktree before starting the worker, the check failed on the unfinished work (an unformatted file and a guide test still pinning old wording; an uncommitted, half-rewritten test), and the run sent each ticket `todo → error` without starting a worker. The repair needed was finishing the work, which is the worker's job. The pre-session check exists to catch a broken environment or `main`, not to judge the ticket's own unfinished work. Planning should decide, for example: run the pre-session check only when the branch has no commits beyond `main` and the worktree is clean, or pass a failing check to the worker as context instead of erroring.

## Notes

Checked 2026-11-24: fixed. `b386eaec` (2026-11-20, "Resume todo branches with work after failed checks") and `668c3fd7` (2026-11-14, "Resume work after pre-session check failure") make `chitty run` start the worker on a `doing` or `error` ticket, or a `todo` ticket whose branch has work, when the pre-session check fails, with a `Check failed before this session: ...` note, instead of moving it to `error` (`_handle_check_failure` in `src/chitty/run.py`). Covered by `tests/test_next.py` `test_run_check_failure_on_todo_ticket_with_work_starts_agent` and the tests near it.

Reviewed: closed without a code change (2026-11-24, at the person's request for already-fixed tickets). Fixed by `b386eaec` and `668c3fd7`; see the note above.

## History

- 2026-11-17T22:48:50Z kind-umber-toad → backlog
- 2026-11-24T12:26:19Z kind-navy-toad: changed notes
- 2026-11-24T12:26:21Z kind-navy-toad backlog → review
- 2026-11-24T12:26:23Z kind-navy-toad: changed notes; overrode review independence
- 2026-11-24T12:26:23Z kind-navy-toad review → done
