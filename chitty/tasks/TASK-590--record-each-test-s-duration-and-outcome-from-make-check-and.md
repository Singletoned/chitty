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

`unittest-parallel` 1.8.6 takes `--result <module>.<class>`, a custom result class used in each worker. Tried while planning: a `unittest.TextTestResult` subclass overriding `addDuration(test, elapsed)` gets one call per test, in each worker process, and the run still reports normally.

Add `tests/timing.py` with `TimingResult(unittest.TextTestResult)`:

- Track each test's outcome from `addSuccess` (`pass`), `addFailure` (`fail`), `addError` (`error`), `addSkip` (`skip`), `addExpectedFailure` (`expected-fail`) and `addUnexpectedSuccess` (`unexpected-pass`), each calling `super()`. Subtest failures arrive through `addSubTest`: record `fail` or `error` for the parent test if any subtest fails or errors.
- In `addDuration(test, elapsed)`, after `super()`, append one JSON object per line: `time` (UTC, `datetime.now(UTC).isoformat()`), `test` (`test.id()`), `seconds`, `outcome`, `tier` (from `TEST_TIER`) and `commit` (from `TEST_COMMIT`). Create the file's parent directories if missing. Write each line with one `os.write` on a descriptor opened with `O_APPEND`, because several worker processes append at once.
- Read `TEST_TIMINGS_FILE` from the environment. Unset means record nothing, for plain `python -m unittest` and editor runs. When it is set, `TEST_TIER` and `TEST_COMMIT` are required: raise naming the missing one rather than writing a partial record. None of the names may start with `CHITTY_`, which `tests/__init__.py` deletes from the environment.

`Makefile`: on the `unittest-parallel` line of both `check` and `test`, add `TEST_TIMINGS_FILE="$$(git rev-parse --path-format=absolute --git-common-dir)/chitty/test-timings.jsonl" TEST_COMMIT="$$(git rev-parse HEAD)"` to the environment and `--result tests.timing.TimingResult` to the options, keeping what is already there (`TEST_TIER`, and the coverage options `TASK-589` adds to `test`). The git common directory is shared by every worktree, so all runs land in one file in the main checkout's `.git`, outside the working tree (no `.gitignore` change). `scripts/check_linux.sh` makes its own repository in the container before `make check`, so this works there and those records are discarded with the container.

Out of scope: reading or summarising the file, the retro step, rotating or trimming the file, and timing anything other than Python tests.

No property: the outcomes are a fixed set of six, and the criteria test the four common ones end to end; `expected-fail` and `unexpected-pass` follow the same code path.

## Acceptance Criteria

- [ ] Tests in `tests/test_timing_records.py` write a temporary test module with one passing, one failing, one erroring and one skipped test, run it with `[sys.executable, "-m", "unittest_parallel", ..., "--result", "tests.timing.TimingResult"]` (`PYTHONPATH` at the repository root, `TEST_TIMINGS_FILE` in a temporary directory whose parent does not yet exist, `TEST_TIER=check`, `TEST_COMMIT=abc`), and assert exactly four JSON lines, one per test id, with `outcome` `pass`, `fail`, `error` and `skip` respectively, a `seconds` float at least 0, `tier` `check`, `commit` `abc` and a `time` that parses with `datetime.fromisoformat`. They fail before the change on behaviour: first commit `tests/timing.py` with `TimingResult` subclassing `unittest.TextTestResult` and writing nothing
- [ ] With `TEST_TIMINGS_FILE` unset the same run exits as before and writes no file; with `TEST_TIMINGS_FILE` set but `TEST_TIER` or `TEST_COMMIT` unset, the run fails with an error naming the missing variable (tested in the same file)
- [ ] `make -n check` and `make -n test` each show `--result tests.timing.TimingResult` on the `unittest-parallel` line with `TEST_TIMINGS_FILE` set under the git common directory at `chitty/test-timings.jsonl`; after `make check` in a worktree, that file in the main checkout's `.git` has gained exactly as many lines as the `Ran N tests` count (compare `wc -l` before and after); `git status --short` is empty; `make check` passes

## History

- 2026-11-22T17:11:06Z plucky-umber-wren → planning
