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

Only `test_run_cases` reads stdin, at `tests/test_next.py` line 394; `run_cli` uses `CliRunner`, which replaces only the in-process `sys.stdin`, so the fake `pi` reads the real file descriptor 0. Make that test set what it depends on: point descriptor 0 at `/dev/null` for its duration and restore it in cleanup. `src/chitty/run.py` does not change. To check, hold the write end of an `os.pipe()` open, pass the read end as `stdin` to `subprocess.run(["make", "check"], timeout=300)`, and confirm it times out before the fix and passes after.

Out of scope: a timeout for `check` in `chitty run`, and changing what `chitty run` does with stdin.

## Acceptance Criteria

- [ ] `make check` is shown timing out with stdin held open before the fix and passing that way after it, with the command recorded in a note
- [ ] `test_run_inherits_stdin` still passes unchanged, so `chitty run` still gives the agent its stdin

## Notes

Same cold read as `TASK-144`. Fixed: the exact test and fix; a reproducible way to hold stdin open, showing the failure first; and the second criterion, which was already true and could not have failed, is now stated as a guard. Removed: looking for how a fake `pi` was orphaned for 19 hours. The interrupt test's fake sleeps for at most 60 seconds, so that test cannot explain it, and it is a separate oddity not needing a ticket yet. Rejected: stdin at a terminal, because pointing the descriptor at `/dev/null` covers it.

## History

- 2026-11-04T12:32:20Z lively-panda → todo
- 2026-11-04T12:34:35Z lively-panda: changed description, acceptance criteria, notes
