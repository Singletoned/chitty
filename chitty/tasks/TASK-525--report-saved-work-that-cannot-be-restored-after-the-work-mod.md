---
title: Report saved work that cannot be restored after the work-mode rebase
status: cold-read
depends_on:
  - TASK-370
  - TASK-541
  - TASK-552
parent: TASK-370
created: 2026-11-21
---

## Description

Split from `TASK-370`; replanned 2026-11-22 against what landed. A work run saves uncommitted work under `refs/chitty/stash/<ID>` before rebasing the worktree onto `main` (`_rebase_work_worktree` in `src/chitty/run.py`) and restores it afterwards with `git.restore_work`, ignoring its result. When the work does not apply cleanly onto the rebased branch, `restore_work` resets the worktree to `HEAD`, keeps the ref and returns `False`, and today nobody is told. The other cases first listed here are already covered: an existing ref makes `save_work` raise a message naming it, recorded as `Runner error (rebase)` (`TASK-541`); a stopped rebase never holds saved work (`TASK-552` stops only on a clean worktree).

- After `_rebase_work_worktree` returns `False` in `_run_ticket_with_log`, if `refs/chitty/stash/<ID>` still exists (`git rev-parse --verify --quiet` in the worktree), add a note to the ticket on its branch: `Repo(worktree, main_repo.config).edit(action.id, Edit(note=..., skip_verdicts=True, skip_current_version=True))` with the text `Uncommitted changes from before the rebase did not apply cleanly; they are in refs/chitty/stash/<ID>.` Then carry on as usual (setup, check, agent).
- Out of scope: naming the ref in the Ctrl-C message.

Test `test_unrestorable_work_is_noted` in `tests/test_run_work_rebases.py`, with its `prepare_branch` fixture for a `doing` ticket: create the worktree first (`git worktree add .worktrees/task-1 task-1`), leave an uncommitted edit to line 1 of `shared.txt` in it, and commit a different line 1 of `shared.txt` on `main` (the branch's own commit must not touch `shared.txt`, so the rebase itself succeeds). After a work run: the ticket on `task-1`'s tip has the note naming `refs/chitty/stash/TASK-1`, that ref exists, `git status --porcelain` in the worktree is empty when setup runs (setup recorded), and the agent started. It fails before the change (no note).

## Acceptance Criteria

- [ ] `test_unrestorable_work_is_noted` passes and fails before the change
- [ ] `make check` passes

## Notes

Keep in planning until `TASK-370` lands; then replan, cold-read and move to `todo`.

## History

- 2026-11-21T23:11:21Z lively-zinc-newt → planning
- 2026-11-22T01:29:49Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:43:04Z lively-zinc-newt: changed dependencies
- 2026-11-22T04:43:57Z lively-zinc-newt: changed dependencies, description, acceptance criteria
- 2026-11-22T04:43:57Z lively-zinc-newt planning → cold-read
