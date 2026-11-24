---
title: renumber and move both refuse to give a provisional ID a sequential number on main
status: backlog
labels:
  - bug
created: 2026-11-24
---

## Description

In echonomicon (chitty 0.7.1), tickets added on a plan/ branch got provisional IDs (TASK-BCHE6A, TASK-VY5XWK). After fast-forwarding main, `chitty renumber chitty/tasks/TASK-BCHE6A--*.md` failed with 'TASK-BCHE6A is used by no other file; use `chitty move` to give it a new ID', and `chitty move TASK-BCHE6A tasks` failed with 'TASK-BCHE6A is already in context tasks'. renumber's help says it renumbers provisional tickets on main, so either renumber should accept a provisional ID with no clash on main, or move should allow the same context. Today there is no way to do it, so the planner kept the provisional IDs.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-24T22:21:23Z zesty-coral-newt → backlog
- 2026-11-24T22:21:24Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:36Z zesty-coral-newt: changed labels
