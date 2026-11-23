---
title: Return a ticket to `doing` when its landing check fails after a clean rebase
status: planning
created: 2026-11-23
---

## Description

When a ticket passes review, `chitty run` lands it (`_land_locked`, `src/chitty/run.py:1262`): rebase onto `main`, run setup, run the landing check, fast-forward `main`. Any `ChittyError` there becomes `error` through `_record_ticket_error` (`run.py:1426`), and `error` stops the loop until a person steps in. In taidy (2026-11-22) TASK-10 passed review but the branch was 39 commits behind `main`, which had added a field and changed formatter output, so two new tests broke after the rebase. That is an implementation defect against clear requirements, which project practice sends back to `doing`, not a runner failure.

Change: when the rebase succeeds but the landing check (`_landing_check`, `run.py:1392`) exits non-zero, move the ticket to `doing` instead of `error`:

- Raise a distinct `LandingCheckFailed(ChittyError)` from `_landing_check` for a non-zero exit only. "Command not found" and timeouts stay plain `ChittyError`.
- In `_run_ticket_with_log`, where landing errors are caught (around `run.py:696-708`), handle `LandingCheckFailed` before `ChittyError`: edit the ticket through the worktree's repo (`branch_repo`, where the reviewer set `done`) with `Edit(status="doing", note=..., skip_verdicts=True, skip_current_version=True)`, as `_record_ticket_error` does. The note starts `Review failed (integration): after rebasing onto `main`, the landing check failed:`, followed by the exit status, the last `LANDING_LOG_TAIL_LINES` (a new module constant, 40) lines of `.chitty/check.log`, and `Worktree: `<absolute path>`` as `_runner_error_note` writes it. `Repo.edit` accepts `done → doing` (no transition table; checked by the cold read).
- Keep the rebased branch in the worktree: do not reset or abort it.
- Everything else that fails while landing (rebase conflicts, setup, protected or config files, the fast-forward) stays `error`, as today.

Out of scope: the pending-landing caller (`_land_pending`, `run.py:403`), which has no handler today and stays unchanged; counting this failure toward escalation (TASK split from this one, see Notes); rerunning flaky checks automatically. Related: TASK-489, HUMAN-13.

## Acceptance Criteria

- [ ] `test_failing_check_after_main_advances_preserves_main_and_worktree` (`tests/test_review_merge.py`, about line 371) and `test_landing_failure_records_error_on_branch_without_advancing_main` (about line 429) are changed to expect `done → doing`: the ticket on the `task-1` branch is `doing`, its newest note starts `Review failed (integration):` and contains `landing check exited with status 7`, the last lines of `.chitty/check.log` (including `LANDING_MARKER`) and the absolute worktree path as today; `main` is unchanged, and `main` is an ancestor of `task-1` (the rebase was kept). Both changed tests fail on `main` today.
- [ ] The existing landing tests for rebase conflicts and protected or config files still pass unchanged, still ending in `error`.

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:01Z witty-russet-gannet → backlog
- 2026-11-23T10:24:02Z witty-russet-gannet: changed notes
- 2026-11-23T10:34:30Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:34:30Z witty-russet-gannet backlog → planning
- 2026-11-23T10:36:05Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:36:05Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:37:51Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:37:51Z witty-russet-gannet cold-read → planning
