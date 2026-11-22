---
title: Start the agent on a work-mode rebase that stops on a conflict
status: planning
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. After `TASK-370`, a work run rebases the ticket worktree onto `main` (`_rebase_work_worktree` in `src/chitty/run.py`) and, if the rebase stops on a conflict, aborts it. This ticket hands the conflict to the agent instead. Draft: keep in planning until `TASK-370` lands, then check its landed code and cold-read.

- When the rebase stops on a conflict (any file): leave it stopped and the saved-work ref in place, skip `setup` and `check`, and start the agent (the work agent, or the repair agent for an `error` ticket). Write nothing to the ticket while the rebase is stopped.
- Prompt rendering (rechecked 2026-11-21): `_agent_command` already passes the worktree to `guide()`, and `guide()` puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress there. `_run_ticket_with_log` renders the command twice; move the second rendering to after the rebase so the prompt reflects the stopped rebase.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.

Test, extending `tests/test_run_work_rebases.py`: a rebase that stops on a code conflict, once on a `doing` ticket and once on an `error` ticket, starts the work agent or the repair agent respectively with a rebase in progress and a prompt in which the body of `src/chitty/roles/rebase.md` directly follows the `Work only on Chitty ticket TASK-<n>.` line (recorded by a fake agent whose command has `{prompt}`); a fake `setup` and `check` record that they did not run. Replaces `TASK-370`'s interim conflict case.

## Acceptance Criteria

- [ ] The conflict test passes for a `doing` and an `error` ticket and fails before the change; `make check` passes

## History

- 2026-11-22T01:29:45Z lively-zinc-newt → planning
- 2026-11-22T02:02:17Z lively-zinc-newt: changed dependencies
