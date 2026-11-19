---
title: Make Chitty work outside Git when `git` is not installed
status: review
created: 2026-11-19
---

## Description

Chitty without Git is supported: in a folder outside any Git repository it behaves like `autocommit = false`. With `git` installed this works, but with `git` missing from `PATH`, `list`, `show`, `edit`, `note`, `move`, `archive`, `path` and `next` crash with `FileNotFoundError: ... 'git'` (checked 2026-11-19); `add`, `check`, `fix`, `inbox` and `whoami` do not.

Three functions run `git` with no `is_repository` guard and turn failures into an empty answer, which is also why real failures inside a repository are hidden:

- `git.dirty_paths` (`src/chitty/git.py`): catches every `ChittyError` and returns an empty set.
- `git.current_branch` (`src/chitty/git.py`): catches every `ChittyError` and returns `None`.
- `config.git_common_dir` (`src/chitty/config.py`, `@cache`d, reached from `chitty next` through `src/chitty/locks.py`): runs `git rev-parse --git-common-dir` directly and returns `None` on any non-zero exit.

Fix each the same way: when `git.is_repository(root)` is `False`, return the empty answer (empty set or `None`) without running `git`; otherwise run `git` without catching its errors, so a failure inside a repository raises `ChittyError`. In `git_common_dir`, replace `if result.returncode: return None` with raising `ChittyError` containing the command and standard error. Its callers then surface the real error: `run_lock` and `landing_lock` (`src/chitty/locks.py`) instead of their own "is not in a Git repository", and `register_project` (`src/chitty/config.py`) instead of an ownership refusal; both are intended. `git.historical_files` already has this guard. `git.is_repository` already returns `False` when `git` is missing and no `.git` exists, and raises when `git` is missing and a `.git` marker exists (`TASK-405`); that error stays. Out of scope: the `git` calls in `src/chitty/run.py`, since `chitty run` needs Git for its worktrees; and `register_project` given a recorded owner path that no longer exists.

Tests go in a new `tests/test_no_git_installed.py`, classes inheriting `RepoTestCase`, whose root is not a Git repository. Make `git` missing with `CliRunner().invoke(..., env={"PATH": <empty directory>})` or `unittest.mock.patch.dict(os.environ, ...)`, which patch the environment, not our code. Call `config.git_common_dir.cache_clear()` between runs, or its cache hides the crash.

## Acceptance Criteria

- [ ] Equivalence test: in a root outside Git with `autocommit = false`, holding one ticket made beforehand with `chitty add` (status `todo`), each of `chitty list`, `chitty show <ID>`, `chitty path <ID>`, `chitty next`, `chitty edit <ID> -s planning`, `chitty note <ID> x`, `chitty check`, `chitty move <ID> human` and `chitty archive <ID>` (in the `archive` case, the ticket is first moved with `chitty move <ID> human` and archived by the ID `move` printed) runs once with `git` on `PATH` and once, in a fresh copy of the same root, with `PATH` set to an empty directory. Both runs exit 0 and give the same standard output after replacing the root path, and the same relative file paths and contents afterwards after replacing History timestamps (`YYYY-MM-DDTHH:MM:SSZ`) with a fixed string. Each command is a `subTest`; the test first asserts `git.is_repository(root)` is `False`. The test as a whole fails on `main` (`chitty check` alone already passes there).
- [ ] Tests inside a real repository with `git` on `PATH`, where `.git/index` is overwritten with `garbage` after `git init` (so `git rev-parse --is-inside-work-tree` prints `true` but `git status` exits 128 with `index file smaller than expected`): `git.dirty_paths` raises `ChittyError` whose message contains `index file smaller than expected`. Fails on `main`, which returns an empty set. Also, in a root outside Git with `PATH` set to an empty directory: `git.dirty_paths` returns `set()`, and `git.current_branch` and `config.git_common_dir` return `None` (each fails on `main` with `FileNotFoundError`).
- [ ] `make check` passes.

## Plan

Extend the outside-Git command equivalence test to include archive and compare post-command filesystem snapshots, normalizing History timestamps and replacing the root path. Use move output to identify the archived ticket, clear git_common_dir cache between executions, then format, verify the focused regression and full checks, and commit the coverage.

## Notes

Regression tests were run before the fix: both helper cases failed as expected (missing Git raised FileNotFoundError outside a repository; corrupt Git index was hidden as an empty dirty-path set). The new command-equivalence coverage exercises list, show, path, next, edit, note, check and move outside Git; it does not yet cover archive or compare resulting filesystem snapshots, so acceptance criterion 1 is only partially covered. make check passes.

Review failed (tests): Complete the specified equivalence regression; this is the first review and the missing coverage was already identified in the worker notes.
1: fail - `tests/test_no_git_installed.py::test_commands_match_with_and_without_git` omits archive, does not compare relative file paths or contents with normalized History timestamps, and does not clear `git_common_dir` cache between runs. Add these assertions and exercise archive using the ID printed by move.
2: pass - `make check` ran all 686 tests successfully, including both helper tests. Running the new tests against source extracted from main produced `ChittyError not raised` for the corrupt index and `FileNotFoundError` outside Git; separate calls against main printed `FileNotFoundError` for each of dirty_paths, current_branch and git_common_dir.
3: pass - `make check` exited 0; ruff, pyright and all 686 tests passed.

Completed acceptance criterion 1 follow-up: the equivalence test now archives by the HUMAN ID printed by move and compares relative file paths and contents with History timestamps normalized. Focused tests pass. `make check` passes (ruff, pyright, 686 unittest cases; Node checks run by target). Commit: 6d0a4691.

## Summary

Completed outside-Git command equivalence coverage, including archive via the moved HUMAN ID and normalized filesystem snapshots. Verification: focused unittest passes; make check passes (ruff, pyright, 686 unittest cases, and remaining configured checks). No follow-ups.

## History

- 2026-11-19T09:13:54Z lively-quartz-crane → planning
- 2026-11-19T09:14:25Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T09:14:33Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:18:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T09:18:08Z lively-quartz-crane cold-read → planning
- 2026-11-19T09:18:12Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:21:21Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T09:21:21Z lively-quartz-crane cold-read → todo
- 2026-11-19T09:21:56Z tidy-pearl-otter todo → doing
- 2026-11-19T09:22:57Z tidy-pearl-otter: wrote the plan
- 2026-11-19T09:26:33Z tidy-pearl-otter: changed notes, summary
- 2026-11-19T09:26:33Z tidy-pearl-otter doing → review
- 2026-11-19T09:29:56Z quick-hazel-newt: changed acceptance criteria, notes
- 2026-11-19T09:29:56Z quick-hazel-newt review → doing
- 2026-11-19T09:32:31Z jolly-yellow-quail: wrote the plan
- 2026-11-19T09:34:40Z jolly-yellow-quail: changed notes, summary
- 2026-11-19T09:34:40Z jolly-yellow-quail doing → review
