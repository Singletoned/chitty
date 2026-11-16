---
title: Route missing review branches to error repair
status: cold-read
owner: open-russet-eel
parent: TASK-318
created: 2026-11-13
---

## Description

A missing ticket branch at review is a runner error, not a human block. Today `_run_session` in `src/chitty/run.py` (the `action.mode == "review"` block that writes `Review blocked: ... has no branch`) sets the ticket to `blocked` with owner `human`. Seen on `TASK-318`, whose work had landed by hand and whose branch was then gone.

Change it to set the ticket to `error`, leaving the owner as it is, with a note in the `Runner error (<phase>): ...` form `_record_ticket_error` writes, phase `review`, naming the missing branch and saying no worktree exists. `_record_ticket_error` itself refuses when the worktree is gone, so write this note directly with `main_repo.edit` (`status="error"`, `skip_verdicts=True`). No agent starts.

Repair needs no new selection: `chitty run --errors` already selects `error` tickets, and for a ticket with no branch `_worktree` creates the branch from `main` as the repair agent's workspace. That empty branch must not pass as recovered work: when a repair session ends with the ticket in `review` and its branch has no commits that are not on `main`, raise `RepairError` saying the repair returned the ticket to review with no commits beyond `main`. This check applies to every repair, since a review of a branch with nothing on it has nothing to review.

Add to `src/chitty/roles/repair.md` one bullet: if the ticket branch was missing, find the original implementation commit (reflogs, `git log --all --grep 'Task: <ID>'`, other worktrees), reset the branch to it, note the commit ID and the evidence, then set `review`; if none can be found, set `blocked` and say what was searched.

Files: `src/chitty/run.py`, `src/chitty/roles/repair.md`, `tests/test_review_merge.py` (rename and rewrite `test_missing_review_branch_blocks_ticket_and_is_not_selected_again`), and a new `tests/test_repair_missing_branch.py` using the fake agents of `tests/test_review_merge.py` or `install_fake_pi` in `tests/test_next.py`. No real model session.

No property test: the states are a small fixed set (branch missing at review; repair ending in `review` with commits, in `review` without commits, in `blocked`), each listed in the criteria and tested, and each needs real git branches and a subprocess agent.

## Acceptance Criteria

- [ ] In `tests/test_review_merge.py`: a review whose branch and worktree are gone prints `TASK-1: review → error`, starts no agent, keeps the owner unchanged, and leaves a note containing `Runner error (review)`, `TASK-1` and `task-1`. `chitty run --mode review` and `chitty run --mode work` then exit 3 with no next ticket, and `chitty next` finds nothing; `chitty run --errors` selects it. Fails before the change (today it prints `review → blocked`).
- [ ] In `tests/test_repair_missing_branch.py`, after the missing-branch error: a fake repair agent that resets `task-1` to a commit kept from the deleted branch and sets `review` ends with `TASK-1` in `review`; one that sets `review` without adding commits makes `chitty run --errors` exit non-zero with the `RepairError` text, and the ticket stays `error`; one that sets `blocked` ends in `blocked`. The no-commits case fails before the change.
- [ ] `src/chitty/roles/repair.md` has the missing-branch bullet described above. `make check` passes.

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
