---
title: Review tickets on review/ branches created by the reviewer
status: backlog
depends_on:
  - TASK-59
parent: TASK-58
created: 2026-10-29
---

## Description

The author commits `-s review` on `doing/…` and stops committing there. "Waiting for review" is review status on a `doing/` branch with no matching `review/` branch; a reviewer claims it by creating `review/task-<n>--<slug>` from `doing/…` (separate branch because git will not check out a branch already checked out in another worktree). The reviewer commits the verdict, merges `review/…` back into `doing/…` (a fast-forward) and deletes it. On a pass the reviewer merges `doing/…` into main and deletes it; on a fail the author resumes on `doing/…`. Update the guide and PLAN.md.

## History

- 2026-10-29 → backlog
