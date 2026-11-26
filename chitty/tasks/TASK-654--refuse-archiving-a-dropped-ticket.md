---
title: Refuse archiving a `dropped` ticket
status: todo
priority: high
depends_on:
  - TASK-599
parent: TASK-599
created: 2026-11-24
---

## Description

`TASK-599` added the `dropped` status. Decided with the person, 2026-11-22: dropped tickets stay visible, so we can see whether agents drop tickets that should have been built (when they may go, by age, is `TASK-600`). Today `chitty archive <id>` archives a dropped ticket.

Change, in `src/chitty/store.py`: `chitty archive <id>` on a `dropped` ticket raises `ChittyError` `<id> is dropped; dropped tickets are kept visible and cannot be archived` before any file is changed, in every `archive` mode. Check it in `Repo._set_archived` only when `archived` is true (restoring a dropped ticket archived before this change still works), after the existing planning-claim check, and before `_delete_done`'s `is not done` check, so `archive = "delete"` gives the same message.

`chitty archive` with no ID already archives only `done` tickets; the regression test pins that (extend `test_archive_all_done_tasks` in `tests/test_cli.py` with a `dropped` ticket, or add one beside it).

Tests: add to the existing `tests/test_status_dropped.py`, writing the `dropped` fixture by replacing `status:` in the file. For the delete mode, use the `tests/support.py` `CONFIG` with `archive = "delete"` added. No property: two fixed modes.

Out of scope: `chitty edit` rules for dropping (`TASK-652`), `chitty add` (`TASK-653`).

## Acceptance Criteria

- [ ] `chitty archive TASK-1` on a `dropped` ticket is refused with `TASK-1 is dropped; dropped tickets are kept visible and cannot be archived`, the file byte-identical and still in `chitty/tasks/`, with `archive = "move"` and with `archive = "delete"`; both fail before the change
- [ ] Regression tests: `chitty archive` with no ID archives a `done` ticket and leaves a `dropped` one in `chitty/tasks/`; `make check` passes

## History

- 2026-11-24T08:45:30Z sunny-hazel-gannet → planning
- 2026-11-24T09:27:49Z sunny-hazel-gannet: changed dependencies
- 2026-11-24T22:32:19Z sunny-hazel-gannet: changed notes
- 2026-11-26T19:00:44Z zesty-ginger-newt: changed notes
- 2026-11-26T19:00:44Z zesty-ginger-newt planning → to-plan
- 2026-11-26T19:00:59Z zesty-ginger-newt: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-26T19:00:59Z zesty-ginger-newt to-plan → planning
- 2026-11-26T19:01:13Z zesty-ginger-newt planning → cold-read
- 2026-11-26T19:05:32Z zesty-ginger-newt: changed description
- 2026-11-26T19:05:32Z zesty-ginger-newt cold-read → planning
- 2026-11-26T19:05:43Z zesty-ginger-newt planning → todo
