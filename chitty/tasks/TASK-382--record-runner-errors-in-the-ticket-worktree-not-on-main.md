---
title: Record runner errors in the ticket worktree, not on `main`
status: cold-read
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket that has a branch is written only on that branch. Today `_record_ticket_error` in `src/chitty/run.py` writes `error` and its `Runner error (<phase>)` note through `main_repo.edit(..., skip_current_version=True)`, so the copy on `main` and the copy on the branch diverge. That stopped `chitty run --loop` repeatedly on 2026-11-17 (`TASK-343`, `TASK-364`).

Decisions:

- `_record_ticket_error` writes through a `Repo` rooted at the ticket worktree and built with the main checkout's config (`Repo(worktree, main_repo.config)`), because the branch's config may be missing or changed, as `_prepare_review` already allows. The edit commits on the ticket branch. `main` gets no commit.
- It still raises, as today, when the worktree is gone.
- Every caller passes the worktree it already has: `setup` failure in work and in review mode, an agent-phase `ChittyError`, and `_handle_check_failure`, which stops calling `git.main_checkout` (work is planned to run in containers, where the runner may not be able to reach the main checkout from the worktree).
- Keep `skip_current_version=True` on this edit for now: a branch can still hold an older copy than `main` until `TASK-385` removes the guard.
- Only the ticket file is committed. Other uncommitted files in the worktree stay uncommitted.
- Out of scope: the review-with-no-branch handoff in `_run_ticket`, which stays on `main` (with no branch, `main` is authoritative); the repair outcome write (`TASK-383`); the claim (`TASK-384`).

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_errors_on_branch.py`, in the style of `tests/test_run_claims_on_main.py`, inheriting `CliTestCase` from `tests/test_cli.py` as that file does. Update existing runner tests that expect the error commit on `main`. No property: a fixed set of four failure phases, each listed in the criteria and each tested; the behaviour drives real Git and runner processes.

## Acceptance Criteria

- [ ] For each phase (work-mode `setup` failure, review-mode `setup` failure, a work-mode `check` failure on a ticket chosen as `todo`, and a `ChittyError` raised during the agent phase) the run leaves `git rev-parse main` unchanged, and the newest commit on the ticket branch sets the ticket to `error` with a `Runner error (<phase>)` note; each case fails before the change
- [ ] After each of those runs, `chitty show <ID>` in the main checkout reports status `error`, and `next_action` (`src/chitty/store.py`) on the main checkout with `modes=("errors",)` returns that ticket
- [ ] An unrelated uncommitted file in the worktree is still uncommitted after the error is recorded, and `_handle_check_failure` no longer calls `git.main_checkout`; `make check` passes

## History

- 2026-11-18T16:20:11Z lively-quartz-crane → backlog
- 2026-11-18T16:24:12Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:24:12Z lively-quartz-crane backlog → planning
- 2026-11-18T16:24:19Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:24:24Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:25:01Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:26:40Z lively-quartz-crane: changed description
