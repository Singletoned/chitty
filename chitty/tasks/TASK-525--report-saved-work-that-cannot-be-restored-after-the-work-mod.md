---
title: Report saved work that cannot be restored after the work-mode rebase
status: doing
depends_on:
  - TASK-370
  - TASK-541
  - TASK-552
parent: TASK-370
created: 2026-11-21
---

## Description

Split from `TASK-370`; replanned 2026-11-22 against what landed. A work run saves uncommitted work under `refs/chitty/stash/<ID>` before rebasing the worktree onto `main` (`_rebase_work_worktree` in `src/chitty/run.py`) and restores it afterwards with `git.restore_work`, ignoring its result. When the work does not apply cleanly onto the rebased branch, `restore_work` resets the worktree to `HEAD`, keeps the ref and returns `False`, and today nobody is told. The other cases first listed here are already covered: an existing ref makes `save_work` raise a message naming it, recorded as `Runner error (rebase)` (`TASK-541`); a stopped rebase never holds saved work (`TASK-552` stops only on a clean worktree).

- Right after the `try` around `_rebase_work_worktree` in `_run_ticket_with_log` (before the `todo` claim), in work mode for any ticket status, when it returned `False` and `refs/chitty/stash/<ID>` still exists (`git rev-parse --verify --quiet` in the worktree), add a note to the ticket on its branch: `Repo(worktree, main_repo.config).edit(action.id, Edit(note=..., skip_verdicts=True, skip_current_version=True))` with the text `Uncommitted changes from before the rebase did not apply cleanly; they are in refs/chitty/stash/<ID>.` Then carry on as usual (setup, check, agent).
- Out of scope: naming the ref in the Ctrl-C message.

Tests in `tests/test_run_work_rebases.py`, in a new class like `TestWorkRebases` whose `setUp` replaces the setup script so it writes `git status --porcelain` (not `git log`) to `sys.argv[1]`. `test_unrestorable_work_is_noted`, for a `doing` ticket made as `prepare_branch` does but calling `self.move_main(shared="main\n")` (`tests/test_review_merge.py`) so `main` changes `shared.txt`: create the worktree first (`git worktree add .worktrees/task-1 task-1`), leave an uncommitted edit to line 1 of `shared.txt` in it, and commit a different line 1 of `shared.txt` on `main` (the branch's own commit must not touch `shared.txt`, so the rebase itself succeeds). After a work run: the ticket on `task-1`'s tip has the note naming `refs/chitty/stash/TASK-1`, that ref exists, `git status --porcelain` in the worktree is empty when setup runs (setup recorded), and the agent started. It fails before the change (no note; a cold reader's probe confirmed the rebase succeeds, the ref survives and setup sees a clean worktree). Control `test_restorable_work_is_not_noted`: the same but the uncommitted edit is to a file `main` does not touch; expect no such note and `refs/chitty/stash/TASK-1` gone (passes before and after; guards against always writing the note).

## Acceptance Criteria

- [ ] `test_unrestorable_work_is_noted` passes and fails before the change; `test_restorable_work_is_not_noted` passes
- [ ] `make check` passes

## Plan

Add focused conflicting and clean restore tests, confirm regression, then report surviving saved-work refs after rebase and run checks.

## Notes

Keep in planning until `TASK-370` lands; then replan, cold-read and move to `todo`.

## History

- 2026-11-21T23:11:21Z lively-zinc-newt → planning
- 2026-11-22T01:29:49Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:43:04Z lively-zinc-newt: changed dependencies
- 2026-11-22T04:43:57Z lively-zinc-newt: changed dependencies, description, acceptance criteria
- 2026-11-22T04:43:57Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:45:39Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:45:39Z lively-zinc-newt cold-read → todo
- 2026-11-22T04:46:53Z upbeat-navy-marten todo → doing
- 2026-11-22T04:49:36Z upbeat-navy-marten: wrote the plan
