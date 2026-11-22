---
title: Record a work-mode rebase failure that is not a conflict as a ticket error
status: planning
depends_on:
  - TASK-370
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. After `TASK-370`, a `rebase_onto` error that is not a conflict restores any saved work and propagates, stopping the run. This ticket records it on the ticket instead. Draft: keep in planning until `TASK-370` lands.

- In work mode, catch that `ChittyError` and record it with `_record_ticket_error(branch_repo, action, "rebase", error)`; the note also says `Uncommitted changes from before the rebase are in refs/chitty/stash/<ID>.` when work was saved and could not be restored. No agent starts.
- Ctrl-C during the rebase runs `git rebase --abort` and raises `RunInterrupted("rebase")` (exit 130). No test: it needs a signal mid-rebase (accepted).

Test, extending `tests/test_run_work_rebases.py`: patch `chitty.git.rebase_onto` to raise `ChittyError`, with an uncommitted file present; the run records `Runner error (rebase)` on the branch and starts no agent, and the uncommitted file is back in the worktree.

## Acceptance Criteria

- [ ] The rebase-failure test passes and fails before the change; `make check` passes

## History

- 2026-11-22T01:29:47Z lively-zinc-newt → planning
