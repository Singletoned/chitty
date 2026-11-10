---
title: Decide what `chitty run` does after the agent in a pure function, with property tests
status: review
created: 2026-11-10
---

## Description

After the agent exits, `src/chitty/run.py` decides through scattered `if`s and exceptions (around lines 300 to 335), and `run_loop` decides whether to continue (around line 110). Make those decisions three pure functions, called where they are made now, with the same messages and exit codes:

- `agent_exit(returncode, timed_out)`: interrupted, timed out, failed, or ok. A timeout wins over `-SIGINT`: when Chitty stopped the agent, the exit status is its own signal. `_run_agent` reports a timeout to its caller instead of raising, and the caller still builds `agent timed out after N seconds`.
- `status_outcome(old_status, new_status)`: unchanged, land (the new status is `done` and the old one was not), or changed. Called only after `agent_exit` returns ok, where `new_status` is read today.
- `loop_step(returncode)`: continue on 0 and 3; otherwise stop with an exit code, where a signal `-N` gives `128 + N`.

Out of scope: reviews that fail before the agent starts (`_prepare_review`, `_fail_check` and the like), which return early.

**Properties** (`tests/test_property_run_outcome.py`): one per rule above, including changed. Draw 0, 3 and `-SIGINT` explicitly alongside other integers, or Hypothesis rarely reaches them.

## Acceptance Criteria

- [x] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [x] Existing `chitty run` and `chitty run --loop` tests pass unchanged, except the three `TestDirectAgentTimeout` tests in `tests/test_run_timeout.py`, which assert the returned timeout instead of a raised `ChittyError`.

## Plan

Add pure outcome functions for agent exits, status transitions, and loop steps, then call them at the existing decision points. Make _run_agent return a timeout result instead of raising, update the three direct timeout tests, and add Hypothesis property tests covering explicit boundary values. Run regression tests before fixing, then make check and commit implementation.

## Notes

Possible starting point: `refs/cold-read/TASK-253/2` (`git show refs/cold-read/TASK-253/2:<path>`). It lets `-SIGINT` win over a timeout, which the ticket now reverses. Check it against the criteria; don't trust it.

Confirmed the three direct timeout tests passed against the original implementation before changing them. Property tests now encode the three decision rules and explicit boundary values. `make format && make check` passes (462 Python tests plus Node tests).

Mutation checks confirmed each property test detects its rule being removed: timeout precedence in agent_exit, unchanged handling in status_outcome, and continue handling in loop_step. Restored the source after each mutation; the full make format && make check passed afterward (462 Python tests and Node tests). Verified existing run/loop tests remain unchanged; only the three TestDirectAgentTimeout assertions were updated.

## Summary

Implemented and committed pure run outcome decisions (ff4237c). Verified both acceptance criteria: mutation testing showed each property fails when its corresponding decision is removed; full formatting and checks pass. Direct timeout tests now assert the returned timeout result. No follow-up.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:14:52Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T22:19:11Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-10T22:19:11Z jolly-heron backlog → todo
- 2026-11-10T23:10:32Z calm-adder todo → doing
- 2026-11-10T23:10:44Z calm-adder: wrote the plan
- 2026-11-10T23:12:44Z calm-adder: changed notes
- 2026-11-10T23:13:51Z calm-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-10T23:13:52Z calm-adder doing → review
