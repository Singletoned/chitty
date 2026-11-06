---
title: Run the unit tests in parallel
status: todo
priority: high
owner: human
created: 2026-11-06
---

## Description

`make check` and `make test` run `python -m unittest discover -s tests -t .` in one process, which takes about 290 seconds, while the machine has 16 cores. A throwaway runner that ran each test in a `ProcessPoolExecutor` with 12 workers took 39 seconds, with all 336 tests passing, while two `chitty run` loops were also running. Tests already use their own temporary directories, `XDG_DATA_HOME` and repositories, so running them side by side is safe.

Use the `unittest-parallel` package from PyPI (a dev dependency in `pyproject.toml`) rather than a hand-written runner: `unittest-parallel -s tests -t . --level test`. Run it through `uv run`, as the `Makefile` does today, in both the `check` and `test` targets. Let it choose the worker count by CPU count; don't hard-code one. If it can't run some test correctly, report which one and why rather than working around it.

Out of scope: making individual tests faster, and the `test_next` restructuring (`TASK-221`).

## Acceptance Criteria

- [ ] `make check` runs the unit tests through `unittest-parallel`, all tests pass, and its unit-test step takes well under half its old time on this machine. Record both timings in the ticket's summary.
- [ ] A deliberately failing test (added temporarily, then removed) makes `make check` exit non-zero and print the failure. `mate --list` still describes `check` and `test`.

## Notes

Reserved for a human-run session. The cold read was stopped before it reported, because the human asked for this to be implemented directly.

## History

- 2026-11-06T19:18:23Z youthful-toad → backlog
- 2026-11-06T19:24:10Z youthful-toad: changed owner, notes
- 2026-11-06T19:24:10Z youthful-toad backlog → todo
