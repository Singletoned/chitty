---
title: Resolve dependencies the same way show does, across branches
status: cold-read
owner: open-russet-eel
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` had to be edited on its branch, which was 241 commits behind `main` and did not contain `TASK-326`. `chitty edit TASK-318 --depends-on TASK-326` passed the pre-write check in `_save` (`Repo.check_dependencies` uses `Repo.find`, which reads every branch, like `chitty show`), then failed the post-write check with `depends_on TASK-326: no such task`.

Cause: `check` in `src/chitty/check.py` reports `depends_on <ID>: no such task` and `parent <ID>: no such task` when the ID is not among the files on disk (`by_id`, built from `scan`). Make both existence checks agree with `Repo.find`: report `no such task` only when `Repo.find` raises for that ID. Keep everything else that uses `by_id` (duplicate IDs, the cycle graphs) as it is; a dependency found only on another branch is not added to the cycle graph.

This also changes `chitty check` and `chitty fix`: on a branch behind `main`, a ticket depending on a ticket that exists only on `main` no longer fails the check. That is intended.

Files: `src/chitty/check.py`; tests in a new `tests/test_check_cross_branch_references.py`, real git repositories in temp dirs, inheriting `CliTestCase` from `tests/test_cli.py`.

No property test: the states are a small fixed set, each listed in the criterion and each tested.

## Acceptance Criteria

- [ ] For each field (`depends_on`, `parent`) and each place the referenced ticket lives, as a separate subtest: in the current checkout; archived in the current checkout; only on another local branch; nowhere. `chitty check` reports `<field> <ID>: no such task` exactly when `chitty show <ID>` exits non-zero, which is only the nowhere case. The only-on-another-branch case fails before the change.
- [ ] A real-file test of the reported case: on a branch created before `TASK-2` was added on `main`, `chitty edit TASK-1 --depends-on TASK-2` exits 0, commits the edit, and leaves `git status --porcelain` empty. Fails before the change. `make check` passes.

## History

- 2026-11-16T10:29:26Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:56Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:56:57Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:57:34Z open-russet-eel: changed owner
- 2026-11-16T16:57:34Z open-russet-eel planning → cold-read
