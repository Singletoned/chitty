---
title: Let planners close a ticket already delivered on main without branch surgery
status: backlog
created: 2026-11-24
---

## Description

In echonomicon on 2026-11-23, TASK-160 and TASK-164 were in `planning` but their work had already landed on `main` through other commits (`022f1db`, `0426d87`). Closing them was awkward:

- `chitty edit -s done` from `planning` is refused ("setting status done requires -s review first"), and sending to `review` would make a reviewer fail the "fails on the current code" criteria.
- `chitty archive` on `main` is refused because the ticket's latest version is on its ticket branch ("run Chitty in worktree ...").
- Archiving in the ticket worktree only commits on that branch. For TASK-160 (ticket commits only) a rebase plus fast-forward of `main` worked. For TASK-164 the branch also held superseded code, so the planner copied the archived file to `main`; then every `chitty list` failed with "ticket `TASK-164` changed on both `task-164` and `main`", even though both files were byte-identical. It only cleared after saving the branch head under `refs/superseded/task-164` and resetting the branch to `main`.

Suggestions: (1) a supported "close as already done or superseded" path from `planning` (for example `chitty archive --reason ...` run from `main`, which records the note and retires or flags the ticket branch); (2) treat identical ticket content on two branches as not conflicting, rather than failing every command.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-24T22:21:44Z zesty-coral-newt → backlog
- 2026-11-24T22:21:45Z zesty-coral-newt: changed notes
