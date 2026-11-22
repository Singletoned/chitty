---
title: Decide how dependents, releases and guides treat a `dropped` ticket
status: backlog
depends_on:
  - TASK-599
created: 2026-11-22
---

## Description

Follow-up to `TASK-599`, which adds the `dropped` status and changes nothing else. Decide and build: (1) a ticket depending on a dropped ticket: today it stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py` around line 2292, `src/chitty/selection.py`); probably show it as blocked by a dropped dependency so a planner re-plans it, rather than letting it run. (2) `scripts/release_version.py`: `blocks-release` counts a ticket as resolved only when `done` (line 21); a dropped `blocks-release` ticket should probably not block a release; `needs-minor` counts only `done` (line 30), which is right for dropped. (3) The role guides (`src/chitty/roles/`, `src/chitty/guide.md`): say to drop a ticket with a reason instead of passing it through `review`.

## Notes

Decided with the person, 2026-11-22: `chitty archive` must not delete tickets until they are some days old, so we can see whether agents drop tickets that should have been built and they then disappear. `TASK-599` leaves `dropped` tickets out of `chitty archive` entirely; this ticket decides when `done` and `dropped` tickets may be archived or deleted by age (a module-level constant for the number of days), including `archive = "delete"`, where `_delete_done` also removes dependency references and so would silently unblock dependents of a dropped ticket.

## History

- 2026-11-22T22:09:28Z plucky-umber-wren → backlog
- 2026-11-22T22:49:08Z plucky-umber-wren: changed notes
