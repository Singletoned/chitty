---
title: Accept task IDs in any case; upper-case is canonical
status: todo
labels:
  - ids
depends_on:
  - TASK-10
created: 2026-10-25
---

## Description

Accept human-1, Human-1 and HUMAN-1 anywhere an ID is typed (CLI and MCP, via ids.resolve). Upper-case stays canonical: filenames, depends_on and output always use it. Because depends_on values must be upper-case by definition, chitty check reports lower- or mixed-case entries and chitty fix (TASK-10) rewrites them.

## Acceptance Criteria

- [ ] Every command and MCP tool accepts IDs in any case
- [ ] chitty always writes IDs upper-case (filenames, depends_on, output)
- [ ] chitty check reports depends_on entries that are not upper-case
- [ ] chitty fix rewrites them upper-case

## Notes

check has been read-only until now. Making it fix files means deciding how the fix interacts with autocommit and autoformat (TASK-8), and what the exit status is when it fixed something but found nothing else.

Superseding the note above: check stays read-only; fixing belongs to chitty fix (TASK-10).
