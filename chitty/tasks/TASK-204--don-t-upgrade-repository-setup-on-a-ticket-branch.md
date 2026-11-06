---
title: Don't upgrade repository setup on a ticket branch
status: todo
priority: high
created: 2026-11-06
---

## Description

When a newer `chitty` writes a ticket in a linked worktree whose `chitty.toml` records an older `chitty_version`, `Repo._prepare_write` in `src/chitty/store.py` runs `init_repo` there and commits "chitty: upgrade repository setup" on the ticket branch. The branch's own code is older and can't read the result.

Seen on `task-197`: commit `df71b12` bumped its `chitty_version` from `0.1.31` to `0.1.33` and added `[contexts.backlog]` with `random_ids = true`. The worker runs the branch's own `.venv` `chitty` (version `0.1.31`), which now fails on every command with `contexts.backlog.random_ids: Extra inputs are not permitted`. Without that key it would still fail, with "repository needs Chitty 0.1.33 or later" (`check_setup_version` in `src/chitty/config.py`). The branch stays stuck until `main` is integrated into it.

`Repo.refresh_setup` already skips linked worktrees ("setup belongs on main"). Make `_prepare_write` do the same. In a linked worktree (`git.is_linked_worktree(self.root)`), keep calling `_check_setup_version()`, so a recorded version newer than the running Chitty still errors. Skip the upgrade and the "setup is stale" error, and write as normal. The branch picks up the new setup when it is rebased onto `main`.

Also update `test_worktree_keeps_the_main_checkout_registered` in `tests/test_cli.py`. It asserts "skipping machine-wide Pi setup" after a write from a stale worktree. That message came from the upgrade this change removes, so drop the assertion.

In `PLAN.md`, extend the `chitty init` bullet near line 53 (the one that ends "tells the caller to run `chitty init`"). Don't add a new section.

There's no `__version__` bump, because nothing `chitty init` writes changes.

Out of scope:
- Repairing `task-197`. It needs `main` integrated, which is the worker's job.
- The strict-config change (`TASK-201`).

## Acceptance Criteria

- [ ] A test makes a linked worktree whose `chitty.toml` records an older `chitty_version`, runs a ticket write there, and asserts that `chitty.toml` and `AGENTS.md` are unchanged and no commit says `chitty: upgrade repository setup`. It fails before the fix.
- [ ] With `autocommit = false` in that linked worktree, the same write succeeds instead of raising `repository setup is stale`.
- [ ] Existing upgrade tests in the main checkout still pass, `test_worktree_keeps_the_main_checkout_registered` no longer expects the machine-wide skip message, and the `chitty init` bullet in `PLAN.md` says upgrades happen only in the main checkout.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-204/1`; both tests failed before and passed after; `make check` OK, 308 tests). Outcomes:
- The existing `test_worktree_keeps_the_main_checkout_registered` breaks under the fix: fixed, the ticket and criterion 3 now name it.
- The "setup-upgrade section" of `PLAN.md` didn't exist: fixed, the ticket now names the `chitty init` bullet.
- A recorded version newer than the running Chitty is untested in a worktree: fixed, the ticket says it must still error. Testing it is optional, since `_check_setup_version` is unchanged.
- `__version__` not bumped: agreed, the ticket now says no bump.
- A non-Git directory is untested: rejected, `is_linked_worktree` is false there and the existing main-checkout path applies.
- The `refresh_setup` path is untested: rejected, it's out of scope and unchanged.

## History

- 2026-11-06T11:30:46Z youthful-toad → backlog
- 2026-11-06T11:41:32Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T11:41:32Z youthful-toad backlog → todo
