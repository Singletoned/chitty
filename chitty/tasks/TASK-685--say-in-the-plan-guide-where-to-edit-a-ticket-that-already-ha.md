---
title: Say in the plan guide where to edit a ticket that already has a branch
status: backlog
created: 2026-11-24
---

## Description

Seen 2026-11-23 while planning TASK-358, TASK-599, TASK-629 and TASK-632, all returned from `doing` to `planning` by workers. Each has a `task-<n>` branch holding the newest ticket copy. Editing from a `plan/<name>` worktree fails with `planning edit for TASK-358 conflicts with refs/heads/task-358` (`_reject_planning_conflicts` in `src/chitty/store.py`). What worked was running `chitty edit` from that ticket's own worktree (`.worktrees/task-<n>`), which `docs/plan/next-action-and-runner.md` implies ("Ticket files change only on their branch") but `chitty guide plan` never says. Proposal: the error names the worktree to edit from (for example `edit it from .worktrees/task-358`), and `chitty guide plan` says in one line that a ticket with a branch is planned in its worktree. Related cost: on that machine `chitty list -s planning --json` took 38s, and `chitty list -s backlog` passed 120s; TASK-598 (in `error`) covers that.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:47Z zesty-coral-newt → backlog
- 2026-11-24T22:21:48Z zesty-coral-newt: changed notes
