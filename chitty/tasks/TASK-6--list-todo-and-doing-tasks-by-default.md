---
title: Make chitty list show active tasks across all contexts
status: todo
labels:
  - cli
created: 2026-10-25
---

## Description

Plain `chitty list` should show every todo and doing task in every context, but not backlog ideas (TASK-5). It currently shows all non-archived tasks in the default context only, including done. Filtering should be easy: e.g. repeatable -c and -s, and a way to include ideas and done tasks.

## Acceptance Criteria

- [ ] Plain chitty list shows todo and doing tasks from every context
- [ ] Backlog ideas and done tasks are hidden unless asked for
- [ ] Filtering by context and status is easy, and documented in --help
