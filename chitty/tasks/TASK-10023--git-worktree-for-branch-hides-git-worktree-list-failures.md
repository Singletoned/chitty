---
title: "`git.worktree_for_branch` hides `git worktree list` failures"
status: todo
labels:
  - bug
priority: medium
created: 2026-11-25
moved_from: TASK-X3784V
---

## Description

`worktree_for_branch` in `src/chitty/git.py` (line 592) catches `ChittyError` from `_git(root, "worktree", "list", "--porcelain")` and returns `None`, so any Git failure reads as "this branch has no worktree". Its callers act on that: the runner may create a second worktree or report that a branch has none, and the "latest committed version is on branch" message in `src/chitty/store.py` picks the wrong instruction. Found by the cold read of TASK-685 on 2026-11-24.

Change: remove the `try`/`except`, so the error propagates with Git's message. Every caller runs inside a repository, so none needs a fallback; check each one and say in a note if any does.

No property test: one external process failure, covered by an example.

## Acceptance Criteria

- [ ] A test calls `git.worktree_for_branch` on a temporary directory that is not a Git repository and expects `ChittyError` naming `git worktree list`. Fails today: it returns `None`.
- [ ] Regression tests: the tests that reach the callers (`src/chitty/run.py` lines near 345, 495, 508 and 1263; `src/chitty/store.py` near 799 and 1594) pass; `make check` passes.

## History

- 2026-11-25T22:28:20Z calm-ochre-quail → backlog
- 2026-11-25T22:28:21Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:14Z calm-ochre-quail: changed labels, priority
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-X3784V
- 2026-11-25T23:32:55Z calm-ochre-quail: replaced notes; changed description, acceptance criteria
- 2026-11-25T23:32:55Z calm-ochre-quail backlog → planning
- 2026-11-25T23:33:07Z calm-ochre-quail planning → cold-read
- 2026-11-25T23:34:16Z calm-ochre-quail cold-read → todo
