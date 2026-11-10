---
title: Decide what `chitty run` does after the agent in a pure function, with property tests
status: backlog
created: 2026-11-10
---

## Description

After the agent exits, `src/chitty/run.py` decides through scattered `if`s and exceptions (around lines 300 to 335), and `run_loop` decides whether to continue (around line 110). Make those decisions three pure functions, called where they are made now, with the same messages and exit codes:

- `agent_exit(returncode, timed_out)`: interrupted, timed out, failed, or ok. `-SIGINT` wins over a timeout. `_run_agent` reports a timeout to its caller instead of raising, and the caller still builds `agent timed out after N seconds`.
- `status_outcome(old_status, new_status)`: unchanged, land (the new status is `done` and the old one was not), or changed. Called only after `agent_exit` returns ok, where `new_status` is read today.
- `loop_step(returncode)`: continue on 0 and 3; otherwise stop with an exit code, where `-N` (N from 1 to 127) gives `128 + N`.

Out of scope: reviews that fail before the agent starts (`_prepare_review`, `_fail_check` and the like), which return early.

**Properties** (`tests/test_property_run_outcome.py`): one per rule above, including changed. Draw 0, 3 and `-SIGINT` explicitly alongside other integers, or Hypothesis rarely reaches them.

## Acceptance Criteria

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty run` and `chitty run --loop` tests pass unchanged.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:14:52Z jolly-heron: changed description, acceptance criteria
