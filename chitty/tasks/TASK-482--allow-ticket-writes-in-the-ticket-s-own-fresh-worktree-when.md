---
title: Allow ticket writes in the ticket's own fresh worktree when `main` holds its copy
status: planning
parent: TASK-376
created: 2026-11-21
---

## Description

Split out of `TASK-378` on 2026-11-21, when its worker found the whole read switch too large for one session. After `TASK-378`, a ticket in a fresh ticket worktree (its branch `task-6` made at `main`'s tip, with no commit of its own yet) is read from `main`, because `main`'s copy is authoritative until the branch changes it. `Repo._require_current_version` (`src/chitty/store.py`) refuses a write when `stored.branch` is neither `None` nor the current branch, so the first write in such a worktree, including the runner's claim on the branch (`TASK-384`), would be refused. This ticket adds the allowance first. Under today's reads it only adds a case where a write is allowed, so nothing that works today stops working.

Decision (owner, 2026-11-20): `_require_current_version` also returns without raising when all of these hold: the current branch is the ticket's own branch (`str(stored.id).lower()`, so `task-6` for `TASK-6`); `stored.branch` is the configured main branch; and `git.changed_since_split(self.root, f"refs/heads/{main}", f"refs/heads/{own}", paths)` (`src/chitty/git.py`) is false, where `paths` is the union of the relative paths returned by `self._ref_ticket_files(ref, stored.id)` for those two refs (call `self.ticket_ids()` first so the cache is filled). The write then commits on the branch, which puts the branch ahead of `main`, so every checkout reads the ticket from the branch afterwards. A branch merged into `main` that `main` has changed since is still refused. Every other case is refused as today; `TASK-385` replaces the guard later.

Tests: real Git, in a new `tests/test_own_worktree_writes.py` with a class inheriting `CliTestCase` from `tests/test_cli.py`, set up with `git init -b main` and `autocommit = true` as `tests/test_check_cross_branch_references.py` does. The linked worktree is made with `git worktree add -b task-6 <dir> main` after `TASK-6` is committed on `main`; the CLI runs with that directory as the working directory. The direct tests open `Repo.open(<worktree>)` and build the `StoredTask` with `branch="main"` and the ticket's real path and parsed task. No property: a fixed set of branch relations, each in the criteria.

## Acceptance Criteria

- [ ] In the linked worktree of a fresh `task-6` made at `main`'s tip, `chitty edit TASK-6 --note x` succeeds and commits on `task-6`; after `task-6` is fast-forward merged into `main` and a further `main` commit changes `TASK-6`, the same edit in that worktree exits 1 with the `_require_current_version` message naming `main` and makes no commit (guards that pass before the change too, under today's reads)
- [ ] Direct tests of `Repo._require_current_version` with a `StoredTask` whose `branch` is `main`, from a checkout on branch `task-6`: it returns when `task-6` has not changed `TASK-6`'s files since it split from `main` and `main` has not either; it raises when `main` changed them since the split; it raises from a checkout on branch `feature` (each against a real Git repository; the first fails before the change)
- [ ] `make check` passes

## History

- 2026-11-21T01:20:56Z quick-pearl-lapwing → planning
