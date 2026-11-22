---
title: Rebase a `doing` ticket's worktree onto `main` before setup in work runs
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-370
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. `TASK-370` adds `_rebase_work_worktree(worktree, task_id, main_branch)` in `src/chitty/run.py`, tested directly. This ticket calls it from the runner. Draft: keep in planning until `TASK-370` lands, then check its landed signature and cold-read.

- In `_run_ticket_with_log` (already over 100 lines; add only the call), in work mode only, call it after the worktree is made and before `setup`, only when the ticket was selected as `doing`. Review mode is unchanged. `TASK-545` extends it to `todo` and `error`.
- Update the work-mode bullet under `## Before a review` in `docs/plan/next-action-and-runner.md` to say work mode rebases a `doing` ticket's branch onto `main` before `setup`, saving uncommitted work under `refs/chitty/stash/<ID>`.

Test in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py` (`ReviewMergeTestCase`): a `doing` ticket whose branch exists, then a commit on `main` touching another file, with `setup` set to a fake command that records `git log --format=%s` of its worktree to a file. After a work run, setup's recorded log includes `main`'s new commit, and `git merge-base --is-ancestor main task-<n>` succeeds. It fails before the change.

## Acceptance Criteria

- [ ] The runner test passes and fails before the change; the doc bullet is updated; `make check` passes

## History

- 2026-11-22T02:02:11Z lively-zinc-newt → planning
