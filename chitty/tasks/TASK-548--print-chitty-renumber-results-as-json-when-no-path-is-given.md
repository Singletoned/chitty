---
title: Print `chitty renumber` results as JSON when no path is given
status: done
depends_on:
  - TASK-392
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-392` on 2026-11-22. After `TASK-392`, `chitty renumber` with no `PATH` renumbers provisional tickets and prints text. This ticket adds `--json` for that form. `TASK-392` landed `TestCliProvisionalRenumbering` (a `CliTestCase` with a `fixture()` helper) in `tests/test_renumber_provisional.py`; add these tests to that class (rechecked 2026-11-22).

- `--json` without `PATH` prints a list of `change.task.as_dict()` items to stdout, as `archive` with no ID does (each `moved_from` holds the old ID), and `[]` when there are none, including off `main`; the `nothing to renumber` and off-`main` messages still go to stderr. With `PATH`, `--json` output (`renumbered_dict`) is unchanged.

Test in `tests/test_renumber_provisional.py`, using that class's `fixture()`: `test_json`: with the fixture's two provisional tickets on `main` (read their old IDs from the `chitty/tasks` file names before the run, as `test_main` does), `chitty renumber --json` prints a JSON list of two `as_dict()` items, each with its new ID and a top-level `moved_from` equal to an old ID; a second run prints `[]` on stdout and `nothing to renumber` on stderr; on `feature` it prints `[]` and `provisional tickets are renumbered on main; nothing changed` on stderr. Mirror the `archive` no-ID branch in `src/chitty/cli.py` (`_print_json([change.task.as_dict() for change in changes])`). A cold reader's probe: today `--json` prints the text lines, so the test fails.

## Acceptance Criteria

- [ ] `TestCliProvisionalRenumbering.test_json` passes, and fails before the change because stdout is not JSON; `make check` passes

## Plan

Add a CLI regression test for JSON results, empty results and off-main behavior; confirm it fails, implement JSON output, and run checks.

## Notes

Regression test fails before the fix with JSONDecodeError because stdout contains text.

Reviewed: JSON output matches the requested no-path behavior; path behavior is unchanged.
1: pass - test_json passes; executing main:src/chitty/cli.py in the CLI module before running it produced JSONDecodeError: Expecting value: line 1 column 1 (char 0). make check passed: 1109 tests, OK; ruff and pyright passed.

## Summary

Implemented JSON output for provisional renumbering, including empty and off-main results. Regression test failed before the fix with JSONDecodeError and passes afterward; make check passed.

## History

- 2026-11-22T03:23:01Z lively-zinc-newt → planning
- 2026-11-22T04:29:41Z lively-zinc-newt: changed description
- 2026-11-22T04:29:41Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:31:53Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:31:53Z lively-zinc-newt cold-read → todo
- 2026-11-22T04:38:43Z tidy-fawn-otter todo → doing
- 2026-11-22T04:41:07Z tidy-fawn-otter: wrote the plan
- 2026-11-22T04:41:23Z tidy-fawn-otter: changed notes
- 2026-11-22T04:45:28Z tidy-fawn-otter: changed summary
- 2026-11-22T04:45:28Z tidy-fawn-otter doing → review
- 2026-11-22T04:51:39Z witty-violet-raven: changed notes
- 2026-11-22T04:51:39Z witty-violet-raven review → done
