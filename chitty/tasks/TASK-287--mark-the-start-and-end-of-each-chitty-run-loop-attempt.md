---
title: Mark the start and end of each `chitty run --loop` attempt
status: done
created: 2026-11-11
---

## Description

- Watching `chitty run --loop`, it is hard to see where one run ends and the wait begins. `run_loop` in `src/chitty/run.py` starts each attempt as a child process and sleeps `RUN_LOOP_PAUSE_SECONDS` between them.
- Before each attempt, `run_loop` prints a full-width rule, `━━━━ chitty run · 16:04:12 ━━━…`. After it, another: `━━━━ finished · next run at 16:05:12 ━━━…`, or `━━━━ no ticket · next run at …` when there was nothing to do, or `━━━━ stopped · exit 2 ━━━…` when the loop ends. The width is the terminal's (`shutil.get_terminal_size`), and times are local.
- Rules go to stderr, with the existing `no next ticket` line. Ctrl-C needs no rule. Only the loop prints these; a single `chitty run` is unchanged.

## Acceptance Criteria

- [x] A test runs `run_loop` with a child that exits 0 once and then non-zero: the output has a start rule before each attempt, a `finished · next run at` rule after the first, and a `stopped · exit` rule after the second. It fails today.
- [x] A child exiting `NO_NEXT_TICKET_EXIT` (3) is followed by a `no ticket · next run at` rule, not `finished`.
- [x] The `next run at` time is `RUN_LOOP_PAUSE_SECONDS` after the end of that attempt, not its start.

## Plan

Add focused run-loop tests for stderr output, exit-3 labeling, and scheduling from attempt completion. First run the new tests against current behavior to confirm they fail. Then implement terminal-width rules in run_loop, send them to stderr, and compute the next-run timestamp after each child finishes. Run make format and make check, commit implementation, then record verified criteria and move to review.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-287/1`. Check it against the current criteria; do not trust it.

The new focused tests failed against the original loop (missing stderr rules and idle exit returned the unexpected result); they pass with the implementation. `make check` passes (ruff, pyright, all 498 Python tests, and Node tests). `make format` and `chitty fix` completed; chitty fix reported existing warnings in unrelated task files, which were left untouched.

Reviewed: `make format && make check` passed (501 Python tests and Node tests); formatting left the tree unchanged.
1: pass - The focused `test_loop_marks_attempts_and_outcomes_on_stderr` passed; executing the same test with `main:src/chitty/run.py` loaded in memory failed with `0 != 4` output lines.
2: pass - `test_loop_marks_idle_queue_and_schedules_from_attempt_end` passed, checking the `no ticket` rule; with the main implementation loaded in memory it failed because the rule was absent.
3: pass - The same focused test passed with a mocked attempt start and end, asserting the completion-based `12:01:00` next-run time and pause; the main implementation failed because the timestamp was absent.

## Summary

Implemented terminal-width start, outcome, and stop rules on stderr for loop attempts. Idle exit 3 is labeled no ticket, and next-run time is calculated after the child exits. Regression tests verify output ordering and completion-based scheduling. Verified with make format and make check; all checks pass. Code committed as df96110 (Task: TASK-287). No known follow-ups.

## History

- 2026-11-11T16:09:29Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:36Z vivid-yellowhammer: changed parent
- 2026-11-11T16:09:48Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T16:12:20Z vivid-yellowhammer: changed description
- 2026-11-11T16:12:21Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T16:12:21Z vivid-yellowhammer cold-read → todo
- 2026-11-11T21:41:08Z jolly-amber-yellowhammer todo → doing
- 2026-11-11T21:41:27Z jolly-amber-yellowhammer: wrote the plan
- 2026-11-11T21:47:12Z jolly-amber-yellowhammer: changed notes, summary; ticked acceptance criteria
- 2026-11-11T21:47:12Z jolly-amber-yellowhammer doing → review
- 2026-11-11T21:49:52Z witty-indigo-jay: changed notes; ticked acceptance criteria
- 2026-11-11T21:49:52Z witty-indigo-jay review → done
