---
title: Run tickets in `cold-read` as `chitty run` jobs
status: backlog
depends_on:
  - TASK-268
parent: TASK-259
created: 2026-11-11
---

## Description

- Mode `cold-read` picks tickets in status `cold-read`, with the usual run lock.
- Create branch `cold-read/<id>/<n>` from `main` (`<n>` is the next free number) in `.worktrees/cold-read-<id>`, run `setup`, then the agent with `chitty guide cold-read <ID>` as `{prompt}`. A command without `{prompt}` fails with a clear error for this mode.
- After the agent exits, `chitty run` commits whatever is left, force-adding `.docs/` (gitignored, so a report never reaches `main`), and removes the worktree but keeps the branch.
- The read fails if its branch changes anything under `chitty/`.
- `chitty run` moves the ticket to `planning` on `main`. The planner polls for that.

## History

- 2026-11-11T13:21:08Z vivid-yellowhammer → backlog
