---
title: Claim a `todo` ticket in the main checkout before preparing its worktree
status: cold-read
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
- The check-failure rule (`_handle_check_failure`) keys on the status the ticket had when the run chose it, not its status after the claim: a check failure on a ticket chosen as `todo` still moves it to `error` with no agent, as today.

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_claims_on_main.py`, in the style of `tests/test_review_merge.py`. Commit order uses `GIT_COMMITTER_DATE`, as `tests/test_store.py` does. No property: one fixed ordering change in a runner that drives real Git and agent processes.

## Acceptance Criteria

- [ ] A work run on a `todo` ticket with no branch commits the claim on `main` (`todo → doing`) before the worktree exists, and the new branch's ticket file is `doing`; the test fails before the change
- [ ] The `TASK-343` case: a `todo` ticket whose branch exists, with a later edit to the ticket on `main`, is claimed without the `latest committed version` error and the agent starts; the test fails before the change
- [ ] A work run on a `todo` ticket whose `check` fails moves it to `error` with no agent started, as today
- [ ] `docs/plan/next-action-and-runner.md` says where the claim happens, and `make check` passes

## History

- 2026-11-18T09:50:52Z witty-ginger-falcon → planning
- 2026-11-18T09:52:30Z witty-ginger-falcon planning → cold-read
