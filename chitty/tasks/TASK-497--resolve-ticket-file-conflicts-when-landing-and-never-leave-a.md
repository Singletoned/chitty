---
title: Resolve ticket-file conflicts when landing, and never leave a worktree mid-rebase
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-20 the review loop rebased `task-384` onto `main` to land it, hit a conflict in `chitty/tasks/TASK-384--*.md` (the runner had claimed the ticket on `main` while the branch existed, and the branch had its own ticket commits), and exited with `duplicate section 'Notes'`, leaving the worktree in an interactive rebase with 13 commits remaining. Nobody was told; the loop just stopped. A planner aborted the rebase and rebuilt the branch by hand as `main` + one code commit + the branch ticket file (TASK-378 needed the same by hand earlier). Since the ticket branch copy is authoritative while the branch exists (`docs/plan/ticket-state.md` on `plan/ticket-state`), landing could take the branch copy for that ticket file on conflict, or squash the branch to `main` + code + final ticket before rebasing. Either way a failed rebase should be aborted, the ticket marked with the conflicting paths, and the loop should continue.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:01Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:02Z nimble-umber-gannet: changed notes
