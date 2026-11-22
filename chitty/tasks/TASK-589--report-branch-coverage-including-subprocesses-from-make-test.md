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

`unittest-parallel` 1.8.6 (the test runner) has `--coverage` and `--coverage-html DIR` built in, and `coverage` 7.17.2 is installed only because `unittest-parallel` depends on it (`uv tree --invert --package coverage`). Many tests start Chitty or other Python scripts as subprocesses (for example `tests/test_run_loop.py`, `tests/test_next.py`); those are measured only when coverage patches subprocesses. Measured while planning on `-p test_run_loop.py` alone: without the patch `src/chitty/run.py` showed 13%; with it, 42%.

Recipe, tried on the full suite while planning (2026-11-22, a worktree at `main` after `make install`): 1135 tests OK, `TOTAL` 94%, `git status` showing only the intended edits and the ignored `.coverage`.

- `pyproject.toml`: add `"coverage==7.17.2"` to the `dev` dependency group (the `patch` setting needs a recent coverage, so do not rely on the transitive version), and add

  ```toml
  [tool.coverage.run]
  branch = true
  source = ["src/chitty"]
  patch = ["subprocess"]
  data_file = "${COVERAGE_ROOT-.}/.coverage"
  ```

  The data file must be absolute: tests run subprocesses in temporary directories, and a relative data file there loses their data. Coverage expands `${COVERAGE_ROOT-.}` from the environment, defaulting to the current directory for a run outside `make`.
- `Makefile` `test` target: set `COVERAGE_ROOT=$(CURDIR)` and add `--coverage --coverage-html tmp/coverage` on its `unittest-parallel` line. Read the rest of that line from the `Makefile` when you start (`TASK-587` changes it first) and keep it.
- `tests/test_run_error_reporter.py`, `test_interrupted_agent_calls_reporter`: its fake agent kills itself with `SIGINT` and the test asserts exit 130. With coverage loaded in the agent, Python turns the signal into `KeyboardInterrupt` and exits 1, so the test fails under `make test`. Change the agent's shebang from `"#!" + sys.executable + "\n"` to `"#!" + sys.executable + " -S\n"`: `-S` skips the `site` module and so the `.pth` file that starts coverage, and the agent needs neither. Keep the exit-130 assertion. Tried while planning: passes with and without coverage. (A `signal.SIG_DFL` reset was also tried; it was not settled, so do not use it.)
- `.gitignore`: add `.coverage` and `.coverage.*`. `tmp/` is already ignored (`/tmp/`).
- `AGENTS.md`: add to the bullet about `make test` that it reports coverage, with the HTML at `tmp/coverage/index.html`.

Known noise, out of scope: the planning run printed three `coverage` warnings or `DataError` tracebacks (`Exception ignored in atexit callback`) from child processes that exit after `unittest-parallel` has removed its temporary data directory. They do not change the exit status or the result.

Also out of scope: a minimum percentage (`--coverage-fail-under`), coverage in `make check` or CI, and per-test timing (a separate ticket).

No property or unit test: this is build configuration, checked by the commands in the criteria.

## Acceptance Criteria

- [ ] `make test` exits 0, prints a coverage table whose rows include `src/chitty/run.py` and `TOTAL`, and writes `tmp/coverage/index.html`; afterwards `git status --short` in the checkout is empty. Before this change, `make test` output has no line starting `TOTAL`
- [ ] Subprocesses are measured: `.venv/bin/unittest-parallel -s tests -t . -p test_run_loop.py --level test --coverage`, run with `COVERAGE_ROOT` set to the checkout, reports `src/chitty/run.py` at 40% or more (42% when planning), and the same run with `patch` removed from `[tool.coverage.run]` reports it under 20% (13% when planning). Do the `patch`-removed run on a temporary edit and restore `pyproject.toml` afterwards; record both lines in a note
- [ ] `test_interrupted_agent_calls_reporter` still asserts exit 130 and passes under both `make check` and `make test`; before the shebang change it fails under `make test` (record the failing line in a note)
- [ ] `pyproject.toml` pins `coverage==7.17.2` in the `dev` group; `.gitignore` lists `.coverage` and `.coverage.*`; `AGENTS.md` names `tmp/coverage/index.html`; `make -n check` shows no `--coverage` (a guard that `check` stays quick); and `make check` passes

## History

- 2026-11-22T16:48:38Z plucky-umber-wren → planning
- 2026-11-22T16:53:09Z plucky-umber-wren: changed description
- 2026-11-22T16:53:12Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:05:11Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T17:05:11Z plucky-umber-wren cold-read → planning
- 2026-11-22T17:05:13Z plucky-umber-wren planning → cold-read
