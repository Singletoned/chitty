---
title: Decide what `chitty run` does after the agent in a pure function, with property tests
status: backlog
created: 2026-11-10
---

## Description

After the agent exits, `src/chitty/run.py` (around lines 300 to 335) decides through scattered `if`s and exceptions: interrupted on `-SIGINT`, failed on another non-zero status or a timeout, an error when the ticket's status is unchanged, and landing when it is `done`. `run_loop` (around line 110) then decides whether to continue and with which exit code.

**Change:** two pure functions, called where those decisions are made now, with the same messages and exit codes:

- `agent_outcome(returncode, timed_out, old_status, new_status)` returns one of: interrupted, timed out, agent failed (with the status), unchanged, land, or changed.
- `loop_step(returncode)` returns continue, or stop with the loop's exit code.

**Properties** (`tests/test_property_run_outcome.py`):

- `-SIGINT` is interrupted whatever the statuses; a timeout is timed out whatever the return code.
- Land only when the return code is 0, no timeout, and the status went from something else to `done`.
- Unchanged exactly when the return code is 0, no timeout, and the status is the same.
- The loop continues exactly on 0 and 3; otherwise its exit code is between 1 and 255 (a signal `-N` gives `128 + N`).

## Acceptance Criteria

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty run` and `chitty run --loop` tests pass unchanged.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
