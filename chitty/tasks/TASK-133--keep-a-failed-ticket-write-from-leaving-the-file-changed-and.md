---
title: Keep a failed ticket write from leaving the file changed, and allow dependencies on tickets from `main`
status: backlog
labels:
  - bug
priority: medium
created: 2026-11-03
---

## Description

Found on 2026-11-03 editing `TASK-126` from its worktree. Adding `depends_on: TASK-129` failed with `no such task`, because that ticket was created on `main` after the branch was cut, although `chitty list` and `chitty next` can see tickets on every branch. The failed `edit` also left the ticket file changed and uncommitted in the worktree, with the error `cannot finalize task write with unresolved problems`. Two questions to settle: whether dependency checks should use the same all-branch view as reads, and whether a refused write should restore the file before exiting. Needs a cold read before work starts.

## History

- 2026-11-03T21:01:34Z lively-panda → backlog
