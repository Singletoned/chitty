---
title: Record History entries for non-status edits and ticket creation
status: blocked
priority: medium
depends_on:
  - TASK-55
created: 2026-11-02
---

## Description

Second half of the `HUMAN-8` scope decision. Once `TASK-55` gives History entries a UTC timestamp and actor, also append an entry for every other deliberate change: flags, fields, ticked criteria, plan, notes and summary from `edit`, and creation by `add`, `suggest`, inbox pull and imports. Do not record reference rewrites in other tickets after a move or rename, `chitty fix` repairs, or `delete`.

## Acceptance Criteria

- [ ] Every `edit` that changes anything other than status appends one History entry naming what changed
- [ ] Creating a ticket by `add`, `suggest`, inbox pull or import records the creating actor in its first History entry
- [ ] Reference rewrites, `chitty fix` repairs and `delete` append no History entries; tests prove it
- [ ] `PLAN.md` documents which writes record History

## Notes

Blocked pending independent review and completion of `TASK-55`, which supplies the History format this follow-on ticket extends.

## History

- 2026-11-02 → todo
- 2026-11-02T08:52:55Z pi-worker todo → blocked
