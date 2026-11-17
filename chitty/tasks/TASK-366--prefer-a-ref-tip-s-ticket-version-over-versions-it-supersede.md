---
title: Prefer a ref tip's ticket version over versions it superseded
status: todo
labels:
  - bug
created: 2026-11-17
---

## Description

Seen 2026-11-17 landing `TASK-326` and `TASK-356` by hand. `git.historical_files` picks, for each path, the newest commit that touched it in the whole history reachable from any ref (`_latest_changes` in `src/chitty/git.py`, `git log --topo-order <all refs> -- chitty/tasks`), not the version at each ref tip. After `main` was merged into the ticket branch with the conflict resolved to the branch side (`status: done`) and `main` fast-forwarded, `main`'s tip held `done`, but `chitty show` returned the older `review → error` version committed on `main` at 17:25:03, because it was newer than the branch's `done` commit at 17:24:56 and the TREESAME merge is not listed for the path. `chitty edit` then refused: "TASK-326's latest committed version is on branch task-343", a branch that had only merged an older `main`. Workaround used: a new commit on `main` touching the file. The version on a ref tip should beat any version that tip has superseded: an ancestor's version must never win over a descendant's.

## History

- 2026-11-17T19:53:03Z kind-umber-toad → todo
