---
title: Record status changes in a History section
status: todo
labels:
  - format
created: 2026-10-27
---

## Description

So people can see a ticket bouncing back and forth, every status change is recorded in the ticket itself, in a ## History section at the end that chitty writes and people don't edit. Example line: - 2026-10-28 review → doing

## Acceptance Criteria

- [ ] Every status change (edit -s, archive/delete, pull, import, CLI and MCP) appends one line: - YYYY-MM-DD old → new
- [ ] chitty add writes the first line (- YYYY-MM-DD → todo, or → backlog)
- [ ] Existing tickets without History get the section at their next status change; nothing is backfilled
- [ ] History is the last section, parses and round-trips through prettier and mdformat unchanged; check reports a malformed History
- [ ] show and --json include the history
- [ ] Tests, PLAN.md and README updated
