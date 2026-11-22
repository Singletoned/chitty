---
title: Record each test's duration and outcome from `make check` and `make test`
status: planning
owner: plucky-umber-wren
depends_on:
  - TASK-589
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: keep a history of how long each test takes, and whether it passed, across runs. Splitting slow tests out of `make check` is then a retro job that rests on data, and a test that fails only sometimes shows up as passing and failing at the same commit. No standard local tool does this for `unittest` (`pytest-monitor` is pytest-only; hosted services would send project data out), so record it ourselves. A later ticket adds the summary script and the retro step; this one only records.

`unittest-parallel` 1.8.6 takes `--result <module>.<class>`, a custom result class used in each worker. Tried while planning: a custom `unittest.TextTestResult` subclass runs in each worker process and the run still reports normally. Do not rely on `addDuration`: on Python 3.13 a skipped test returns before `addDuration` is called (cold read, 2026-11-22), so skips would go unrecorded. `startTest` and `stopTest` run for every test, skips included.

Add `tests/timing.py` with `TimingResult(unittest.TextTestResult)`:

- Track each test's outcome from `addSuccess` (`pass`), `addFailure` (`fail`), `addError` (`error`), `addSkip` (`skip`), `addExpectedFailure` (`expected-fail`) and `addUnexpectedSuccess` (`unexpected-pass`), each calling `super()`. Subtest failures arrive through `addSubTest`: record `fail` or `error` for the parent test if any subtest fails or errors.
- Time each test yourself: `time.perf_counter()` in `startTest`, and in `stopTest`, after `super()`, append one JSON object per line: `time` (UTC, `datetime.now(UTC).isoformat()`), `test` (`test.id()`), `seconds` (the difference), `outcome`, `tier` (from `TEST_TIER`) and `commit` (from `TEST_COMMIT`). Create the file's parent directories if missing. A class or module fixture failure (`setUpClass`, `setUpModule`) reaches `addError` with a placeholder test that never starts or stops: write its record from `addError` directly, with `seconds` 0.0 and `outcome` `error`. Write each line with one `os.write` on a descriptor opened with `O_APPEND`, because several worker processes append at once.
- Read `TEST_TIMINGS_FILE` from the environment. Unset means record nothing, for plain `python -m unittest` and editor runs. When it is set, `TEST_TIER` and `TEST_COMMIT` are required: raise naming the missing one rather than writing a partial record. None of the names may start with `CHITTY_`, which `tests/__init__.py` deletes from the environment.

`Makefile` (after `TASK-589` lands, which this ticket depends on): on the `unittest-parallel` line of both `check` and `test`, add `TEST_TIMINGS_FILE="$$(git rev-parse --path-format=absolute --git-common-dir)/chitty/test-timings.jsonl" TEST_COMMIT="$$(git rev-parse HEAD)"` to the environment and `--result tests.timing.TimingResult` to the options, keeping what is already there (`TEST_TIER`, and the coverage options `TASK-589` adds to `test`). The git common directory is shared by every worktree, so all runs land in one file in the main checkout's `.git`, outside the working tree (no `.gitignore` change). `scripts/check_linux.sh` makes its own repository in the container before `make check`, so this works there and those records are discarded with the container.

Out of scope: reading or summarising the file, the retro step, rotating or trimming the file, and timing anything other than Python tests.

No property for outcomes: they are a fixed set of six, and the criteria test the four common ones end to end; `expected-fail` and `unexpected-pass` follow the same code path. Concurrent appends get a stress test (criterion 4) rather than a property, because they need real worker processes.

## Acceptance Criteria

- [ ] Tests in `tests/test_timing_records.py` write a test module into a temporary directory `D` with one passing, one failing, one erroring and one skipped test, run `[sys.executable, "-m", "unittest_parallel", "-s", D, "-t", D, "--level", "test", "--result", "tests.timing.TimingResult"]` (`PYTHONPATH` at the repository root, `TEST_TIMINGS_FILE` in a temporary directory whose parent does not yet exist, `TEST_TIER=check`, `TEST_COMMIT=abc`), and assert exactly four JSON lines, one per test id, with `outcome` `pass`, `fail`, `error` and `skip` respectively, a `seconds` float at least 0, `tier` `check`, `commit` `abc` and a `time` that parses with `datetime.fromisoformat`. A fifth case adds a class whose `setUpClass` raises and asserts one more line with `outcome` `error`. They fail before the change on behaviour: first commit `tests/timing.py` with `TimingResult` subclassing `unittest.TextTestResult` and writing nothing
- [ ] With `TEST_TIMINGS_FILE` unset the same run writes no file and its exit status is unchanged; with `TEST_TIMINGS_FILE` set but `TEST_TIER` or `TEST_COMMIT` unset, the run exits non-zero and its output names the missing variable (tested in the same file)
- [ ] `make -n check` and `make -n test` each show `--result tests.timing.TimingResult` on the `unittest-parallel` line with `TEST_TIMINGS_FILE` set under the git common directory at `chitty/test-timings.jsonl`; after `make check` in a worktree, that file in the main checkout's `.git` has gained exactly as many lines as the `Ran N tests` count, plus one for each class or module fixture error (none expected) (compare `wc -l` before and after); `git status --short` is empty; `make check` passes
- [ ] A stress test in the same file runs a generated module of 200 trivial tests with `-j 4` and asserts the file has exactly 200 lines, every one parses as JSON, and the 200 test ids are distinct; it fails if records are written with buffered `open(...).write` in several pieces rather than one `os.write` (show this by a committed variant or a note)

## History

- 2026-11-22T17:11:06Z plucky-umber-wren → planning
- 2026-11-22T17:11:14Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:12:24Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T17:12:24Z plucky-umber-wren cold-read → planning
