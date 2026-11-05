---
title: Stop `chitty run` from a ticket worktree changing `main`'s setup
status: backlog
priority: high
created: 2026-11-05
---

## Description

On 2026-11-05 the `TASK-142` worker ran `chitty run` in its worktree, using its branch's code at 0.1.28. `run` in `src/chitty/run.py` opens the main checkout and calls `main_repo.refresh_setup()`, so it committed `chitty_version = "0.1.28"` to `main` as `4eb8087`. `main`'s code was 0.1.27, so every install then warned, and `check_setup_version` should have refused writes and `chitty run` on `main`, until the commit was reverted in `55d6968`. The same refresh can install the branch's Pi extension into `~/.pi`. Any branch that bumps `__version__` can do this again.

In `run`, immediately after `main_repo = Repo.open(main_root)` and before `_preflight`, so before anything is written: when `git.is_linked_worktree(repo.root)` and `main_repo.config.chitty_version` is older than `CHITTY_VERSION` or unrecorded, raise a `ChittyError` naming both versions, with `unrecorded` for a missing one, and saying to run `chitty run` from the main checkout. Compare with `_version_key`, not as strings. When `main` records a newer version, leave `check_setup_version`'s existing error to report it.

This also refuses a person who upgrades their global `chitty` and then starts `chitty run` from a worktree. That is deliberate: the check cannot tell a branch's code from an upgrade, and running from the main checkout does the upgrade. `test_run_refresh_is_silent_when_current_or_in_a_worktree` and `test_run_from_another_worktree_uses_the_branch_not_main` use the current version, so neither should need changing. Running from another worktree with matching versions stays allowed, as `test_run_from_another_worktree_uses_the_branch_not_main` expects, and so does upgrading from the main checkout.

Out of scope: stopping a worker starting a nested `chitty run` at all, and running a branch's `chitty` binary with the main checkout as its working directory.

## Acceptance Criteria

- [ ] A test running `chitty run` from a linked worktree, with `main` recording a different version, shows it failing with that message, `main`'s `HEAD` and `chitty.toml` unchanged, and the fake agent not started

## History

- 2026-11-05T09:37:43Z mellow-newt → backlog
- 2026-11-05T09:39:56Z mellow-newt: changed description, acceptance criteria
