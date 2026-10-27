---
title: "Name the task in commit messages with a Task: line"
status: done
labels:
  - docs
created: 2026-10-27
---

## Description

Commits end with a Task: TASK-12 line so git log --grep TASK-12 finds a ticket's code for review. Convention only: no checks or hooks enforce it.

## Acceptance Criteria

- [x] Agent guide, AGENTS.md block and README describe the Task: line convention
- [x] Autocommit adds a Task: line naming each task the commit writes
- [x] Tests cover the autocommit Task: lines

## Plan

Inspect autocommit message construction and its tests. Add task trailers for every written task while preserving existing subjects, document the convention in the generated and repository guides plus README, then run make check.

## Notes

Reviewed: independent review confirmed Task trailers cover single, multi-write, and batch autocommits.

## Summary

Autocommit now appends Task trailers for every task it writes. Updated the guide, AGENTS.md, README, PLAN, and integration tests; make check passes.

## History

- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
