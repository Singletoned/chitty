---
title: Start the agent on a work-mode rebase that stops on a conflict
status: planning
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-540` on 2026-11-22. `TASK-540` landed `_rebase_work_worktree(..., *, stop_on_conflict: bool) -> bool` (commit `9027093c`), which can leave a rebase stopped. This ticket starts the agent on a stopped rebase. (`TASK-551`, an extraction of the claim, setup and check, was dropped: those blocks are interleaved with the agent-command render and `Repo.open`.)

- Call the helper with `stop_on_conflict=selected_status in ("doing", "error")` (decided 2026-11-22: a `todo` ticket's claim cannot be committed during a stopped rebase, so a conflicting `todo` ticket is still aborted and carries on unrebased).
- Keep the call inside its existing `try` as `stopped = _rebase_work_worktree(...)` (`stopped = False` outside work mode). When `stopped`, skip exactly three blocks in `_run_ticket_with_log`, leaving everything between them as it is: add `and not stopped` to the `todo` claim condition (`if action.mode == "work" and selected_status == "todo":`), to the setup condition (`if action.mode == "work":` around `_setup`), and guard the `_run_check` call (`if failed := _run_check(...)`) so it does not run when `stopped`. Write nothing to the ticket while stopped; the agent then starts as usual. `agent_command` is already rendered after the rebase, and `guide()` puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress.
- Out of scope: an agent that sets the ticket `done` while the rebase is still stopped.

Tests in `tests/test_run_work_rebases.py`: `test_conflict_doing_starts_agent_with_rebase` and `test_conflict_error_starts_agent_with_rebase` (`--errors`). Each makes `main` and the branch change the same line of a code file, then runs; it asserts the agent started, the agent saw a rebase in progress, its prompt has the `rebase.md` body directly after the `Work only on Chitty ticket TASK-<n>.` line, and `self.logs / "setup"` does not exist. The fake agent must receive `{prompt}`: the existing forms are `agent_command = "fake-agent {mode} {id} {prompt}"` (`tests/test_run_continue.py`) and `"fake-agent {prompt}"` (`tests/test_run_repair_mode.py`); use one in a new test class rather than changing `ReviewMergeTestCase`, because `{prompt}` also enables continuations for every test in that class.

## Acceptance Criteria

- [ ] Both conflict runner tests pass and fail before the change; `make check` passes

## History

- 2026-11-22T03:43:02Z lively-zinc-newt → planning
- 2026-11-22T04:28:11Z lively-zinc-newt: changed dependencies, description
