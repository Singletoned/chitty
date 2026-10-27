---
title: "Name the task in commit messages with a Task: line"
status: todo
labels:
  - docs
created: 2026-10-27
---

## Description

Commits end with a Task: TASK-12 line so git log --grep TASK-12 finds a ticket's code for review. Convention only: no checks or hooks enforce it.

## Acceptance Criteria

- [ ] Agent guide, AGENTS.md block and README describe the Task: line convention
- [ ] Autocommit adds a Task: line naming each task the commit writes
- [ ] Tests cover the autocommit Task: lines
