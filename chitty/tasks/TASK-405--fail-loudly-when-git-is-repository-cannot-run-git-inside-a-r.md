---
title: Fail loudly when `git.is_repository` cannot run `git` inside a repository
status: planning
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

- [ ] Property test, generated with Hypothesis: each example builds its own new resolved temporary directory (Hypothesis runs `setUp` once for all examples), asserts no `.git` exists above it, nests directories 1 to 4 deep inside it, places a `.git` directory, a `.git` file, a `.git` symbolic link to a missing path, or nothing, at a drawn level from the temporary directory itself through the deepest directory, and calls `is_repository` on the deepest directory with `PATH` set to an empty directory. With no `.git` at or above it, the result is `False`; otherwise it raises `ChittyError` whose message contains `` `git` ``, `PATH` and the `.git` path. Fails on `main`, where every case returns `False`.
- [ ] Example test: `is_repository` on a path that does not exist, and on a regular file, raises `ChittyError` naming the resolved path, both with `git` on `PATH` and without it. Fails on `main`, which returns `False` for the missing path and raises `NotADirectoryError` for the file.
- [ ] No-regression guard, passing before and after the change: with `git` on `PATH`, `True` for a work tree root and a subdirectory of it, `False` with the directory set to a repository `.git` directory and for a plain temporary directory outside any repository. `make check` passes.

## History

- 2026-11-19T08:43:02Z lively-quartz-crane → planning
- 2026-11-19T08:43:24Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:44:03Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:44:18Z lively-quartz-crane: changed description
- 2026-11-19T08:46:00Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:46:00Z lively-quartz-crane cold-read → planning
