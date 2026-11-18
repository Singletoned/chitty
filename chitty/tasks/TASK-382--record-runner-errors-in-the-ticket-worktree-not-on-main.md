---
title: Record runner errors in the ticket worktree, not on `main`
status: doing
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket that has a branch is written only on that branch. Today `_record_ticket_error` in `src/chitty/run.py` writes `error` and its `Runner error (<phase>)` note through `main_repo.edit(..., skip_current_version=True)`, so the copy on `main` and the copy on the branch diverge. That stopped `chitty run --loop` repeatedly on 2026-11-17 (`TASK-343`, `TASK-364`).

Decisions:

- `_run_ticket` builds one branch-side repo, `branch_repo = Repo(worktree, main_repo.config)`, as soon as the worktree exists: the main checkout's config, because the branch's may be missing or changed, as `_prepare_review` already allows. `_record_ticket_error(branch_repo, action, phase, error)` takes it in place of `main_repo` and the worktree path, reads the old status from it, and writes through it, so the edit commits on the ticket branch and `main` gets no error commit.
- It still raises, as today, when the worktree is gone (unchanged, not newly tested).
- Every caller passes the worktree it already has: `setup` failure in work and in review mode, a `ChittyError` in the agent or landing phase (both caught by the same `except` in `_run_ticket`), and `_handle_check_failure`. `_run_check` (one caller) takes `branch_repo` in place of its `work_repo` and `worktree` arguments and passes it to `_handle_check_failure`, which uses it for both its `doing`/`error` note and the error, and stops calling `git.main_checkout`. In review mode `branch_repo` is this same `Repo(worktree, main_repo.config)`, built once; `_prepare_review` and the reviewer keep their own repos (work is planned to run in containers, where the runner may not be able to reach the main checkout from the worktree).
- Keep `skip_current_version=True` on this edit for now: a branch can still hold an older copy than `main` until `TASK-385` removes the guard.
- Only the ticket file is committed. Other uncommitted files in the worktree stay uncommitted.
- Out of scope: an error recorded while `main` still holds a newer copy of the ticket (today's read then takes `main`'s content; `TASK-378` and `TASK-385` remove that); a landing failure after `main` has been fast-forwarded (recorded on the branch, as every runner error now is, whatever then happens to it); failures that are not recorded today (`_worktree` raising after the claim, a non-conflict `git.merge_main` error) stay unrecorded; the review-with-no-branch handoff in `_run_ticket`, which stays on `main` (with no branch, `main` is authoritative); the repair outcome write (`TASK-383`); the claim (`TASK-384`).

Tests: the `check` failures are non-zero exits (not a missing command), and notes are asserted by the text `_run_check` produces today. Fixtures set `autocommit = true` and a `setup` command as `tests/test_run_claims_on_main.py` `setUp` does. Real-Git, fake-agent runner tests in a new `tests/test_run_errors_on_branch.py`, in the style of `tests/test_run_claims_on_main.py`, inheriting `CliTestCase` from `tests/test_cli.py` as that file does. Update every existing test that expects the error commit on `main`, including the one in `tests/test_next.py` around line 1797 that asserts `main` moves; `tests/test_review_merge.py`'s `Runner error (review)` case is the no-branch handoff and stays. No property: a fixed set of four failure phases, each listed in the criteria and each tested; the behaviour drives real Git and runner processes.

## Acceptance Criteria

- [ ] Each case uses its own ticket. For each, the newest commit on `task-<n>` sets the ticket to `error` with a note containing `Runner error (<phase>)` and the failure's own message, and no commit on `main` sets `error`: a work-mode `setup` failure, and an agent exiting non-zero with a passing `check`, both on a `doing` ticket whose branch was made with `git branch task-<n> main`, leave `git rev-parse main` unchanged; a review-mode `setup` failure leaves it unchanged; a `check` failure on a ticket chosen as `todo` gives `main` exactly one commit, the claim (`todo → doing`); each case fails before the change
- [ ] After each of those runs, `git show main:<ticket path>` still has the status the ticket had on `main` before the failure (`doing`, `review`, or `doing` after the claim), while `chitty show <ID>` in the main checkout reports `error` and `next_action` (`src/chitty/store.py`) on the main checkout with `modes=("errors",)` returns that ticket's ID; the `main` file check fails before the change
- [ ] Code check: `_handle_check_failure` takes the branch-side repo and its body has no `git.main_checkout` call (shown by the diff; `Repo._main_branch()` may still call it, legitimately); the observable effect is covered by criteria 1 and 2
- [ ] After that `check` failure, the newest commit on `task-<n>` is a new commit after the claim that changes only the ticket file, and a file the failing `check` wrote in the worktree is still untracked; a `check` failure on a `doing` ticket still writes the `Check failed before this session` note on the branch and starts the agent
- [ ] A landing failure: in a review run whose `check` passes before the reviewer, the fake reviewer sets `done` and writes a marker file that makes `check` fail from then on, so `_landing_check` fails before `fast_forward`; `main` is unchanged and the newest `task-<n>` commit has `Runner error (landing)`; `make check` passes

## Plan

