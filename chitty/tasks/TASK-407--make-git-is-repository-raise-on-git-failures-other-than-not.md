---
title: Make `git.is_repository` raise on `git` failures other than "not a git repository"
status: planning
depends_on:
  - TASK-405
  - TASK-406
created: 2026-11-19
---

## Description

`TASK-406` adds `git.repository_answer`. Make `git.is_repository` (`src/chitty/git.py:371`) use it, so `git` failures other than "not a git repository" raise instead of reading as a folder outside Git.

- Run `git rev-parse --is-inside-work-tree` with `LC_ALL=C` added to a copy of the environment, so the message `repository_answer` matches is English whatever the user's locale.
- Return `repository_answer(command, directory, ...)`, passing the resolved directory that `TASK-405` introduces.
- `TASK-405`'s handling of a missing directory or missing `git` stays as it is.

Tests go in `tests/test_git.py`, in a class inheriting `RepoTestCase`. Set environment variables with `unittest.mock.patch.dict(os.environ, ...)`: that patches the environment, not our code.

## Acceptance Criteria

- [ ] Example test with real Git: in a repository whose `.git/config` sets `repositoryformatversion = 99`, `is_repository` raises `ChittyError` containing `found 99`. Fails on `main`, which returns `False`.
- [ ] Example test with a fake `git`: `PATH` is set to a directory holding only an executable `git` script starting `#!/bin/sh` (not `#!/usr/bin/env sh`, which cannot find `sh` on that `PATH`), which exits 128 printing `fatal: not a git repository` to standard error when `LC_ALL` is `C`, and `Schwerwiegend: Kein Git-Repository` otherwise. With `LC_ALL` removed and `LANG=de_DE.UTF-8` set, `is_repository` on a plain temporary directory returns `False`. It passes on `main`; the evidence is that it raises on a version without `LC_ALL=C`.
- [ ] `make check` passes.

## History

- 2026-11-19T08:51:09Z lively-quartz-crane → planning
