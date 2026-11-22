---
title: Print `chitty renumber` results as JSON when no path is given
status: cold-read
depends_on:
  - TASK-392
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-392` on 2026-11-22. After `TASK-392`, `chitty renumber` with no `PATH` renumbers provisional tickets and prints text. This ticket adds `--json` for that form. `TASK-392` landed `TestCliProvisionalRenumbering` (a `CliTestCase` with a `fixture()` helper) in `tests/test_renumber_provisional.py`; add these tests to that class (rechecked 2026-11-22).

- `--json` without `PATH` prints a list of `change.task.as_dict()` items to stdout, as `archive` with no ID does (each `moved_from` holds the old ID), and `[]` when there are none, including off `main`; the `nothing to renumber` and off-`main` messages still go to stderr. With `PATH`, `--json` output (`renumbered_dict`) is unchanged.

Test in `tests/test_renumber_provisional.py`, using that class's `fixture()`: with two provisional tickets on `main`, `chitty renumber --json` prints a JSON list of two items, each with its new ID and `moved_from` the old one; a second run prints `[]`; on `feature` it prints `[]` and the off-`main` message on stderr.

## Acceptance Criteria

- [ ] The JSON test passes and fails before the change; `make check` passes

## History

- 2026-11-22T03:23:01Z lively-zinc-newt → planning
- 2026-11-22T04:29:41Z lively-zinc-newt: changed description
- 2026-11-22T04:29:41Z lively-zinc-newt planning → cold-read
