---
title: Warn when chitty show reads a ticket that a plan branch has changed
status: backlog
created: 2026-11-24
---

## Description

Seen 2026-11-24: a planner on branch `plan/branch-race-setup-commit` (worktree `.worktrees/plan-branch-race-setup-commit`) started a `cold-reader` subagent for `TASK-464` and named the worktree in its prompt. The reader ran `chitty guide cold-read` and `chitty show TASK-464` from the main checkout. `ticket_source` looks only at `main` and `task-<n>` branches, so the reader got the stale `main` copy with no Acceptance Criteria, nothing warned it, and it reported a missing criteria section as its most serious finding. The read was wasted and had to be redone.

Suggestion: when `chitty show <ID>` (and `chitty guide cold-read <ID>`) runs outside the branch that holds the newest copy, and a local `plan/...` branch changed that ticket since it split from `main`, print a warning naming the branch and its worktree (`git worktree list`). This fits the 2026-11-23 decision on `TASK-602` to warn generously rather than refuse, and touches the open question in `TASK-340` about how cold readers read a planning branch copy. Alternatively, `chitty guide cold-read <ID>` could print the checkout to run in when the ticket was last changed on a `plan/` branch.

## Notes

Suggestion origin: chitty

Archived 2026-11-25: folded into TASK-602, whose warnings name other branches that changed the ticket; a note there asks it to cover plan/ branches and name the worktree.

## History

- 2026-11-24T22:21:40Z zesty-coral-newt → backlog
- 2026-11-24T22:21:41Z zesty-coral-newt: changed notes
- 2026-11-25T20:46:23Z golden-coral-stoat: changed notes
- 2026-11-25T20:46:32Z golden-coral-stoat backlog → archived
