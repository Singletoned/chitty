---
title: Renumber Backlog.md subtasks and rewrite references
status: done
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

- [x] TASK-n keeps its number; TASK-n.m gets the next free number in the context with parent TASK-n
- [x] Every old ID in depends_on and in body text is rewritten to the new ID
- [x] Each converted task gets a note recording its Backlog.md ID
- [x] Tests cover subtask numbering, reference rewriting in frontmatter and body, and references to IDs that don't exist

## Plan

Build pure whole-set ID allocation and reference rewriting over ConvertedTask values, then add focused fixtures for subtasks and unresolved references.

## Notes

Added pure flat-ID allocator/reference rewriter regression test covering subtask parent linkage, frontmatter and body references, provenance notes, unknown references, and parser-valid output. Full make check passes.
