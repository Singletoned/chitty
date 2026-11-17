---
title: Resolve dependencies the same way show does, across branches
status: doing
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` had to be edited on its branch, which was 241 commits behind `main` and did not contain `TASK-326`. `chitty edit TASK-318 --depends-on TASK-326` passed the pre-write check in `_save` (`Repo.check_dependencies` uses `Repo.find`, which reads every branch, like `chitty show`), then failed the post-write check with `depends_on TASK-326: no such task`.

Cause: `check` in `src/chitty/check.py` reports `depends_on <ID>: no such task` and `parent <ID>: no such task` when the ID is not among the files on disk (`by_id`, built from `scan`). Make both existence checks use the lookup `Repo.find` uses, across every branch. `Repo.find` raises `ChittyError` for three reasons: no task with the ID, a duplicate ID, or an unreadable task file on some branch. Add `Repo.lookup(task_id) -> StoredTask | None` in `src/chitty/store.py`, which returns `None` only when no task has the ID and raises as `find` does otherwise; `find` calls it. `check` reports `no such task` only when `lookup` returns `None`, and lets its other errors propagate, as `chitty show` does. Do not tell the cases apart by matching error text. Keep everything else that uses `by_id` (duplicate IDs, the cycle graphs) as it is; a dependency found only on another branch is not added to the cycle graph.

This also changes `chitty check` and `chitty fix`: on a branch behind `main`, a ticket depending on a ticket that exists only on `main` no longer fails the check. That is intended.

Files: `src/chitty/check.py`, `src/chitty/store.py`; tests in a new `tests/test_check_cross_branch_references.py`, inheriting `CliTestCase` from `tests/test_cli.py`. `CliTestCase` has no git helpers and its config has `autocommit = false`: write `chitty.toml` with `autocommit = true`, run `git init` with a user, and add `git` and `commit` helpers like `TestCrossBranchWrites` in `tests/test_cli.py`.

No property test: the states are a small fixed set, each listed in the criterion and each tested.

## Acceptance Criteria

- [ ] For each field (`depends_on`, `parent`) and each place the referenced ticket lives, as a separate subtest: active in the current checkout; archived with `chitty archive` in the current checkout; created on a branch that is not checked out, with no copy on the current branch; nowhere. Each subtest runs both `chitty show <ID>` and `chitty check` and asserts `check` reports `<field> <ID>: no such task` exactly when `show` exits non-zero. One more subtest commits a malformed task file on another branch: `chitty check` fails with that file's parse error, not `no such task`. The other-branch subtests fail before the change.
- [ ] A real-file test of the reported case: create branch `b` from `main`, add `TASK-2` on `main`, switch back to `b`, then `chitty edit TASK-1 --depends-on TASK-2` exits 0, commits the edit, and leaves `git status --porcelain` empty. Fails before the change. `make check` passes.

## Plan

Add Repo.lookup(task_id) returning StoredTask or None for absence while preserving find error behavior, and make find delegate to it. Update check reference existence diagnostics to use lookup, retaining by_id for duplicate detection and cycle graphs. Add focused real-Git CLI regression tests for both reference fields across active, archived, other-branch, and missing references, malformed historical task files, plus the cross-branch edit/autocommit report. Run the new tests against the current implementation first to confirm the regressions, then implement, run make format && make check, and commit code/tests with a Task: TASK-356 trailer.

## History

- 2026-11-16T10:29:26Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:56Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:56:57Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:57:34Z open-russet-eel: changed owner
- 2026-11-16T16:57:34Z open-russet-eel planning → cold-read
- 2026-11-16T17:03:14Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:03:14Z open-russet-eel cold-read → planning
- 2026-11-16T17:03:16Z open-russet-eel: changed owner
- 2026-11-16T17:03:16Z open-russet-eel planning → todo
- 2026-11-17T18:08:46Z plucky-jade-heron todo → doing
- 2026-11-17T18:09:14Z plucky-jade-heron: wrote the plan
