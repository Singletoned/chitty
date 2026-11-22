---
title: Report branch coverage, including subprocesses, from `make test`
status: cold-read
owner: plucky-umber-wren
depends_on:
  - TASK-587
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: measure coverage. It goes in the thorough tier, `make test`; `make check` stays quick. Report only: no minimum percentage for now.

`unittest-parallel` 1.8.6 (the test runner) has `--coverage`, `--coverage-branch` and `--coverage-html DIR` built in, and `coverage` 7.17.2 is installed only because `unittest-parallel` depends on it (`uv tree --invert --package coverage`). Many tests start Chitty as a subprocess (for example `tests/test_run_loop.py`, `tests/test_next.py`), and those are not measured unless coverage patches subprocesses. Measured while planning, on `-p test_run_loop.py` alone: without the patch `src/chitty/run.py` showed 13% and `TOTAL` 34%; with it, 42% and 47%.

Changes:

- `pyproject.toml`: add `"coverage==7.17.2"` to the `dev` dependency group (the `patch` setting needs a recent coverage, so do not rely on the transitive version), and add

  ```toml
  [tool.coverage.run]
  branch = true
  source = ["src/chitty"]
  patch = ["subprocess"]
  ```

  `unittest-parallel` passes no rcfile, so coverage reads `pyproject.toml` itself.
- `Makefile` `test` target: run with `COVERAGE_FILE=$(CURDIR)/.coverage` in its environment and add `--coverage --coverage-html tmp/coverage` to its `unittest-parallel` line. The absolute data file matters: tests change into temporary directories, and subprocess data written relative to them would be lost. Keep the rest of the line as `TASK-587` leaves it.
- `.gitignore`: add `.coverage` and `.coverage.*`. `tmp/` is already ignored (`/tmp/`).
- `README.md` or `AGENTS.md`, wherever `make test` is described: one line saying it reports coverage, with the HTML at `tmp/coverage/index.html`.

Known obstacle, found while planning (full suite with this configuration, 2026-11-22: 1135 tests, `TOTAL` 94%, one failure): `tests/test_run_error_reporter.py` `test_interrupted_agent_calls_reporter` expects exit 130, but its fake agent (`os.kill(os.getpid(), signal.SIGINT)`) now runs with coverage loaded, turns the signal into `KeyboardInterrupt` and exits 1. Two fixture changes were tried on that module alone: `signal.signal(signal.SIGINT, signal.SIG_DFL)` before the kill, and a `-S` shebang (skips the `.pth` file that starts coverage). Each run ended with `coverage.exceptions.DataError: ... unable to open database file`, and the second reported `TOTAL` 0%, so the cause is not settled: possibly a data file left by a process killed by a signal, or the trial passing `COVERAGE_FILE` beside `--coverage-rcfile`. Find the cause and fix the fixture or configuration so the test passes with and without coverage; this is a fixture whose behaviour coverage changes, not a runner bug, but do not drop or loosen the test. Record what you found in a note.

Out of scope: a minimum percentage (`--coverage-fail-under`), coverage in `make check` or CI, and per-test timing (a separate ticket).

No property or unit test: this is build configuration, checked by the commands in the criteria.

## Acceptance Criteria

- [ ] `make test` exits 0, prints a coverage table whose rows include `src/chitty/run.py` and `TOTAL`, and writes `tmp/coverage/index.html`; afterwards `git status --short` in the checkout is empty (no stray `.coverage*` files there or in `tests/`). On `main`, `make test` prints no coverage table
- [ ] Subprocesses are measured: `.venv/bin/unittest-parallel -s tests -t . -p test_run_loop.py --level test --coverage` with the new configuration reports `src/chitty/run.py` at 40% or more (it was 42% when planning), while the same command with `patch` removed from `[tool.coverage.run]` reports it under 20% (13% when planning). Record both lines in a note
- [ ] `make -n check` shows no `--coverage` option, and `make check` passes

## History

- 2026-11-22T16:48:38Z plucky-umber-wren → planning
- 2026-11-22T16:53:09Z plucky-umber-wren: changed description
- 2026-11-22T16:53:12Z plucky-umber-wren planning → cold-read
