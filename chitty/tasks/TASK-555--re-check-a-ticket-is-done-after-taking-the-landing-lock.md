---
title: Re-check a ticket is `done` after taking the landing lock
status: doing
labels:
  - bug
priority: high
created: 2026-11-22
---

## Description

Seen 2026-11-22 on `TASK-540`: its code landed on `main` while its ticket said `error`, so a landed ticket was stuck and its dependants blocked.

Cause (planner, 2026-11-22, from `git reflog show main`, the run logs and the Pi sessions): every `chitty run`, in any mode, first calls `_land_pending` in `src/chitty/run.py` (around line 376), which picks local ticket branches whose ticket says `done` and calls `_land`. It reads the status before taking `locks.landing_lock`, and `_land_locked` never reads it again. Timeline: the review loop's agent set `done` at 04:03:31 and that loop started landing (lock held); the other loop's `_land_pending` saw `done` and waited on the lock; the review loop's landing check failed (a flaky test) and it committed `error` on the branch at 04:05:05, releasing the lock; the waiting loop then ran setup and the check again, which passed, and fast-forwarded `main` to the branch tip (already saying `error`) at 04:06:48, removing the worktree and branch. No run log covers that landing, because `_land_pending` runs before a ticket is locked and logged.

Decisions:

- `_land_locked` reads the ticket again after the landing lock is held, from a fresh `Repo.open(main_root)` (not the cached `main_repo`): `Repo.open(main_root).find(action.id)`. If its status is not `done`, it prints `not landing <ID>: it is <status>` to stderr and returns without changing anything (no rebase, no setup, no check, no fast-forward, worktree and branch kept). Put the check after the existing early return for an already removed ticket and before `git.current_branch`.
- `_land` and `_land_locked` return `bool`: `False` only for that skip, `True` otherwise (including the existing early returns). `_land_pending` prints `landed <ID>` and returns its `RunResult` only when `_land` returns `True`; otherwise it goes on to the next pending ticket, and returns `None` if none landed. The review-mode caller in `_run_ticket` ignores the result.
- Out of scope: run logs for `_land_pending` landings.

Tests in a new `tests/test_landing_status_recheck.py`, inheriting `LandingTestCase` from `tests/test_landing.py`. No property: a small fixed set, every member tested: for each status in `STATUSES` (`src/chitty/model.py`) other than `done`, set it on the branch's ticket file and commit in the worktree (as `finish_ticket` does for `done`), then call `self.land()`, capturing stderr with `contextlib.redirect_stderr`. Rewrite the status line with a regular expression (`finish_ticket` only replaces `status: todo`).

## Acceptance Criteria

- [ ] For every status other than `done`, `self.land()` leaves `main`'s tip, the branch tip and the worktree unchanged, prints `not landing TASK-1: it is <status>` to stderr, and returns `False`; this fails before the change (the ticket lands)
- [ ] With `done` the ticket lands as before and `_land` returns `True`; the existing tests in `tests/test_landing.py` and `tests/test_run_*.py` pass; `make check` passes

## Plan

Add fixed-status regression tests, verify failure, then recheck status under the landing lock and adjust landing return values. Run checks and commit.

## Notes

Suggestion origin: chitty

Planner investigation, 2026-11-22. Timeline from `git reflog show main` and `.git/chitty/run/`: the review agent marked `done` at 04:03:31 (log `TASK-540-20261122035901604530Z.log`, last written 04:03:34); the runner rebased the branch at 04:03:37, the landing check failed and `error` was committed on the branch at 04:05:05 (`ad7d201b`). Then `main@{04:06:48}: merge task-540: Fast-forward` moved `main` to `ad7d201b`, the branch tip that already said `error`, and the worktree and branch were removed. The landing order in `_land_locked` (`src/chitty/run.py` around line 1300) is correct: check before `git.fast_forward`. `_land_pending` only lands tickets whose authoritative copy is `done`, and the branch said `error`. No runner log exists between 04:04 and 04:10, and the overnight planner session only read the worktree. So I cannot find a Chitty code path that did this.

Question for the owner: did you (or a session you started by hand) run `git merge --ff-only task-540` in the main checkout around 04:06 on 2026-11-22, then remove the worktree and branch? If yes, this is not a runner bug; the useful follow-up would be making `chitty check` on `main` flag a ticket whose work is on `main` but whose status is `error` (close to `TASK-358`). If no, I will add logging around `git.fast_forward` so the next occurrence shows the caller.

Owner, 2026-11-22: may have been a Pi session, not remembered. Planner checked: the `TASK-540` Pi review session ended at 04:03:34 with no merge, and no Pi session ran a merge of `task-540`; the race above explains the 04:06:48 fast-forward.

Regression test failed before the fix (unittest exit 1).

## History

- 2026-11-22T09:47:31Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
- 2026-11-22T09:53:26Z friendly-jade-stoat: changed labels, notes
- 2026-11-22T10:28:11Z friendly-jade-stoat: changed title, labels, description, acceptance criteria, notes
- 2026-11-22T10:28:11Z friendly-jade-stoat backlog → cold-read
- 2026-11-22T10:29:04Z friendly-jade-stoat: changed labels, priority, description
- 2026-11-22T10:29:04Z friendly-jade-stoat cold-read → planning
- 2026-11-22T10:29:05Z friendly-jade-stoat planning → todo
- 2026-11-22T14:16:04Z rosy-silver-quail todo → doing
- 2026-11-22T14:18:36Z rosy-silver-quail: wrote the plan
- 2026-11-22T14:19:06Z rosy-silver-quail: changed notes
