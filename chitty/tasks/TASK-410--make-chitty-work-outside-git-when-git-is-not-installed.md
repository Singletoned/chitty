---
title: Make Chitty work outside Git when `git` is not installed
status: cold-read
created: 2026-11-19
---

## Description

Chitty without Git is supported: in a folder outside any Git repository it behaves like `autocommit = false`. With `git` installed this works, but with `git` missing from `PATH` every command except `chitty add` crashes with `FileNotFoundError: ... 'git'` (checked 2026-11-19: `list`, `show`, `edit`, `note`). The path is `Repo._dirty_paths_for` (`src/chitty/store.py`) calling `git.dirty_paths` (`src/chitty/git.py`), which runs `git status` and only works outside Git because it turns every `ChittyError` into an empty set. That also hides real `git status` failures inside a repository.

Fix:

- `git.dirty_paths`: return an empty set when `git.is_repository(root)` is `False`; otherwise run `git status` without catching errors, so a failure inside a repository raises.
- Find every other `git` call that commands reach in a folder outside Git (for example `git.historical_files`, `git.current_branch`, the readers behind `chitty show` and `chitty list`) and give each the same `is_repository` guard, rather than catching errors. `git.is_repository` already returns `False` when `git` is missing and no `.git` exists (`TASK-405`).

Tests go in a new `tests/test_no_git_installed.py`, classes inheriting `RepoTestCase`, whose root is not a Git repository. Make `git` missing with `CliRunner().invoke(..., env={"PATH": <empty directory>})` or `unittest.mock.patch.dict(os.environ, ...)`, which patch the environment, not our code.

## Acceptance Criteria

- [ ] Equivalence test: in a root outside Git with `autocommit = false`, holding one ticket made beforehand, each of `chitty list`, `chitty show <ID>`, `chitty edit <ID> -s planning`, `chitty note <ID> x`, `chitty check`, `chitty move <ID> human` and `chitty archive <ID>` runs once with `git` on `PATH` and once, in a fresh copy of the same root, with `PATH` set to an empty directory. Both runs give the same exit status (0), the same standard output after replacing the root path, and the same files and contents afterwards. Each command is a `subTest`; the test first asserts `git.is_repository(root)` is `False`. Fails on `main`, where the runs without `git` show a `FileNotFoundError` traceback.
- [ ] Test: inside a real repository with `git` on `PATH`, where `.git/index` is overwritten with `garbage` after `git init` (so `git rev-parse --is-inside-work-tree` prints `true` but `git status` exits 128 with `index file smaller than expected`), `git.dirty_paths` raises `ChittyError` containing that message. Fails on `main`, which returns an empty set.
- [ ] `make check` passes.

## History

- 2026-11-19T09:13:54Z lively-quartz-crane → planning
- 2026-11-19T09:14:25Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T09:14:33Z lively-quartz-crane planning → cold-read
