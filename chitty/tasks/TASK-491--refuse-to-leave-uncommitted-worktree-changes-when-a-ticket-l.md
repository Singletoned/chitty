---
title: Refuse to leave uncommitted worktree changes when a ticket leaves `doing`
status: backlog
created: 2026-11-21
---

## Description

Seen 2026-11-20 on `TASK-347`. On 2026-11-17 a worker moved it `doing` to `planning` with about 70 lines of `src/chitty/cli.py` changes left uncommitted in `.worktrees/task-347`. Three days later the branch was 1324 commits behind `main`, the diff no longer applied, and because the branch copy of the ticket had the later history, `chitty show` read `planning` from it although `main` said `todo`. Nothing reported the stale dirty worktree; it blocked TASK-348 silently. Suggest: a status edit out of `doing` (to planning, blocked, review) in a ticket worktree refuses while that worktree has uncommitted changes, naming the paths, so the worker commits a WIP or discards it. Recovered by committing the work, tagging it `task-347-partial`, and removing the worktree and branch.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:53Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:54Z nimble-umber-gannet: changed notes
