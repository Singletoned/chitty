---
title: Use `main_branch` instead of `main` in the code
status: backlog
priority: medium
depends_on:
  - TASK-214
created: 2026-11-06
---

## Description

`TASK-214` adds the `main_branch` setting. Use it everywhere the code means the integration branch:

- `main_files` in `src/chitty/git.py`, which `_dependency_is_done` in `src/chitty/store.py` uses to judge dependencies on the main branch, and that function's `refs/heads/main:...` error text.
- In `src/chitty/run.py`: `_preflight`'s branch check and its error text, `_prepare_review`'s rebase and its "rebasing onto `main`" conflict note, and the `git worktree add ... main` that creates ticket worktrees.

Always read the setting from the main checkout's config (`main_repo`, found by the existing `_main_checkout` in `src/chitty/run.py`), never from a ticket worktree's. Older ticket branches may lack the key, and the main checkout's config is the one that counts. `_main_checkout` and `_refuse_stale_linked_worktree` mean the primary checkout, not the branch, so leave their names alone.

Out of scope: docs and guides (`TASK-217`).

## Acceptance Criteria

- [ ] Tests in a repository with `main_branch = "master"` show `chitty run` creating the worktree from `master`, rebasing a review onto `master` (its conflict note names `master`), `chitty next` judging a dependency done on `master`, and `_preflight` requiring the main checkout to be on `master`.
- [ ] A ticket worktree whose own config lacks `main_branch` is still reviewed using the main checkout's setting, and `grep -n '"main"\|heads/main' src/chitty/*.py` finds nothing.

## History

- 2026-11-06T16:48:06Z youthful-toad → backlog
- 2026-11-06T16:48:39Z youthful-toad: changed description
