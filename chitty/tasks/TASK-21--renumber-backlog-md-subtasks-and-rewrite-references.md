---
title: Renumber Backlog.md subtasks and rewrite references
status: todo
labels:
  - import
depends_on:
  - TASK-20
parent: TASK-19
created: 2026-10-27
---

## Description

Across a whole converted set: give subtasks flat IDs, set parent, and rewrite every old ID. Pure functions; no files written.

## Acceptance Criteria

- [ ] TASK-n keeps its number; TASK-n.m gets the next free number in the context with parent TASK-n
- [ ] Every old ID in depends_on and in body text is rewritten to the new ID
- [ ] Each converted task gets a note recording its Backlog.md ID
- [ ] Tests cover subtask numbering, reference rewriting in frontmatter and body, and references to IDs that don't exist
