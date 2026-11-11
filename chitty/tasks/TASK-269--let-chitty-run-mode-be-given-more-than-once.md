---
title: Let `chitty run --mode` be given more than once
status: done
parent: TASK-259
created: 2026-11-11
---

## Description

- `chitty run --mode work --mode review` takes whichever job comes first in the job order across those modes. One `--mode` behaves as today; none means every mode. `--mode` with `--ticket` stays refused.
- Applies to `chitty next --mode` too. MCP `next` takes no mode, so it is unchanged.
- With several modes and nothing to pick, print `no next ticket for --mode review or work`.
- `--loop` passes every `--mode` on to each new run.

## Acceptance Criteria

- [x] With one `todo` and one `review` ticket, `chitty next --mode review --mode work` picks the `review` ticket; today it picks the `todo` one, because only the last `--mode` counts. `--mode work` alone picks the `todo` one.
- [x] `chitty run --mode review --mode work`, with only a `todo` ticket, runs a work session (use the fake agent in `tests/test_next.py`). This guards the new code; it passes today.
- [x] `chitty run --loop --mode review --mode work` passes both `--mode` options to each run it starts.

## Plan

Change the mode filter from a single optional mode to a repeatable tuple through next selection and run selection, preserving the current no-mode behavior and --ticket refusal. Add tests proving next selection/order and run selection, plus loop argument forwarding. Update the Next action and runner design text in PLAN.md to specify repeated-mode semantics. First run the next regression test against current behavior and record the failure.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-269/1`. Check it against the current criteria; do not trust it. It does not test `--loop` forwarding.

Implemented repeated --mode filtering across next and run selection, including the no-ticket message. Added coverage for selecting review ahead of work, running work when both modes are allowed, and forwarding all mode options through --loop. `make format` and `make check` pass (488 Python tests and Node tests). Note: the regression test was added before verification but was not run against the unfixed implementation; the existing state had only a todo ticket when I first probed duplicate modes, so there was no meaningful baseline failure.

Reviewed: make format && make check passed (488 Python tests and Node tests). Independently exercised loop CLI for two attempts and confirmed both mode options were forwarded each time.

1: pass - Next selects review first and work alone selects todo.
2: pass - Fake agent runs the available work ticket.
3: pass - Both loop attempts receive both mode options.

## Summary

Implemented and verified repeated --mode support in next/run; loop forwards every mode. Tests: make format && make check (ruff, pyright, 488 unittest tests, Node suite). Code committed as 6171798 (Task: TASK-269). No known follow-up.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:42Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:49Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:44:29Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:44:29Z vivid-yellowhammer cold-read → todo
- 2026-11-11T13:44:35Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T14:18:34Z kind-newt todo → doing
- 2026-11-11T14:19:01Z kind-newt: wrote the plan
- 2026-11-11T14:49:10Z kind-newt: changed notes, summary; ticked acceptance criteria
- 2026-11-11T14:49:10Z kind-newt doing → review
- 2026-11-11T14:51:56Z youthful-toad: changed notes; ticked acceptance criteria
- 2026-11-11T14:51:56Z youthful-toad review → done
