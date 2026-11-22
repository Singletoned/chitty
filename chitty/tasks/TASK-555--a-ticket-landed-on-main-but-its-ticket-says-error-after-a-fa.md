---
title: A ticket landed on `main` but its ticket says `error` after a failed landing check
status: backlog
labels:
  - bug
  - question
created: 2026-11-22
---

## Description

Seen 2026-11-22 on `TASK-540`. History: `review → done` at 04:03:31 by the review loop, then `done → error` at 04:05:03 with `Runner error (landing): landing check exited with status 2` (the check failed on a flaky test, since fixed by `TASK-553`). Yet the code is on `main` (commit `9027093c`, "Allow work rebase to stop on non-ticket conflicts", plus the ticket commit `ad7d201b` that records `error`), and the `task-540` branch and worktree are gone. So either the landing fast-forwarded `main` before (or despite) the failing check, or a later run landed the branch without updating the ticket. Result: a landed ticket stuck in `error`, its dependants blocked, and only a person can mark it `done` (a planner must not write the `Reviewed:` note). Worth checking the order in the landing code (`_land_locked` / `_land_pending` in `src/chitty/run.py`) and making a landed ticket end `done`.

## Notes

Suggestion origin: chitty

Planner investigation, 2026-11-22. Timeline from `git reflog show main` and `.git/chitty/run/`: the review agent marked `done` at 04:03:31 (log `TASK-540-20261122035901604530Z.log`, last written 04:03:34); the runner rebased the branch at 04:03:37, the landing check failed and `error` was committed on the branch at 04:05:05 (`ad7d201b`). Then `main@{04:06:48}: merge task-540: Fast-forward` moved `main` to `ad7d201b`, the branch tip that already said `error`, and the worktree and branch were removed. The landing order in `_land_locked` (`src/chitty/run.py` around line 1300) is correct: check before `git.fast_forward`. `_land_pending` only lands tickets whose authoritative copy is `done`, and the branch said `error`. No runner log exists between 04:04 and 04:10, and the overnight planner session only read the worktree. So I cannot find a Chitty code path that did this.

Question for the owner: did you (or a session you started by hand) run `git merge --ff-only task-540` in the main checkout around 04:06 on 2026-11-22, then remove the worktree and branch? If yes, this is not a runner bug; the useful follow-up would be making `chitty check` on `main` flag a ticket whose work is on `main` but whose status is `error` (close to `TASK-358`). If no, I will add logging around `git.fast_forward` so the next occurrence shows the caller.

## History

- 2026-11-22T09:47:31Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
- 2026-11-22T09:53:26Z friendly-jade-stoat: changed labels, notes
