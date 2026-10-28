---
title: Accept notes when adding a task
status: todo
created: 2026-10-28
---

## Description

chitty add has no --note, so recording context or a decision at creation takes a second chitty edit call (and a second autocommit). Accept repeatable --note on add, matching edit, so a task can be created complete in one write.

## Acceptance Criteria

- [ ] chitty add accepts repeatable --note TEXT, with each note appended as its own paragraph in Notes, the same as edit
- [ ] The MCP add tool accepts notes too, with the behaviour in store.py
- [ ] Creating a task with notes takes one write and one autocommit
- [ ] Tests cover one note, several notes, and none; README and PLAN.md list the option

## History

- 2026-10-28 → todo
