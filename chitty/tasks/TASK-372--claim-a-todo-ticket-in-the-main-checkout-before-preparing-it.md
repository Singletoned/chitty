---
title: Claim a `todo` ticket in the main checkout before preparing its worktree
status: planning
labels:
  - bug
priority: high
created: 2026-11-18
---

## Description

Today `_run_ticket` in `src/chitty/run.py` claims a `todo` ticket (`work_repo.edit(action.id, claim_edit())`) in the worktree after `setup` and `check`. When `main` holds a newer copy of the ticket, that write fails with `<ID>'s latest committed version is on branch main` (`Repo._require_current_version`, `src/chitty/store.py`): seen on `TASK-343`, 2026-11-17, after an error repair wrote `error → todo` on `main`. The runner is to rebase the branch onto `main` before setup (`TASK-370`), and nothing can commit to the ticket during a stopped rebase, so the claim must happen first.

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

Decisions:

- In work mode, claim a `todo` ticket in the main checkout, before `_worktree`: `main_repo.edit(action.id, Edit(status="doing", skip_verdicts=True, skip_current_version=True))`, the way the runner's other handoffs write. Remove the worktree claim. `doing` and `error` tickets are not claimed, as today.
- A new branch made by `_worktree` from `main` then starts with the claim. An existing branch gets it when it is rebased (`TASK-370`).
- The check-failure rule keys on the status the ticket had when the run chose it, not its status after the claim: pass that status from `_run_ticket` through `_run_check` into `_handle_check_failure` instead of reading it from the worktree. A check failure on a ticket chosen as `todo` still moves it to `error` with no agent, as today.
- Accepted consequences: a setup or check failure on a ticket chosen as `todo` now records `todo → doing` then `doing → error`, two commits on `main`. A `_worktree` failure after the claim leaves the ticket `doing`, which the next run resumes.
- On an existing branch whose ticket copy is older than `main`'s, the claim now succeeds, but the agent's own ticket writes in the worktree are still refused until the branch is rebased onto `main` (`TASK-370`). Today the run fails at the claim, so this is no worse.
- In `docs/plan/next-action-and-runner.md`, replace "runs `setup` there, then claims a `todo` ticket on its branch" with "claims a `todo` ticket in the main checkout, then makes or reuses its worktree and runs `setup` there", and "Work mode runs `setup` and `check` before claiming" with "Work mode claims a `todo` ticket in the main checkout before preparing the worktree, then runs `setup` and `check`".

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_claims_on_main.py`, in the style of `tests/test_review_merge.py`. Commit order uses `GIT_COMMITTER_DATE`, as `tests/test_store.py` does. No property: one fixed ordering change in a runner that drives real Git and agent processes.

## Acceptance Criteria

- [ ] A work run on a `todo` ticket with no branch: the claim commit (`todo → doing`) is on `main` and is an ancestor of the new branch, and the fake agent records the worktree ticket as `doing`; the test fails before the change
- [ ] The `TASK-343` state, made with real commits (branch created and its ticket edited, then a later edit to the ticket committed on `main`): a work run on the `todo` ticket claims it on `main` without the `latest committed version` error and the fake agent starts; the test fails before the change
- [ ] A ticket chosen as `todo` whose `setup` fails, and one whose `check` fails, both end `error` with no agent started; a `doing` ticket whose `check` fails still starts the agent
- [ ] `docs/plan/next-action-and-runner.md` has the two replacement sentences from the Description, and `make check` passes

## History

- 2026-11-18T09:50:52Z witty-ginger-falcon → planning
- 2026-11-18T09:52:30Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:54:52Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:54:54Z witty-ginger-falcon: changed description, acceptance criteria
