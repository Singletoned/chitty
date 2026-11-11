---
title: Run cold reads as `chitty run` jobs
status: backlog
labels:
  - plan-next
depends_on:
  - TASK-255
created: 2026-11-11
---

## Description

- `chitty run` picks up tickets in `cold-read` as queued jobs, like work and review.
- It runs the cold-read role in a worktree, keeps the commit at `refs/cold-read/<ID>/<n>`, and moves the ticket back to `planning`.
- The report goes in that commit as `.docs/cold-read/<ID>.md`, not in ticket notes (TASK-251). It is scratch: the planner deletes it once the findings have outcomes, and it must never reach `main`.

## History

- 2026-11-11T10:37:04Z vivid-yellowhammer → backlog
- 2026-11-11T10:44:22Z vivid-yellowhammer: changed description
