---
title: Remove `Edit.skip_current_version` and `allow_stale`, and refuse remote-only review handoffs early
status: backlog
depends_on:
  - TASK-385
parent: TASK-376
created: 2026-11-23
---

## Description

Split from `TASK-385` (2026-11-22 plan, part 3; old criteria 2 and 3 there). Once `_require_writable` allows identical copies, no runner write should need the bypass.

- Remove `Edit.skip_current_version`, `allow_stale` in `Repo._save`, and every use in `src/chitty/run.py` and the tests (`tests/test_review_trailers.py` has two: rewrite them to assert the refusal).
- The review-with-no-branch handoff in `_run_ticket` (entered when there is no worktree and no local branch): if `main_repo.find(id).branch is None`, write `error` on `main` as today; else if `stored.branch` is not the local branch `task-<n>` (remote-only, or a remote ahead of a stale local one), call `main_repo._require_writable(stored)` so its error propagates before any agent starts.

Old criteria, to refine when planned: `git grep -nE 'skip_current_version|allow_stale' -- src tests` prints nothing and the runner tests pass; a review run on a ticket with only `origin/task-<n>` fails with `write_refusal`'s message, starts no agent and writes nothing on `main`; with no branch anywhere it records `error` on `main` as before.

## History

- 2026-11-23T14:35:34Z youthful-quartz-zander → backlog
