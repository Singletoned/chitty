---
title: Start the agent when the pre-session check fails on a doing or error ticket
status: done
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
- leave the status unchanged, so the agent starts with the ticket still `doing` or `error`. The note is written through the worktree's `Repo` and committed on the ticket branch, like other session edits;
- return `None`, so the run claims nothing and starts the agent as if the check had passed. For an `error` ticket this is the repair agent, and the existing rule that it must finish in `review` or `blocked` still applies.

Only a check that ran and exited non-zero takes this path; `check command not found` is a configuration fault and still goes to `error`. Unchanged: a `todo` ticket still goes to `error` without being claimed or starting an agent; review-mode check failures keep their current handling. The pre-`44bca53` code (`git show 44bca53^:src/chitty/run.py`, `_handle_check_failure`) shows the old `doing` branch; reuse its note wording but keep full output.

Update `docs/plan/next-action-and-runner.md`: the work-mode bullet (around line 114) and the ticket-scoped failure bullet (around line 133) must agree on `todo`, `doing` and `error`.

Tests go in `tests/test_next.py`, using its fake `pi` pattern and a check script that exits 1. No property test: the behaviour is a small fixed set (statuses `todo`, `doing`, `error` in work mode), each listed in a criterion and tested. Out of scope: review-mode check handling, landing checks, and the TASK-318 children.

## Acceptance Criteria

- [x] Rewrite `test_run_check_failure_on_doing_ticket_starts_agent` in `tests/test_next.py` (it now asserts the opposite). For a `doing` ticket whose check prints 25 numbered lines and exits 1, the fake agent starts, records the ticket it sees, then commits `-s review`. The recorded ticket has status `doing` and notes containing `Check failed before this session` and all 25 lines; the run prints `doing → review`. Record that it fails on `main` before the fix.
- [x] A new test in `tests/test_next.py`: `chitty run --errors` on an `error` ticket whose check exits 1 starts the fake repair agent, which sees status `error` and the same note, then commits `-s review`; the run prints `error → review`. Record that it fails before the fix.
- [x] `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` (a `todo` ticket goes to `error`, no agent) passes unchanged; a `doing` ticket whose check command does not exist still goes to `error` without starting the agent; `docs/plan/next-action-and-runner.md` describes the `todo`, `doing` and `error` cases consistently; `make check` passes.

## Plan

Update _handle_check_failure to distinguish a check process exiting non-zero from a missing command. In work mode, for doing/error tickets, write the full-detail note through the worktree Repo, preserve status, and continue without a claimed result; keep todo, missing-command, and review behavior unchanged. Update focused tests for doing/error and missing command, verify the doing/error regression tests fail before the implementation, update the runner design note, then format and run make check.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-329/1` (a cold read of the current text: tests failed first, all six mutants killed, `make check` passed). Check it against the current criteria; do not trust it.

The doing and error regression tests were run before the fix and both failed with the runner changing the ticket to error before an agent could commit review. After the fix, all four focused tests pass: doing, error repair, todo failure without claim/agent, and missing check command. make format && make check passed (549 Python suites and Node tests). Commit: 668c3fd.

Reviewed:
1: pass - make check passed; test_run_check_failure_on_doing_ticket_starts_agent passed and, with main run.py in a temporary PYTHONPATH, failed with doing → error instead of doing → review.
2: pass - make check passed; test_run_check_failure_on_error_ticket_starts_repair_agent passed and, with main run.py in a temporary PYTHONPATH, failed with error → error instead of error → review.
3: pass - make format && make check passed (552 tests and Node tests); the unchanged todo test and missing-command test passed, and docs/plan/next-action-and-runner.md describes all three statuses consistently.

## Summary

Implemented and committed as 668c3fd. Pre-session non-zero checks on doing/error work tickets now record the complete output and preserve status while allowing the agent to start; todo and missing-command behavior remains error handling. Updated runner design notes. Verified regression tests fail before the fix, focused tests pass, make format && make check pass, and git status is clean. Ready for review.

## History

- 2026-11-14T11:33:09Z jolly-silver-falcon → backlog
- 2026-11-14T11:33:17Z jolly-silver-falcon: changed description, acceptance criteria
- 2026-11-14T11:33:17Z jolly-silver-falcon backlog → planning
- 2026-11-14T11:33:26Z jolly-silver-falcon planning → cold-read
- 2026-11-14T11:37:56Z jolly-silver-falcon: changed description, acceptance criteria
- 2026-11-14T11:37:56Z jolly-silver-falcon cold-read → planning
- 2026-11-14T11:38:10Z jolly-silver-falcon planning → cold-read
- 2026-11-14T11:42:53Z jolly-silver-falcon: changed notes
- 2026-11-14T11:42:53Z jolly-silver-falcon cold-read → planning
- 2026-11-14T11:42:55Z jolly-silver-falcon planning → todo
- 2026-11-14T11:43:45Z calm-silver-puffin todo → doing
- 2026-11-14T11:44:00Z calm-silver-puffin: wrote the plan
- 2026-11-14T11:45:59Z calm-silver-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-14T11:45:59Z calm-silver-puffin doing → review
- 2026-11-14T18:32:44Z honest-indigo-dormouse: changed notes; ticked acceptance criteria
- 2026-11-14T18:32:44Z honest-indigo-dormouse review → done
