---
title: Commit or restore a ticket file when a Chitty write fails after writing it
status: backlog
parent: TASK-376
created: 2026-11-18
---

## Description

This ticket needs refining.

## Notes

Reproduced 2026-11-18 in `.worktrees/task-359` (branch `task-359`, clean worktree, ticket committed there and also present on `main`): `chitty edit TASK-359 --note ...` succeeded, then `chitty archive TASK-359` failed with `TASK-359 is used by more than one file: .../chitty/tasks/TASK-359--....md, .../chitty/tasks/archive/TASK-359--....md`, leaving the active file deleted and the archive file untracked, uncommitted. The same command on `main` for `TASK-366` (also on branch `task-366`) succeeded. Undone by hand with `git restore` and `rm`.

## History

- 2026-11-18T16:20:21Z lively-quartz-crane → backlog
- 2026-11-18T16:25:57Z lively-quartz-crane: changed notes
