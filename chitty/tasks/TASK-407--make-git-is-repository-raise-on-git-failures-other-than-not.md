---
title: Make `git.is_repository` raise on `git` failures other than "not a git repository"
status: done
labels:
  - needs-minor
depends_on:
  - TASK-405
  - TASK-406
created: 2026-11-19
---

## Description

`TASK-406` adds `git.repository_answer`. Make `git.is_repository` (`src/chitty/git.py:371`) use it, so `git` failures other than "not a git repository" raise instead of reading as a folder outside Git.

- Run `git rev-parse --is-inside-work-tree` with `env={**os.environ, "LC_ALL": "C"}`, so the message `repository_answer` matches is English whatever the user's locale. It must be `LC_ALL`: it overrides `LANG` and the other `LC_*` settings.
- Return `repository_answer(["git", "rev-parse", "--is-inside-work-tree"], directory, result.returncode, result.stdout, result.stderr)`, with `directory` the resolved path that `TASK-405` introduces.
- `TASK-405`'s handling of a missing directory or missing `git` stays as it is.
- Intended user-visible change (hence `needs-minor`): a linked worktree whose main repository was moved or deleted (`gitfile does not point to a valid repository`) and a repository with dubious ownership now raise `ChittyError` instead of being treated as a folder outside Git. Bare repositories and `.git` directories still give `False` (status 0, output `false`).

Property tests: none here; the decision is `TASK-406`'s pure function, which carries them. Tests go in `tests/test_git.py`, in a class inheriting `RepoTestCase`. Set environment variables with `unittest.mock.patch.dict(os.environ, ...)`: that patches the environment, not our code.

## Acceptance Criteria

- [x] Example test with real Git: in a repository whose `.git/config` sets `repositoryformatversion = 99`, `is_repository` raises `ChittyError` containing `found 99`. Fails on `main`, which returns `False`.
- [x] Example test with a fake `git`: `PATH` is set to a directory holding only an executable `git` script starting `#!/bin/sh` (not `#!/usr/bin/env sh`, which cannot find `sh` on that `PATH`), which exits 128 printing `fatal: not a git repository` to standard error when `LC_ALL` is `C`, and `Schwerwiegend: Kein Git-Repository` otherwise. With `LC_ALL` removed and `LANG=de_DE.UTF-8` set, `is_repository` on a plain temporary directory returns `False`. This passes on `main`, so the evidence, recorded in a note, is that the test raises when the `LC_ALL` entry is removed from the new `is_repository`.
- [x] `make check` passes.

## Plan

Update `is_repository` to pass `LC_ALL=C` to the subprocess, preserving the resolved directory and existing missing-directory/missing-git handling, then delegate its result to `repository_answer`. Add the two specified integration tests in `tests/test_git.py`; establish their behavior before implementing the change. Run `make check`, format if needed, and commit implementation/test changes with a `Task: TASK-407` trailer.

## Notes

Regression evidence: `test_invalid_repository_format_raises` failed before the implementation because current `is_repository` returned False for repositoryformatversion 99. The fake-git locale test passes with current code, as expected; after implementation, removing the explicit `LC_ALL` entry must make this test fail.

Reviewed: implementation and complete diff checked.
1: pass - `test_invalid_repository_format_raises` passes; running it with `is_repository` loaded from `main` failed with `ChittyError not raised`.
2: pass - `test_not_repository_detection_uses_c_locale` passes; running it with the `LC_ALL` subprocess entry removed raised `ChittyError` with `Schwerwiegend: Kein Git-Repository`.
3: pass - `make check` exited 0; 696 tests passed, ruff and pyright passed.

## Summary

Updated `is_repository` to force `LC_ALL=C` for Git probes and delegate return classification to `repository_answer`, preserving existing missing-directory and missing-Git behavior. Added repositoryformatversion and localized fake-Git tests. Verification: `make check` passed (ruff, pyright, 696 unittest tests, and remaining configured checks); formatter applied to tests. Follow-up: none.

## History

- 2026-11-19T08:51:09Z lively-quartz-crane → planning
- 2026-11-19T08:52:57Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:54:27Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:54:41Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-19T08:54:41Z lively-quartz-crane planning → todo
- 2026-11-19T10:43:58Z honest-quartz-lapwing todo → doing
- 2026-11-19T10:45:02Z honest-quartz-lapwing: wrote the plan
- 2026-11-19T10:45:39Z honest-quartz-lapwing: changed notes
- 2026-11-19T10:47:14Z honest-quartz-lapwing: changed summary
- 2026-11-19T10:47:14Z honest-quartz-lapwing doing → review
- 2026-11-19T10:49:24Z witty-indigo-newt: changed notes; ticked acceptance criteria
- 2026-11-19T10:49:24Z witty-indigo-newt review → done
