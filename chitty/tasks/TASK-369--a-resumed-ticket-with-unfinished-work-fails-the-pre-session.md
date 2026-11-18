---
title: A resumed ticket with unfinished work fails the pre-session check and goes to error
status: backlog
labels:
  - bug
created: 2026-11-17
---

## Description

Seen 2026-11-17 on `TASK-343` and `TASK-364`. Each had been returned to planning with partial work preserved in its worktree, as `work.md` tells workers to do, and was then put back in `todo`. `chitty run` runs the configured check in the worktree before starting the worker, the check failed on the unfinished work (an unformatted file and a guide test still pinning old wording; an uncommitted, half-rewritten test), and the run sent each ticket `todo → error` without starting a worker. The repair needed was finishing the work, which is the worker's job. The pre-session check exists to catch a broken environment or `main`, not to judge the ticket's own unfinished work. Planning should decide, for example: run the pre-session check only when the branch has no commits beyond `main` and the worktree is clean, or pass a failing check to the worker as context instead of erroring.

## History

- 2026-11-17T22:48:50Z kind-umber-toad → backlog
