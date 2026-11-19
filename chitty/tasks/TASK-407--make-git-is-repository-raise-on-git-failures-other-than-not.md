---
title: Make `git.is_repository` raise on `git` failures other than "not a git repository"
status: doing
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

- [ ] Example test with real Git: in a repository whose `.git/config` sets `repositoryformatversion = 99`, `is_repository` raises `ChittyError` containing `found 99`. Fails on `main`, which returns `False`.
- [ ] Example test with a fake `git`: `PATH` is set to a directory holding only an executable `git` script starting `#!/bin/sh` (not `#!/usr/bin/env sh`, which cannot find `sh` on that `PATH`), which exits 128 printing `fatal: not a git repository` to standard error when `LC_ALL` is `C`, and `Schwerwiegend: Kein Git-Repository` otherwise. With `LC_ALL` removed and `LANG=de_DE.UTF-8` set, `is_repository` on a plain temporary directory returns `False`. This passes on `main`, so the evidence, recorded in a note, is that the test raises when the `LC_ALL` entry is removed from the new `is_repository`.
- [ ] `make check` passes.

## History

- 2026-11-19T08:51:09Z lively-quartz-crane → planning
- 2026-11-19T08:52:57Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:54:27Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:54:41Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-19T08:54:41Z lively-quartz-crane planning → todo
- 2026-11-19T10:43:58Z honest-quartz-lapwing todo → doing
