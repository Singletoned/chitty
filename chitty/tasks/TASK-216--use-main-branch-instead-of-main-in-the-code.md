---
title: Use `main_branch` instead of `main` in the code
status: doing
priority: medium
depends_on:
  - TASK-214
created: 2026-11-06
---

## Description

`TASK-214` adds the `main_branch` setting. Use it everywhere the code means the integration branch:

- `main_files` in `src/chitty/git.py`, which `_dependency_is_done` in `src/chitty/store.py` uses to judge dependencies on the main branch, and that function's `refs/heads/main:...` error text.
- In `src/chitty/run.py`: `_preflight`'s branch check and its error text, `_prepare_review`'s rebase and its "rebasing onto `main`" conflict note, and the `git worktree add ... main` that creates ticket worktrees.

Always read the setting from the main checkout's config, never from a ticket worktree's. `chitty next` and the MCP `next` tool also call `next_action(_repo())` from wherever they run, which may be a ticket worktree. So add a `_main_branch(repo)` helper in `src/chitty/store.py`: in a linked worktree it loads the main checkout's config, otherwise it uses `repo.config`. It needs `git.main_checkout`, which is `_main_checkout` moved out of `src/chitty/run.py` because `store.py` can't import `run.py`. `TASK-212` makes the same move, and whichever lands second reuses it. `main_files` takes the branch as a required argument; it has a second caller in `_ticket_action`'s dependency-lookup `except` block. Older ticket branches may lack the key, and the main checkout's config is the one that counts. `_main_checkout` and `_refuse_stale_linked_worktree` mean the primary checkout, not the branch, so leave their names alone.

The `REPORT` script in `tests/test_review_rebase.py` hard-codes `main`. Under a `master` repository it prints a harmless `fatal`, so don't use it to assert anything about `master`.

Out of scope: docs and guides (`TASK-217`), and the `Makefile` `release` target, which releases this repository's own `main`.

## Acceptance Criteria

- [ ] Tests in a repository with `main_branch = "master"` show `chitty run` creating the worktree from `master`, rebasing a review onto `master` (its conflict note names `master`), `chitty next` judging a dependency done on `master`, and `_preflight` requiring the main checkout to be on `master`.
- [ ] A ticket worktree whose own config lacks `main_branch` is still reviewed, and `chitty next` run inside it is still judged, using the main checkout's setting. `grep -n '"main"\|heads/main' src/chitty/*.py` matches only the `main_branch` default in `config.py` and `chitty init`'s `!= "main"` check from `TASK-214`.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-216/1`, built on `TASK-214`'s read; the `master` tests failed before and passed after; `make check` OK). Outcomes:
- `chitty next` and MCP `next` run from worktrees: fixed, the ticket adds the `_main_branch` helper.
- The circular import from `store.py`: fixed, `git.main_checkout`, shared with `TASK-212`.
- A second `main_files` caller: fixed, it's named.
- The criterion-2 grep matched two legitimate lines: fixed, both are listed.
- The `Makefile` release target: out of scope.
- The `REPORT` fixture's hard-coded `main`: noted.
- Size: confirmed right.

## History

- 2026-11-06T16:48:06Z youthful-toad → backlog
- 2026-11-06T16:48:39Z youthful-toad: changed description
- 2026-11-06T17:09:58Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T17:09:58Z youthful-toad backlog → todo
- 2026-11-06T21:13:50Z intrepid-otter todo → doing
