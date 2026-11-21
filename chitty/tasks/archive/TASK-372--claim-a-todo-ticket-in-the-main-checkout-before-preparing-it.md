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

- [x] A work run on a `todo` ticket with no branch: the claim commit (`todo → doing`) is on `main` and is an ancestor of the new branch, and the fake agent records the worktree ticket as `doing`; the test fails before the change
- [x] The `TASK-343` state, made with real commits (branch created and its ticket edited, then a later edit to the ticket committed on `main`): a work run on the `todo` ticket claims it on `main` without the `latest committed version` error and the fake agent starts; the test fails before the change
- [x] A ticket chosen as `todo` whose `setup` fails, and one whose `check` fails, both end `error` with no agent started; a `doing` ticket whose `check` fails still starts the agent
- [x] `docs/plan/next-action-and-runner.md` has the two replacement sentences from the Description, and `make check` passes

## Plan

In `src/chitty/run.py`, capture the selected status and, for work-mode `todo`, claim through `main_repo.edit` before preparing the worktree. Remove the worktree claim and pass the selected status through check handling so failure decisions retain the pre-claim behavior. Add real-Git fake-agent regression coverage in `tests/test_run_claims_on_main.py`, including main ancestry, stale-ticket commits, and todo/doing setup/check outcomes. Update the two runner descriptions in `docs/plan/next-action-and-runner.md`; run focused tests and `make check`.

## Notes

Regression evidence: `tests.test_run_claims_on_main` fails against the pre-change runner and passes with the fix. Verification: `make check` passes (629 tests), and `chitty fix` completes with existing repository warnings only.

Review failed (tests): Strengthen the stale-history regression so it reproduces the original claim failure and fails for that behavior, not only for the changed run summary. This is newly discovered; there are no earlier review failures.
1: pass - The focused test passes; with main version of run.py and the summary assertion removed it errors because the branch tip is not an ancestor of main.
2: fail - The focused test passes with the fix, but when run against main version of run.py with only the doing-to-error stdout assertion removed it also passes: the fake agent starts and no latest committed version error occurs. Construct and verify the TASK-343 history so the old claim actually fails, then assert the claim is committed on main and the agent starts with the fix.
3: pass - The focused setup-failure, todo check-failure, and doing check-failure tests all report ok and exercise the required outcomes.
4: pass - The diff contains both requested documentation replacements; make check reports 629 tests OK, ruff clean, and pyright 0 errors.

Stale-history regression verified: running the focused test with run.py from the parent of the implementation commit fails with the original `latest committed version is on branch main` error before the fake agent starts. The fixed runner passes and records todo → doing on main.

Reviewed: The previous stale-history regression finding is resolved; no new defects found.
1: pass - `python -m unittest tests.test_run_claims_on_main -v` reports both tests OK; the prior review verified the ancestry assertion fails without the change, and the current test also fails against the parent runner.
2: pass - The focused tests report OK; with `run.py` from `321c7647^`, the stale-history test fails with `latest committed version is on branch main`, resolving the earlier review finding.
3: pass - The three focused `TestNext` setup failure, todo check failure and doing check failure tests report OK.
4: pass - The diff contains both requested documentation replacements; `make check` reports 629 tests OK, Ruff clean and Pyright 0 errors.

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

Its code landed (claim on `main`) and passed review on 2026-11-18. Superseded by `TASK-384`, which claims on the new branch instead under `docs/plan/ticket-state.md`. Archived.

## Summary

Strengthened the stale-history regression with deterministic author and committer dates and assertions that the main checkout records the claim and the fake agent starts. Verified the regression fails with the pre-change runner and passes with the fix; `python -m unittest tests.test_run_claims_on_main -v` passes (2 tests), and `make check` passes (629 tests). `chitty fix` completes with existing warnings only. No follow-ups.

## History

- 2026-11-18T09:50:52Z witty-ginger-falcon → planning
- 2026-11-18T09:52:30Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:54:52Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:54:54Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:54:56Z witty-ginger-falcon planning → todo
- 2026-11-18T10:36:15Z eager-teal-crane todo → doing
- 2026-11-18T10:36:35Z eager-teal-crane: wrote the plan
- 2026-11-18T10:41:09Z eager-teal-crane: changed notes
- 2026-11-18T10:52:01Z eager-teal-crane: replaced notes; changed summary; ticked acceptance criteria
- 2026-11-18T10:52:01Z eager-teal-crane doing → review
- 2026-11-18T10:54:40Z friendly-dusky-wren: changed acceptance criteria, notes
- 2026-11-18T10:54:40Z friendly-dusky-wren review → doing
- 2026-11-18T11:00:53Z vivid-hazel-wren: changed notes, summary; ticked acceptance criteria
- 2026-11-18T11:00:53Z vivid-hazel-wren doing → review
- 2026-11-18T11:03:34Z upbeat-teal-ibis: changed notes
- 2026-11-18T11:03:34Z upbeat-teal-ibis review → done
- 2026-11-18T15:47:44Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:44Z witty-ginger-falcon done → planning
- 2026-11-18T16:26:06Z lively-quartz-crane: changed notes
- 2026-11-21T22:55:40Z lively-zinc-newt planning → archived
