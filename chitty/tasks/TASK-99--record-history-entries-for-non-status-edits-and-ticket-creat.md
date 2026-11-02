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

- [ ] Every `edit` that changes anything other than status appends one History entry naming what changed
- [x] Reference rewrites, `chitty fix` repairs and `delete` append no History entries; tests prove it
- [ ] `PLAN.md` documents which writes record History
- [x] Creating a ticket by `add`, `suggest` or inbox pull records the creating actor in its first History entry; an import keeps the source's creation entry and appends an entry naming the importing actor and time

## Plan

Finish the branch: (1) merge each `edit`'s non-status changes into one History entry, with actions joined by `; `, and have `review_work` split them; (2) skip History when an `edit` changes nothing, so a no-op edit still writes no file; (3) rewrite the `PLAN.md` History section so it matches the behaviour; (4) regression tests first, then `make check` and `npm test` in the worktree `.venv`.

## Notes

Blocked pending independent review and completion of `TASK-55`, which supplies the History format this follow-on ticket extends.

`TASK-55` is done; unblocked.

Blocked: imports preserve the legacy source-created date in their initial History entry, while criterion 2 requires the creating actor in that first entry. A human must choose whether import should replace source provenance with the importing actor/timestamp or retain source provenance and append a separate actor-attributed creation event.

Needs a product decision on the import History compatibility policy described above; no safe default preserves both requirements.

Import decision by the human, 2026-11-02: keep the original creation entry and append a separate actor-attributed import entry. Where the original entry needs an actor and none is known, use an artificial actor such as `import` or `unknown`.

Review failed: acceptance criterion 2 requires tests proving that reference rewrites, chitty fix repairs, and delete append no History entries. The changed suite has no History assertions for these three paths; add focused regression tests for each, then rerun make check.

Review failed: criterion 3 is unmet. PLAN.md still says History records only creation plus status/archive transitions; it does not document deliberate non-status edits, add/suggest/inbox/import creation, or the reference-rewrite, fix, and delete exclusions. Update the specification and rerun make check.

Unticked criteria 1 and 3: one `edit` wrote up to three History lines (`changed …`, `wrote the plan`, `ticked acceptance criteria`), and `PLAN.md` lines 171-176 still described only creation and status History. Picked up by lively-otter on `task-99-history-tests`.

## Summary

Added focused regression assertions that dependency rewrites during move, chitty fix repairs, and delete-mode archiving leave the dependent task History unchanged. Verified the targeted tests, make check, and npm test in a worktree-local `.venv`.

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
- 2026-11-02T11:36:13Z jolly-falcon: changed summary
- 2026-11-02T11:36:13Z jolly-falcon doing → review
- 2026-11-02T11:45:52Z kind-otter: changed notes
- 2026-11-02T11:45:52Z kind-otter review → doing
- 2026-11-02T12:58:37Z lively-otter: changed acceptance criteria, notes
- 2026-11-02T12:58:37Z lively-otter: wrote the plan
