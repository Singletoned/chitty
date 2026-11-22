---
title: Rebase `todo` and `error` tickets before setup in work runs
status: planning
depends_on:
  - TASK-370
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. After `TASK-370`, work mode rebases the ticket worktree onto `main` before `setup` (`_rebase_work_worktree` in `src/chitty/run.py`), tested on a `doing` ticket. tested on a `doing` ticket and called only for tickets selected as `doing`. This ticket extends the call to tickets selected as `todo` (after the claim is written) and `error` (repair runs), and tests both. Draft: keep in planning until `TASK-370` lands, then reuse its fixtures and cold-read.

Tests, extending `tests/test_run_work_rebases.py`, each with a fake `setup` command that records `git log --format=%s` of its worktree to a file:

1. `todo` with an existing branch: `TASK-<n>` is `todo` and has a branch `task-<n>` with one code commit, then `main` gains a commit touching another file. After a work run, setup's recorded log includes `main`'s new commit, the claim commit (`doing`) is on the branch, and the agent records the ticket as `doing`.
2. `error` repair: `TASK-<n>` is `error` on its branch (as `make_doing_branch()` plus an error edit in `tests/test_run_errors_on_branch.py`), then `main` gains a commit. `chitty run --errors` starts the repair agent, and setup's recorded log includes `main`'s new commit.

Each fails before `TASK-370`'s change only if run against `main` from before it; record that run in a note.

## Acceptance Criteria

- [ ] Both tests pass, and each fails against the runner from before `TASK-370` (noted); `make check` passes

## History

- 2026-11-22T01:47:36Z lively-zinc-newt → planning
- 2026-11-22T01:56:10Z lively-zinc-newt: changed description
