---
title: Define the scope for TASK-55 actor history
status: done
created: 2026-11-01
---

## Description

Decide whether “every write” in `TASK-55` includes imports, inbox pulls, `chitty fix`, move/reference rewrites, and archive-delete cleanup; alternatively split the work into independently verifiable tickets.

## Notes

Decided by the human, 2026-11-02: record History for deliberate changes to a ticket, not side effects. In scope: every `edit` (status, flags, fields, `--check`, plan, notes, summary), creation by `add`, `suggest`, inbox pull and imports, and `archive`. Out of scope: rewriting references in other tickets after a move or rename, `chitty fix` repairs, and `delete` (the file is gone; Git keeps the record). Split: `TASK-55` adds time and actor to the History entries written today (status change, archive); `TASK-99` adds entries for the remaining edits and for creation.

Scope agreed; split into TASK-55 and TASK-99

## History

- 2026-11-01 → todo
- 2026-11-02 todo → review
- 2026-11-02 review → done
- 2026-11-05T14:44:56Z vivid-wren done → archived
