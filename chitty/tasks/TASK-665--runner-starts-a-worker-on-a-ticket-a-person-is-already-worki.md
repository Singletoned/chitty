---
title: Runner starts a worker on a ticket a person is already working on by hand
status: backlog
created: 2026-11-24
---

## Description

TASK-598, 2026-11-23. At 16:47:42 a hand-run session (youthful-quartz-zander) moved TASK-598 `error` -> `doing` and finished it in `.worktrees/task-598`. At 16:49:04 `chitty run` (actor calm-bronze-marten, mode `work`, lock `.git/chitty/run/TASK-598.lock`) picked the same `doing` ticket and started a worker in the same worktree. The hand session moved it to `review` at 16:50:25. The runner's `old_status` (`run.py` ~line 628, read from the branch) appears to have been read as `review` after the move, so each worker session ("TASK-598 is already in `review`; no further work is needed") counted as unchanged, and after 5 idle continuations the runner set the finished ticket to `error` (log `.git/chitty/run/TASK-598-20261123164904527311Z.log`).

Two possible fixes: (1) do not pick a `doing` ticket whose last status change was by a different actor a few minutes ago, or whose owner is not the runner; (2) if the worker finds the ticket already at a hand-off status for its mode (`review`, `done`), stop at once instead of continuing and then erroring.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:28Z zesty-coral-newt → backlog
- 2026-11-24T22:21:29Z zesty-coral-newt: changed notes
