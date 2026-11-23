---
title: Return a ticket to `doing` when its landing check fails after a clean rebase
status: planning
created: 2026-11-23
---

## Description

When a ticket passes review, `chitty run` lands it (`_land_locked`, `src/chitty/run.py:1262`): rebase onto `main`, run setup, run the landing check, fast-forward `main`. Any `ChittyError` there becomes `error` through `_record_ticket_error` (`run.py:1426`), and `error` stops the loop until a person steps in. In taidy (2026-11-22) TASK-10 passed review but the branch was 39 commits behind `main`, which had added a field and changed formatter output, so two new tests broke after the rebase. That is an implementation defect against clear requirements, which project practice sends back to `doing`, not a runner failure.

Change: when the rebase succeeds but the landing check (`_landing_check`, `run.py:1392`) exits non-zero, move the ticket to `doing` instead of `error`:

- Raise a distinct `LandingCheckFailed(ChittyError)` from `_landing_check` for a non-zero exit only. "Command not found" and timeouts stay plain `ChittyError` (runner or setup problems).
- Where `chitty run` catches landing errors after a review (around `run.py:697-708`), handle `LandingCheckFailed` first: edit the ticket in the worktree with a note starting `Review failed (integration): after rebasing onto `main`, the landing check failed:`, followed by the exit status, the last `LANDING_LOG_TAIL_LINES` (a new module constant, 40) lines of `.chitty/check.log`, and the worktree path. Route it through the same failure counting as a failed review (`fail_review_edit`, `_escalate_repeated_failure`), so a ticket that keeps failing escalates rather than looping.
- Keep the rebased branch in the worktree: do not reset or abort it.
- Everything else that fails while landing (rebase conflicts, setup failures, protected or config files, the fast-forward) stays `error`, as today.

The status before landing is `done` on the branch (the reviewer set it). Check that `Repo.edit` accepts `done → doing` with this note; if a guard refuses it, return the ticket to `planning` with the evidence rather than weakening the guard.

The second caller of `_land` (`run.py:403`, landing tickets already `done` and pending) should behave the same; if it cannot share the handler cheaply, say so in a note and leave it unchanged.

Related: TASK-489 (skip rerunning the landing check when `main` moved only by ticket files), HUMAN-13 (Linux check at landing).

Out of scope: rerunning flaky checks automatically.

## Acceptance Criteria

- [ ] `test_failing_check_after_main_advances_preserves_main_and_worktree` in `tests/test_review_merge.py` (fixture `fail_landing_check`) is changed to expect `done → doing`: the ticket on the `task-1` branch is `doing`, its newest note starts `Review failed (integration):` and contains `landing check exited with status 7`, the last lines of `.chitty/check.log` (including `LANDING_MARKER`) and the worktree path relative to the main checkout; `main` is unchanged and the worktree keeps the rebased branch (`main` is an ancestor of `task-1`). The changed test fails on `main` today.
- [ ] A test where the landing setup command fails (exit non-zero) still ends `done → error` with `Runner error (landing)` or `(setup)` as today, and the existing rebase-conflict and protected-file landing tests still pass unchanged.
- [ ] A test in which the ticket already has `MAX_REVIEW_FAILURES`-many failed reviews (or whatever count `_escalate_repeated_failure` uses in `src/chitty/store.py`) shows that a landing check failure counts as one more failure and escalates the same way a failed review does.

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:01Z witty-russet-gannet → backlog
- 2026-11-23T10:24:02Z witty-russet-gannet: changed notes
- 2026-11-23T10:34:30Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:34:30Z witty-russet-gannet backlog → planning
