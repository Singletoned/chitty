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

## Plan

Add a regression test in `tests/test_autocommit.py` that enables autocommit, stages an unrelated file, renames a task through `edit --title`, then verifies the old path is deleted by `HEAD`, the task paths are clean, and the unrelated staged file remains uncommitted. Run it first to reproduce the failure. Update `git.commit` to inspect staged paths with rename detection disabled, so both sides of a staged rename are included in the path-limited commit. Run the focused test and `make check`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Added the root cause, and a check that the fix does not sweep in other staged files. Rejected: the other batch writes and the failure path, which go through the same line.

Implementation choice: use Git `--no-renames` when deriving staged paths. This is a narrowly scoped, cheap-to-reverse fix that makes a staged rename expose both its old deletion and new addition; the code comment will explain this.

## History

- 2026-11-03T10:28:43Z lively-panda → backlog
- 2026-11-04T19:36:33Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T19:36:34Z mellow-newt backlog → todo
- 2026-11-05T07:42:14Z jolly-crane todo → doing
- 2026-11-05T07:45:07Z jolly-crane: changed notes; wrote the plan
