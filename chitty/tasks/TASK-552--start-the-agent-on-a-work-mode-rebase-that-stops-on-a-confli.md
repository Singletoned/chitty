---
title: Start the agent on a work-mode rebase that stops on a conflict
status: review
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-540` on 2026-11-22. `TASK-540` landed `_rebase_work_worktree(..., *, stop_on_conflict: bool) -> bool` (commit `9027093c`), which can leave a rebase stopped. This ticket starts the agent on a stopped rebase. (`TASK-551`, an extraction of the claim, setup and check, was dropped: those blocks are interleaved with the agent-command render and `Repo.open`.)

- Today the only call passes `stop_on_conflict=False` and ignores the result. Change it to pass `stop_on_conflict=selected_status in ("doing", "error") and not git.uncommitted_paths(worktree)` and keep the result. Decided 2026-11-22: a `todo` ticket's claim cannot be committed during a stopped rebase, and a stopped rebase would leave uncommitted work stranded in `refs/chitty/stash/<ID>` with nothing telling the agent, so in both cases the conflict is still aborted and the run carries on unrebased, as today.
- A conflict in ticket files raises from the helper and is recorded as `Runner error (rebase)` by the existing `except` (`TASK-541`); no new test.
- Out of scope: continuation prompts do not repeat the `rebase.md` text.
- Keep the call inside its existing `try` as `stopped = _rebase_work_worktree(...)` (`stopped = False` outside work mode). When `stopped`, skip exactly three blocks in `_run_ticket_with_log`, leaving everything between them as it is: add `and not stopped` to the `todo` claim condition (`if action.mode == "work" and selected_status == "todo":`), to the setup condition (`if action.mode == "work":` around `_setup`), and guard the `_run_check` call (`if failed := _run_check(...)`) so it does not run when `stopped`. Write nothing to the ticket while stopped; the agent then starts as usual. `agent_command` is already rendered after the rebase, and `guide()` puts the body of `src/chitty/roles/rebase.md` after the `Work only on Chitty ticket <ID>.` line when a rebase is in progress.
- Out of scope: an agent that sets the ticket `done` while the rebase is still stopped.

Tests in `tests/test_run_work_rebases.py`: `test_conflict_doing_starts_agent_with_rebase` and `test_conflict_error_starts_agent_with_rebase` (`--errors`). Each makes `main` and the branch change the same line of a code file, then runs; it asserts the agent started, the agent saw a rebase in progress, its prompt has the `rebase.md` body directly after the `Work only on Chitty ticket TASK-<n>.` line, and `self.logs / "setup"` does not exist. Fake agent contract: a new test class with its own fake agent script that, when started, appends to `self.logs / "prompt"` its last argument (the prompt) and whether `git rev-parse -q --verify REBASE_HEAD` succeeds in its working directory, then exits 0 without changing the ticket (the runner then continues it and finally records `was unchanged`; the tests assert only on the first start and on `self.logs / "setup"`). The worktree must be clean before the run; conflict on a non-ticket file (for example `move_main(shared=...)` in `tests/test_review_merge.py` plus a matching branch edit). The fake agent must receive `{prompt}`: the existing forms are `agent_command = "fake-agent {mode} {id} {prompt}"` (`tests/test_run_continue.py`) and `"fake-agent {prompt}"` (`tests/test_run_repair_mode.py`); use one in a new test class rather than changing `ReviewMergeTestCase`, because `{prompt}` also enables continuations for every test in that class.

## Acceptance Criteria

- [ ] Both conflict runner tests pass and fail before the change; `make check` passes
- [ ] A third test shows a conflicting `doing` ticket with an uncommitted file in its worktree is still aborted: setup runs and no rebase is in progress when the agent starts

## Plan

Add conflict runner tests with a prompt-recording agent, verify regression, then gate rebase preparation and run checks.

## Notes

Planner correction 2026-11-22 04:3x: a planner tooling slip replaced this Description with an older draft at 04:30 (it named a nonexistent `_prepare_work_session`). The Description is now the intended text: gate the three blocks with a `stopped` flag, stop only for `doing`/`error` tickets with a clean worktree, and the fake-agent contract. Please work from this version.

Before the fix, both stopped-rebase tests fail on the prompt/rebase assertion; the dirty-worktree test passes.

## Summary

Start agents on stopped clean work rebases; preserve abort for dirty worktrees. Both conflict tests failed before the fix and pass after it; make check passes.

## History

- 2026-11-22T03:43:02Z lively-zinc-newt → planning
- 2026-11-22T04:28:11Z lively-zinc-newt: changed dependencies, description
- 2026-11-22T04:28:54Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:30:35Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:30:35Z lively-zinc-newt cold-read → todo
- 2026-11-22T04:30:59Z intrepid-ginger-gannet todo → doing
- 2026-11-22T04:31:20Z lively-zinc-newt: changed description, notes
- 2026-11-22T04:32:54Z intrepid-ginger-gannet: wrote the plan
- 2026-11-22T04:33:40Z intrepid-ginger-gannet: changed notes
- 2026-11-22T04:35:37Z intrepid-ginger-gannet: changed summary
- 2026-11-22T04:37:10Z intrepid-ginger-gannet doing → review
