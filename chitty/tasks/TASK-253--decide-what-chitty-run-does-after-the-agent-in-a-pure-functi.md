---
title: Decide what `chitty run` does after the agent in a pure function, with property tests
status: doing
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

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty run` and `chitty run --loop` tests pass unchanged, except the three `TestDirectAgentTimeout` tests in `tests/test_run_timeout.py`, which assert the returned timeout instead of a raised `ChittyError`.

## Notes

Possible starting point: `refs/cold-read/TASK-253/2` (`git show refs/cold-read/TASK-253/2:<path>`). It lets `-SIGINT` win over a timeout, which the ticket now reverses. Check it against the criteria; don't trust it.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:14:52Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T22:19:11Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-10T22:19:11Z jolly-heron backlog → todo
- 2026-11-10T23:10:32Z calm-adder todo → doing
