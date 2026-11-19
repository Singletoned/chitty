---
title: Commit or restore a ticket file when a Chitty write fails after writing it
status: done
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

A Chitty write that fails after writing files leaves them changed and uncommitted. Seen repeatedly: `TASK-366`'s and `TASK-359`'s worktrees, and on 2026-11-18 `chitty archive TASK-359` (in its worktree) and `chitty archive TASK-372` (on `main`) both moved the file, then failed with `used by more than one file` and left the active file deleted and the archive file untracked (details in the notes). That trigger comes from the history-based read, which `TASK-378` replaces, but the missing restore is general: only `Repo.edit` in `src/chitty/store.py` snapshots ticket files and the index (`_task_file_bytes`, `_restore_task_files`), and only for errors whose message contains `cannot finalize task write`, so it does not restore after `autocommit failed` either (a cold read reproduced every command below, `edit` included, leaving files behind with a failing pre-commit hook). `add`, `archive`, `archive_done`, `restore`, `move`, `renumber` and delete-mode archiving restore nothing.

Decisions:

- One helper in `src/chitty/store.py`, a context manager `Repo._all_or_nothing()`, used by every public ticket write (`add`, `edit`, `archive`, `archive_done`, `restore`, `move`, `renumber`, and `renumber_provisional` once `TASK-391` adds it): before the first file write it snapshots the ticket files (`_task_file_bytes`) and the index bytes; on any exception it restores both, calls `self._invalidate()` and re-raises the original exception unchanged. `Repo.edit` uses it in place of its message test.
- `_prepare_write()` (setup upgrade) runs before the snapshot and is not undone, as today.
- Out of scope: the history-read trigger itself (`TASK-378`).

Tests: real-Git tests in a new `tests/test_failed_writes_restore.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`, a configured user, `autocommit = true`, a current setup (`chitty_version` equal to `CHITTY_VERSION`, so `_prepare_write` writes nothing), and a `.git/hooks/pre-commit` that exits 1 to make every autocommit fail after the files are written (as `tests/test_autocommit.py` does). No property: a fixed set of commands, each listed in the criteria and tested.

## Acceptance Criteria

- [x] With the failing hook, each of `chitty add`, `chitty edit --note`, `chitty archive <ID>`, `chitty archive` (no ID), `chitty move <ID> human`, `chitty renumber <PATH>` (a duplicate made with `git mv`), and a direct `Repo.restore(<ID>)` call (there is no CLI command) fails with the autocommit error, and afterwards `git status --porcelain` and every ticket file's bytes equal what they were before; each fails before the change
- [x] The same holds with `archive = "delete"` for `chitty archive <ID>`; a later run of each command without the hook succeeds; `make check` passes

## Plan

Add Repo._all_or_nothing() to snapshot task-context file bytes and the Git index after _prepare_write(), restore them and invalidate caches on any exception, then re-raise unchanged. Wrap every listed public ticket-write operation, including edit. Add real-Git regression tests in tests/test_failed_writes_restore.py for each specified failing-hook command, including archive delete mode and direct Repo.restore; verify status and ticket bytes restore, then rerun each successfully without the hook. Run regressions unfixed to confirm failure, then make check and commit implementation and tests.

## Notes

Reproduced 2026-11-18 in `.worktrees/task-359` (branch `task-359`, clean worktree, ticket committed there and also present on `main`): `chitty edit TASK-359 --note ...` succeeded, then `chitty archive TASK-359` failed with `TASK-359 is used by more than one file: .../chitty/tasks/TASK-359--....md, .../chitty/tasks/archive/TASK-359--....md`, leaving the active file deleted and the archive file untracked, uncommitted. The same command on `main` for `TASK-366` (also on branch `task-366`) succeeded. Undone by hand with `git restore` and `rm`.

