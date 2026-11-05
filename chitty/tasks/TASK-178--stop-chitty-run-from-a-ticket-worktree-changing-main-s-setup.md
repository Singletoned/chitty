---
title: Stop `chitty run` from a ticket worktree changing `main`'s setup
status: doing
priority: high
created: 2026-11-05
---

## Description

On 2026-11-05 the `TASK-142` worker ran `chitty run` in its worktree, using its branch's code at 0.1.28. `run` in `src/chitty/run.py` opens the main checkout and calls `main_repo.refresh_setup()`, so it committed `chitty_version = "0.1.28"` to `main` as `4eb8087`. `main`'s code was 0.1.27, so every install then warned, and `check_setup_version` should have refused writes and `chitty run` on `main`, until the commit was reverted in `55d6968`. The same refresh can install the branch's Pi extension into `~/.pi`. Any branch that bumps `__version__` can do this again.

In `run`, immediately after `main_repo = Repo.open(main_root)` and before `_preflight`, so before anything is written: when `git.is_linked_worktree(repo.root)` and `main_repo.config.chitty_version` is older than `CHITTY_VERSION` or unrecorded, raise a `ChittyError` naming both versions, with `unrecorded` for a missing one, and saying to run `chitty run` from the main checkout. Compare with `_version_key`, not as strings. When `main` records a newer version, leave `check_setup_version`'s existing error to report it.

This also refuses a person who upgrades their global `chitty` and then starts `chitty run` from a worktree. That is deliberate: the check cannot tell a branch's code from an upgrade, and running from the main checkout does the upgrade. `test_run_refresh_is_silent_when_current_or_in_a_worktree` and `test_run_from_another_worktree_uses_the_branch_not_main` use the current version, so neither should need changing. Running from another worktree with matching versions stays allowed, as `test_run_from_another_worktree_uses_the_branch_not_main` expects, and so does upgrading from the main checkout.

Out of scope: stopping a worker starting a nested `chitty run` at all, and running a branch's `chitty` binary with the main checkout as its working directory.

## Acceptance Criteria

- [x] A test running `chitty run` from a linked worktree, with `main`'s `chitty.toml` recording an older version such as `0.0.1`, shows it failing with a message containing both versions and `from the main checkout`, `main`'s `HEAD` and `chitty.toml` unchanged, and the fake agent not started
- [x] `README.md`'s setup paragraph and the `PLAN.md` passage on `chitty run` setup, which both say linked worktrees leave setup alone, say that `chitty run` from a linked worktree refuses in this case

## Plan

Add a linked-worktree guard in run.py immediately after opening the main repository, comparing setup versions with _version_key and rejecting only missing/older main setup before preflight. Add focused integration coverage for the older-version refusal and verify no agent start or main checkout changes. Update the README and PLAN setup descriptions, then run the targeted tests and full make check.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: a test recording a newer version would have passed with nothing built, because `check_setup_version` already refuses that, so the criterion now says older; where the check goes; a missing version; a newer version keeping its existing error; saying that refusing after a global upgrade is deliberate; and naming the docs, which are already misleading because the refresh runs on `main_repo`.

## History

- 2026-11-05T09:37:43Z mellow-newt → backlog
- 2026-11-05T09:39:56Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T09:39:57Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T09:39:58Z mellow-newt backlog → todo
- 2026-11-05T10:03:55Z human todo → doing
- 2026-11-05T10:28:28Z honest-crane: wrote the plan
- 2026-11-05T10:36:23Z honest-crane: ticked acceptance criteria
