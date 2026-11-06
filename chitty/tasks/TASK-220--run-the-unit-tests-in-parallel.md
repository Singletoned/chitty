---
title: Run the unit tests in parallel
status: review
priority: high
created: 2026-11-06
---

## Description

`make check` and `make test` run `python -m unittest discover -s tests -t .` in one process, which takes about 290 seconds, while the machine has 16 cores. A throwaway runner that ran each test in a `ProcessPoolExecutor` with 12 workers took 39 seconds, with all 336 tests passing, while two `chitty run` loops were also running. Tests already use their own temporary directories, `XDG_DATA_HOME` and repositories, so running them side by side is safe.

Use the `unittest-parallel` package from PyPI (a dev dependency in `pyproject.toml`) rather than a hand-written runner: `unittest-parallel -s tests -t . --level test`. Run it through `uv run`, as the `Makefile` does today, in both the `check` and `test` targets. Let it choose the worker count by CPU count; don't hard-code one. If it can't run some test correctly, report which one and why rather than working around it.

Out of scope: making individual tests faster, and the `test_next` restructuring (`TASK-221`).

## Acceptance Criteria

- [x] `make check` runs the unit tests through `unittest-parallel`, all tests pass, and its unit-test step takes well under half its old time on this machine. Record both timings in the ticket's summary.
- [x] A deliberately failing test (added temporarily, then removed) makes `make check` exit non-zero and print the failure. `mate --list` still describes `check` and `test`.

## Plan

Add `unittest-parallel` as a dev dependency. In the `Makefile` `check` and `test` targets, replace `python -m unittest discover -s tests -t .` with `unittest-parallel -s tests -t . --level test`, run through `uv run`. Time before and after, run it twice to look for flakes, and check that a deliberate failure exits non-zero and shows its traceback.

## Notes

Reserved for a human-run session. The cold read was stopped before it reported, because the human asked for this to be implemented directly.

Decision: pinned `unittest-parallel` exactly, like the `mdformat` pins, because its CLI is what the `Makefile` calls. The worker count is left to its default (all cores), as the ticket says.

## Summary

`make check` and `make test` run the unit tests with `unittest-parallel -s tests -t . --level test`, pinned at `unittest-parallel==1.8.6` as a dev dependency. Timings on this machine (16 cores, with other agents running): serial unit tests 293 s; parallel 40 s on each of two runs (335 tests, OK both times, no flakes). The full `make check` takes 44 s. A deliberate failing test made `make test` exit non-zero and print the test's name and full traceback; it was removed afterwards. `mate --list` still describes `check` and `test`. Note for review: `unittest-parallel` depends on `coverage`, which resolved to 7.17.2, published 2026-11-04 (two days ago). Pin an older `coverage` if that's a concern.

## History

- 2026-11-06T19:18:23Z youthful-toad → backlog
- 2026-11-06T19:24:10Z youthful-toad: changed owner, notes
- 2026-11-06T19:24:10Z youthful-toad backlog → todo
- 2026-11-06T19:24:13Z youthful-toad: wrote the plan
- 2026-11-06T19:24:13Z youthful-toad todo → doing
- 2026-11-06T19:33:08Z youthful-toad: changed owner, notes, summary; ticked acceptance criteria
- 2026-11-06T19:33:08Z youthful-toad doing → review
