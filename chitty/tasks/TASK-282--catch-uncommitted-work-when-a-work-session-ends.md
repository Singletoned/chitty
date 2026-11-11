---
title: Catch uncommitted work when a work session ends
status: backlog
labels:
  - bug
created: 2026-11-11
---

## Description

- TASK-167 went to `review` three times with its changes verified but never committed. Each review start found the dirty worktree and blocked it (`_block_dirty_review` in `src/chitty/run.py`), and the next work session repeated the mistake.
- After a work agent exits, if the ticket is in `review` and its worktree has uncommitted changes, `chitty run` should move it back to `doing` with a note listing the files and saying to commit them, instead of leaving it for the review to block to a human.

## Acceptance Criteria

- [ ] A `chitty run` whose fake work agent moves the ticket to `review` and leaves an uncommitted file ends with the ticket in `doing` and a note naming the file. It fails today.

## History

- 2026-11-11T15:57:40Z vivid-yellowhammer → backlog
