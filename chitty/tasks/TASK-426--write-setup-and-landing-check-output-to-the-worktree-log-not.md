---
title: Write `setup` and landing-check output to the worktree log, not the ticket
status: planning
priority: high
depends_on:
  - TASK-353
created: 2026-11-19
---

## Description

`TASK-353` sends the configured `check` output to the worktree log `.chitty/check.log` through `_run_logged` in `src/chitty/run.py`, and keeps it out of ticket notes. `setup` (`_setup`) and the landing check (`_landing_check`) still capture their output and put it into the error, and so into the note. Decided with the owner 2026-11-19: command output never goes into tickets.

Decisions:

- `_setup` uses `_run_logged("setup", ...)` and `_landing_check` uses `_run_logged("landing check", ...)`. Both overwrite the same log, which therefore holds whichever command ran last. Landing runs `setup` and then the landing check, so after a failed landing check the log holds the landing check.
- Their errors are exactly `` setup exited with status <N>; output in `.chitty/check.log` `` and `` landing check exited with status <N>; output in `.chitty/check.log` ``. The `command not found` errors and `RunInterrupted` handling are unchanged.
- The setup that `refresh_setup` runs in the main checkout is out of scope.

Tests, changing existing ones. No property: fixed runner runs with real Git.

- `tests/test_run_error_reporter.py`, the test that asserts `setup exited with status 9`: `assertIn("SETUP_MARKER", note)` becomes `assertNotIn`; the note contains `` output in `.chitty/check.log` ``; `self.root / ".worktrees/task-1/.chitty/check.log"` starts with `# chitty setup: `, contains `SETUP_MARKER` and ends with `# exit 9\n`.
- `tests/test_review_merge.py`, `test_failing_check_after_main_advances_preserves_main_and_worktree`: the notes contain `` output in `.chitty/check.log` ``; `self.worktree / ".chitty/check.log"` starts with `# chitty landing check: ` and ends with `# exit 7\n`.

## Acceptance Criteria

- [ ] The changed assertions pass, and each fails against the `run.py` of `TASK-353` (recorded in the notes); `make check` passes

## History

- 2026-11-19T17:28:48Z quick-ginger-lapwing → planning
