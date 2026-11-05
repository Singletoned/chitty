---
title: Commit the old path when `edit --title` renames a task under autocommit
status: doing
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

With `autocommit = true`, `chitty edit <ID> --title ...` commits the renamed file but leaves the old path's deletion staged and uncommitted, so `HEAD` holds both paths until someone commits the deletion. Seen on `TASK-106`, 2026-11-03: commit `d8cf115` added the new path only. Cross-branch task reads use committed state, so they may see the stale copy too.

Root cause, reproduced in a scratch repository: `git mv` has already removed the old path from the index, and `git diff --cached --name-only` at `src/chitty/git.py:30` detects the rename and prints only the new name, so `commit --only` leaves the deletion staged. The likely fix is `--no-renames` there, as `require_clean` already uses.

## Acceptance Criteria

- [ ] A test renames a task under autocommit and shows `git status --porcelain` empty and the commit removing the old path, with an unrelated staged file left out of the commit

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Added the root cause, and a check that the fix does not sweep in other staged files. Rejected: the other batch writes and the failure path, which go through the same line.

## History

- 2026-11-03T10:28:43Z lively-panda → backlog
- 2026-11-04T19:36:33Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T19:36:34Z mellow-newt backlog → todo
- 2026-11-05T07:42:14Z jolly-crane todo → doing
