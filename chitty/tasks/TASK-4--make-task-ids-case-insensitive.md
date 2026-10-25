---
title: Accept task IDs in any case; upper-case is canonical
status: done
labels:
  - ids
depends_on:
  - TASK-10
created: 2026-10-25
---

## Description

Accept human-1, Human-1 and HUMAN-1 anywhere an ID is typed (CLI and MCP, via ids.resolve). Upper-case stays canonical: filenames, depends_on and output always use it. Because depends_on values must be upper-case by definition, chitty check reports lower- or mixed-case entries and chitty fix (TASK-10) rewrites them.

## Acceptance Criteria

- [x] Every command and MCP tool accepts IDs in any case
- [x] chitty always writes IDs upper-case (filenames, depends_on, output)
- [x] chitty check reports depends_on entries that are not upper-case
- [x] chitty fix rewrites them upper-case

## Plan

Canonicalize user-entered IDs in TaskId.parse while allowing stored dependency spellings through parsing. Have check diagnose noncanonical depends_on values and extend fix to rewrite only those values, so CLI/MCP writes and filenames remain upper-case.

## Notes

check has been read-only until now. Making it fix files means deciding how the fix interacts with autocommit and autoformat (TASK-8), and what the exit status is when it fixed something but found nothing else.

Superseding the note above: check stays read-only; fixing belongs to chitty fix (TASK-10).

Question: Should lower-case filenames be accepted too? Answer: no. They are stored identifiers and must remain canonical; case-insensitivity applies to typed ID arguments and legacy depends_on values that fix can safely rewrite.

Verified: typed full IDs canonicalize through the central resolver; stored lower-case depends_on values are diagnosed by check and repaired by fix; upper-case filenames remain required. make check passes.
