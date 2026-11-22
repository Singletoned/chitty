---
title: Rebase `todo` and `error` tickets before setup in work runs
status: doing
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. `TASK-546` landed the call `if action.mode == "work" and selected_status == "doing": _rebase_work_worktree(worktree, action.id, main_repo.config.main_branch)` in `_run_ticket_with_log` (`src/chitty/run.py`), right after `_worktree` and before the `todo` claim, with tests `test_doing_rebases_before_setup` and `test_todo_does_not_rebase_before_setup` in `tests/test_run_work_rebases.py` (rechecked on `main` 2026-11-22). This ticket rebases every work-mode ticket: `todo` and `error` (repair runs, whose `action.mode` is also `work`) too.

- Change the guard to `if action.mode == "work":`. The rebase stays before the claim; the claim is then written on the rebased branch.
- Delete `test_todo_does_not_rebase_before_setup` and add `test_todo_rebases_before_setup` with the same fixture, asserting setup's recorded log includes `main`'s new commit (the ordering check) and `git log -p task-1 -- chitty/tasks` contains `+status: doing` (the claim; claim commits are titled `chitty: edit TASK-1 ...`, not `doing`).
- Add `test_error_rebases_before_setup`: `TASK-<n>` is `error` on its branch (change `prepare_branch`'s `if status == "doing":` to `if status in ("doing", "error"):` in `tests/test_run_work_rebases.py`, and pass `"error"`), then `chitty run --errors`; setup's recorded log includes `main`'s new commit and the agent started (`(self.logs / "agent").exists()`).
- In `docs/plan/next-action-and-runner.md` (near lines 139-140), change "rebases a `doing` ticket's branch onto `main` before `setup`" to say every work-mode ticket's branch.

Both new tests fail before the change (setup's log lacks `main`'s commit).

## Acceptance Criteria

- [ ] `test_todo_rebases_before_setup` and `test_error_rebases_before_setup` pass and each fails before the change; the doc bullet is updated; `make check` passes

## History

- 2026-11-22T01:47:36Z lively-zinc-newt → planning
- 2026-11-22T01:56:10Z lively-zinc-newt: changed description
- 2026-11-22T02:02:13Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:11:34Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:11:34Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:13:18Z lively-zinc-newt: changed description
- 2026-11-22T03:13:18Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:14:50Z friendly-violet-urchin todo → doing
