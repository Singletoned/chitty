---
title: Commit the old path when `edit --title` renames a task under autocommit
status: backlog
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

With `autocommit = true`, `chitty edit <ID> --title ...` commits the renamed file but leaves the old path's deletion staged and uncommitted, so `HEAD` holds both paths until someone commits the deletion. Seen on `TASK-106`, 2026-11-03: commit `d8cf115` added the new path only. Cross-branch task reads use committed state, so they may see the stale copy too.

## Acceptance Criteria

- [ ] A test renames a task under autocommit and asserts the commit removes the old path, leaving `git status` clean

## History

- 2026-11-03T10:28:43Z lively-panda → backlog
