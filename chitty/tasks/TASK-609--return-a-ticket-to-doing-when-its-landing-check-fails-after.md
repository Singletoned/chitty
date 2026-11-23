---
title: Return a ticket to `doing` when its landing check fails after a clean rebase
status: doing
created: 2026-11-23
---

## Description

When a ticket passes review, `chitty run` lands it (`_land_locked`, `src/chitty/run.py:1262`): rebase onto `main`, run setup, run the landing check, fast-forward `main`. Any `ChittyError` there becomes `error` through `_record_ticket_error` (`run.py:1426`), and `error` stops the loop until a person steps in. In taidy (2026-11-22) TASK-10 passed review but the branch was 39 commits behind `main`, which had added a field and changed formatter output, so two new tests broke after the rebase. That is an implementation defect against clear requirements, which project practice sends back to `doing`, not a runner failure.

Change: when the rebase succeeds but the landing check (`_landing_check`, `run.py:1392`) exits non-zero, move the ticket to `doing` instead of `error`:

- Raise a distinct `LandingCheckFailed(ChittyError)` from `_landing_check` for a non-zero exit only. "Command not found" stays a plain `ChittyError`, and a timeout stays `CommandTimedOut` (`commands.py`, a `ChittyError` subclass); neither is `LandingCheckFailed`.
- `_land` (`run.py:1250-1259`) wraps every `ChittyError` in a new plain `ChittyError` with a "Resolve the landing problem in ..." suffix; make it re-raise `LandingCheckFailed` unchanged (keeping its type), and leave that suffix out of the new note. `_land_pending` loses the suffix for this one failure; that is intended, because the note already names the worktree and the log.
- In `_run_ticket_with_log`, where landing errors are caught (the `except` at about `run.py:707-709`), handle `LandingCheckFailed` before `ChittyError`: edit the ticket through the worktree's repo (`branch_repo`, where the reviewer set `done`) with `Edit(status="doing", note=..., skip_verdicts=True, skip_current_version=True)`, as `_record_ticket_error` does. The note starts `Review failed (integration): after rebasing onto `main`, the landing check failed:`, followed by `landing check exited with status <N>; output in `.chitty/check.log`` (the existing message, kept verbatim), the last `LANDING_LOG_TAIL_LINES` (a new module constant, 40) lines of `.chitty/check.log` fenced with `code_block` as `_runner_error_note` does, and `Worktree: `<absolute path>`` as `_runner_error_note` writes it. `Repo.edit` accepts `done → doing` (no transition table; checked by the cold read).
- Keep the rebased branch in the worktree: do not reset or abort it. (Criterion 1 adds a new assertion that `main` is an ancestor of `task-1`; the existing tests do not check this.)
- Everything else that fails while landing (landing-time rebase conflicts, setup, protected or config files, the fast-forward) stays `error`, as today.

Out of scope: the pending-landing caller (`_land_pending`, defined at `run.py:376`, calling `_land` at 403), which has no handler today and stays unchanged; counting this failure toward escalation (TASK split from this one, see Notes); rerunning flaky checks automatically. Related: TASK-489, HUMAN-13.

## Acceptance Criteria

- [ ] In `tests/test_review_merge.py`, `test_failing_check_after_main_advances_preserves_main_and_worktree` (about line 371) and `test_landing_failure_records_error_on_branch_without_advancing_main` (about line 429) are changed to expect `done → doing` in stdout (today `done → error`, about lines 378 and 466): the ticket on the `task-1` branch is `doing`; its newest note starts `Review failed (integration):`, contains `landing check exited with status 7; output in `.chitty/check.log`` and the absolute worktree path, and does not contain `Resolve the landing problem`; in the first test the note also contains `LANDING_MARKER` from the fenced log tail (flip its `assertNotIn`); `main` is unchanged, and `main` is an ancestor of `task-1`. Both changed tests fail on `main` today.
- [ ] The `tests/test_landing.py` test that expects `landing check exited` from `_land` (about line 336) uses `assertRaises(LandingCheckFailed)` (fails on `main`, where the class does not exist). A new guard test in `tests/test_review_merge.py` (fixture config at about line 110, with a top-level `landing_check` set to a missing path) ends `done → error` with a `Runner error (landing)` note; it passes on `main` as a guard and must fail if a missing command were routed to `LandingCheckFailed`. `test_landing_check_timeout_records_error_without_advancing_main` (about line 398) still passes unchanged.

## Notes

Suggestion origin: taidy

Escalation split out to TASK-625: until it lands, a ticket whose landing check keeps failing cycles doing → review → done without escalating.

## History

- 2026-11-23T10:24:01Z witty-russet-gannet → backlog
- 2026-11-23T10:24:02Z witty-russet-gannet: changed notes
- 2026-11-23T10:34:30Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:34:30Z witty-russet-gannet backlog → planning
- 2026-11-23T10:36:05Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:36:05Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:37:51Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:37:51Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:37:55Z witty-russet-gannet: changed notes
- 2026-11-23T10:38:42Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:40:57Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:40:57Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:40:59Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:42:55Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:42:55Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:42:59Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:44:04Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:44:04Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:44:06Z witty-russet-gannet planning → todo
- 2026-11-23T10:55:41Z golden-dusky-puffin todo → doing
