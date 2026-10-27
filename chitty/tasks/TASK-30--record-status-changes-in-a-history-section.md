---
title: Record status changes in a History section
status: done
labels:
  - format
created: 2026-10-27
---

## Description

So people can see a ticket bouncing back and forth, every status change is recorded in the ticket itself, in a ## History section at the end that chitty writes and people don't edit. Example line: - 2026-10-28 review → doing

## Acceptance Criteria

- [x] Every status change (edit -s, archive/delete, pull, import, CLI and MCP) appends one line: - YYYY-MM-DD old → new
- [x] chitty add writes the first line (- YYYY-MM-DD → todo, or → backlog)
- [x] Existing tickets without History get the section at their next status change; nothing is backfilled
- [x] History is the last section, parses and round-trips through prettier and mdformat unchanged; check reports a malformed History
- [x] show and --json include the history
- [x] Tests, PLAN.md and README updated

## Plan

Inspect task parsing, mutation paths, presentation, and validation. Add a canonical trailing History section that records all status transitions across shared store operations. Cover CLI and MCP surfaces through shared behaviour; add formatter round-trip and malformed-history tests; update documentation and run make check.

## Summary

Added validated, trailing History entries for task creation, status edits, archiving/restoring, import, pull, CLI, and MCP. Updated docs and tests; make check passes.

## History

- 2026-10-27 doing → done
