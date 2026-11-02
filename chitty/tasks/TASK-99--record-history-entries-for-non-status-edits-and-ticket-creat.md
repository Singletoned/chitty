---
title: Record History entries for non-status edits and ticket creation
status: todo
priority: medium
depends_on:
  - TASK-55
created: 2026-11-02
---

## Description

Second half of the `HUMAN-8` scope decision. Once `TASK-55` gives History entries a UTC timestamp and actor, also append an entry for every other deliberate change: flags, fields, ticked criteria, plan, notes and summary from `edit`, and creation by `add`, `suggest`, inbox pull and imports. Do not record reference rewrites in other tickets after a move or rename, `chitty fix` repairs, or `delete`.

## Acceptance Criteria

- [ ] Every `edit` that changes anything other than status appends one History entry naming what changed
- [ ] Reference rewrites, `chitty fix` repairs and `delete` append no History entries; tests prove it
- [ ] `PLAN.md` documents which writes record History
- [ ] Creating a ticket by `add`, `suggest` or inbox pull records the creating actor in its first History entry; an import keeps the source's creation entry and appends an entry naming the importing actor and time

## Plan

Inventory every task-creation and edit write path. Generalize History events so each deliberate non-status edit records one concise actor-attributed description, update creation paths to record their actor, and preserve the explicit no-history paths. Add focused store, inbox/import, and CLI tests; update `PLAN.md`; run `make check` and `chitty fix`.

## Notes

Blocked pending independent review and completion of `TASK-55`, which supplies the History format this follow-on ticket extends.

`TASK-55` is done; unblocked.

Blocked: imports preserve the legacy source-created date in their initial History entry, while criterion 2 requires the creating actor in that first entry. A human must choose whether import should replace source provenance with the importing actor/timestamp or retain source provenance and append a separate actor-attributed creation event.

Needs a product decision on the import History compatibility policy described above; no safe default preserves both requirements.

Import decision by the human, 2026-11-02: keep the original creation entry and append a separate actor-attributed import entry. Where the original entry needs an actor and none is known, use an artificial actor such as `import` or `unknown`.

## History

- 2026-11-02 → todo
- 2026-11-02T08:52:55Z pi-worker todo → blocked
- 2026-11-02T09:34:51Z lively-otter blocked → todo
- 2026-11-02T09:44:51Z amber-stoat todo → doing
- 2026-11-02T09:44:51Z amber-stoat: wrote the plan
- 2026-11-02T09:45:27Z amber-stoat doing → blocked
- 2026-11-02T10:59:08Z lively-otter blocked → todo
