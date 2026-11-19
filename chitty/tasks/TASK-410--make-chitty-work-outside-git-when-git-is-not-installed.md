---
title: Make Chitty work outside Git when `git` is not installed
status: cold-read
created: 2026-11-19
---

## Description

Chitty without Git is supported: in a folder outside any Git repository it behaves like `autocommit = false`. With `git` installed this works, but with `git` missing from `PATH`, `list`, `show`, `edit`, `note`, `move`, `archive`, `path` and `next` crash with `FileNotFoundError: ... 'git'` (checked 2026-11-19); `add`, `check`, `fix`, `inbox` and `whoami` do not.

Three functions run `git` with no `is_repository` guard and turn failures into an empty answer, which is also why real failures inside a repository are hidden:

- `git.dirty_paths` (`src/chitty/git.py`): catches every `ChittyError` and returns an empty set.
- `git.current_branch` (`src/chitty/git.py`): catches every `ChittyError` and returns `None`.
- `config.git_common_dir` (`src/chitty/config.py`, `@cache`d, reached from `chitty next` through `src/chitty/locks.py`): runs `git rev-parse --git-common-dir` directly.

Fix each the same way: when `git.is_repository(root)` is `False`, return the empty answer (empty set or `None`) without running `git`; otherwise run `git` without catching its errors, so a failure inside a repository raises `ChittyError`. `git.historical_files` already has this guard. `git.is_repository` already returns `False` when `git` is missing and no `.git` exists, and raises when a `.git` exists (`TASK-405`); that error stays. Out of scope: the `git` calls in `src/chitty/run.py`, since `chitty run` needs Git for its worktrees.

Tests go in a new `tests/test_no_git_installed.py`, classes inheriting `RepoTestCase`, whose root is not a Git repository. Make `git` missing with `CliRunner().invoke(..., env={"PATH": <empty directory>})` or `unittest.mock.patch.dict(os.environ, ...)`, which patch the environment, not our code. Call `config.git_common_dir.cache_clear()` between runs, or its cache hides the crash.

## Acceptance Criteria

- [ ] Equivalence test: in a root outside Git with `autocommit = false`, holding one ticket made beforehand, each of `chitty list`, `chitty show <ID>`, `chitty path <ID>`, `chitty next`, `chitty edit <ID> -s planning`, `chitty note <ID> x`, `chitty check`, `chitty move <ID> human` and `chitty archive <ID>` runs once with `git` on `PATH` and once, in a fresh copy of the same root, with `PATH` set to an empty directory. Both runs exit 0 and give the same standard output after replacing the root path, and the same relative file paths and contents afterwards after replacing History timestamps (`YYYY-MM-DDTHH:MM:SSZ`) with a fixed string. Each command is a `subTest`; the test first asserts `git.is_repository(root)` is `False`. The test as a whole fails on `main` (`chitty check` alone already passes there).
- [ ] Tests inside a real repository with `git` on `PATH`, where `.git/index` is overwritten with `garbage` after `git init` (so `git rev-parse --is-inside-work-tree` prints `true` but `git status` exits 128 with `index file smaller than expected`): `git.dirty_paths` raises `ChittyError` whose message contains `index file smaller than expected`. Fails on `main`, which returns an empty set. Also: `git.current_branch` and `config.git_common_dir` return `None` in a root outside Git with `PATH` set to an empty directory.
- [ ] `make check` passes.

## History

- 2026-11-19T09:13:54Z lively-quartz-crane → planning
- 2026-11-19T09:14:25Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T09:14:33Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:18:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T09:18:08Z lively-quartz-crane cold-read → planning
- 2026-11-19T09:18:12Z lively-quartz-crane planning → cold-read
