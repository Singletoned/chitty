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

- Parent: cold reads run as `chitty run` jobs, as decided with the human on 2026-11-11. The children, smallest first, carry the work.
- A read runs on branch `cold-read/<id>/<n>`, which ticket discovery skips. The report is `.docs/cold-read/<ID>.md` in that branch, and is deleted with the branch once it is no longer needed.
- `chitty run` does every mechanical step (branch, worktree, commit, status back to `planning`). The agent only reads, implements and reports.
- The planner polls Chitty for the ticket to return to `planning`.

## History

- 2026-11-11T10:37:04Z vivid-yellowhammer → backlog
- 2026-11-11T10:44:22Z vivid-yellowhammer: changed description
- 2026-11-11T13:21:11Z vivid-yellowhammer: changed description
