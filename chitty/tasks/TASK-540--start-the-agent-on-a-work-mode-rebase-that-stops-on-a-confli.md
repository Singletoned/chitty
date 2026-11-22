---
title: Start the agent on a work-mode rebase that stops on a conflict
status: cold-read
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22. Today `_rebase_work_worktree(worktree, task_id, main_branch) -> None` in `src/chitty/run.py` aborts a rebase that stops on a conflict and restores any saved work, and `_run_ticket_with_log` calls it for every work-mode ticket right after `_worktree`, recording a `ChittyError` as a `rebase` ticket error (`TASK-545`, `TASK-541`; rechecked on `main` 2026-11-22). This ticket hands the conflict to the agent instead, as the plan says (`docs/plan/ticket-state.md`: any conflict goes to an agent).

Decisions:

- `_rebase_work_worktree` returns `bool`: `True` when it leaves a rebase stopped on a conflict, else `False`. On a conflict it no longer calls `git.abort_rebase` and does not restore saved work: the work stays in `refs/chitty/stash/<ID>` (`TASK-525` tells the agent). The other paths are unchanged.
- In `_run_ticket_with_log`, keep `stopped = _rebase_work_worktree(...)` inside the existing `try`. When `stopped`: skip the `todo` claim, `setup` and `check`, write nothing to the ticket, and go straight to starting the agent (the work agent, or the repair agent for an `error` ticket). The agent command is rendered after the rebase already (`agent_command = _agent_command(...)` follows it), and `guide()` puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress in the worktree.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.

Tests:

- Update case 3 of `tests/test_rebase_work_worktree.py` (the conflict case): the helper now returns `True`, a rebase is in progress, and `refs/chitty/stash/TASK-1` exists (it holds `u.txt`, which is no longer in the worktree).
- Add to `tests/test_run_work_rebases.py`: a rebase that stops on a code conflict, once on a `doing` ticket and once on an `error` ticket (run with `--errors`), starts the agent with a rebase in progress and a prompt in which the body of `src/chitty/roles/rebase.md` directly follows the `Work only on Chitty ticket TASK-<n>.` line, and the fake `setup` records nothing. The fake agent must record its prompt, so its command needs `{prompt}`; find how existing prompt tests configure that (for example `git grep -n "{prompt}" tests`).

The new runner tests fail before the change (today the rebase is aborted and setup runs).

## Acceptance Criteria

- [ ] The conflict runner tests pass for a `doing` and an `error` ticket and fail before the change; the updated helper conflict test passes; `make check` passes

## History

- 2026-11-22T01:29:45Z lively-zinc-newt → planning
- 2026-11-22T02:02:17Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:40:17Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:40:17Z lively-zinc-newt planning → cold-read
