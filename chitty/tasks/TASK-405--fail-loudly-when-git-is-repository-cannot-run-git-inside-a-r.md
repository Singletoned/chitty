---
title: Fail loudly when `git.is_repository` cannot run `git` inside a repository
status: review
created: 2026-11-19
---

## Description

`git.is_repository` (`src/chitty/git.py:371`) catches `FileNotFoundError` and returns `False`. That exception means either that `directory` does not exist or that the `git` program is not on `PATH`; a regular file as `directory` raises `NotADirectoryError`, uncaught. Its callers in `src/chitty/store.py` (lines 457, 586, 631, 672) and `src/chitty/git.py` (lines 297, 331) treat `False` as a folder outside Git and skip Git work silently, so inside a real repository with `git` missing, tickets stop being committed and the main-branch check is skipped, with no error.

Chitty in a folder outside Git is supported: it behaves like `autocommit = false` with nothing ever committed. That must keep working when `git` is not installed.

Decisions:

- Resolve `directory` first; messages name the resolved path.
- `directory` does not exist, or is not a directory: raise `ChittyError` naming it. Check this before running `git`, so the two causes of `FileNotFoundError` never share a branch.
- `git` is not on `PATH`: look for a `.git` entry in `directory` and each of its parents, nearest first, counting a file, a directory or a symbolic link even when it points nowhere (`os.path.lexists`). None found: return `False`. One found: raise `ChittyError` containing `` `git` ``, `PATH` and the nearest `.git` path.
- Everything else is unchanged; non-zero exits from `git` are `TASK-406`'s.

Out of scope: `GIT_DIR` and other Git environment variables; other functions in `git.py` that run `git` (they already fail loudly with `FileNotFoundError`).

Tests go in `tests/test_git.py`, in a class inheriting `RepoTestCase` (`tests/support.py`). To make `git` missing, set `PATH` for the call to an empty temporary directory with `unittest.mock.patch.dict(os.environ, {"PATH": ...})`; this changes the environment, not our code, and the test resolves its own `git` before patching. The repository's property-testing tool is Hypothesis.

## Acceptance Criteria

- [x] Property test, generated with Hypothesis: each example makes its own `tempfile.TemporaryDirectory`, resolved, not `self.root` (Hypothesis runs `setUp` once for all examples), and asserts no parent of it holds a `.git`. It nests directories 1 to 4 deep inside it (level 0 is the temporary directory, level k the k-th nested one), places a `.git` directory, a `.git` file, a `.git` symbolic link to a missing path, or nothing, at a drawn level from 0 through the deepest, and calls `is_repository` on the deepest directory with `PATH` set to an empty directory. With no marker placed, the result is `False`; otherwise it raises `ChittyError` whose message contains `` `git` ``, `PATH` and the `.git` path. Every example with a marker fails on `main`, which returns `False`.
- [x] Example test: `is_repository` on a path that does not exist, and on a regular file, raises `ChittyError` naming the resolved path, both with `git` on `PATH` and without it. Fails on `main`, which returns `False` for the missing path and raises `NotADirectoryError` for the file.
- [x] No-regression guard, passing before and after the change: with `git` on `PATH`, `True` for a work tree root and a subdirectory of it, `False` with the directory set to a repository `.git` directory and for a plain temporary directory outside any repository. `make check` passes.

## Plan

Update git.is_repository to validate the resolved directory before invoking git, and distinguish missing git from a missing directory using nearest-ancestor .git markers via lexists. Add Hypothesis coverage and examples in tests/test_git.py, first run regression tests against the current implementation, then run formatting and make check.

## Notes

Regression tests were run before the implementation and failed as expected: missing Git returned False for repository markers, and invalid directories did not raise ChittyError. The full `make check` passed after implementation.

## Summary

Implemented validation of resolved directories and loud handling of missing Git when an ancestor has a .git marker. Added Hypothesis marker tests and invalid-path and behavior guards in tests/test_git.py. Verification: make check passes (682 tests); committed as d2231ad1. No follow-ups.

## History

- 2026-11-19T08:43:02Z lively-quartz-crane → planning
- 2026-11-19T08:43:24Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:44:03Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:44:18Z lively-quartz-crane: changed description
- 2026-11-19T08:46:00Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:46:00Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:46:03Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:46:58Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:46:58Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:47:02Z lively-quartz-crane planning → todo
- 2026-11-19T08:47:30Z nimble-pearl-eel todo → doing
- 2026-11-19T08:48:22Z nimble-pearl-eel: wrote the plan
- 2026-11-19T08:50:16Z nimble-pearl-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-19T08:50:16Z nimble-pearl-eel doing → review
