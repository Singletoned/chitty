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

When the rebase before a review (`TASK-374`) stops on a code conflict, the review fails back to `doing` today, and a full work session is spent on what is only conflict resolution. The conflict should be resolved by a separate, cheaper agent session, so that conflict context never mixes with review context.

Decisions:

- New agent mode `rebase`. When the rebase in `_prepare_review` stops on code conflicts, instead of aborting, the runner starts one agent session in the worktree with `{mode}` `rebase` and `{prompt}` from `chitty guide rebase <ID>` (`TASK-373`). It uses the configured agent command, with `--model` from a new optional setting `rebase_model`, handled like `work_model` and `review_model` in `src/chitty/config.py`. No continuations.
- Success: the agent exits 0 with no rebase in progress and a clean worktree. The runner then carries on with the review preparation (config and `AGENTS.md` checks, `setup`, `check`) and starts a separate reviewer session.
- Failure (non-zero exit, timeout, a rebase still in progress, or uncommitted files): `git rebase --abort` if one is in progress, and fail the review as `Review failed (integration)` naming the conflicted files, as `TASK-374` does.
- The rebase session writes no ticket fields and records no verdict. It gets a usage-log line with mode `rebase`.
- Document `rebase_model` in `docs/plan/config.md` and the flow under "Before a review" in `docs/plan/next-action-and-runner.md`.

Tests: real-Git runner tests with a fake agent command in a new `tests/test_review_rebase_session.py`. No property: real Git and agent processes over the fixed outcomes in the criteria.

## Acceptance Criteria

- [ ] A review run whose rebase stops on a code conflict starts one agent with mode `rebase` and the `chitty guide rebase` prompt; when that fake agent resolves and continues the rebase, a separate reviewer session starts on the rebased branch
- [ ] When the fake rebase agent exits 0 with the rebase still in progress, the rebase is aborted and the ticket moves to `doing` with `Review failed (integration)` naming the file, and no reviewer starts
- [ ] With `rebase_model` set, the rebase session command gets `--model <value>`, and the reviewer gets `review_model`'s
- [ ] `docs/plan/config.md` and `docs/plan/next-action-and-runner.md` describe the session and setting, and `make check` passes

## History

- 2026-11-18T09:51:22Z witty-ginger-falcon → planning
- 2026-11-18T09:52:36Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:28Z witty-ginger-falcon cold-read → planning
