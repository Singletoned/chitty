---
title: Stray empty uv-*.lock files block status changes in worktrees
status: backlog
created: 2026-11-12
---

## Description

In the echonomicon project, two tickets (TASK-113 on 2026-11-11 and TASK-128 on 2026-11-12) were stuck because their worktree held an untracked, empty, unheld file named like `uv-b0ec4981ce3f0b41.lock` at the worktree root. The agent refused to move the ticket to review because the worktree was not clean, blocked the ticket, and asked a human about the file. `lsof` showed no process holding it, and deleting it was safe both times. It is presumably left by `uv` runs with a project or cache lock in the working directory. Ideas: have `chitty run` ignore or clean root-level `uv-*.lock` files that no process holds before its cleanliness check, or tell agents in `chitty guide work` that such a file may be removed after checking `lsof`. Evidence: the TASK-128 note in echonomicon (`chitty show TASK-128`).

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-12T21:43:34Z kind-yellow-vole → backlog
- 2026-11-12T21:43:35Z kind-yellow-vole: changed notes
