---
title: Remove merged branches of archived tickets that are not done
status: backlog
labels:
  - bug
created: 2026-11-24
---

## Description

`_remove_merged_branches` in `src/chitty/run.py` keeps any merged ticket branch whose ticket status is not `done`. A ticket archived without reaching `done` keeps its status (for example `planning`), so its branch and worktree are kept forever and every `chitty run` prints a line about it.

Evidence (echonomicon, 2026-11-24): TASK-160 and TASK-164 were archived from `planning` on 2026-11-23 (work found already done on `main`). Branches `task-160` and `task-164` have 0 commits ahead of `main`, clean worktrees in `.worktrees/`, yet each run prints `kept merged branch task-160: TASK-160 is planning`.

Suggested change: treat an archived ticket as finished for branch cleanup (or at least when its branch has no commits beyond `main`), still respecting the lock, uncommitted-changes and rebase/merge checks. Add a test with an archived `planning` ticket whose branch is merged.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:35Z zesty-coral-newt → backlog
- 2026-11-24T22:21:36Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:46Z zesty-coral-newt: changed labels
