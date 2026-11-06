---
title: Let `main`'s `chitty` write on a branch that records a newer version
status: backlog
priority: high
created: 2026-11-06
---

## Description

A ticket branch that changes the managed guide block bumps `__version__` and `chitty_version` above `main`'s, as `AGENTS.md` requires. Until it lands, `main`'s `chitty` refuses every write in that branch's worktree with `repository needs Chitty <newer> or later`. This comes from `check_setup_version`, which `Repo._prepare_write` in `src/chitty/store.py` calls first.

`chitty run` runs `main`'s code and writes in the worktree: the `todo → doing` claim, and `_fail_review`. So a branch at `0.1.35` stops the `0.1.34` review loop as soon as its rebase conflicts. Seen on 2026-11-06 with `TASK-173`. `TASK-179` is in the same state.

`TASK-204` already stops `_prepare_write` upgrading setup in a linked worktree, but it kept this check. Move the `git.is_linked_worktree(self.root)` early return above `self._check_setup_version()`, so a linked worktree skips the version check entirely. The branch is reconciled when it is rebased onto `main`.

Leave unchanged:
- The check in the main checkout.
- The check in `init_repo`.
- `_refuse_stale_linked_worktree` in `src/chitty/run.py`, which compares the main checkout's setup.

Update the `chitty init` bullet in `PLAN.md` that `TASK-204` extended: it says a linked worktree still refuses a setup newer than Chitty, which is no longer true.

Out of scope: running each branch's own `chitty` for these writes.

## Acceptance Criteria

- [ ] A test makes a linked worktree whose `chitty.toml` records a newer `chitty_version` than `CHITTY_VERSION`, and runs a ticket write there. The write succeeds and leaves `chitty.toml` unchanged. It fails before the fix with `repository needs Chitty`.
- [ ] The same write in the main checkout still fails with `repository needs Chitty`, and `PLAN.md`'s `chitty init` bullet describes both rules.

## History

- 2026-11-06T16:15:42Z youthful-toad → backlog
