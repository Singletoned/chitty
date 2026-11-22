---
title: Run the test suite with `pytest` and `pytest-xdist`
status: cold-read
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: use `pytest` as the test runner instead of `unittest-parallel`. The earlier rule against `pytest` came from reviewing tests by hand and no longer applies. `pytest` runs the existing `unittest.TestCase` tests unchanged, so this ticket only swaps the runner; tests keep their `unittest` style. What `pytest` gives that the current runner does not: a failing `setUpClass` or `setUpModule` is reported as an error (`TASK-596`: under `unittest-parallel --level test` it is silently dropped); `-m` markers for the `slow` split (`TASK-593`); `mutmut` for mutation testing (`TASK-594`, `pytest` only); and a `conftest.py` hook for the timing recorder (`TASK-590`).

Tried while planning, 2026-11-22, on `main` at the time: `TEST_TIER=check pytest -q -n auto tests` gave `1142 passed, 788 subtests passed` in 97 s (`unittest-parallel` took 87 s on the same tree). `COVERAGE_ROOT=$PWD TEST_TIER=thorough coverage run -m pytest -q -n auto tests`, then `coverage combine` and `coverage report`, gave 93% total in 4 min 20 s with the existing `[tool.coverage.run]` settings (`patch = ["subprocess"]` also covers the `pytest-xdist` workers, which are started with `subprocess`). A scratch module whose `setUpClass` raises gave `ERROR test_fx.py::Cases::test_ok - RuntimeError: boom` and `1 error`, exit non-zero, under `pytest -n 2`.

Changes:

- `pyproject.toml` dev group: remove `unittest-parallel==1.8.6`; add `pytest==9.2.0` and `pytest-xdist==3.8.0`; run `uv lock`.
- `Makefile` `check`: replace the `unittest-parallel` line with `TEST_TIER=check uv run pytest -q -n auto tests`.
- `Makefile` `test`: replace its line with `COVERAGE_ROOT=$(CURDIR) TEST_TIER=thorough uv run coverage run -m pytest -q -n auto tests`, then `uv run coverage combine -q`, `uv run coverage report` and `uv run coverage html -q -d tmp/coverage`. Keep the existing `##` descriptions.
- `.gitignore`: add `.pytest_cache/`.
- `tests/__init__.py`: the suite-timeout comment names the `unittest-parallel` parent, and `_is_worker` uses `multiprocessing.parent_process()`, which is `None` in a `pytest-xdist` worker. Use `os.environ.get("PYTEST_XDIST_WORKER") is not None` instead (set in every worker by `pytest-xdist`), so the controller still fires `PARENT_GRACE_SECONDS` after the workers, and update the comment to name the `pytest` controller.
- Docs that name `unittest` as the runner: `AGENTS.md` (the `make check` bullet and the "Tests use `unittest`" bullet: say tests are `unittest.TestCase` classes run by `pytest`), `README.md` (`make check      # ruff, pyright, unittest`) and `docs/plan/stack.md` (the Dev bullet).

Out of scope: rewriting tests in `pytest` style, `pytest` fixtures or markers, the timing recorder, and per-test timeouts.

No new test: build configuration, checked by the commands in the criteria.

## Acceptance Criteria

- [ ] `make check` passes and its output ends with a `pytest` summary line reporting at least 1142 passed and no failures or errors; `grep -rn unittest-parallel Makefile pyproject.toml uv.lock AGENTS.md README.md docs tests` prints nothing
- [ ] `make test` passes, prints a `coverage report` `TOTAL` line of at least 90%, and leaves `tmp/coverage/index.html`; afterwards `git status --short` is empty
- [ ] A temporary `tests/test_fx_probe.py` (deleted afterwards, not committed) with class `Cases` whose `setUpClass` raises `RuntimeError` and one passing `test_ok` makes `make check` exit non-zero with a `pytest` summary containing `1 error`; record the command and the summary line in a note
- [ ] A temporary `tests/test_probe_worker.py` (deleted afterwards, not committed) asserting `import tests; tests._is_worker is True` passes under `.venv/bin/pytest -n 2 tests/test_probe_worker.py` and fails under `.venv/bin/pytest -p no:xdist tests/test_probe_worker.py`; record both outputs in a note

## History

- 2026-11-22T20:15:42Z plucky-umber-wren → planning
- 2026-11-22T20:15:51Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T20:15:51Z plucky-umber-wren planning → cold-read
- 2026-11-22T20:16:43Z plucky-umber-wren: changed acceptance criteria
