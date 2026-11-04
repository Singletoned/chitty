---
title: Refuse to land a ticket unless both checkouts are clean
status: todo
priority: medium
depends_on:
  - TASK-131
parent: TASK-106
created: 2026-11-04
---

## Description

Second part of landing, after `TASK-131`. Before landing, refuse with a message and a non-zero exit, changing nothing, if the main checkout is not on branch `main` or is not clean, using the existing `git.require_clean`, which includes untracked files. Ignored files are allowed. Also refuse if the ticket's worktree has uncommitted changes, including untracked files; otherwise they would only surface when removal fails, after landing.

Out of scope: landing at the start of a run.

## Acceptance Criteria

- [ ] Tests show the main checkout on another branch, with a tracked change and with an untracked file, and uncommitted files in the ticket's worktree, each refusing and changing nothing
- [ ] A test shows an ignored file not preventing landing

## History

- 2026-11-04T15:11:35Z mellow-newt → todo
