---
title: Record the repair outcome in the ticket worktree, not on `main`
status: doing
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket that has a branch is written only on that branch. After a repair agent session on an `error` ticket, the agent has already set the ticket to `review` or `blocked` in its worktree (`_status_after_agent` reads it there). `_run_ticket` in `src/chitty/run.py` then writes the same status again on `main` through `main_repo.edit(..., skip_current_version=True)`, adding the note `Repair agent determined that human action is required.` for `blocked`. That second copy is what makes `main` and the branch diverge.

Decisions:

- Remove the `main_repo.edit` after a repair session. `main` gets no commit from a repair.
- For `blocked`, write the `Repair agent determined that human action is required.` note in the worktree instead, appended after the agent's own note (the repair guide and `Repo.edit` already require one for `blocked`), through a `Repo` rooted at the worktree with the main checkout's config (`Repo(worktree, main_repo.config)`, as `_run_ticket` already builds for review). The runner requires `autocommit`, so this is its own ticket-only commit after the agent's commits. Leave the owner unchanged, as today. Write it inside the existing `try` in `_run_ticket`, so a failure is handled like any other runner error (`_record_ticket_error`; where that writes is `TASK-382`'s). For `review`, write nothing more: the agent's own edit is the record.
- A repair on an `error` ticket with no branch: `_worktree` makes the branch from `main` first, so the repair is written on that new branch and `main` stays `error`; by the rule, the branch is then the ticket.
- The existing repair checks stay as they are: an invalid status after repair, and a return to `review` with no change beyond ticket files, still raise `RepairError`.
- Out of scope: runner errors (`TASK-382`) and the claim (`TASK-384`).

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_repair_on_branch.py`, in the style of `tests/test_run_repair_mode.py`, inheriting `TestRunContinue` from `tests/test_run_continue.py` as that file does. The fake repair agent commits a code change and sets the ticket's status in the worktree; for `blocked` it runs `chitty edit <ID> -s blocked --note <text>` (the runner puts `chitty` on `PATH`), so it has its own note. No existing test is expected to need changing; `make check` shows any that do. No property: two fixed outcomes (`review`, `blocked`), each tested, driving real Git and runner processes.

## Acceptance Criteria

- [ ] A repair run whose fake agent commits a code change and moves the ticket to `review` in the worktree leaves `git rev-parse main` unchanged and the ticket file on the branch at `review`, with no runner commit after the agent's; `chitty show <ID>` in the main checkout reports `review`; the test fails before the change
- [ ] A repair run whose fake agent moves the ticket to `blocked` with its own note leaves `main` unchanged, and the ticket on the branch is `blocked`, keeps the agent's note, has `Repair agent determined that human action is required.` appended after it, and its owner unchanged; the test fails before the change
- [ ] Regression guard: the existing `RepairError` cases in `tests/test_repair_requires_work.py` (invalid status after repair, `review` with only ticket-file changes) still pass
- [ ] A repair run on an `error` ticket with no branch creates `task-<n>` from `main`, records the outcome on it, and leaves `main` unchanged; `make check` passes

## History

- 2026-11-18T16:20:12Z lively-quartz-crane → backlog
- 2026-11-18T16:24:45Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:24:45Z lively-quartz-crane backlog → planning
- 2026-11-18T16:25:03Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:26:38Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:26:38Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:26:53Z lively-quartz-crane planning → todo
- 2026-11-18T16:29:25Z lively-quartz-crane todo → cold-read
- 2026-11-18T16:31:17Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:31:17Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:31:29Z lively-quartz-crane planning → todo
- 2026-11-18T22:12:26Z vivid-russet-raven todo → doing
