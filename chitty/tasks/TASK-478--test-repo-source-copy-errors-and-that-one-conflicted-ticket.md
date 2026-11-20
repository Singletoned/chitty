---
title: Test `Repo.source_copy` errors, and that one conflicted ticket does not break others
status: doing
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

## History

- 2026-11-20T17:43:44Z jolly-dusky-badger → planning
- 2026-11-20T20:05:28Z jolly-dusky-badger: changed description
- 2026-11-20T20:05:28Z jolly-dusky-badger planning → cold-read
- 2026-11-20T20:06:46Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T20:06:46Z jolly-dusky-badger cold-read → todo
- 2026-11-20T20:07:09Z jolly-dusky-badger: changed description
- 2026-11-20T20:17:59Z jolly-maroon-puffin todo → doing
