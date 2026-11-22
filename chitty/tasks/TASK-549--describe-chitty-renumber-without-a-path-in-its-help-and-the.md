---
title: Describe `chitty renumber` without a path in its help and the CLI docs
status: review
depends_on:
  - TASK-392
  - TASK-548
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-392` on 2026-11-22. After `TASK-392`, `chitty renumber` with no `PATH` renumbers provisional tickets on `main`. This ticket updates its help and the CLI docs.

- The first line of the `renumber` docstring in `src/chitty/cli.py` (the first line of `chitty renumber --help`) becomes `Renumber provisional tickets on main, or one of several files sharing an ID.`; update `test_help` in `tests/test_renumber.py`, which pins that line.
- In `docs/plan/cli.md`, describe `renumber` with no `PATH`: one `renumbered <old ID> -> <new ID> <path>` line per ticket on stdout, `nothing to renumber` and `provisional tickets are renumbered on main; nothing changed` on stderr, exit 0, and the `--json` list (`TASK-548`).

## Acceptance Criteria

- [ ] `chitty renumber --help` starts with the new line and `test_help` asserts it; `docs/plan/cli.md` describes the no-`PATH` form as listed; `make check` passes

## Plan

Update the pinned help assertion and command docstring, document no-path output and JSON behavior, then run formatting and checks.

## Notes

The updated help assertion failed against the original docstring as expected.

## Summary

Updated renumber help and no-path CLI documentation. The revised help test failed before the change; make check passed afterward.

## History

- 2026-11-22T03:23:03Z lively-zinc-newt → todo
- 2026-11-22T04:55:57Z jolly-maroon-adder todo → doing
- 2026-11-22T04:58:23Z jolly-maroon-adder: wrote the plan
- 2026-11-22T04:58:41Z jolly-maroon-adder: changed notes
- 2026-11-22T05:02:33Z jolly-maroon-adder: changed summary
- 2026-11-22T05:04:05Z jolly-maroon-adder doing → review
