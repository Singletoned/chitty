---
title: Start the agent when the pre-session check fails on a doing or error ticket
status: cold-read
labels:
  - bug
  - runner
priority: high
parent: TASK-318
created: 2026-11-14
---

## Description

Before a work session, `chitty run` runs `setup` and `check` in the ticket worktree. Since `44bca53` (TASK-318), every check failure moves the ticket to `error` and no agent starts. A `doing` ticket with unfinished work naturally fails its tests, so it can never be resumed: TASK-321 went `doing → error` this way on 2026-11-14. An `error` ticket whose failure is a check failure also re-fails before its repair agent starts.

Change `_handle_check_failure` in `src/chitty/run.py` (around line 1076). In work mode (`action.mode == "work"`; repair runs also use it), when the ticket status is `doing` or `error`:

- append a note `Check failed before this session: <detail>`, where `<detail>` is the existing `check exited with status N:` line plus the fenced full output, as `_run_check` already builds it;
- leave the status unchanged;
- return `None`, so the run claims nothing and starts the agent as if the check had passed. For an `error` ticket this is the repair agent, and the existing rule that it must finish in `review` or `blocked` still applies.

Unchanged: a `todo` ticket still goes to `error` without being claimed or starting an agent; review-mode check failures keep their current handling. The pre-`44bca53` code (`git show 44bca53^:src/chitty/run.py`, `_handle_check_failure`) shows the old `doing` branch; reuse its note wording but keep full output.

Update `docs/plan/next-action-and-runner.md`: the work-mode bullet (around line 114) and the ticket-scoped failure bullet (around line 133) must agree on `todo`, `doing` and `error`.

Tests go in `tests/test_next.py`, using its fake `pi` pattern and a check script that exits 1. No property test: the behaviour is a small fixed set (statuses `todo`, `doing`, `error` in work mode), each listed in a criterion and tested. Out of scope: review-mode check handling, landing checks, and the TASK-318 children.

## Acceptance Criteria

- [ ] `test_run_check_failure_on_doing_ticket_starts_agent` in `tests/test_next.py` asserts that, for a `doing` ticket whose check exits 1, the fake agent starts (its marker file exists), the ticket stays `doing`, and its notes contain `Check failed before this session` and the fenced check output. Record that it fails on `main` before the fix.
- [ ] A new test in `tests/test_next.py`: `chitty run --errors` on an `error` ticket whose check exits 1 starts the fake repair agent, adds the same note, and keeps the ticket `error` until the agent moves it; a fake agent that sets `review` ends the run in `review`. Record that it fails before the fix.
- [ ] `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` (a `todo` ticket goes to `error`, no agent) passes unchanged; `docs/plan/next-action-and-runner.md` describes the `todo`, `doing` and `error` cases consistently; `make check` passes.

## History

- 2026-11-14T11:33:09Z jolly-silver-falcon → backlog
- 2026-11-14T11:33:17Z jolly-silver-falcon: changed description, acceptance criteria
- 2026-11-14T11:33:17Z jolly-silver-falcon backlog → planning
- 2026-11-14T11:33:26Z jolly-silver-falcon planning → cold-read
