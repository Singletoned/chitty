---
title: "`git.worktree_for_branch` hides `git worktree list` failures"
status: backlog
created: 2026-11-25
provisional: true
---

## Description

`worktree_for_branch` in `src/chitty/git.py` (around line 592) catches `ChittyError` from `_git(root, "worktree", "list", "--porcelain")` and returns `None`, so any Git failure reads as "this branch has no worktree". Callers in `src/chitty/run.py` (merged-branch cleanup, landing) and `src/chitty/store.py` then act on that: for example cleanup could delete a branch whose worktree it could not see. This goes against the rule that errors surface plainly. Found by the cold read of TASK-685 on 2026-11-24, which left it out of scope. Suggest: let the error propagate, and check each caller.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:20Z calm-ochre-quail → backlog
- 2026-11-25T22:28:21Z calm-ochre-quail: changed notes
