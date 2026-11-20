---
title: Test `Repo.source_copy` errors, and that one conflicted ticket does not break others
status: done
depends_on:
  - TASK-476
parent: TASK-376
created: 2026-11-20
---

## Description

`TASK-476` adds `Repo.source_copy` in `src/chitty/store.py`, which raises errors from `ticket_source` (`src/chitty/ticket_source.py`) and `git.changed_since_split`, and its own parse and duplicate-file errors, for the ID being read only. `TASK-476` tests only successful reads. This ticket tests the errors and that a conflicted ticket does not break reads of other tickets. No new code is expected; if a test shows `source_copy` disagreeing with the expected error, fix `source_copy` and say so in the review note.

Expected errors (all `ChittyError`):

- Local `task-1` and `origin/task-1` both ahead of `main` and diverged: `ticket_source`'s `has diverged refs` error naming `origin/task-1` and `task-1`.
- `TASK-1` changed on both `task-1` and `main` since they split: `changed on both` naming `task-1` and `main`.
- `task-1` an orphan branch (no history in common with `main`): `git.changed_since_split`'s `unrelated histories` error.
- A malformed `TASK-1` file committed on `task-1`: `task-1:<relative path>: <error>`.
- Two working-tree files for `TASK-2`: `TASK-2 is used by more than one file: <paths>`.
- A malformed working-tree `TASK-3` on `main`: `<absolute path>: <error>`.

Because the code exists, each test must be shown to catch a wrong version. Commit these mutants as tests, in the style of `tests/test_property_blockers.py` (`TestBlockerPropertyMutants`): each applies the wrong version with `unittest.mock.patch.object`, runs the same check, and asserts it fails (`assertRaises(AssertionError)`). Each mutant is a `with unittest.mock.patch(...)` block around the same check helper the positive test uses; a wrapper captures the real function before patching, so it does not call itself. The wrong versions: (1) `Repo.source_copy` wrapped so that it first calls `self._choose_source` for every ID in `self.ticket_ids()`, so one conflict fails every read, against the `TASK-2` check of criterion 1; (2) `Repo.source_copy` wrapped to call the original and return `None` if it raises `ChittyError`, against the malformed-file checks; (3) `chitty.store.ticket_source` wrapped to pass a `changed_on_both` that always returns `False`, against the changed-on-both check.

Tests: a new `tests/test_source_copy_errors.py`, set up as `tests/test_source_copy.py` from `TASK-476` is, calling `Repo.open(root)` directly, one test per error. Make remote-tracking refs with `git update-ref refs/remotes/origin/task-1 <commit>`; make the orphan with `git checkout --orphan task-1`, commit, then `git checkout main` before reading. Put the mutant tests in the same file, as one `TestSourceCopyErrorMutants` class. Build expected paths from `repo.root`, not the raw temporary directory, and check each duplicate path is contained in the message rather than their order. No property: a fixed set of error cases.

## Acceptance Criteria

- [ ] Each conflict case in the Description (diverged refs, changed on both, orphan branch) makes `source_copy(TASK-1)` raise the stated error, and a `TASK-1` file committed on `task-1` with its closing `---` removed raises `ChittyError` starting with `task-1:chitty/tasks/TASK-1--`; in each case, on the same `Repo`, `ticket_ids()` and `source_copy(TASK-2)` for a ticket only on `main` succeed
- [ ] The two working-tree cases in the Description raise the stated errors for `TASK-2` and `TASK-3`
- [ ] Mutant 1 is caught by the `TASK-2` check of criterion 1, mutant 2 by the malformed-file checks, and mutant 3 by the changed-on-both check: each mutant test asserts the matching check fails against it; `make check` passes

## Plan

Add isolated Git fixtures and shared checks for each error and unaffected ticket; exercise the shared checks against the three specified patched mutants, then format and run the full checks.

## Notes

The mutant tests confirm the shared checks fail against eager selection, swallowed malformed-file errors in both locations, and ignored changed-on-both detection.

Reviewed:
1: pass - `.venv/bin/python -m unittest -v tests.test_source_copy_errors` printed OK for all four branch error and isolation tests; the eager-selection and swallowed-error mutants confirm the shared checks fail against those wrong versions.
2: pass - the same command printed OK for duplicate and malformed working-tree tests; the swallowed-error mutant confirms the malformed-file check fails against that wrong version.
3: pass - the same command printed OK for all three mutant tests, which assert the shared checks fail under the specified patches; `make check` printed OK for 842 tests, with ruff and pyright passing.

## Summary

Added source-copy error and isolation tests with three mutation checks; no production changes needed. Verified targeted tests and make check (837 tests). No follow-ups.

## History

- 2026-11-20T17:43:44Z jolly-dusky-badger → planning
- 2026-11-20T20:05:28Z jolly-dusky-badger: changed description
- 2026-11-20T20:05:28Z jolly-dusky-badger planning → cold-read
- 2026-11-20T20:06:46Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T20:06:46Z jolly-dusky-badger cold-read → todo
- 2026-11-20T20:07:09Z jolly-dusky-badger: changed description
- 2026-11-20T20:17:59Z jolly-maroon-puffin todo → doing
- 2026-11-20T20:19:54Z jolly-maroon-puffin: wrote the plan
- 2026-11-20T20:20:53Z jolly-maroon-puffin: changed notes
- 2026-11-20T20:22:21Z jolly-maroon-puffin: changed summary
- 2026-11-20T20:22:24Z jolly-maroon-puffin doing → review
- 2026-11-20T20:24:53Z plucky-silver-badger: changed notes
- 2026-11-20T20:24:53Z plucky-silver-badger review → done
