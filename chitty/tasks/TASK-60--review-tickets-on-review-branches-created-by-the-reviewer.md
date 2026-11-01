---
title: Review tickets on review/ branches created by the reviewer
status: backlog
depends_on:
  - TASK-84
parent: TASK-58
created: 2026-10-29
---

## Description

The author commits `-s review` on `doing/…` and stops committing there. "Waiting for review" is review status on a `doing/` branch with no matching `review/` branch; a reviewer claims it by creating `review/task-<n>--<slug>` from `doing/…` (separate branch because git will not check out a branch already checked out in another worktree). The reviewer commits the verdict, merges `review/…` back into `doing/…` (a fast-forward) and deletes it. On a pass the reviewer merges `doing/…` into main and deletes it; on a fail the author resumes on `doing/…`. Update the guide and PLAN.md.

## Notes

Reconciled 2026-11-01: reading other branches' task state is now TASK-84 (TASK-59 archived). The reviewer merging to `main` on a pass is already in the guide (TASK-86).

## History

- 2026-10-29 → backlog
