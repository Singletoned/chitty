---
title: Record a runner error once in its note, not twice
status: planning
priority: medium
depends_on:
  - TASK-426
created: 2026-11-19
---

## Description

`_record_ticket_error` in `src/chitty/run.py` writes every runner error twice: in the first line, `Runner error (<phase>): <error>`, and again in a fenced `Error output:` block. A multi-line error, such as an agent's output or a Git hint, therefore appears twice in the note.

Decisions:

- The note's first line is `Runner error (<phase>): <first line of the error>`, followed by the `Worktree:` line as today.
- The `Error output:` block, fenced with `_code_block` as today, follows only when the error has more than one line, and holds the lines after the first. A one-line error has no block.

Tests in `tests/test_run_errors_on_branch.py`, no property (fixed runner runs with real Git):

- `test_agent_failure_keeps_error_and_message_on_branch`: the fake agent first prints `AGENT_LINE_1` and `AGENT_LINE_2` on separate lines, then exits 7. In the newest copy on `task-1` (`tip` in `assert_branch_error`), `Runner error (agent): agent exited with status 7:` appears exactly once, and `AGENT_LINE_1` and `AGENT_LINE_2` each appear exactly once, after the line `Error output:`.
- `test_work_setup_failure_is_only_recorded_on_branch`: the tip contains `Runner error (setup): setup exited with status 1` exactly once and does not contain `Error output:`. This assumes `TASK-426` has landed (setup output is in the log, so the error is one line).

## Acceptance Criteria

- [ ] The changed assertions pass, and each fails against the `run.py` of the commit before this change (recorded in the notes); `make check` passes

## History

- 2026-11-19T17:28:50Z quick-ginger-lapwing → planning
