---
title: Work on each ticket in its own branch
status: backlog
created: 2026-10-29
---

## Description

Several agents or people working on one branch collide: lock contention, commits landing mid-rebase, pre-commit hooks stashing other work, and autocommit interleaving with agent commits. Give each ticket its own branch and worktree instead. Each person creates the branch for their own work and closes it when done. `doing/task-<n>--<slug>` is created by the author and merged to main by the reviewer on a pass. `review/task-<n>--<slug>` is created by the reviewer and merged back into `doing/` by the reviewer. chitty reads status from the task file on each branch with `git show`, so it can report what is claimed and what is waiting for review without checking anything out. No ticket IDs are allocated off main: work found on a branch goes through the inbox. Design discussed with the human on 2026-10-29; see child tasks.

## Notes

Multiple review kinds (`review/code/…`, `review/ux/…`) were considered as a robustness test only; they should run in sequence because parallel reviews conflict when appending Notes. Not to be built.

## History

- 2026-10-29 → backlog
