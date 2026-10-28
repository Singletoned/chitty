---
title: Accept notes when adding a task
status: done
created: 2026-10-28
---

## Description

chitty add has no --note, so recording context or a decision at creation takes a second chitty edit call (and a second autocommit). Accept repeatable --note on add, matching edit, so a task can be created complete in one write.

## Acceptance Criteria

- [x] chitty add accepts repeatable --note TEXT, with each note appended as its own paragraph in Notes, the same as edit
- [x] The MCP add tool accepts notes too, with the behaviour in store.py
- [x] Creating a task with notes takes one write and one autocommit
- [x] Tests cover one note, several notes, and none; README and PLAN.md list the option

## Plan

Thread repeatable add notes from CLI and MCP through the existing store add path, reuse task note rendering, add CLI/MCP/autocommit tests and documentation, then run make check.

## Notes

Ready for review: make check passes.

## Summary

add now accepts repeatable notes through CLI, MCP, and store, retaining one creation write. Verified with make check.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → done
