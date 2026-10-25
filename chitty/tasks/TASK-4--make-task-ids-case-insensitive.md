---
title: Accept task IDs in any case; upper-case is canonical
status: todo
labels:
  - ids
created: 2026-10-25
---

## Description

Accept human-1, Human-1 and HUMAN-1 anywhere an ID is typed (CLI and MCP, via ids.resolve). Upper-case stays canonical: filenames, depends_on and output always use it. Because depends_on values must be upper-case by definition, chitty check fixes lower- or mixed-case entries in place rather than only reporting them.

## Acceptance Criteria

- [ ] Every command and MCP tool accepts IDs in any case
- [ ] chitty always writes IDs upper-case (filenames, depends_on, output)
- [ ] chitty check rewrites non-upper-case depends_on entries to upper-case and reports what it fixed
- [ ] PLAN.md records that check can now write files

## Notes

check has been read-only until now. Making it fix files means deciding how the fix interacts with autocommit and autoformat (TASK-8), and what the exit status is when it fixed something but found nothing else.
