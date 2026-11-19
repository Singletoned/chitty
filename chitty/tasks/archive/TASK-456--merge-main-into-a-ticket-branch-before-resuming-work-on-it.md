---
title: Merge main into a ticket branch before resuming work on it
status: backlog
created: 2026-11-19
---

## Description

Seen 2026-11-14 on TASK-321. The runner recorded the ticket's `error` on `main` while its branch `task-321` and worktree still existed. A planner then moved it `error` to `doing` (also a write on `main`, allowed because `main` held the latest version). The next `chitty run` ran the check in `.worktrees/task-321` and failed with: `Error: TASK-321's latest committed version is on branch main; run Chitty in worktree /Users/singletoned/src/singletoned/chitty`. So any ticket whose error or repair handoff is written on `main` cannot be resumed in its existing worktree until someone merges `main` into the branch by hand (done here as merge commit `279f3c4`, taking `main`'s side of the ticket-file conflict). Before a work session on an existing branch, `chitty run` already merges `main` for reviews; it could do the same for work (or at least when the ticket's latest version is on `main`), resolving the ticket file to `main`'s version, which is the later one. The worktree may hold uncommitted worker changes, which must be preserved.

## Notes

Suggestion origin: chitty

Archived as covered by `TASK-370` (rebase the ticket branch onto `main` before every work session).

## History

- 2026-11-19T20:55:32Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:33Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:13Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:17Z sunny-white-dormouse backlog → archived
