---
title: Allow writes from a checkout that already holds the latest ticket version
status: doing
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

`TASK-105` refuses a write when a ticket's latest committed version is on another branch, but it misreports the branch when several branches hold that same version. `historical_files` in `src/chitty/git.py` takes `matching[0]`, the alphabetically first ref holding the blob. In a new `task-126` worktree, the unchanged ticket is therefore reported as being on `main`, and the claim is refused. So every new ticket's first write from its worktree fails, which is what blocked `TASK-126` on 2026-11-03. The reverse also happens: a branch sorting before `main` makes writes from `main` fail.

Prefer the current branch when it is one of the refs holding the latest version. A ticket that really is newer elsewhere must still be refused. No setup change, so no version bump.

Bootstrap: the global `chitty` runs `main`, so until this lands it refuses these writes. Work on this ticket uses the worktree's own `.venv/bin/chitty`.

## Acceptance Criteria

- [ ] A test shows a write succeeding from a new worktree with no commits of its own, and it fails before the fix
- [ ] A test shows a write succeeding from `main` when a branch sorting before `main` holds the same version, and it fails before the fix
- [ ] The existing refusal tests still pass, including a ticket newer on another branch

## Plan

Prefer the current branch in `historical_files` when it is one of the refs holding the latest version. Regression tests written first and confirmed failing.

## History

- 2026-11-03T19:25:31Z lively-panda → todo
- 2026-11-03T19:28:14Z lively-panda: wrote the plan
- 2026-11-03T19:28:14Z lively-panda todo → doing
