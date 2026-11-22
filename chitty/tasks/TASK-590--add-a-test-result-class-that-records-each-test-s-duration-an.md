---
title: Add a test result class that records each test's duration and outcome
status: planning
owner: plucky-umber-wren
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: keep a history of how long each test takes, and whether it passed, across runs. Splitting slow tests out of `make check` is then a retro job that rests on data, and a test that fails only sometimes shows up as passing and failing at the same commit. No standard local tool does this for `unittest` (`pytest-monitor` is pytest-only; hosted services would send project data out), so record it ourselves. This ticket adds only the recorder; a separate ticket wires it into the `Makefile`, and a later one summarises the file.

`unittest-parallel` 1.8.6 takes `--result <module>.<class>`: it imports the module in the parent process (`unittest_parallel/main.py`, around line 104) and uses the class in each worker. Do not rely on `addDuration`: on Python 3.13 a skipped test returns before it is called. `startTest` and `stopTest` run for every test, skips included.

Add `tests/timing.py` with `TimingResult(unittest.TextTestResult)`. Every override calls `super()`.

- Environment, read when the module is imported: `TEST_TIMINGS_FILE` (the file to append to), `TEST_TIER` and `TEST_COMMIT`. If `TEST_TIMINGS_FILE` is unset, record nothing (plain `python -m unittest` and editor runs). If it is set and `TEST_TIER` or `TEST_COMMIT` is unset, raise at import with a message naming the missing variable; because the parent imports the module first, the run fails before any test starts. None of the names may start with `CHITTY_`, which `tests/__init__.py` deletes.
- `startTest`: note the test id as started and its `time.perf_counter()`.
- Outcome, kept per test id: `addSuccess` gives `pass`, `addFailure` `fail`, `addError` `error`, `addSkip` `skip`, `addExpectedFailure` `expected-fail`, `addUnexpectedSuccess` `unexpected-pass`. Subtests arrive through `addSubTest(test, subtest, err)`, where `err` is `None` for a passing subtest; a failing subtest leaves the parent with no `addSuccess`. For the parent: `error` if any subtest errored, else `fail` if any failed; a passing subtest never overwrites either. Tell failure from error with `issubclass(err[0], test.failureException)`.
- `stopTest`: append the record (below) with `seconds` from `perf_counter`.
- Fixture failures: `setUpClass`, `setUpModule` and their tear-downs reach `addError` (or `addSkip`, for a `SkipTest` raised there) with a placeholder test that never starts or stops. When `addError` or `addSkip` gets a test whose id was never started, write its record there directly with `seconds` 0.0; otherwise leave it to `stopTest`.
- Record: one JSON object per line with `time` (`datetime.now(UTC).isoformat()`), `test` (`test.id()`), `seconds`, `outcome`, `tier` and `commit`. Create the file's parent directories if missing. Write each line with a single `os.write` on a descriptor opened with `O_APPEND`, because several worker processes append at once.

Tests in `tests/test_timing_records.py` share one harness: write a test module into a fresh temporary directory `D` and run `[sys.executable, "-m", "unittest_parallel", "-s", D, "-t", D, "--level", "test", "--result", "tests.timing.TimingResult"]` with `cwd` at the repository root and `PYTHONPATH` set to it. Build the child environment from `os.environ` with `TEST_TIMINGS_FILE`, `TEST_TIER` and `TEST_COMMIT` removed, then set each one the case needs explicitly: `make check` itself will export them once the wiring ticket lands, and the child must not inherit them. Unless a case says otherwise: `TEST_TIMINGS_FILE` in a temporary directory whose parent does not yet exist, `TEST_TIER=check`, `TEST_COMMIT=abc`.

To show the tests fail before the change, run them first against a stub `TimingResult` that only subclasses `unittest.TextTestResult`, and record the failures in a note; the stub is not a deliverable.

Out of scope: the `Makefile` (a separate ticket), reading or summarising the file, the retro step, and rotating or trimming the file.

No property for outcomes: they are a fixed set, each case listed in the criteria and tested. Concurrent appends get a stress test rather than a property, because they need real worker processes.

## Acceptance Criteria

- [ ] A module with class `Cases` holding `test_pass`, `test_fail`, `test_error`, a skipped `test_skip` and an `@unittest.expectedFailure` `test_expected` that fails gives exactly five lines, one per test id, with `outcome` `pass`, `fail`, `error`, `skip` and `expected-fail`; each has a `seconds` float at least 0, `tier` `check`, `commit` `abc` and a `time` that `datetime.fromisoformat` parses
- [ ] Subtests and fixtures, each in its own module: a `self.subTest` loop that fails, then passes gives one line with `outcome` `fail`; one that errors, then fails gives `error`; a class whose `setUpClass` raises `RuntimeError` gives one line with `outcome` `error` and `seconds` 0.0; and a class whose `setUpClass` raises `unittest.SkipTest` gives one line with `outcome` `skip` and `seconds` 0.0
- [ ] With `TEST_TIMINGS_FILE` removed, the module from criterion 1 writes no file and exits with the same status as the same command without `--result`; with `TEST_TIMINGS_FILE` set and `TEST_TIER` removed, and again with `TEST_COMMIT` removed, the run exits non-zero, its output names the missing variable, and no test runs
- [ ] A stress test runs a generated module of 200 trivial tests with the harness plus `-j 4` and asserts the file has exactly 200 lines, every one parses as JSON, and the 200 test ids are distinct. It checks counts and parseability only; `make check` passes

## History

- 2026-11-22T17:11:06Z plucky-umber-wren → planning
- 2026-11-22T17:11:14Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:12:24Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T17:12:24Z plucky-umber-wren cold-read → planning
- 2026-11-22T17:12:27Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:13:39Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T17:13:39Z plucky-umber-wren cold-read → planning
- 2026-11-22T17:13:41Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:15:11Z plucky-umber-wren: changed title, dependencies, description, acceptance criteria
- 2026-11-22T17:15:11Z plucky-umber-wren cold-read → planning
