---
title: Work on each ticket in its own branch
status: backlog
created: 2026-10-29
---

## Description

Several agents or people working on one branch collide: lock contention, commits landing mid-rebase, pre-commit hooks stashing other work, and autocommit interleaving with agent commits. Give each ticket its own branch and worktree instead. Parent goal for the branch workflow; the children carry the work.

Decided with the human:
- 2026-10-29: the author creates `doing/task-<n>--<slug>` for their ticket; the reviewer creates `review/task-<n>--<slug>` from it (TASK-60); the reviewer merges to `main` on a pass. No ticket IDs are allocated off `main`: work found on a branch goes through the inbox (TASK-61).
- 2026-11-01: worktrees live in `.worktrees/` unless an agent's own instructions say otherwise, and worktree work uses autocommit (TASK-85). Chitty reads task state from every branch through Git history, local and remote-tracking, without checking anything out (TASK-84). The reviewer who passes branch work merges it into `main` (TASK-86, in the guide).

## Notes

Multiple review kinds (`review/code/…`, `review/ux/…`) were considered as a robustness test only; they should run in sequence because parallel reviews conflict when appending Notes. Not to be built.

Archived in backlog triage (human approved, 2026-11-11): already done or superseded.

## History

- 2026-10-29 → backlog
- 2026-11-11T10:16:49Z vivid-yellowhammer: changed notes
- 2026-11-11T10:16:49Z vivid-yellowhammer backlog → archived
