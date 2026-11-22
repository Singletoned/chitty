---
title: Rebase `todo` and `error` tickets before setup in work runs
status: cold-read
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. `TASK-546` landed the call `if action.mode == "work" and selected_status == "doing": _rebase_work_worktree(worktree, action.id, main_repo.config.main_branch)` in `_run_ticket_with_log` (`src/chitty/run.py`), right after `_worktree` and before the `todo` claim, with tests `test_doing_rebases_before_setup` and `test_todo_does_not_rebase_before_setup` in `tests/test_run_work_rebases.py` (rechecked on `main` 2026-11-22). This ticket rebases every work-mode ticket: `todo` and `error` (repair runs, whose `action.mode` is also `work`) too.

- Change the guard to `if action.mode == "work":`. The rebase stays before the claim; the claim is then written on the rebased branch.
- Replace `test_todo_does_not_rebase_before_setup` with `test_todo_rebases_before_setup`: the same fixture, asserting setup's recorded log includes `main`'s new commit and the claim commit (`doing`) is on the branch.
- Add `test_error_rebases_before_setup`: `TASK-<n>` is `error` on its branch (use the fixture of `test_doing_rebases_before_setup` and set the ticket to `error` on the branch before `main` gains its commit), then `chitty run --errors`; setup's recorded log includes `main`'s new commit and the repair agent starts.
- Update the `docs/plan/next-action-and-runner.md` bullet `TASK-546` wrote, which says `doing`, to say every work-mode ticket.

Both new tests fail before the change (setup's log lacks `main`'s commit).

## Acceptance Criteria

- [ ] `test_todo_rebases_before_setup` and `test_error_rebases_before_setup` pass and each fails before the change; the doc bullet is updated; `make check` passes

## History

- 2026-11-22T01:47:36Z lively-zinc-newt → planning
- 2026-11-22T01:56:10Z lively-zinc-newt: changed description
- 2026-11-22T02:02:13Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:11:34Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:11:34Z lively-zinc-newt planning → cold-read
