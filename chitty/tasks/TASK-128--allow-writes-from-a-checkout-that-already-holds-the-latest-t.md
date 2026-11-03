---
title: Allow writes from a checkout that already holds the latest ticket version
status: review
labels:
  - bug
  - escape
priority: high
created: 2026-11-03
---

## Description

`TASK-105` refuses a write when a ticket's latest committed version is on another branch, but it misreports the branch when several branches hold that same version. `historical_files` in `src/chitty/git.py` takes `matching[0]`, the alphabetically first ref holding the blob. In a new `task-126` worktree, the unchanged ticket is therefore reported as being on `main`, and the claim is refused. So every new ticket's first write from its worktree fails, which is what blocked `TASK-126` on 2026-11-03. The reverse also happens: a branch sorting before `main` makes writes from `main` fail.

Prefer the current branch when it is one of the refs holding the latest version. A ticket that really is newer elsewhere must still be refused. No setup change, so no version bump.

Bootstrap: the global `chitty` runs `main`, so until this lands it refuses these writes. Work on this ticket uses the worktree's own `.venv/bin/chitty`.

## Acceptance Criteria

- [x] A test shows a write succeeding from a new worktree with no commits of its own, and it fails before the fix
- [x] A test shows a write succeeding from `main` when a branch sorting before `main` holds the same version, and it fails before the fix
- [x] The existing refusal tests still pass, including a ticket newer on another branch

## Plan

Prefer the current branch in `historical_files` when it is one of the refs holding the latest version. Regression tests written first and confirmed failing.

## Notes

Bootstrap: the claim came after the fix, because the global `chitty` refuses it until this lands, so this used the worktree `.venv/bin/chitty`. Both new tests failed before the fix with the reported refusal, naming `main` and `aaa`. Verified with `make check` and `npm test`. No cold read: small, with the cause already traced. The reviewer should also use `.venv/bin/chitty` here, or the global one if the ticket on this branch is newest, which it now is.

Retro: this bug shipped in `TASK-105`, which passed first time with no cold read. Its criterion 3 said writes work when the checkout holds the latest version, but the only test had a commit on the branch, so a new worktree was never tried. The `TASK-126` cold read also saw `branch: main` from a worktree; the author changed `TASK-126` to work around it without asking whether it was a bug. A first-review pass is not evidence the ticket is right, which is what the escape loop is for: treat this as the first `escape` from `TASK-105`.

## History

- 2026-11-03T19:25:31Z lively-panda → todo
- 2026-11-03T19:28:14Z lively-panda: wrote the plan
- 2026-11-03T19:28:14Z lively-panda todo → doing
- 2026-11-03T19:28:15Z lively-panda: changed notes; ticked acceptance criteria
- 2026-11-03T19:28:15Z lively-panda doing → review
- 2026-11-03T19:28:15Z lively-panda: changed labels, notes
