---
title: Let a repository declare files ticket branches must not change
status: doing
created: 2026-11-16
---

## Description

`_prepare_review` in `src/chitty/run.py` already fails a review when the branch changes the Chitty config (`_changed_config`) or the managed `AGENTS.md` block (`_changed_agents_block`), and `_land` refuses the same. This repository also forbids branches changing `__version__` in `src/chitty/__init__.py`, and only prose in `AGENTS.md` enforces it. Let a repository list further protected files in its Chitty config, checked the same way.

Decisions:

- Whole files, not line patterns: `src/chitty/__init__.py` holds only a docstring and `__version__`, and no other need is known.
- New optional setting in `RepoConfig` in `src/chitty/config.py`: `protected_paths: list[str] = []`, repository-relative POSIX file paths, compared exactly. A validator rejects an entry that is empty or only whitespace, starts or ends with `/`, contains a backslash, or has an empty, `.` or `..` part when split on `/` (so `a//b` and `./x` are rejected, `a..b` is accepted). Its message includes the entry as `repr(entry)`, because the config error built from pydantic's `loc` has no list index. A path need not exist on `main`: adding it on a branch counts as a change. A directory entry is accepted but matches no file, since matching is exact.
- Add `git.changed_files(root: Path, base: str, paths: Sequence[str]) -> list[str]` in `src/chitty/git.py`: `git --literal-pathspecs diff -z --no-renames --name-only <base>...HEAD -- <paths>` run in `root`, split on NUL with the empty last item dropped, keeping only names equal to an entry (a pathspec also matches files under a directory of that name), in git's order. `--literal-pathspecs` stops `*`, `?`, `[` and a leading `:` acting as globs or magic. With no paths it returns `[]` without running git (an empty pathspec would mean every file). `--no-renames` makes renaming a listed file report it as deleted. The three-dot diff means a listed file changed on `main` and merged into the branch is not a branch change.
- In `_prepare_review`, after the `_changed_agents_block` check, when `changed_files(worktree, main_branch, config.protected_paths)` is not empty, `_fail_review` with `Review failed (work): the branch changes protected files: <paths>, each in backticks and comma-separated. Restore them from <main>.` Read `work_repo.config.protected_paths`: `work_repo` carries the main checkout's config, and the branch cannot change it, since `_changed_config` runs first.
- In `_land`, after the second `_changed_config` check (after the merge), raise `ChittyError` `cannot land <ID>; the branch changes protected files: <paths>`, listed the same way.
- Document the setting in `docs/plan/config.md`, in the commented TOML example, with one line saying it lists files only `main` may change.
- Leave `chitty.toml` and `AGENTS.md` alone on the branch. After this lands, the main checkout adds `protected_paths = ["src/chitty/__init__.py"]` to `chitty.toml` and replaces the `__version__` sentence in `AGENTS.md` with nothing (keeping the `make release` sentence).

First add the `protected_paths` field to `RepoConfig` with no other use, so the new tests fail on their assertions, not on the config rejecting an unknown key.

Tests: real-repository tests in a new `tests/test_protected_paths.py`, inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` and following `test_managed_block_change_fails_without_starting_review` there. Each writes `protected_paths` into `chitty.toml` and commits it on `main` before branching. Review cases, one subtest each: the branch adds, changes, deletes or renames a listed file (fails); changes only unlisted files, including `__init__.py.bak` beside a listed `__init__.py` and `ab.py` beside a listed `a*b.py` (reaches the reviewer); `main` changes a listed file after branching and the branch merges `main` without touching it (reaches the reviewer and lands); no `protected_paths` (reaches the reviewer). The landing test calls `_land` in the same file, as `tests/test_landing.py` does. Validator tests go in `tests/test_config.py`, following its `assertRaisesRegex(ChittyError, ...)` tests. No property tests: the behaviour is a literal `git diff` pathspec and a validator with a fixed rule list, each case tested.

Out of scope: globs or line patterns, protecting paths outside review and landing, and changing how the config and `AGENTS.md` checks work.

## Acceptance Criteria

- [ ] A review of a branch that adds, changes, deletes or renames a file listed in `protected_paths` ends in `doing` with the specified note and starts no reviewer, while the other cases in Tests reach the reviewer; the tests fail before the change on those assertions, not on a config error
- [ ] `_land` refuses a merged branch that changes a listed file with the specified `ChittyError` and leaves `main` unmoved, tested in `tests/test_protected_paths.py`; the test fails before the change
- [ ] Loading a config whose `protected_paths` has an entry the validator rejects fails with a message containing that entry, while `a..b` loads; `docs/plan/config.md` documents the setting; `make check` passes

## Plan

Add protected_paths to RepoConfig first, then regression tests and validation for exact protected-file matching; implement git.changed_files with literal pathspecs and exact filtering; enforce the rule during review and landing; document the setting. Run regression tests against the pre-enforcement behavior, then make check, format if needed, and commit implementation in logical commits with Task: TASK-345 trailers.

## Notes

Cold read by a Haiku subagent, 2026-11-17. Fixed: git pathspecs are globs and match directory prefixes (now `--literal-pathspecs` plus exact filtering); tests would have failed on `extra="forbid"` rather than behaviour; test locations; missing cases (add, delete, rename, prefix-alike names, `main` changing a listed file); the validator message lacking the entry; the trailing NUL; the wrong `TASK-179` claim (dropped). Not adopted: case-only differences on case-insensitive filesystems, out of scope.

## History

- 2026-11-16T09:59:55Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:37Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:31Z intrepid-coral-raven: changed title, description
- 2026-11-17T19:54:38Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T19:55:19Z kind-umber-toad: changed owner
- 2026-11-17T19:55:19Z kind-umber-toad planning → cold-read
- 2026-11-17T19:57:35Z kind-umber-toad: changed description, acceptance criteria, notes
- 2026-11-17T19:57:35Z kind-umber-toad cold-read → planning
- 2026-11-17T22:01:54Z kind-umber-toad: changed owner
- 2026-11-17T22:01:54Z kind-umber-toad planning → todo
- 2026-11-17T22:13:17Z jolly-russet-stoat todo → doing
- 2026-11-17T22:13:31Z jolly-russet-stoat: wrote the plan
