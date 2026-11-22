---
title: Read a ticket from the current branch when that branch changed it
status: cold-read
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: Chitty, and cold readers, should read tickets from the branch they are on. This is needed for planning on a branch (`TASK-340`): a planner working in a worktree on a planning branch must see, and be able to edit, the tickets as that branch has them.

Today `ticket_source` (`src/chitty/ticket_source.py`) looks only at `main` and the ticket's own `task-<n>` branch (and its remote-tracking refs). On any other branch, with no ticket branch ahead of `main`, it returns `main`: a planner on a branch reads `main`'s copy of a ticket, not the branch's, even after editing it there.

Decisions, for a checkout on a branch `B` that is neither the configured main branch nor the ticket's own branch (`str(task_id).lower()`), and only when `main` has a tip:

- Work out, for this ticket's paths (as `changed_on_both` in `Repo._choose_source` already gathers them), whether `B` changed them since it split from `main` and whether `main` changed them since the split, with `git.changed_since_split` (`src/chitty/git.py`).
- Pass both answers to `ticket_source` as two new boolean arguments, `current_changed` and `main_changed`, and apply, before today's candidate logic:
  - `B` changed it and `main` did not: `WORKING_TREE`.
  - Neither changed it: `WORKING_TREE` (the copies are the same, and edits then go to `B`).
  - `main` changed it and `B` did not: fall through to today's logic (which gives `main`, or a ticket branch ahead of it).
  - Both changed it: raise `ChittyError` `ticket <id> changed on both <B> and <main>; rebase <B> onto <main>` (backticks around the id and branch names, as the existing `changed on both` message has).
  - If a ticket-branch candidate ahead of `main` exists and `B` changed the ticket, raise `ChittyError` `ticket <id> changed on both <B> and <ticket branch>`; if `B` did not change it, today's logic applies (the ticket branch wins).
- On `main` itself, and on the ticket's own branch, nothing changes.
- Writes follow the chosen source, as today: when the source is `WORKING_TREE`, `chitty edit` on `B` writes and commits there.

Out of scope: landing a planning branch (`TASK-340`), and the cold-read guide's wording (it already tells readers to run `chitty show`; they get this for free when started in the planner's worktree).

Tests:

- Pure, in `tests/test_property_ticket_source.py`: extend the existing property strategies with the two booleans and a current branch that is neither main nor the ticket branch, and assert the table above (including that the old behaviour holds whenever `current_branch` is main or the ticket branch, whatever the booleans).
- Real Git, in a new `tests/test_source_current_branch.py` with `RepoTestCase`: a repository with `TASK-1` and `TASK-2` committed on `main`; a branch `plan-a` in a linked worktree. (a) On `plan-a`, `chitty edit TASK-1 --title "Branch title"`; then `chitty show TASK-1` in that worktree prints `Branch title`, and in the main checkout prints the old title. (b) Commit a change to `TASK-2` on `main`; `chitty show TASK-2` in the `plan-a` worktree prints `main`'s new copy. (c) Then change `TASK-2` on `plan-a` too (commit with `git` directly): `chitty show TASK-2` there fails with the both-changed message. (d) `TASK-3` with a `task-3` branch ahead of `main`: on `plan-a`, `chitty show TASK-3` gives the `task-3` copy.

## Acceptance Criteria

- [ ] The extended property and the four real-Git cases pass; the property and cases (a) and (c) fail before the change; record both runs in a note
- [ ] All existing `ticket_source` and source-copy tests pass unchanged; `make check` passes

## History

- 2026-11-22T22:51:27Z plucky-umber-wren → cold-read
