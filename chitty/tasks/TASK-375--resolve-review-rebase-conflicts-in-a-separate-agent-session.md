---
title: Resolve review rebase conflicts in a separate agent session
status: review
priority: medium
depends_on:
  - TASK-374
  - TASK-373
  - TASK-401
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model (`docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`) a ticket file changes only on its branch, so it rebases like any other file; there is no ticket merge. Any conflict goes to an agent.

When the rebase before a review (`TASK-374`) stops on a code conflict, the review fails back to `doing`, and a full work session is spent on what is only conflict resolution. A separate, cheaper agent session should resolve it, so conflict context never mixes with review context.

Starts after `TASK-373` and `TASK-374` land: `chitty guide rebase` and `git.rebase_onto` do not exist yet.

Decisions:

- New session mode `rebase`. When `git.rebase_onto` in `_prepare_review` returns conflicts, instead of aborting, the runner starts one agent session in the worktree, then carries on. The action's mode stays `review`; the session's mode is `rebase`. `_agent_command` in `src/chitty/run.py` becomes `_agent_command(repo, action, agent, worktree, mode)`, both new arguments required (every existing caller, in `_run_ticket` and `_agent_sessions`, passes the ticket worktree and `action.mode`); it takes the session mode (overriding both the mode it derives from the ticket's status and the `repair` guide it picks for an `error` ticket), and is called for the session inside `_prepare_review`, after the worktree exists, with the worktree as `guide()`'s directory (`TASK-373`); so the session gets `{mode}` `rebase`, the `{prompt}` from `guide("rebase", ...)`, and the `rebase` model: `_run_session` gains a required `mode` argument and passes it to `_model_arguments(mode=...)` (`TASK-401`); existing callers pass `action.mode`. With mode `rebase`, an `agent_command` without `{prompt}` raises `ChittyError` (`the rebase session needs {prompt} in agent_command`), handled as a session failure below. `_prepare_review` gains `agent`, `project` and `environment` parameters, passed by `_run_ticket`. The agent environment (the runner's `chitty` on `PATH`) is built before `_prepare_review` is called rather than inside the agent phase; a missing runner `chitty` is then recorded as a ticket error with phase `review preparation`. No continuations. `agent_timeout` applies.
- Success: the session exits 0, no rebase is in progress, and the worktree is clean. `_prepare_review` then carries on as after a clean rebase (config and `AGENTS.md` checks, `setup`, `check`), and a separate reviewer session starts. Those later checks can still fail the review as today.
- Failure: non-zero exit, `agent_timeout` expiry, a rebase still in progress, or uncommitted files. `_prepare_review` catches the session's `ChittyError` itself, so it never reaches `_record_ticket_error`. It runs `git rebase --abort` if a rebase is in progress, and fails the review with the note `Review failed (integration): rebasing onto `main` conflicts in <paths>; the rebase session failed: <error>`, where `<paths>` are the paths `rebase_onto` returned, each in backticks, and `<error>` is the first line of the session's `ChittyError` text only (`agent exited with status N:`, `agent timed out after N seconds:`, `rebase still in progress`, or the uncommitted paths), so the note stays one line. "Clean" means `git.uncommitted_paths` is empty; add a `git.abort_rebase` helper beside `git.rebase_in_progress`. No reviewer starts.
- Ctrl-C during the session: `_run_session` already turns `KeyboardInterrupt` into `RunInterrupted("agent")`; `_prepare_review` catches both `RunInterrupted` and `KeyboardInterrupt` around the session, aborts the rebase if one is in progress, and re-raises it as `RunInterrupted("rebase")` (exit 130). No reviewer starts.
- The session writes no ticket fields and records no verdict. It writes its own usage-log line (`_run_ticket` writes one per ticket run, in its `finally`), in a `finally` around the session so it is written on success, failure and interrupt: mode `rebase`, `status_before` `review`, `status_after` the ticket's status when the session returns, and `started` and `seconds` timing the session only.
- Document the session, its mode and its failure note under `## Before a review` in `docs/plan/next-action-and-runner.md`.

Tests: real-Git runner tests with a fake agent command in a new `tests/test_review_rebase_session.py`, inheriting `CliTestCase` from `tests/test_cli.py` as `tests/test_review_merge.py` does, so usage logs go to a temporary `XDG_DATA_HOME`. The fake agent's behaviour is chosen per test. Outcome table, the full product of 12 rows, one test per row: {exit 0, exit 1, timeout} by {rebase finished, rebase still stopped} by {worktree clean, uncommitted file}. Exactly the row (exit 0, finished, clean) starts the reviewer; every other row ends with `Review failed (integration)`, no rebase in progress, and no reviewer. No property: a fixed table of real-process outcomes.

## Acceptance Criteria

- [x] A review run whose rebase stops on a code conflict starts one fake agent with `{mode}` `rebase` and the `chitty guide rebase` prompt; when it resolves and finishes the rebase, a separate reviewer session starts on the rebased branch; the fake agent writes no ticket file, and the fixture puts its ticket commit before the conflicting commit, so the ticket file's bytes at session start (after the rebase stops) equal those at session end; the test fails before the change
- [x] Every other row of the outcome table ends with no rebase in progress, the ticket `doing` with the failure note naming the paths `rebase_onto` returned and the session's error text, and no reviewer started; none moves the ticket to `error`
- [x] With `rebase_model` set, the rebase session command gets `--model <value>` and the reviewer gets `review_model`'s; with `_run_session` patched to raise `RunInterrupted("agent")` for the rebase session, no rebase is in progress afterwards, the run exits 130 with `interrupted during rebase`, and no reviewer starts; an `agent_command` without `{prompt}` fails the review with `the rebase session needs {prompt}`
- [x] The usage log has a separate line with mode `rebase` for the session; `docs/plan/config.md` lists `rebase_model` and its unset behaviour, and `## Before a review` names the session, its mode and its failure note; `make check` passes

## Plan

Implement the dedicated rebase session inside `_prepare_review`, using the existing `rebase_model`, `git.rebase_onto`, and `git.abort_rebase`. Extend `_agent_command` with required worktree and explicit session mode, and `_run_session` with required mode so rebase uses the rebase guide/model independently of ticket status; update all existing callers. Build the selected agent environment before review preparation and pass agent/project/environment through. On a conflict, run one timed session without continuations, record a separate rebase usage line in `finally`, then require exit 0, no active rebase, and a clean worktree before continuing review preparation. On errors fail back to doing with a one-line integration note containing conflict paths and first-line error; abort any stopped rebase. Translate interruption to `RunInterrupted("rebase")`. Add real-Git tests for all 12 exit/rebase/worktree combinations, prompt/guide and ticket-file preservation, model selection, interruption, missing prompt, and usage logging. Document rebase-session behavior and failure note. First run regression tests against pre-change behavior, then focused tests, `make format`, `make check`, `chitty fix`, inspect diff, and commit implementation with Task: TASK-375.

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

Regression evidence: the successful-conflict test fails against the prior abort-on-conflict preparation behavior because no rebase-resolution or reviewer agent starts. The real-Git suite covers all 12 exit/rebase/worktree combinations, mode/model selection, interrupted sessions, prompt validation, usage records, and unchanged ticket bytes across rebase-session execution.

## Summary

Implemented the dedicated `rebase` session when review rebasing conflicts. It uses the rebase guide and configured model, runs once without continuations, verifies the rebase finished and worktree is clean, aborts stopped rebases on failure/interruption, records its own usage line, and returns failed reviews to `doing` with a one-line integration note. Updated runner design docs. Verification: the new real-Git suite passes (14 tests); `make check` passes (768 tests), `make format` and `chitty fix` completed. The success regression was shown failing with the prior abort-on-conflict behavior. Follow-up: none.

## History

- 2026-11-18T09:51:22Z witty-ginger-falcon → planning
- 2026-11-18T09:52:36Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:28Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:29Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:31Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:48Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:48Z witty-ginger-falcon todo → planning
- 2026-11-18T18:02:34Z lively-quartz-crane: changed description
- 2026-11-18T18:02:34Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:18:12Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:18:12Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:18:14Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:19:57Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:19:57Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:19:59Z lively-quartz-crane planning → todo
- 2026-11-19T16:18:42Z zesty-dusky-zander todo → doing
- 2026-11-19T16:20:04Z zesty-dusky-zander: wrote the plan
- 2026-11-19T17:10:49Z zesty-dusky-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-19T17:10:49Z zesty-dusky-zander doing → review
