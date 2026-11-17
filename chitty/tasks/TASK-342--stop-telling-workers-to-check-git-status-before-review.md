---
title: Stop telling workers to check git status before review
status: done
labels:
  - untestable
owner: human
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers to run `git status --short` and see it empty before `-s review`. Chitty already enforces this: `Repo.edit` in `src/chitty/store.py` refuses to enter or pass review while the worktree has uncommitted or untracked non-ignored files, and lists them (added by `TASK-231`, tested by `test_dirty_branch_cannot_enter_review_until_committed` in `tests/test_review_merge.py`). So the guide only needs to say what happens, not ask for a manual check.

In `work.md`, replace ``then run `git status --short`. It must be empty before moving the ticket to `review`; commit intended changes and resolve leftover files first.`` with ``then commit your changes: `chitty edit -s review` refuses while the worktree has uncommitted files.`` Update the phrases `tests/test_guide_work_commits.py` asserts to match. Leave `src/chitty/roles/review.md` alone: the reviewer's `git status --short` step decides how a review fails, which the refusal does not cover.

`TASK-343` later edits the same sentence to drop the fix and check instruction; this ticket does not.

## Notes

Implemented by the planner on branch `task-342` (worktree `.worktrees/task-342`), commit `4a59e28`: the `work.md` sentence and `tests/test_guide_work_commits.py` as the Description says. `make check` in the worktree: `Ran 583 tests`, `OK`. Untestable, so no cold read or runner review: a human reviews the diff and lands it.

Reviewed: the human reviewed the diff and asked for it to land. Merged `main` into `task-342`, `make check` passed (583 tests OK), and `main` fast-forwarded to `38c2f5f`.

## History

- 2026-11-16T09:59:51Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:32Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:22:49Z kind-umber-toad: changed title, labels, owner, description
- 2026-11-17T16:22:58Z kind-umber-toad: changed description
- 2026-11-17T16:32:59Z kind-umber-toad: changed owner, notes
- 2026-11-17T16:32:59Z kind-umber-toad planning → blocked
- 2026-11-17T17:24:58Z kind-umber-toad blocked → review
- 2026-11-17T17:25:00Z kind-umber-toad: changed notes; overrode review independence
- 2026-11-17T17:25:00Z kind-umber-toad review → done
