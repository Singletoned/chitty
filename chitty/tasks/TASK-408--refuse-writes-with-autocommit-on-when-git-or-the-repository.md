---
title: Refuse writes with `autocommit` on when `git` or the repository is missing
status: planning
created: 2026-11-19
---

## Description

With `autocommit = true`, every write commits, so Git is required. Today Chitty only finds out after writing: outside a Git work tree, `chitty add` writes the ticket file and then fails with `` `git ls-files -- ...` failed ``; with `git` missing from `PATH` and no `.git`, it writes the file and then dies with a `FileNotFoundError` traceback. Both leave an uncommitted ticket behind. (With `git` missing and a `.git` present, `git.is_repository` already raises before the write, since `TASK-405`.)

Check before writing. In `Repo._prepare_write` (`src/chitty/store.py:413`), which every write calls before changing anything, first, before the `chitty_version` early return and the linked-worktree return:

- `autocommit` is `false`: do nothing new. Chitty without Git is supported and behaves like `autocommit = false`.
- `autocommit` is `true` and `shutil.which("git")` is `None`: raise `ChittyError` saying `autocommit` is on, `git` was not found on `PATH`, and to install Git or set `autocommit = false`.
- `autocommit` is `true` and `git.is_repository(self.root)` is `False`: raise `ChittyError` saying `autocommit` is on, naming `self.root` as not in a Git work tree, and to run `git init` or set `autocommit = false`.

Reads are unchanged. Tests go in a new `tests/test_autocommit_requires_git.py`, classes inheriting `RepoTestCase`; make `git` missing with `unittest.mock.patch.dict(os.environ, {"PATH": <empty directory>})`, which patches the environment, not our code. `RepoTestCase` repositories are not Git repositories until a test runs `git init`.

Several test files set `autocommit = true` (`git grep -l "autocommit = true" tests`); any that write without running `git init` first now fail and must create the repository.

No property: the behaviour is a small fixed set of states, every one listed in criterion 1 and tested.

## Acceptance Criteria

- [ ] A test in `tests/test_autocommit_requires_git.py` runs each of `chitty add`, `chitty edit <ID> -s planning` and `chitty note <ID> x` (the ticket made beforehand with `autocommit = false`) in every combination of `autocommit` on or off, `git` on `PATH` or not, and `git init` run or not, as a `subTest` each (24 cases). With `autocommit` off, each succeeds. With it on and `git init` run with `git` on `PATH`, each succeeds and commits. Otherwise each exits non-zero with a `ChittyError` message, no traceback, naming `autocommit` and either `PATH` or `git init`, and every file under the root has the same content as before.
- [ ] On `main` this test fails: the not-a-repository and missing-`git` cases with `autocommit` on change the files (or show a `FileNotFoundError` traceback). Record that run in a note.
- [ ] `make check` passes, with any existing test that enabled `autocommit` without a repository fixed to create one.

## History

- 2026-11-19T09:06:20Z lively-quartz-crane → planning
