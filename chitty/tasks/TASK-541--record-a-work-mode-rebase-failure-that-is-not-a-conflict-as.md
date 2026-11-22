---
title: Record a work-mode rebase failure that is not a conflict as a ticket error
status: review
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. Today `_rebase_work_worktree` (`src/chitty/run.py`) restores any saved work and re-raises a `ChittyError` from `git.rebase_onto` that is not a conflict, so the run stops with exit 1 (`TASK-546`'s interim behaviour). This ticket records it on the ticket instead, as other runner phases do. Rechecked on `main` 2026-11-22.

- In `_run_ticket_with_log`, wrap the work-mode `_rebase_work_worktree(...)` call (right after `_worktree`) in `try`/`except ChittyError as error:` and `return _record_ticket_error(Repo(worktree, main_repo.config), action, "rebase", error)` (`_record_ticket_error(branch_repo, action, phase, error)` writes `status: error` and a `Runner error (rebase)` note on the branch). No agent starts.
- Every `ChittyError` from the helper is recorded this way, including `save_work`'s `refs/chitty/stash/<ID> already exists ...` refusal, whose message already names the ref. Naming a ref left behind by a failed restore is `TASK-525`.
- Ctrl-C during the rebase is out of scope (it needs a signal mid-rebase).

Test `test_rebase_failure_is_recorded` in `tests/test_run_work_rebases.py`, using its `prepare_branch` fixture for a `doing` ticket: create the worktree first with `git worktree add .worktrees/task-1 task-1` (the run reuses it), put an untracked `u.txt` in it, patch `chitty.run.git.rebase_onto` to raise `ChittyError("boom")`, and run a work run. Assert the run exits 0, the ticket on `task-<n>`'s tip has `status: error` and a note containing `Runner error (rebase)` and `boom`, the agent did not start (`(self.logs / "agent")` does not exist), `u.txt` has its contents, and `refs/chitty/stash/TASK-<n>` does not exist. It fails before the change on the exit code (the run exits 1 today, verified by a cold reader's probe); the stash-ref assertion is a guard that holds before and after.

## Acceptance Criteria

- [ ] `test_rebase_failure_is_recorded` passes and fails before the change; `make check` passes

## Plan

Add the specified failing regression test, record its pre-fix result, then handle rebase errors through the existing ticket error recorder and run formatting and checks.

## Notes

Regression test failed before the fix: run exited 1 rather than 0 with Error: boom.

## Summary

Records work-mode rebase errors on the branch ticket without starting the agent. Regression test failed before the fix on exit code 1 and passes afterward; make check passed.

## History

- 2026-11-22T01:29:47Z lively-zinc-newt → planning
- 2026-11-22T02:02:20Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:13:44Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:13:44Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:14:54Z lively-zinc-newt: changed description
- 2026-11-22T03:14:54Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:23:18Z brisk-hazel-gannet todo → doing
- 2026-11-22T03:25:46Z brisk-hazel-gannet: wrote the plan
- 2026-11-22T03:26:03Z brisk-hazel-gannet: changed notes
- 2026-11-22T03:28:17Z brisk-hazel-gannet: changed summary
- 2026-11-22T03:30:03Z brisk-hazel-gannet doing → review