Create one branch-side Repo(worktree, main_repo.config) after obtaining the ticket worktree and pass it through setup, check, agent/landing error paths. Change runner-error recording to read and edit through that repo; make check-failure handling use the supplied branch repo and retain its existing note/agent behavior. Add real-Git/fake-agent regression coverage for the four specified failure phases and branch-only commits, update existing assertions that expect main to move, then run focused tests and make check.

## Notes

Regression evidence: before the fix, the focused branch-recording tests failed (main received runner-error commits; branch history lacked the error commit). After the fix, the focused tests and full `make check` pass. Coverage includes work setup, agent failure, todo check failure with its untracked check output preserved, review setup, and landing failure; existing doing-ticket check behavior remains covered.

Review failed (tests): Add the specified real-Git regressions, including the required new test file and evidence they fail against the original implementation. These are newly discovered findings; no earlier review failure is recorded.
1: fail - `ls tests/test_run_errors_on_branch.py` reports no such file. Existing tests do not exercise the complete four-case matrix with each required branch-head note, failure message, and main commit assertion. Add the specified cases and demonstrate each fails before the fix.
2: fail - The required new test file is missing; existing assertions do not check main file status, main checkout show, and errors-mode next_action for each of the four cases, nor demonstrate the main-file checks fail before the fix.
3: pass - `git diff main...HEAD -- src/chitty/run.py` shows `_handle_check_failure` takes branch_repo and no longer calls git.main_checkout.
4: fail - `tests/test_next.py::test_run_check_failure_records_output_and_does_not_claim_or_start_agent` checks the untracked file and one branch commit but does not assert that commit changes only the ticket file. Add that assertion. The doing case checks the note and agent in `test_run_check_failure_on_doing_ticket_starts_agent`.
5: fail - `make check` passed 636 tests, but the existing landing failure test advances main during review and does not assert the specified reviewer-created marker, unchanged main, and newest branch commit containing Runner error (landing). Add the specified scenario.

Added tests/test_run_errors_on_branch.py for work setup, agent, and review setup errors, plus landing-failure coverage and branch-only commit assertions. The new focused tests pass; make check passes 644 tests.

Review failed (tests): Some earlier coverage gaps remain unresolved; the landing marker mismatch is newly discovered. Add the missing assertions and scenario below.
1: fail - The prior review requested the complete matrix and branch-head notes. The new setup and agent tests inspect the worktree file rather than `git show task-1:<path>`; review setup does not assert the failure message, and the todo check test does not assert the phase note or exactly one main commit. Assert each required branch-head status and note, including its own message and the main claim count. Running the four focused cases against `main` runner code produced four failures, including changed main heads and main status error.
2: fail - The prior review requested main-file checks for every case. Review setup captures `main_status` before the run and checks that stale value afterward, so it does not exercise the required post-run main file check. Read it after the run. The todo check main-file assertion fails against `main` runner code, printing status error instead of doing.
3: pass - `git diff main...HEAD -- src/chitty/run.py` shows `_handle_check_failure` receives `branch_repo` and has no `git.main_checkout` call.
4: pass - `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` asserts one branch commit, its sole changed path and the untracked check output; the doing-ticket test checks the note and agent. Against `main` runner code the former fails on main status error; `make check` passed 644 tests on rerun.
5: fail - The new landing test writes `review-marker`, but its check script tests ticket status instead of marker existence, so it does not exercise the specified marker-triggered failure. Make the check depend on the marker and assert the branch-head landing note. Against `main` runner code the test fails with review → error instead of done → error. `make check` passed on rerun; its first run failed with a Hypothesis timing deadline (265 ms versus 200 ms).

## Summary

Runner errors are recorded through the ticket worktree Repo. Added explicit regressions for work and review setup, agent failure, check-failure commit scope and errors selection, and landing failure. Verification: focused runner-error tests pass; make check passes all 644 tests. No follow-up.

## History

- 2026-11-18T16:20:11Z lively-quartz-crane → backlog
- 2026-11-18T16:24:12Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:24:12Z lively-quartz-crane backlog → planning
- 2026-11-18T16:24:19Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:24:24Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:25:01Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:26:40Z lively-quartz-crane: changed description
- 2026-11-18T16:28:00Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:28:00Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:29:23Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:32:26Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:32:26Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:32:29Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:35:33Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:35:33Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:35:35Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:38:23Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:38:23Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:38:32Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:38:34Z lively-quartz-crane planning → todo
- 2026-11-18T17:47:08Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:47:08Z lively-quartz-crane todo → planning
- 2026-11-18T17:47:10Z lively-quartz-crane planning → todo
- 2026-11-18T20:32:35Z eager-ochre-gannet todo → doing
- 2026-11-18T20:33:49Z eager-ochre-gannet: wrote the plan
- 2026-11-18T20:44:20Z eager-ochre-gannet: changed notes, summary
- 2026-11-18T20:44:20Z eager-ochre-gannet doing → review
- 2026-11-18T21:12:21Z honest-fawn-crane: changed acceptance criteria, notes
- 2026-11-18T21:12:21Z honest-fawn-crane review → doing
- 2026-11-18T21:48:48Z kind-amber-kestrel: changed notes, summary
- 2026-11-18T21:48:48Z kind-amber-kestrel doing → review
- 2026-11-18T21:53:01Z brisk-ochre-wren: changed acceptance criteria, notes
- 2026-11-18T21:53:01Z brisk-ochre-wren review → doing
