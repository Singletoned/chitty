---
title: Report saved work that cannot be restored after the work-mode rebase
status: planning
depends_on:
  - TASK-370
  - TASK-540
  - TASK-541
parent: TASK-370
created: 2026-11-21
---

## Description

Split from `TASK-370` on 2026-11-21. `TASK-370` saves uncommitted work under `refs/chitty/stash/<ID>` with `git.save_work` (`TASK-524`) before rebasing a work worktree, and restores it with `git.restore_work`. This ticket handles the cases where the saved work cannot come straight back. Draft: replan against what `TASK-370` and `TASK-524` land before moving to `todo`.

- `restore_work` returns `False` (applying conflicts): add a note on the ticket through `branch_repo`: `Uncommitted changes from before the rebase did not apply cleanly; they are in refs/chitty/stash/<ID>.` Then carry on to `setup`, `check` and the agent.
- `save_work` raises because `refs/chitty/stash/<ID>` already exists from an earlier run: record it as a ticket error on the branch (`_record_ticket_error(branch_repo, ...)`, phase `rebase`) with that message; no agent starts.
- The rebase stops on a conflict after work was saved: the agent's prompt adds `Uncommitted changes from before the rebase are in refs/chitty/stash/<ID>; re-apply them with git stash apply after the rebase if they are still useful, then delete the ref.`
- Ctrl-C during the rebase: the interrupt message names the ref (no test: needs a signal mid-rebase).

Tests: real-Git, fake-agent runner tests in `tests/test_run_work_rebases.py`, extending `TASK-370`'s fixtures.

## Acceptance Criteria

- [ ] When applying the saved work conflicts (`main` changed the same lines as an uncommitted edit), the worktree matches `HEAD` when the agent starts, `refs/chitty/stash/TASK-<n>` exists and is named in a note on the branch's ticket, and the agent starts
- [ ] A run that finds `refs/chitty/stash/TASK-<n>` already present records `Runner error (rebase)` naming the ref and starts no agent; a rebase stopped on a conflict with work saved gives a prompt naming the ref; `make check` passes

## Notes

Keep in planning until `TASK-370` lands; then replan, cold-read and move to `todo`.

## History

- 2026-11-21T23:11:21Z lively-zinc-newt → planning
- 2026-11-22T01:29:49Z lively-zinc-newt: changed dependencies
