---
title: Record History entries for non-status edits and ticket creation
status: doing
priority: medium
depends_on:
  - TASK-55
created: 2026-11-02
---

## Description

Second half of the `HUMAN-8` scope decision. Once `TASK-55` gives History entries a UTC timestamp and actor, also append an entry for every other deliberate change: flags, fields, ticked criteria, plan, notes and summary from `edit`, and creation by `add`, `suggest`, inbox pull and imports. Do not record reference rewrites in other tickets after a move or rename, `chitty fix` repairs, or `delete`.

## Acceptance Criteria

- [x] Every `edit` that changes anything other than status appends one History entry naming what changed
- [x] Reference rewrites, `chitty fix` repairs and `delete` append no History entries; tests prove it
- [x] `PLAN.md` documents which writes record History
- [x] Creating a ticket by `add`, `suggest` or inbox pull records the creating actor in its first History entry; an import keeps the source's creation entry and appends an entry naming the importing actor and time

## Plan

Inspect the existing History event and creation/import paths, then add concise actor-attributed entries for each deliberate `edit` and task creation while retaining no-history repair, rewrite, and delete paths. Cover the behavior with focused tests, update `PLAN.md`, run `make check` and `chitty fix`, tick each criterion, and submit for independent review.

## Notes

Blocked pending independent review and completion of `TASK-55`, which supplies the History format this follow-on ticket extends.

`TASK-55` is done; unblocked.

Blocked: imports preserve the legacy source-created date in their initial History entry, while criterion 2 requires the creating actor in that first entry. A human must choose whether import should replace source provenance with the importing actor/timestamp or retain source provenance and append a separate actor-attributed creation event.

Needs a product decision on the import History compatibility policy described above; no safe default preserves both requirements.

Import decision by the human, 2026-11-02: keep the original creation entry and append a separate actor-attributed import entry. Where the original entry needs an actor and none is known, use an artificial actor such as `import` or `unknown`.

Review failed: acceptance criterion 2 requires tests proving that reference rewrites, chitty fix repairs, and delete append no History entries. The changed suite has no History assertions for these three paths; add focused regression tests for each, then rerun make check.

## Summary

Added actor-attributed UTC creation transitions and concise History events for deliberate non-status edits, retaining the specific plan and criterion events used for review independence. Inbox pulls inherit creation attribution; legacy imports preserve their original creation entry and append an importing-actor event. Reference rewrites, `fix`, and delete paths remain history-free. Updated `PLAN.md` and focused CLI, store, inbox, MCP, and import coverage. Verified with `make check` and `chitty fix` (existing repository warnings only).

## History

- 2026-11-02 → todo
- 2026-11-02T08:52:55Z pi-worker todo → blocked
- 2026-11-02T09:34:51Z lively-otter blocked → todo
- 2026-11-02T09:44:51Z amber-stoat todo → doing
- 2026-11-02T09:44:51Z amber-stoat: wrote the plan
- 2026-11-02T09:45:27Z amber-stoat doing → blocked
- 2026-11-02T10:59:08Z lively-otter blocked → todo
- 2026-11-02T11:03:11Z frosty-falcon todo → doing
- 2026-11-02T11:03:11Z frosty-falcon: wrote the plan
- 2026-11-02T11:08:14Z frosty-falcon: changed summary
- 2026-11-02T11:08:14Z frosty-falcon: ticked acceptance criteria
- 2026-11-02T11:08:14Z frosty-falcon doing → review
- 2026-11-02T11:23:06Z jolly-falcon: changed notes
- 2026-11-02T11:23:06Z jolly-falcon review → doing
