---
title: Refuse writes with `autocommit` on when `git` or the repository is missing
status: doing
depends_on:
  - TASK-410
created: 2026-11-19
---

## Description

With `autocommit = true`, every write commits, so Git is required. Today Chitty only finds out after writing: outside a Git work tree, `chitty add` writes the ticket file and then fails with `` `git ls-files -- ...` failed ``; with `git` missing from `PATH` and no `.git`, it writes the file and then dies with a `FileNotFoundError` traceback. Both leave an uncommitted ticket behind. (With `git` missing and a `.git` present, `git.is_repository` already raises before the write, since `TASK-405`.)

Check before writing, in `Repo._prepare_write` (`src/chitty/store.py`), which every `Repo` write method calls before changing a file, as do `chitty fix` (`src/chitty/check.py`) and `chitty import` (`src/chitty/import_backlog.py`). Put the check immediately after `self._check_setup_version()`, before the `chitty_version` early return, the linked-worktree return and the setup upgrade:

- `autocommit` is `false`: do nothing new. Chitty without Git is supported and behaves like `autocommit = false`.
- `autocommit` is `true` and `shutil.which("git")` is `None`: raise `ChittyError` naming `autocommit`, saying `git` was not found on `PATH`, and to install Git or set `autocommit = false`. This is checked first, so it wins when a `.git` exists.
- `autocommit` is `true` and `git.is_repository(self.root)` is `False`: raise `ChittyError` naming `autocommit`, naming `self.root` as not in a Git work tree, and to run `git init` or set `autocommit = false`.

Reads are unchanged. With `git` missing and no repository, commands other than `add` crash today; `TASK-410`, which this depends on, fixes that. Out of scope: `chitty init --autocommit` (it changes no files when it fails, and has its own ticket) and `chitty run`'s `refresh_setup`, since `chitty run` needs Git for its worktrees.

Tests go in a new `tests/test_autocommit_requires_git.py`, classes inheriting `RepoTestCase`. Make `git` missing with `unittest.mock.patch.dict(os.environ, {"PATH": <empty directory>})` or `CliRunner().invoke(..., env=...)`, which patch the environment, not our code (as `tests/test_git.py` does). Several test files set `autocommit = true` (`git grep -l "autocommit = true" tests`); any that write without `git init` now fail and must create the repository.

No property: the behaviour is a small fixed set of states, every one listed in criterion 1 and tested.

## Acceptance Criteria

- [ ] Grid test in `tests/test_autocommit_requires_git.py`: each of `chitty add`, `chitty edit <ID> -s planning` and `chitty note <ID> x` in every combination of `autocommit` on or off, `git` on `PATH` or not, and `git init` run or not (24 cases), each as a `subTest` building a fresh root in its own temporary directory. The `<ID>` ticket is made first, with `autocommit = false`, `git` on `PATH` and before any `git init`; `git init` then sets repository-local `user.email` and `user.name` as `tests/test_autocommit.py` does. Rows without `git init` first assert `git.is_repository(root)` is `False`, so an enclosing checkout fails loudly. Succeeds: `autocommit` off without `git init`, with or without `git`; off with `git init` and `git`; on with `git init` and `git`, where `git log -1 --format=%s` starts `chitty:` and the commit holds the ticket file. Off with `git init` but no `git`: the existing `TASK-405` error naming `PATH`. On without `git`: a message naming `autocommit` and `PATH`. On with `git` but no `git init`: a message naming `autocommit` and `git init`. Every failing case exits non-zero without a traceback and leaves every file under the root outside `.git` unchanged.
- [ ] Further tests, `autocommit` on, no `git init`, `git` on `PATH`: `chitty move <ID> human` and `chitty fix` (with nothing to fix) refuse with the `git init` message and change no file; `chitty show <ID>` and `chitty list` succeed; with `chitty_version = "0.0.1"` in `chitty.toml`, `chitty add` refuses with the `git init` message and no setup file (`.gitignore`, `AGENTS.md`, `CLAUDE.md`, `chitty.toml`) changes.
- [ ] Evidence, recorded in a note: on `main`, every refusing row of criteria 1 and 2 fails (it exits 0 without refusing, changes files, or shows a traceback).
- [ ] `make check` passes, with any existing test that enabled `autocommit` without a repository fixed to create one.

## History

- 2026-11-19T09:06:20Z lively-quartz-crane → planning
- 2026-11-19T09:06:59Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T09:06:59Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:10:33Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T09:10:33Z lively-quartz-crane cold-read → planning
- 2026-11-19T09:10:53Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:14:28Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-19T09:21:32Z lively-quartz-crane cold-read → todo
- 2026-11-19T11:42:06Z sunny-ochre-raven todo → doing
