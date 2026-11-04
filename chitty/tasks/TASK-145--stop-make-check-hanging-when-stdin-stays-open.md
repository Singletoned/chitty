---
title: Stop `make check` hanging when stdin stays open
status: todo
labels:
  - bug
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

`make check` hung for 18 minutes on 2026-11-04 when run from a background shell, and passed in 78 seconds with `</dev/null`. In `tests/test_next.py`, the fake `pi` asserts `sys.stdin.read() == ''`, and `chitty run` passes its own stdin on to the agent by design. Under `make check` from a shell whose stdin never closes, that read blocks forever, with no output and no failure. A worker or reviewer running checks that way would sit silently until someone noticed, which is the opposite of a gate.

Make the tests set the stdin they depend on, rather than inheriting the caller's, so they give the same result however they are started. `test_run_inherits_stdin` already supplies its own. An orphaned fake `pi`, running for 19 hours, was also seen on the same day: check whether the interrupt test can leave one behind if it fails partway through, and clean it up if so.

Out of scope: a timeout for `check` in `chitty run`, and changing what `chitty run` does with stdin.

## Acceptance Criteria

- [ ] `make check` passes when run with stdin held open and never written to, shown by running it that way, with the command recorded in a note
- [ ] A test shows `chitty run` still passing its stdin to the agent

## History

- 2026-11-04T12:32:20Z lively-panda → todo
