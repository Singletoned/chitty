---
title: Start the agent on a work-mode rebase that stops on a conflict
status: todo
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-540` on 2026-11-22. After `TASK-540` and `TASK-551`, `_rebase_work_worktree(..., stop_on_conflict=...)` can leave a rebase stopped, and the work-mode claim, setup and check live in `_prepare_work_session`. This ticket starts the agent on a stopped rebase. Draft: keep in planning until both land, then check names and cold-read.

- Call the helper with `stop_on_conflict=selected_status in ("doing", "error")` (decided 2026-11-22: a `todo` ticket's claim cannot be committed during a stopped rebase, so a conflicting `todo` ticket is still aborted and carries on unrebased).
- When it returns `True`, skip `_prepare_work_session` entirely and write nothing to the ticket; go straight to starting the agent. `agent_command` is already rendered after the rebase, and `guide()` puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress.
- Out of scope: an agent that sets the ticket `done` while the rebase is still stopped.

Tests in `tests/test_run_work_rebases.py`: `test_conflict_doing_starts_agent_with_rebase` and `test_conflict_error_starts_agent_with_rebase` (`--errors`). Each makes `main` and the branch change the same line of a code file, then runs; it asserts the agent started, the agent saw a rebase in progress, its prompt has the `rebase.md` body directly after the `Work only on Chitty ticket TASK-<n>.` line, and `self.logs / "setup"` does not exist. The fake agent must receive `{prompt}`: the existing forms are `agent_command = "fake-agent {mode} {id} {prompt}"` (`tests/test_run_continue.py`) and `"fake-agent {prompt}"` (`tests/test_run_repair_mode.py`); use one in a new test class rather than changing `ReviewMergeTestCase`, because `{prompt}` also enables continuations for every test in that class.

## Acceptance Criteria

- [ ] Both conflict runner tests pass and fail before the change; `make check` passes
- [ ] A third test shows a conflicting `doing` ticket with an uncommitted file in its worktree is still aborted: setup runs and no rebase is in progress when the agent starts

## History

- 2026-11-22T03:43:02Z lively-zinc-newt → planning
- 2026-11-22T04:28:11Z lively-zinc-newt: changed dependencies, description
- 2026-11-22T04:28:54Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:30:35Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:30:35Z lively-zinc-newt cold-read → todo
