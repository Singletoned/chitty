---
title: Let a repository declare files ticket branches must not change
status: cold-read
owner: planner-cold-read
created: 2026-11-16
---

## Description

`_prepare_review` in `src/chitty/run.py` already fails a review when the branch changes the Chitty config (`_changed_config`) or the managed `AGENTS.md` block (`_changed_agents_block`), and `_land` refuses the same. This repository also forbids branches changing `__version__` in `src/chitty/__init__.py`, which caused the 56-failure loop on `TASK-179`, and only prose in `AGENTS.md` enforces it. Let a repository list further protected files in its Chitty config, checked the same way.

Decisions:

- Whole files, not line patterns: `src/chitty/__init__.py` holds only a docstring and `__version__`, and no other need is known.
- New optional setting in `RepoConfig` in `src/chitty/config.py`: `protected_paths: list[str] = []`, repository-relative POSIX paths, compared exactly (no globs). A validator rejects an empty string, a path starting with `/`, and a path with a `..` part, with an error naming the bad entry. A path need not exist on `main`: adding it on a branch counts as a change.
- Add `git.changed_files(root: Path, base: str, paths: Sequence[str]) -> list[str]` in `src/chitty/git.py`: `git diff -z --no-renames --name-only <base>...HEAD -- <paths>` run in `root`, split on NUL, in git's order. With no paths it returns `[]` without running git (an empty pathspec would mean every file).
- In `_prepare_review`, after the `_changed_agents_block` check, when `changed_files(worktree, main_branch, config.protected_paths)` is not empty, `_fail_review` with `Review failed (work): the branch changes protected files: <paths>, each in backticks and comma-separated. Restore them from <main>.` Use the main checkout's config (the branch cannot change it, since `_changed_config` runs first).
- In `_land`, after the second `_changed_config` check (after the merge), raise `ChittyError` `cannot land <ID>; the branch changes protected files: <paths>`, listed the same way.
- Document the setting in `docs/plan/config.md`, in the commented TOML example, with one line saying it lists files only `main` may change.
- Leave `chitty.toml` and `AGENTS.md` alone on the branch. After this lands, the main checkout adds `protected_paths = ["src/chitty/__init__.py"]` to `chitty.toml` and replaces the `__version__` sentence in `AGENTS.md` with nothing (keeping the `make release` sentence).

Tests: real-repository tests in a new `tests/test_protected_paths.py`, inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` and following `test_managed_block_change_fails_without_starting_review` there. Each writes `protected_paths` into `chitty.toml` and commits it on `main` before branching. No property tests: the behaviour is a `git diff` pathspec and a config validator, and the outcomes are the fixed set in the criteria.

Out of scope: globs or line patterns, protecting paths outside review and landing, and changing how the config and `AGENTS.md` checks work.

## Acceptance Criteria

- [ ] A review of a branch that adds, changes or deletes a file listed in `protected_paths` ends in `doing` with the specified note and starts no reviewer, while a branch changing only unlisted files, or any branch when `protected_paths` is absent, reaches the reviewer; the tests fail before the change
- [ ] `_land` refuses a merged branch that changes a listed file with the specified `ChittyError` and leaves `main` unmoved, tested as `tests/test_landing.py` calls `_land`; the test fails before the change
- [ ] Loading a config whose `protected_paths` has an empty, absolute or `..` entry fails naming the entry; `docs/plan/config.md` documents the setting; `make check` passes

## History

- 2026-11-16T09:59:55Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:37Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:31Z intrepid-coral-raven: changed title, description
- 2026-11-17T19:54:38Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T19:55:19Z kind-umber-toad: changed owner
- 2026-11-17T19:55:19Z kind-umber-toad planning → cold-read
