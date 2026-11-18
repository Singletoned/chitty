---
title: Resolve review rebase conflicts in a separate agent session
status: planning
priority: medium
depends_on:
  - TASK-374
  - TASK-373
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

When the rebase before a review (`TASK-374`) stops on a code conflict, the review fails back to `doing`, and a full work session is spent on what is only conflict resolution. A separate, cheaper agent session should resolve it, so conflict context never mixes with review context.

Starts after `TASK-373` and `TASK-374` land: `chitty guide rebase` and `git.rebase_onto` do not exist yet.

Decisions:

- New session mode `rebase`. When `git.rebase_onto` in `_prepare_review` returns conflicts, instead of aborting, the runner starts one agent session in the worktree, then carries on. The action's mode stays `review`; the session's mode is `rebase`. `_agent_command` and `_model_arguments` in `src/chitty/run.py` take the session mode as an argument instead of reading `action.mode`, so the session gets `{mode}` `rebase`, the `{prompt}` from `guide("rebase", ...)` with the worktree as its directory, and the `rebase` model. No continuations. `agent_timeout` applies.
- New optional setting `rebase_model`, handled like `work_model` and `review_model` in `src/chitty/config.py` (field, validator, commented template line) and in the `chitty init` template in `src/chitty/store.py`. When unset, the session command gets no `--model`, as for the other modes.
- Success: the session exits 0, no rebase is in progress, and the worktree is clean. `_prepare_review` then carries on as after a clean rebase (config and `AGENTS.md` checks, `setup`, `check`), and a separate reviewer session starts. Those later checks can still fail the review as today.
- Failure: non-zero exit, `agent_timeout` expiry, a rebase still in progress, or uncommitted files. `_prepare_review` catches the session's `ChittyError` itself, so it never reaches `_record_ticket_error`. It runs `git rebase --abort` if a rebase is in progress, and fails the review as `Review failed (integration)` naming each conflicted path in backticks, as `TASK-374` does. No reviewer starts.
- Ctrl-C during the session: abort the rebase if one is in progress, then raise `RunInterrupted`, exit 130.
- The session writes no ticket fields and records no verdict. It writes its own usage-log line with mode `rebase`.
- Document `rebase_model` (and that unset means no `--model`) in `docs/plan/config.md`, and the session, its mode and its failure note under `## Before a review` in `docs/plan/next-action-and-runner.md`.

Tests: real-Git runner tests with a fake agent command in a new `tests/test_review_rebase_session.py`, inheriting `CliTestCase` from `tests/support.py` as `tests/test_review_merge.py` does, so usage logs go to a temporary `XDG_DATA_HOME`. The fake agent's behaviour is chosen per test. Outcome table, one test per row: {exit 0, exit 1, timeout} by {rebase finished, rebase still stopped} by {worktree clean, uncommitted file}. Exactly the row (exit 0, finished, clean) starts the reviewer; every other row ends with `Review failed (integration)`, no rebase in progress, and no reviewer. No property: a fixed table of real-process outcomes.

## Acceptance Criteria

- [ ] A review run whose rebase stops on a code conflict starts one fake agent with `{mode}` `rebase` and the `chitty guide rebase` prompt; when it resolves and finishes the rebase, a separate reviewer session starts on the rebased branch, and the ticket file is byte-identical before and after the rebase session; the test fails before the change
- [ ] Every other row of the outcome table ends with no rebase in progress, the ticket `doing` with `Review failed (integration)` naming each conflicted path, and no reviewer started; none moves the ticket to `error`
- [ ] With `rebase_model` set, the rebase session command gets `--model <value>` and the reviewer gets `review_model`'s; unset, the rebase session gets no `--model`; `chitty init` writes the commented `rebase_model` line beside the other model lines
- [ ] The usage log has a separate line with mode `rebase` for the session; `docs/plan/config.md` lists `rebase_model` and its unset behaviour, and `## Before a review` names the session, its mode and its failure note; `make check` passes

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

## History

- 2026-11-18T09:51:22Z witty-ginger-falcon → planning
- 2026-11-18T09:52:36Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:28Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:29Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:31Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:48Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:48Z witty-ginger-falcon todo → planning
