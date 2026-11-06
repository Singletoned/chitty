---
title: Don't upgrade repository setup on a ticket branch
status: backlog
priority: high
created: 2026-11-06
---

## Description

When a newer `chitty` writes a ticket in a linked worktree whose `chitty.toml` records an older `chitty_version`, `Repo._prepare_write` in `src/chitty/store.py` runs `init_repo` there and commits "chitty: upgrade repository setup" on the ticket branch. The branch's own code is older and cannot read the result.

Seen on `task-197`: commit `df71b12` bumped its `chitty_version` from `0.1.31` to `0.1.33` and added `[contexts.backlog]` with `random_ids = true`. The worker runs the branch's own `.venv` `chitty` (version `0.1.31`), which then fails on every command with `contexts.backlog.random_ids: Extra inputs are not permitted`. Even without that key it would fail with "repository needs Chitty 0.1.33 or later" (`check_setup_version` in `src/chitty/config.py`). The branch is wedged until `main` is integrated into it.

`Repo.refresh_setup` already skips linked worktrees ("setup belongs on main"). Make `_prepare_write` do the same: in a linked worktree (`git.is_linked_worktree(self.root)`), keep `_check_setup_version()` but skip the upgrade and the "setup is stale" error, and write as normal. The branch picks up the new setup when it is rebased onto `main`.

Out of scope: repairing `task-197` (it needs `main` integrated, which is the worker's job), and the strict-config change (TASK-201).

## Acceptance Criteria

- [ ] A test makes a linked worktree whose `chitty.toml` records an older `chitty_version`, runs a ticket write there, and asserts that `chitty.toml` and `AGENTS.md` are unchanged and no commit says `chitty: upgrade repository setup`. It fails before the fix.
- [ ] With `autocommit = false` in that linked worktree, the same write succeeds instead of raising `repository setup is stale`.
- [ ] Existing tests of the upgrade in the main checkout still pass, and the setup-upgrade section of `PLAN.md` says upgrades happen only in the main checkout.

## History

- 2026-11-06T11:30:46Z youthful-toad → backlog
