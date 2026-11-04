---
title: Do not fail `chitty run` when a passed review removes its worktree
status: todo
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

Seen on 2026-11-04 at the end of the `TASK-119` review, which passed: `Error: no Chitty configuration in .../.worktrees/task-119`. The guide tells a reviewer to merge on a pass and then remove the branch and worktree. `run` in `src/chitty/run.py` then calls `Repo.open(worktree)` to read the new status, and the directory has gone. So every passed review ends in a non-zero exit, which stops an unattended loop even though the work landed. `TASK-126` introduced this by moving Pi into the worktree, and no test has a fake agent that removes it.

After the agent exits, if the worktree no longer exists, read the status from the main checkout, through a new `Repo.open(main_root)`, because the ticket has been merged there. Report the result as usual. `TASK-131` stops reviewers removing worktrees, but a person or an agent can still do it, so keep this.

Out of scope: landing.

## Acceptance Criteria

- [ ] A test with a fake agent that merges the branch, removes the worktree and exits shows `chitty run` exiting 0 and printing the status change
- [ ] A test shows a worktree removed with the ticket not merged failing with a message naming the ticket, not a traceback

## History

- 2026-11-04T15:12:08Z mellow-newt → todo
