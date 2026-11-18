---
title: Sync a ticket file newer on another branch into its worktree before a work session
status: cold-read
labels:
  - bug
priority: high
created: 2026-11-18
---

## Description

Seen 2026-11-17 on `TASK-343`. An error repair committed `error → todo` to the ticket on `main` after the branch `task-343` last committed it. The next `chitty run` ran `check` in the worktree, then the claim (`work_repo.edit(action.id, claim_edit())` in `_run_ticket`, `src/chitty/run.py`) failed with `TASK-343's latest committed version is on branch main; run Chitty in worktree <main checkout>` (`Repo._require_current_version`, `src/chitty/store.py`) and stopped `chitty run --loop`.

Principle (decided 2026-11-18): bringing a ticket branch up to date is mechanical and done by the runner; only code conflicts go to an agent. The ticket file is Chitty's own data, so the runner can always bring it up to date.

Decisions:

- New helper `_sync_ticket(worktree: Path, task_id: TaskId) -> bool` in `src/chitty/run.py`. It opens `Repo.open(worktree)` and finds the ticket. When the found version's `branch` is set and is not the worktree's current branch, and the worktree's ticket file is not dirty (`git.dirty_paths`), it writes that version's content byte for byte to the worktree path and commits only that file with the message `chitty: sync <ID> from <branch>` and a `Task: <ID>` trailer. It returns whether it committed.
- Call it in work mode only, in `_run_ticket`, after `setup` and before `check`, for every ticket status. `TASK-370` will also call it after an aborted merge.
- A dirty worktree ticket file is left alone, and the run continues as today.
- No change to review mode, which merges `main` (`_prepare_review`; ticket-file conflicts are `TASK-359`), or to the stale-copy guard.

Out of scope: merging `main` in work mode (`TASK-370`).

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_syncs_ticket.py`, in the style of `tests/test_review_merge.py`. Commit the `main` edit after the branch edit with a later `GIT_COMMITTER_DATE`, as `tests/test_store.py` does. No property: the behaviour is real Git and runner processes over the small fixed set of cases in the criteria, and its only decision (sync or not) reads three Git facts with no pure core worth separating.

## Acceptance Criteria

- [ ] The `TASK-343` case: a `todo` ticket whose branch exists, with a later edit to the ticket on `main`; a work run commits `chitty: sync` on the branch with the worktree ticket file equal to `main`'s copy byte for byte, claims the ticket and starts the agent; the test fails before the change
- [ ] The same state on an `error` ticket syncs and starts the repair agent
- [ ] With the worktree ticket file dirty, no sync commit is made and the dirty content is unchanged
- [ ] A second work run with no newer edit elsewhere adds no sync commit
- [ ] `make check` passes

## History

- 2026-11-18T09:24:53Z witty-ginger-falcon → cold-read
- 2026-11-18T09:25:14Z witty-ginger-falcon: changed dependencies