Also on `main` 2026-11-18: `chitty edit TASK-372 --note ...` then `chitty archive TASK-372` (status `planning`, no local or remote `task-372` branch; the branch existed earlier and was removed after landing) failed the same way and left the move uncommitted. `TASK-366` archived fine on `main` minutes earlier. Repro candidate: a ticket whose active path appears in the history of a deleted branch or of `main` itself.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
570 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 641 test suites (641 total tests) across 16 workers
..........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:23:45 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................................./Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
............E..............................................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/.worktrees/task-1...
........TASK-1: doing → review
......no next ticket for --mode work
....................................chitty 0.1.31 is out: run uv tool upgrade chitty
..............................landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_suffix_round_trips (tests.test_property_provisional.TestProvisionalProperties.test_suffix_round_trips)
----------------------------------------------------------------------
  + Exception Group Traceback (most recent call last):
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/tests/test_property_provisional.py", line 29, in test_suffix_round_trips
  |     def test_suffix_round_trips(self, prefix, seed):
  |                ^^^^^^^
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
  |     raise the_error_hypothesis_found
  | hypothesis.errors.FlakyFailure: Hypothesis test_suffix_round_trips(self=<tests.test_property_provisional.TestProvisionalProperties testMethod=test_suffix_round_trips>, prefix='FPQPEC', seed=HypothesisRandom(generated data)) produces unreliable results: Failed on the first call but did not on a subsequent one (1 sub-exception)
  | Failing test case: test_suffix_round_trips(
  |     self=<tests.test_property_provisional.TestProvisionalProperties testMethod=test_suffix_round_trips>,
  |     prefix='FPQPEC',
  |     seed=HypothesisRandom(generated data),
  | )
  | Unreliable test timings! On an initial run, this test took 278.76ms, which exceeded the deadline of 200.00ms, but on a subsequent run it took 0.06 ms, which did not. If you expect this sort of variability in your test timings, consider turning deadlines off for this test by setting deadline=None.
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1253, in _execute_once_for_engine
    |     result = self.execute_once(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1187, in execute_once
    |     result = self.test_runner(data, run)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 831, in default_executor
    |     return function(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1144, in run
    |     return test(*args, **kwargs)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/tests/test_property_provisional.py", line 29, in test_suffix_round_trips
    |     def test_suffix_round_trips(self, prefix, seed):
    |                ^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1040, in test
    |     raise DeadlineExceeded(
    |         datetime.timedelta(seconds=runtime), self.settings.deadline
    |     )
    | hypothesis.errors.DeadlineExceeded: Test took 278.76ms, which exceeds the deadline of 200.00ms. If you expect test cases to take this long, you can use @settings(deadline=...) to either set a higher deadline, or to disable it with deadline=None.
    +------------------------------------

----------------------------------------------------------------------
Ran 641 tests in 45.538s

FAILED (errors=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-388`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
570 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 641 test suites (641 total tests) across 16 workers
..........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:23:45 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................................./Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
............E..............................................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvf_kn42c/repo/.worktrees/task-1...
........TASK-1: doing → review
......no next ticket for --mode work
....................................chitty 0.1.31 is out: run uv tool upgrade chitty
..............................landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_suffix_round_trips (tests.test_property_provisional.TestProvisionalProperties.test_suffix_round_trips)
----------------------------------------------------------------------
  + Exception Group Traceback (most recent call last):
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/tests/test_property_provisional.py", line 29, in test_suffix_round_trips
  |     def test_suffix_round_trips(self, prefix, seed):
  |                ^^^^^^^
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
  |     raise the_error_hypothesis_found
  | hypothesis.errors.FlakyFailure: Hypothesis test_suffix_round_trips(self=<tests.test_property_provisional.TestProvisionalProperties testMethod=test_suffix_round_trips>, prefix='FPQPEC', seed=HypothesisRandom(generated data)) produces unreliable results: Failed on the first call but did not on a subsequent one (1 sub-exception)
  | Failing test case: test_suffix_round_trips(
  |     self=<tests.test_property_provisional.TestProvisionalProperties testMethod=test_suffix_round_trips>,
  |     prefix='FPQPEC',
  |     seed=HypothesisRandom(generated data),
  | )
  | Unreliable test timings! On an initial run, this test took 278.76ms, which exceeded the deadline of 200.00ms, but on a subsequent run it took 0.06 ms, which did not. If you expect this sort of variability in your test timings, consider turning deadlines off for this test by setting deadline=None.
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1253, in _execute_once_for_engine
    |     result = self.execute_once(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1187, in execute_once
    |     result = self.test_runner(data, run)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 831, in default_executor
    |     return function(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1144, in run
    |     return test(*args, **kwargs)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/tests/test_property_provisional.py", line 29, in test_suffix_round_trips
    |     def test_suffix_round_trips(self, prefix, seed):
    |                ^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-388/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1040, in test
    |     raise DeadlineExceeded(
    |         datetime.timedelta(seconds=runtime), self.settings.deadline
    |     )
    | hypothesis.errors.DeadlineExceeded: Test took 278.76ms, which exceeds the deadline of 200.00ms. If you expect test cases to take this long, you can use @settings(deadline=...) to either set a higher deadline, or to disable it with deadline=None.
    +------------------------------------

----------------------------------------------------------------------
Ran 641 tests in 45.538s

FAILED (errors=1)
make: *** [check] Error 1

```
````

Back to `todo` 2026-11-19: the runner error was the flaky `test_suffix_round_trips` deadline in the check before work started, fixed by `TASK-417`. No work had been done.

The new regression tests fail against the pre-change store (8 failures) and pass with the fix. make check passes, including the complete test suite. Commands without the failing hook succeed after rollback checks.

Reviewed:
1: pass - The eight real-Git regressions in tests.test_failed_writes_restore report 8 failures against ebea2856^ store.py and 8 OK with the change, covering all seven requested operations and checking status and file bytes.
2: pass - The delete-mode regression is among those 8 baseline failures and 8 passes; each test reruns without the hook successfully. make check passed: 726 tests OK, ruff and pyright clean.

## Summary

Implemented all-or-nothing rollback for add, edit, archive, archive_done, restore, move and renumber; added real-Git regression coverage for each listed failure path and updated the existing autocommit expectation. Verification: the eight regression tests failed on baseline and pass with the fix; make check passes (725 tests). Follow-up: none.

## History

- 2026-11-18T16:20:21Z lively-quartz-crane → backlog
- 2026-11-18T16:25:57Z lively-quartz-crane: changed notes
- 2026-11-18T16:26:22Z lively-quartz-crane: changed notes
- 2026-11-18T17:56:41Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T17:56:41Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:43Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:56:59Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:59:25Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:25Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:59:27Z lively-quartz-crane planning → todo
- 2026-11-18T22:23:26Z kind-lilac-eel todo → doing
- 2026-11-18T22:24:19Z kind-lilac-eel: changed notes
- 2026-11-18T22:24:19Z kind-lilac-eel doing → error
- 2026-11-19T13:25:56Z quick-ginger-lapwing: changed notes
- 2026-11-19T13:25:56Z quick-ginger-lapwing error → todo
- 2026-11-19T13:27:07Z zesty-navy-zander todo → doing
- 2026-11-19T13:29:52Z zesty-navy-zander: wrote the plan
- 2026-11-19T13:38:40Z zesty-navy-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-19T13:38:40Z zesty-navy-zander doing → review
- 2026-11-19T13:41:24Z lively-ginger-wren: changed notes
- 2026-11-19T13:41:24Z lively-ginger-wren review → done
