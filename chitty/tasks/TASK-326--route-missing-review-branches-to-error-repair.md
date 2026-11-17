---
title: Route missing review branches to error repair
status: doing
parent: TASK-318
created: 2026-11-13
---

## Description

A missing ticket branch at review is a runner error, not a human block. Today `_run_session` in `src/chitty/run.py` (the `action.mode == "review"` block that writes `Review blocked: ... has no branch`) sets the ticket to `blocked` with owner `human`. Seen on `TASK-318`, whose work had landed by hand and whose branch was then gone.

Change it to set the ticket to `error`, leaving the owner as it is, with a note in the `Runner error (<phase>): ...` form `_record_ticket_error` writes, phase `review`, naming the missing branch and saying no worktree exists. `_record_ticket_error` itself refuses when the worktree is gone, so write this note directly with `main_repo.edit(..., Edit(status="error", note=..., skip_verdicts=True, skip_current_version=True))`, as `_record_ticket_error` does. No agent starts.

Repair needs no new selection: `chitty run --errors` already selects `error` tickets (action mode `work`), and for a ticket with no branch `_worktree` creates the branch from `main` as the repair agent's workspace. Guarding against that empty branch passing as recovered work is `TASK-364`.

In `src/chitty/roles/repair.md`, qualify the first bullet (`inspect the preserved branch and worktree`) with "if they exist", and add after it: if the ticket branch was missing, find the original implementation commit (reflogs, other worktrees, `git log --all` commits whose `Task:` trailer is exactly this ID and that change files other than the ticket file, since every Chitty edit also carries the trailer), reset the branch to it, note the commit ID and the evidence, then set `review`; if none can be found, set `blocked` and say what was searched.

Update `docs/plan/next-action-and-runner.md`: add the missing branch to the list under "Before a review", and say in the error-note bullet that this note has no worktree.

Files: `src/chitty/run.py`, `src/chitty/roles/repair.md`, `docs/plan/next-action-and-runner.md`, `tests/test_review_merge.py` (rename and rewrite `test_missing_review_branch_blocks_ticket_and_is_not_selected_again`), and `tests/test_guide_repair_missing_branch.py`.

Out of scope: a leftover `.worktrees/task-<n>` directory with no branch.

No property test: one fixed state (branch and worktree missing at review), which needs real git and the runner; the guide change is fixed text.

## Acceptance Criteria

- [ ] In `tests/test_review_merge.py`: a review whose branch and worktree are gone prints `TASK-1: review → error`, starts no agent, keeps the owner unchanged, and leaves a note containing `Runner error (review)`, `TASK-1` and `task-1`. `chitty run --mode review` and `chitty run --mode work` then exit 3 with no next ticket, and `chitty next` finds nothing; `chitty run --errors` selects it. Fails before the change (today it prints `review → blocked`).
- [ ] Flattened `guide("repair")` contains `if they exist`, `was missing`, `exactly this ID`, and `say what was searched`; tested in `tests/test_guide_repair_missing_branch.py`, which fails before the change.
- [ ] `docs/plan/next-action-and-runner.md` lists the missing branch under "Before a review". `make check` passes.

## Plan

Update missing-review-branch handling to record a review-phase runner error directly without changing owner or starting an agent. Add regression coverage proving error selection/availability behavior and repair-guide recovery instructions, update the runner plan, run focused tests before the fix where possible, then format and run make check.

## History

- 2026-11-13T23:27:55Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:26Z mellow-umber-lapwing: changed title, description
- 2026-11-14T09:23:16Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-14T09:23:16Z mellow-umber-lapwing backlog → planning
- 2026-11-14T09:23:19Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:23:19Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:27:58Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-14T09:27:58Z mellow-umber-lapwing cold-read → planning
- 2026-11-14T09:28:01Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:32:06Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:32:06Z mellow-umber-lapwing cold-read → planning
- 2026-11-16T17:04:24Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:04:26Z open-russet-eel: changed owner
- 2026-11-16T17:04:26Z open-russet-eel planning → cold-read
- 2026-11-16T17:08:35Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:08:35Z open-russet-eel cold-read → planning
- 2026-11-16T17:08:37Z open-russet-eel: changed owner
- 2026-11-16T17:08:37Z open-russet-eel planning → todo
- 2026-11-17T17:18:03Z nimble-amber-urchin todo → doing
- 2026-11-17T17:18:13Z nimble-amber-urchin: wrote the plan
