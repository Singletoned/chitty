---
title: Rebase a `doing` ticket's worktree onto `main` before setup in work runs
status: review
labels:
  - needs-minor
depends_on:
  - TASK-370
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. `TASK-370` adds `_rebase_work_worktree(worktree, task_id, main_branch)` in `src/chitty/run.py`, tested directly. This ticket calls it from the runner. `TASK-370` landed `_rebase_work_worktree(worktree: Path, task_id: TaskId, main_branch: str) -> None` on `main` (rechecked 2026-11-22).

- In `_run_ticket_with_log` (already over 100 lines; add only the call), call it right after `worktree = _worktree(...)` and before the `if action.mode == "work":` block that writes the `todo` claim and runs `setup`, guarded by `action.mode == "work" and selected_status == "doing"`. Use `selected_status` (the status when the run chose the ticket), not the status after the claim, so `todo` tickets are not rebased yet. Remove the `# pyright: ignore[reportUnusedFunction]` on the helper once it is called. Review mode is unchanged. `TASK-545` extends it to `todo` and `error`.
- Interim behaviour (decided 2026-11-22): on a conflict the helper has already aborted the rebase, so the run carries on with the branch as it was (`TASK-540` will hand the conflict to the agent); a `ChittyError` from the helper propagates and the run exits 1 (`TASK-541` will record it on the ticket).
- Update the bullet starting `- Work mode makes or reuses the worktree` (near line 139, under `## Before a review`) in `docs/plan/next-action-and-runner.md` to say work mode rebases a `doing` ticket's branch onto `main` before `setup`, saving uncommitted work under `refs/chitty/stash/<ID>`.

Test in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py` (`ReviewMergeTestCase`): a `doing` ticket whose branch exists, then a commit on `main` touching another file, with `setup` recording `git log --format=%s` of its worktree. Fixture: subclass `ReviewMergeTestCase`; in `setUp`, after `super().setUp()`, overwrite `self.tmp / "setup.py"` (which the base `chitty.toml` already runs as `setup`, writing to `self.logs / "setup"`) with a script that writes `subprocess.check_output(["git", "log", "--format=%s"], text=True)` to `sys.argv[1]`. Do not edit `chitty.toml`. The fake agent leaves the work ticket unchanged, so the run ends `doing → error`; that does not affect these assertions. After a work run, setup's recorded log includes `main`'s new commit, and `git merge-base --is-ancestor main task-<n>` succeeds. It fails before the change (a cold reader's probe on `main` 2026-11-22: setup's log lacks `main`'s commit). Also run the same fixture with the ticket `todo` and assert setup's log does not include `main`'s commit, guarding the `selected_status` choice.

## Acceptance Criteria

- [ ] The `doing` runner test passes and fails before the change, and the `todo` guard passes; the doc bullet is updated; `make check` passes

## Plan

Add runner integration regression tests for doing and todo, verify the doing test fails first, then call the existing helper and update the runner plan documentation. Run formatting and checks.

## Notes

Regression verified before the fix: doing test fails because setup log lacks main moved; todo guard passes.

## Summary

Rebase doing worktrees before setup; todo remains unchanged. Regression failed before the fix and both tests pass afterwards; make check passes.

## History

- 2026-11-22T02:02:11Z lively-zinc-newt → planning
- 2026-11-22T02:21:20Z lively-zinc-newt: changed description
- 2026-11-22T02:21:20Z lively-zinc-newt planning → cold-read
- 2026-11-22T02:23:29Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T02:23:29Z lively-zinc-newt cold-read → todo
- 2026-11-22T02:56:18Z eager-russet-vole todo → doing
- 2026-11-22T02:58:39Z eager-russet-vole: wrote the plan
- 2026-11-22T02:58:58Z eager-russet-vole: changed notes
- 2026-11-22T03:01:34Z eager-russet-vole: changed summary
- 2026-11-22T03:03:06Z eager-russet-vole doing → review
