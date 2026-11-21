---
title: Edit existing tickets in planning worktrees
status: planning
parent: TASK-376
created: 2026-11-21
---

## Description

Allow multiple planners to revise existing tickets on separate Git branches without sharing the main checkout. On a local branch named `plan/...`, use that worktree's copy of an existing ticket as the authority for `chitty edit` and `chitty show`, including when a cold reader inspects the draft there. Non-planning checkouts and the runner must not adopt or pick up the draft before it lands. The branch is the draft: use ordinary Git to integrate it, not an overlay or a new publish command.

Before editing, check visible competing branches, including configured main, the ticket's own branch and other planning branches. A competing committed change to the same ticket since the pairwise merge base blocks the edit and the error names the branch. A branch that merely carries the same copy, or changes only unrelated files or tickets, is not a conflict. Account for ticket renames, moves and deletions by ID, not just the draft's current filename. This check only sees refs the checkout knows about; concurrent drafts can still race and must be reconciled when integrating. Preserve the current behavior outside `plan/...` and do not expand the write exception to `move`, archive or other commands as part of this ticket.

A `task-<id>` branch existing is not evidence of active work. If the runner currently holds a lock for that ID, warn the planner on stderr that work or review is in progress and they should coordinate. A held lock alone does not block an otherwise permitted edit, and the conflict check still blocks a competing committed change regardless of lock state. Manual work without a runner lock is not detectable by this warning.

Planning pointers: `Repo.edit`, `Repo._choose_source` and the working-tree parser in `src/chitty/store.py`; `git.branch_tips` and `git.changed_since_split` in `src/chitty/git.py`; `locks.holder` in `src/chitty/locks.py` and normal stderr reporting in `src/chitty/cli.py`. Refine the ref-selection and conflict fixtures before moving to `todo`. Use real Git worktrees and a real held runner lock, verify error cases preserve bytes and HEAD, and run regression tests before and after implementation. Do not launch a real worker or reviewer to test the warning.

## Acceptance Criteria

- [ ] In a `plan/...` worktree a planner edits an existing local ticket via `chitty edit`; `show` and the cold-read workflow use that draft. The same ID from main still shows the main copy, and the edit commit is confined to the planning branch.
- [ ] A visible competing branch changing the same ticket since the split makes `edit` fail with that branch named and leaves the planning worktree and HEAD unchanged. A branch that carries the ticket unchanged or changes a different ticket does not block the edit.
- [ ] An existing but idle `task-<id>` branch does not warn on its own. A held runner lock for that ID warns on stderr and allows the edit if there is no competing change; releasing the lock removes the warning.

## History

- 2026-11-21T22:26:20Z eager-ginger-adder → backlog
- 2026-11-21T22:26:38Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T22:26:38Z eager-ginger-adder backlog → planning
