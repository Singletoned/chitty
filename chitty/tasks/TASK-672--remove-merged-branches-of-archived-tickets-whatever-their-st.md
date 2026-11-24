---
title: Remove merged branches of archived tickets whatever their status
status: planning
labels:
  - bug
created: 2026-11-24
---

## Description

### Why

`_remove_merged_branches` in `src/chitty/run.py` (around line 331) keeps every merged ticket branch whose ticket is not `done`. A ticket archived without reaching `done` keeps its status, for example `planning`, so its branch and worktree are kept forever, and every `chitty run` prints a line about it.

Evidence, echonomicon, 2026-11-24: TASK-160 and TASK-164 were archived from `planning` because their work was already on `main`. Their branches `task-160` and `task-164` have no commits beyond `main` and clean worktrees, yet every run prints `kept merged branch task-160: TASK-160 is planning`.

### Change

In `_remove_merged_branches`, keep a branch for its status only when the ticket is not archived:

`if stored is not None and not stored.archived and stored.task.frontmatter.status != "done":`

`StoredTask.archived` is already set by `Repo.lookup`. Every other reason to keep a branch (run lock held, main checkout, uncommitted changes, rebase or merge in progress) still applies, in the same order. With `archive = "delete"` the ticket file is gone, `lookup` returns `None`, and the branch is already removed as an unknown ticket, so nothing changes there.

Decided: an archived ticket counts as finished whatever its status. Archiving is a deliberate close, and the branch is only removed when it holds nothing beyond `main`.

### Tests

No property: the input is the fixed set of statuses in `chitty.model.STATUSES`, and the first test covers every member except `done` (already covered by `test_removes_done_and_unknown_branches`). Follow `test_keeps_non_done_statuses`: `self.json("add", ..., "-s", status)`, then `self.run_cli("archive", ticket)` (the fixture has `autocommit = true`, so the archive is committed on `main`), then `self.git("branch", ticket.lower())`. Create the branches after archiving, so each is an ancestor of `main`.

### Out of scope

The `dropped` status (TASK-599) and any change to `chitty archive` itself.

## Acceptance Criteria

- [ ] A new test in `tests/test_run_removes_merged_branches.py` adds one ticket in each status in `chitty.model.STATUSES` other than `done`, archives each with `chitty archive`, makes a branch for each at `main`, and runs `chitty run --errors`: every branch is deleted and stderr has `removed merged branch <branch>` for each. It fails without the change.
- [ ] A second new test archives a `planning` ticket whose merged branch has a worktree with an untracked file: the branch is kept and stderr has `kept merged branch <branch>: worktree has uncommitted changes`. `test_keeps_non_done_statuses` (tickets not archived) still passes unchanged, and `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:35Z zesty-coral-newt → backlog
- 2026-11-24T22:21:36Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:46Z zesty-coral-newt: changed labels
- 2026-11-24T22:48:31Z zesty-coral-newt: changed title, labels, description, acceptance criteria
- 2026-11-24T22:48:31Z zesty-coral-newt backlog → planning
