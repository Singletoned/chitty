---
title: Don't upgrade repository setup on a ticket branch
status: done
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

- [x] A test makes a linked worktree whose `chitty.toml` records an older `chitty_version`, runs a ticket write there, and asserts that `chitty.toml` and `AGENTS.md` are unchanged and no commit says `chitty: upgrade repository setup`. It fails before the fix.
- [x] With `autocommit = false` in that linked worktree, the same write succeeds instead of raising `repository setup is stale`.
- [x] Existing upgrade tests in the main checkout still pass, `test_worktree_keeps_the_main_checkout_registered` no longer expects the machine-wide skip message, and the `chitty init` bullet in `PLAN.md` says upgrades happen only in the main checkout.

## Plan

In `Repo._prepare_write`, after `_check_setup_version()`, return early when `git.is_linked_worktree(self.root)`, so a ticket branch is never upgraded and never gets the stale-setup error. Tests in `tests/test_autocommit.py`: a linked worktree with an older recorded version takes a write without changing `chitty.toml` or `AGENTS.md` and without an upgrade commit, with `autocommit` both on and off. Drop the skip-message assertion from `test_worktree_keeps_the_main_checkout_registered`. Extend the `chitty init` bullet in `PLAN.md`.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-204/1`; both tests failed before and passed after; `make check` OK, 308 tests). Outcomes:
- The existing `test_worktree_keeps_the_main_checkout_registered` breaks under the fix: fixed, the ticket and criterion 3 now name it.
- The "setup-upgrade section" of `PLAN.md` didn't exist: fixed, the ticket now names the `chitty init` bullet.
- A recorded version newer than the running Chitty is untested in a worktree: fixed, the ticket says it must still error. Testing it is optional, since `_check_setup_version` is unchanged.
- `__version__` not bumped: agreed, the ticket now says no bump.
- A non-Git directory is untested: rejected, `is_linked_worktree` is false there and the existing main-checkout path applies.
- The `refresh_setup` path is untested: rejected, it's out of scope and unchanged.

Second case, on `task-144` (fixed by hand): `main`'s `chitty` upgraded the branch's setup (`4d3e1bb`), and because it didn't know the branch's new `<!-- chitty:end -->` marker, it dropped it from `AGENTS.md`. So the bug corrupts newer branch files as well as writing config older branch code can't read.

Reserved for a human-run session so the loops leave it alone.

Reviewed: rebased cleanly onto main; make check passes. Both new tests fail on main's store.py (stale setup error / upgrade) and pass with the fix.
1: pass - test_linked_worktree_write_does_not_upgrade_setup checks chitty.toml and AGENTS.md unchanged and no upgrade commit; fails without the fix.
2: pass - the autocommit=false test succeeds with the fix, raises 'repository setup is stale' without it.
3: pass - upgrade tests in main checkout pass in make check; the skip-message assertion is removed from test_worktree_keeps_the_main_checkout_registered; PLAN.md init bullet says upgrades happen only in the main checkout.

## Summary

`Repo._prepare_write` returns early in a linked worktree after `_check_setup_version()`. A ticket branch is never upgraded and never gets the stale-setup error, but a recorded version newer than the running Chitty still fails. Tests in `tests/test_autocommit.py` cover autocommit on and off and failed before the fix. `test_worktree_keeps_the_main_checkout_registered` no longer expects the machine-wide skip message. The `chitty init` bullet in `PLAN.md` now says upgrades happen only in the main checkout. `make check` OK (311 tests). Built from cold read `refs/cold-read/TASK-204/1`, taking only this ticket's hunks, because `main` had moved.

## History

- 2026-11-06T11:30:46Z youthful-toad → backlog
- 2026-11-06T11:41:32Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T11:41:32Z youthful-toad backlog → todo
- 2026-11-06T12:54:24Z youthful-toad: changed notes
- 2026-11-06T13:38:00Z youthful-toad: changed owner, notes
- 2026-11-06T13:38:03Z youthful-toad: wrote the plan
- 2026-11-06T13:38:03Z youthful-toad todo → doing
- 2026-11-06T13:43:25Z youthful-toad: changed owner, summary; ticked acceptance criteria
- 2026-11-06T13:43:25Z youthful-toad doing → review
- 2026-11-06T14:05:17Z youthful-toad: changed notes; overrode review independence
- 2026-11-06T14:05:17Z youthful-toad review → done
