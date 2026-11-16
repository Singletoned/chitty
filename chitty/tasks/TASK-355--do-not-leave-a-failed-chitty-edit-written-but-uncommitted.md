---
title: Do not leave a failed chitty edit written but uncommitted
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16 in `.worktrees/task-318`: `chitty edit TASK-318 --depends-on TASK-325 --depends-on TASK-326 --note ...` printed `depends_on TASK-326: no such task` and exited non-zero, but had already written the dependencies, note and history entry to the ticket file, leaving it modified and uncommitted. An edit that fails validation must leave the file unchanged.

## History

- 2026-11-16T10:29:24Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:55Z intrepid-coral-raven backlog → planning
