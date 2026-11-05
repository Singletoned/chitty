---
title: Stop `chitty run` from a ticket worktree changing `main`'s setup
status: backlog
priority: high
created: 2026-11-05
---

## Description

On 2026-11-05 the `TASK-142` worker ran `chitty run` in its worktree, using its branch's code at 0.1.28. `run` in `src/chitty/run.py` opens the main checkout and calls `main_repo.refresh_setup()`, so it committed `chitty_version = "0.1.28"` to `main` as `4eb8087`. `main`'s code was 0.1.27, so every install then warned, and `check_setup_version` should have refused writes and `chitty run` on `main`, until the commit was reverted in `55d6968`. The same refresh can install the branch's Pi extension into `~/.pi`. Any branch that bumps `__version__` can do this again.

In `run`, before anything is written, including the inbox pull and the claim: when `repo.root` is not the main checkout and `main_repo.config.chitty_version` differs from `CHITTY_VERSION`, raise a `ChittyError` naming both versions and saying to run `chitty run` from the main checkout. Running from another worktree with matching versions stays allowed, as `test_run_from_another_worktree_uses_the_branch_not_main` expects, and so does upgrading from the main checkout.

Out of scope: stopping a worker starting a nested `chitty run` at all, and running a branch's `chitty` binary with the main checkout as its working directory.

## Acceptance Criteria

- [ ] A test running `chitty run` from a linked worktree, with `main` recording a different version, shows it failing with that message, `main`'s `HEAD` and `chitty.toml` unchanged, and the fake agent not started
- [ ] `README.md` or `PLAN.md`, wherever `chitty run` from another worktree is described, says so

## History

- 2026-11-05T09:37:43Z mellow-newt → backlog
